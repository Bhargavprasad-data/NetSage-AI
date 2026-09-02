import json
import re
import ipaddress
from typing import List, Dict, Optional, Tuple, Any
from . import schemas

def generate_diagnosis_prompt(case: schemas.Case) -> str:
    """
    Constructs a comprehensive diagnosis prompt capturing all case metadata.
    """
    prompt = "Analyze the following network troubleshooting case:\n"
    prompt += f"Hostname: {case.hostname}\n"
    prompt += f"Device Type: {case.device_type}\n"
    prompt += f"Issue Description: {case.issue_description}\n"
    if case.topology_note:
        prompt += f"Topology Note: {case.topology_note}\n"
    if case.expected_fault:
        prompt += f"Reference / Expected Fault: {case.expected_fault}\n"
    if case.osi_layer:
        prompt += f"OSI Layer: {case.osi_layer}\n"
    if case.concept_tag:
        prompt += f"Concept Tag: {case.concept_tag}\n"
    if case.severity:
        prompt += f"Severity: {case.severity}\n"
    if case.show_outputs:
        prompt += f"CLI Outputs:\n{json.dumps(case.show_outputs, indent=2)}\n"
    return prompt

def _extract_interfaces(text: str) -> List[str]:
    """Extracts Cisco interface names (e.g. Gi0/24, FastEthernet0/1, Eth0/0, Po1, Serial0/0/0) from text."""
    phys_pattern = r"\b(?:GigabitEthernet|FastEthernet|TenGigabitEthernet|Ethernet|Port-channel|Serial|Loopback|Gi|Fa|Te|Eth|Po|Se|Lo)\s*\d+(?:[\/\.:]\d+)*\b"
    phys_matches = re.findall(phys_pattern, text, re.IGNORECASE)
    
    seen = set()
    cleaned = []
    for m in phys_matches:
        norm = m.replace(" ", "")
        if norm.lower() not in seen:
            seen.add(norm.lower())
            cleaned.append(norm)

    if not cleaned:
        svi_pattern = r"\b(?:Vlan|VLAN)\s*(\d+)\b"
        for v in re.findall(svi_pattern, text, re.IGNORECASE):
            svi_name = f"Vlan{v}"
            if svi_name.lower() not in seen:
                seen.add(svi_name.lower())
                cleaned.append(svi_name)

    return cleaned

def _extract_vlans(text: str) -> List[str]:
    """Extracts explicitly referenced VLAN numbers from text."""
    matches = re.findall(r"\b(?:vlan|VLAN)\s*(\d+)\b", text)
    seen = set()
    cleaned = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            cleaned.append(m)
    return cleaned

def _extract_cidr_and_ips(text: str) -> Tuple[List[str], List[str]]:
    """Extracts CIDR network/host strings (e.g. 192.168.20.15/24) and standalone IPv4 addresses."""
    cidr_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b"
    cidrs = list(dict.fromkeys(re.findall(cidr_pattern, text)))

    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    all_ips = list(dict.fromkeys(re.findall(ip_pattern, text)))

    return cidrs, all_ips

def _extract_gateway_details(topology_text: str, cidrs: List[str], ips: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Dynamically extracts the (correct_gateway_ip, incorrect_gateway_ip) from topology notes.
    """
    correct_gw: Optional[str] = None
    incorrect_gw: Optional[str] = None

    # 1. Match explicit correct gateway patterns
    correct_match = re.search(
        r"(?:gateway\s+should\s+be|correct\s+gateway\s+is|router\s+interface\s+is|router\s+interface\s+for\s+that\s+subnet\s+is|gateway\s+is\s+supposed\s+to\s+be)\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        topology_text,
        re.IGNORECASE
    )
    if correct_match:
        correct_gw = correct_match.group(1)

    # 2. Match explicit incorrect gateway patterns
    incorrect_match = re.search(
        r"(?:host\s+uses|configured\s+gateway\s+is|uses\s+gateway|default\s+gateway\s+is)\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        topology_text,
        re.IGNORECASE
    )
    if incorrect_match:
        # Only treat as incorrect if different from the correct gateway
        cand = incorrect_match.group(1)
        if cand != correct_gw:
            incorrect_gw = cand

    # 3. If correct_gw not found yet, but we have host CIDR, infer default gateway for that subnet
    if not correct_gw and cidrs:
        try:
            net = ipaddress.ip_network(cidrs[0], strict=False)
            # Default first usable host in host's subnet (e.g. 192.168.20.1)
            correct_gw = str(list(net.hosts())[0])
        except Exception:
            pass

    return correct_gw, incorrect_gw

def _is_pc_or_host(device_type: str, hostname: str) -> bool:
    """Detects if the target device is a PC / End-host / Client versus a Switch / Router."""
    text = f"{device_type or ''} {hostname or ''}".lower()
    return any(k in text for k in ["pc", "host", "endpoint", "client", "workstation", "laptop", "server", "desktop"])

def mock_llm_inference(prompt: str, rule_evidence: list[str], case: schemas.Case) -> schemas.AIDiagnosisBase:
    """
    Intelligent Dynamic Network Troubleshooting Engine.
    Evaluates case description, topology, concept domain, and CLI outputs
    to produce an evidence-backed diagnosis, appropriate confidence, and
    targeted commands appropriate to the device type (PC/Host vs Switch/Router).
    """
    desc = (case.issue_description or "").strip()
    topo = (case.topology_note or "").strip()
    fault = (case.expected_fault or "").strip()
    concept = (case.concept_tag or "").strip()
    osi_in = (case.osi_layer or "").strip()
    host = (case.hostname or "").strip()
    device_type = (case.device_type or "").strip()
    show_outputs = case.show_outputs or {}

    is_host_device = _is_pc_or_host(device_type, host)

    combined_text = f"{desc} {topo} {fault} {concept} {json.dumps(show_outputs)}"

    interfaces = _extract_interfaces(combined_text)
    primary_iface = interfaces[0] if interfaces else None
    vlans = _extract_vlans(combined_text)
    primary_vlan = vlans[0] if vlans else None
    cidrs, ips = _extract_cidr_and_ips(combined_text)

    # 1. Check for genuinely insufficient info
    meaningful_chars = len(desc) + len(topo) + len(concept) + len(show_outputs)
    if meaningful_chars < 15 and not rule_evidence and not fault:
        return schemas.AIDiagnosisBase(
            root_cause="Insufficient diagnostic information provided: Missing network topology details, affected device/interfaces, IP scheme, and CLI outputs to isolate the failure.",
            osi_layer="Layer 3 - Network",
            confidence=schemas.ConfidenceLevel.LOW,
            evidence=[
                "Insufficient data available in case report to identify root cause.",
                "Missing topology notes, interface configuration, and 'show' command outputs."
            ],
            next_commands=[
                "ipconfig /all" if is_host_device else "show ip interface brief",
                "ping 127.0.0.1" if is_host_device else "show interfaces status",
                "tracert <destination>" if is_host_device else "show cdp neighbors",
                "route print" if is_host_device else "show ip route"
            ],
            fix_steps=[
                f"Collect basic device state with {'ipconfig /all' if is_host_device else 'show ip interface brief'}.",
                "Verify network interface connectivity and status.",
                "Re-run diagnosis with updated topology notes and CLI outputs."
            ]
        )

    # 2. Text normalization for semantic analysis
    c_lower = concept.lower()
    f_lower = fault.lower()
    t_lower = topo.lower()
    d_lower = desc.lower()

    # Evidence accumulator
    evidence_list: List[str] = []
    if topo:
        evidence_list.append(f"Topology note indicates: {topo}")
    if desc:
        evidence_list.append(f"Reported symptom: {desc}")
    if concept:
        evidence_list.append(f"Protocol domain: {concept}")
    if rule_evidence:
        for r in rule_evidence:
            evidence_list.append(f"CLI detection: {r}")

    # =========================================================================
    # DYNAMIC DOMAIN EVALUATION
    # =========================================================================

    # -------------------------------------------------------------------------
    # DOMAIN A: DEFAULT GATEWAY ISSUES
    # -------------------------------------------------------------------------
    is_gateway_case = (
        "gateway" in c_lower or "gateway" in f_lower or "gateway" in t_lower or
        "default gateway" in d_lower or "remote lan" in d_lower or "another network" in d_lower or
        ("ping local" in d_lower and "cannot reach" in d_lower) or
        ("same-subnet" in d_lower and "remote" in d_lower) or
        ("inter-vlan" in d_lower and "gateway" in t_lower)
    )

    if is_gateway_case and not ("dhcp" in c_lower and "pool" in t_lower and not ("missing default" in f_lower)):
        osi_layer = "Layer 3 - Network"
        confidence = schemas.ConfidenceLevel.HIGH

        correct_gw, incorrect_gw = _extract_gateway_details(topo, cidrs, ips)

        gw_reason = ""
        # Dynamic Subnet Mismatch Analysis
        if cidrs and len(ips) >= 1:
            try:
                host_net = ipaddress.ip_network(cidrs[0], strict=False)
                outside_ips = [ip for ip in ips if ipaddress.ip_address(ip) not in host_net]
                if outside_ips:
                    bad_gw = outside_ips[0]
                    gw_reason = (
                        f"Incorrect default gateway: Host ({cidrs[0]}) is configured with gateway {bad_gw}, "
                        f"which belongs to a different subnet ({ipaddress.ip_network(f'{bad_gw}/24', strict=False).network_address}/24). "
                        f"The host cannot directly reach or ARP for this gateway, causing all remote LAN and inter-subnet traffic to fail."
                    )
            except Exception:
                pass

        if not gw_reason:
            if "empty" in t_lower or "missing" in f_lower or "not set" in t_lower or "is empty" in t_lower:
                gw_reason = (
                    f"Missing default gateway: Host has a valid local IP configuration but lacks a default gateway address. "
                    f"While local same-subnet communication succeeds, any traffic destined for remote networks is dropped."
                )
            elif "should be" in t_lower or "mismatch" in f_lower or "incorrect" in f_lower or "uses gateway" in t_lower or "router interface is" in t_lower:
                gw_reason = f"Gateway mismatch: {topo}."
            else:
                gw_reason = (
                    f"Default gateway misconfiguration on {host or 'host'}. "
                    f"Traffic to remote destinations cannot be forwarded because the configured gateway is unreachable or mismatched with the local router interface."
                )

        root_cause = gw_reason

        # Generate commands appropriate to device type (PC/Host vs Switch/Router)
        if is_host_device:
            next_cmds = ["ipconfig /all"]
            if correct_gw:
                next_cmds.append(f"ping {correct_gw}")
            next_cmds.append("tracert <remote_destination>")

            fix_steps = [
                "Run `ipconfig /all` on the PC to inspect the current network adapter IPv4 configuration.",
                f"Reconfigure the PC's default gateway address to {correct_gw or '<correct_gateway_ip>'} in the network adapter properties.",
                f"Verify gateway reachability: `ping {correct_gw or '<correct_gateway_ip>'}`.",
                "Verify inter-VLAN / remote network reachability using `tracert <remote_destination>`."
            ]
        else:
            next_cmds = [
                "show ip route",
                "show ip interface brief",
                "show ip arp"
            ]
            if correct_gw:
                next_cmds.append(f"ping {correct_gw}")
            next_cmds.append("show running-config | include ip route|default-gateway")

            fix_steps = [
                f"Verify IP and configure the correct default gateway on the switch: `ip default-gateway {correct_gw or '<correct_gateway_ip>'}`",
                "Ensure the default gateway router / SVI interface is in the UP/UP state: `show ip interface brief`",
                "Verify local ARP resolution for the default gateway: `show ip arp`",
                "Verify the default route on the gateway router: `show ip route`",
                "Test end-to-end connectivity using ping and traceroute to the remote destination."
            ]

        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN B: VLAN & 802.1Q TRUNKING
    # -------------------------------------------------------------------------
    is_vlan_case = "vlan" in c_lower or "vlan" in f_lower or "vlan" in t_lower or "trunk" in f_lower or "trunk" in t_lower

    if is_vlan_case:
        osi_layer = "Layer 2 - Data Link"
        confidence = schemas.ConfidenceLevel.HIGH
        iface_str = primary_iface or "Gi0/24"
        vlan_str = primary_vlan or "10"

        if "trunk" in f_lower or "trunk" in t_lower or "access instead of trunk" in t_lower or "across switch" in d_lower:
            root_cause = (
                f"Trunk/access mismatch: Link {iface_str} between switches is operating in access mode instead of trunk mode, "
                f"blocking VLAN {vlan_str} inter-switch forwarding."
            )
            next_cmds = [
                f"show interfaces {iface_str} switchport",
                "show interfaces trunk",
                "show vlan brief",
                f"show interfaces {iface_str} status"
            ]
            fix_steps = [
                f"Enter interface configuration mode on {host or 'SW2'}: `interface {iface_str}`",
                "Configure trunk encapsulation if required: `switchport trunk encapsulation dot1q`",
                "Set the switchport mode to trunk: `switchport mode trunk`",
                f"Ensure VLAN {vlan_str} is allowed: `switchport trunk allowed vlan add {vlan_str}`",
                "Verify trunk status using `show interfaces trunk` and test connectivity across switches."
            ]
        elif "wrong vlan" in f_lower or "vlan assignment" in f_lower or ("access" in t_lower and "assigned" in t_lower):
            root_cause = (
                f"Incorrect VLAN assignment on access port {iface_str}. "
                f"The port is assigned to the wrong VLAN, isolating the connected host from its intended broadcast domain (VLAN {vlan_str})."
            )
            if is_host_device:
                next_cmds = [
                    "ipconfig /all",
                    "ping <target_host_in_same_vlan>",
                    "arp -a"
                ]
                fix_steps = [
                    f"Identify the connected switchport on the access switch (e.g. {iface_str}).",
                    f"Configure the switchport to access VLAN {vlan_str}: `switchport access vlan {vlan_str}`",
                    "Verify host receives traffic in the correct VLAN broadcast domain."
                ]
            else:
                next_cmds = [
                    f"show interfaces {iface_str} switchport",
                    "show vlan brief",
                    f"show mac address-table interface {iface_str}",
                    f"show running-config interface {iface_str}"
                ]
                fix_steps = [
                    f"Enter interface configuration: `interface {iface_str}`",
                    "Ensure port is in access mode: `switchport mode access`",
                    f"Assign to the correct VLAN: `switchport access vlan {vlan_str}`",
                    "Verify VLAN assignment with `show vlan brief` and verify host connectivity."
                ]
        elif "missing vlan" in f_lower or "vlan does not exist" in t_lower or "not found in current vlan" in t_lower:
            root_cause = (
                f"VLAN {vlan_str} is missing from the switch VLAN database. "
                f"Although access or trunk ports reference VLAN {vlan_str}, the VLAN has not been created locally or is suspended, causing traffic to be dropped."
            )
            next_cmds = [
                "show vlan brief",
                f"show vlan id {vlan_str}",
                "show vtp status",
                "show interfaces trunk"
            ]
            fix_steps = [
                "Enter global configuration mode on the switch: `configure terminal`",
                f"Create the missing VLAN: `vlan {vlan_str}`",
                f"Optionally name the VLAN: `name DATA_VLAN_{vlan_str}`",
                "Exit and verify creation using `show vlan brief`."
            ]
        else:
            root_cause = f"VLAN configuration anomaly on {host or 'switch'}: {topo or desc}."
            next_cmds = [
                "show vlan brief",
                "show interfaces trunk",
                f"show interfaces {iface_str} switchport"
            ]
            fix_steps = [
                "Verify VLAN database: `show vlan brief`",
                "Verify trunk operational status: `show interfaces trunk`",
                "Test connectivity across VLAN hosts."
            ]

        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN C: DNS SERVICE & RESOLUTION
    # -------------------------------------------------------------------------
    if "dns" in c_lower or "dns" in f_lower or "dns" in t_lower or "name resolution" in d_lower or "domain" in d_lower:
        osi_layer = "Layer 7 - Application"
        confidence = schemas.ConfidenceLevel.HIGH
        root_cause = f"DNS resolution failure: {topo or desc}."
        if "missing" in f_lower or "empty" in t_lower:
            root_cause = "Missing DNS server configuration on client. Host cannot resolve domain names to IP addresses."
        elif "incorrect" in f_lower or "wrong" in f_lower or "wrong" in t_lower:
            root_cause = f"Incorrect DNS server address configured: {topo}. Client sends DNS queries to an invalid or unreachable server IP."
        elif "disabled" in f_lower:
            root_cause = "DNS lookup service is disabled on the device (`no ip domain-lookup`), preventing hostname resolution."

        if is_host_device:
            next_cmds = [
                "ipconfig /all",
                "nslookup <domain_name>",
                "ping " + (ips[0] if ips else "8.8.8.8")
            ]
            fix_steps = [
                "Run `ipconfig /all` to view configured DNS servers.",
                "Update TCP/IP properties with a valid reachable DNS server IP address.",
                "Flush DNS resolver cache: `ipconfig /flushdns`.",
                "Verify name resolution with `nslookup <domain_name>`."
            ]
        else:
            next_cmds = [
                "show hosts",
                "show running-config | include ip name-server|ip domain",
                "ping " + (ips[0] if ips else "8.8.8.8")
            ]
            fix_steps = [
                "Configure correct DNS server address on client or switch: `ip name-server <dns_ip>`",
                "Ensure domain lookup is enabled: `ip domain-lookup`",
                "Verify IP reachability to the DNS server using ping.",
                "Test name resolution using domain lookups."
            ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN D: DHCP SERVICES & RELAYS
    # -------------------------------------------------------------------------
    if "dhcp" in c_lower or "dhcp" in f_lower or "dhcp" in t_lower or "169.254" in d_lower or "apipa" in d_lower:
        osi_layer = "Layer 7 - Application"
        confidence = schemas.ConfidenceLevel.HIGH
        if "relay" in f_lower or "helper" in f_lower or "behind router" in d_lower:
            root_cause = "Missing DHCP relay configuration. Router SVI interface facing clients lacks the `ip helper-address` command to forward DHCP broadcasts across subnets."
        elif "default-router" in t_lower or "gateway option" in f_lower:
            root_cause = "Missing DHCP default-router option. DHCP pool distributes IP addresses without a default gateway option, leaving clients unable to communicate outside local subnet."
        elif "scope" in f_lower or "wrong network" in f_lower:
            root_cause = f"DHCP pool network configuration mismatch: {topo}."
        else:
            root_cause = f"DHCP failure: {topo or desc}. Clients unable to obtain a valid IP lease from DHCP server."

        if is_host_device:
            next_cmds = [
                "ipconfig /release",
                "ipconfig /renew",
                "ipconfig /all"
            ]
            fix_steps = [
                "Attempt to release and request a new lease: `ipconfig /release` followed by `ipconfig /renew`.",
                "Check whether the DHCP server is reachable and running on the subnet.",
                "If on a separate subnet, ensure DHCP relay (`ip helper-address`) is configured on the router gateway.",
                "Verify client receives an IP address, subnet mask, and default gateway with `ipconfig /all`."
            ]
        else:
            next_cmds = [
                "show ip dhcp binding",
                "show ip dhcp pool",
                "show ip dhcp conflict",
                "show running-config | section dhcp"
            ]
            fix_steps = [
                "Verify DHCP pool configuration and available scope: `show ip dhcp pool`",
                "If clients reside on a separate subnet, configure `ip helper-address <server_ip>` on the gateway interface.",
                "Ensure `default-router <gateway_ip>` and `dns-server <dns_ip>` options are configured in the DHCP pool.",
                "Renew client IP configuration."
            ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN E: IP ADDRESSING & DUPLICATE IP (Strictly evidence-backed)
    # -------------------------------------------------------------------------
    is_duplicate_ip = (
        "duplicate ip" in f_lower or "duplicate ip" in t_lower or "duplicate ip" in d_lower or
        "both configured with" in t_lower or "ip conflict" in d_lower or
        any("duplicate" in r.lower() for r in rule_evidence)
    )
    is_wrong_mask = (
        "wrong subnet mask" in f_lower or "wrong mask" in f_lower or
        ("/25" in t_lower and "/24" in t_lower) or ("mask" in f_lower and "subnet" in f_lower) or
        any("wrong mask" in r.lower() for r in rule_evidence)
    )

    if is_duplicate_ip:
        osi_layer = "Layer 3 - Network"
        confidence = schemas.ConfidenceLevel.HIGH
        conflicting_ip = cidrs[0] if cidrs else (ips[0] if ips else "192.168.120.10")
        root_cause = f"Duplicate IP address conflict on the subnet. Multiple devices are assigned the same IP ({conflicting_ip}), causing ARP entry collisions and intermittent drops."
        if is_host_device:
            next_cmds = [
                "ipconfig /all",
                "arp -a"
            ]
            fix_steps = [
                f"Inspect current IP on host: `ipconfig /all`",
                "Reconfigure host network adapter with an unassigned static IP or switch to DHCP.",
                "Clear ARP cache (`netsh interface ip delete arpcache`) and test reachability."
            ]
        else:
            next_cmds = [
                "show ip arp",
                "show ip interface brief",
                "show mac address-table",
                "show log | include %IP-4-DUPADDR"
            ]
            fix_steps = [
                "Identify the conflicting MAC addresses from ARP logs: `show ip arp` and `show mac address-table`",
                "Locate the offending host switchport and reconfigure with an unallocated unique IP.",
                "Clear ARP cache on the default gateway: `clear arp-cache`",
                "Verify IP address uniqueness and test sustained ping reachability."
            ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    if is_wrong_mask:
        osi_layer = "Layer 3 - Network"
        confidence = schemas.ConfidenceLevel.HIGH
        root_cause = f"Subnet mask mismatch on host: {topo}. The configured subnet mask does not encompass the default gateway IP, treating the local gateway as a remote unreachable destination."
        if is_host_device:
            next_cmds = [
                "ipconfig /all",
                "ping <gateway_ip>",
                "tracert <remote_destination>"
            ]
            fix_steps = [
                "Run `ipconfig /all` to check current subnet mask.",
                "Correct the subnet mask in IPv4 properties to match the local subnet.",
                "Verify default gateway and remote network reachability."
            ]
        else:
            next_cmds = [
                "show ip route",
                "show ip interface brief",
                "show ip arp"
            ]
            fix_steps = [
                "Reconfigure the interface with the correct subnet mask matching the LAN network.",
                "Verify the default gateway falls within the host's subnet boundary.",
                "Test ping reachability to default gateway and remote subnets."
            ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN F: ROUTING & PROTOCOLS (OSPF, BGP, Static Route)
    # -------------------------------------------------------------------------
    if "ospf" in c_lower or "ospf" in f_lower or "ospf" in t_lower or "ospf" in d_lower:
        osi_layer = "Layer 3 - Network"
        confidence = schemas.ConfidenceLevel.HIGH
        iface_str = primary_iface or "GigabitEthernet0/1"
        root_cause = f"OSPF adjacency failure on {iface_str}: {topo or desc}. Mismatched OSPF interface parameters (Area ID, Hello/Dead timers, or MTU) are preventing neighbor relationship."
        next_cmds = [
            "show ip ospf neighbor",
            f"show ip ospf interface {iface_str}",
            "show ip protocols",
            "show ip route ospf"
        ]
        fix_steps = [
            f"Inspect OSPF interface settings: `show ip ospf interface {iface_str}`",
            "Verify Area ID and Hello/Dead timers match on both ends of the link.",
            f"Verify MTU matches across link: `show interfaces {iface_str} | include MTU`",
            "Verify neighbor reaches FULL state: `show ip ospf neighbor`"
        ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    if "bgp" in c_lower or "bgp" in f_lower or "bgp" in t_lower:
        osi_layer = "Layer 3 - Network"
        confidence = schemas.ConfidenceLevel.HIGH
        root_cause = f"BGP peering failure: {topo or desc}. Neighbor session is in Idle/Active state due to AS mismatch, missing update-source, or lack of eBGP multihop."
        next_cmds = [
            "show ip bgp summary",
            "show ip bgp neighbors",
            "show ip route bgp",
            "show ip route"
        ]
        fix_steps = [
            "Verify BGP neighbor IP and Autonomous System (AS) number: `show ip bgp summary`",
            "Check IP reachability to neighbor IP using `ping <neighbor_ip>`",
            "If peering via loopbacks, ensure `update-source Loopback0` and `ebgp-multihop` are configured.",
            "Verify session establishes: `show ip bgp summary`"
        ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    if "routing" in c_lower or "route" in f_lower or "route" in t_lower or "next-hop" in f_lower or "unreachable" in d_lower:
        osi_layer = "Layer 3 - Network"
        confidence = schemas.ConfidenceLevel.HIGH
        if "next-hop" in f_lower or "next-hop" in t_lower or "next hop" in t_lower:
            root_cause = f"Incorrect next-hop IP in static route: {topo}. Traffic is routed toward an unreachable or invalid next-hop address."
        else:
            root_cause = f"Missing or invalid routing entry for destination network: {topo or desc}. Packets are dropped due to lack of a valid route in the routing table."
        next_cmds = [
            "show ip route",
            "show ip interface brief",
            "show ip protocols",
            "show running-config | section ip route"
        ]
        fix_steps = [
            "Inspect the routing table: `show ip route`",
            "Correct or add the static route: `ip route <dest_net> <mask newspaper> <valid_next_hop>`",
            "Verify next-hop IP reachability using ping.",
            "Verify end-to-end routing with traceroute."
        ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN G: ACL & SECURITY FILTERING
    # -------------------------------------------------------------------------
    if "acl" in c_lower or "acl" in f_lower or "access-list" in f_lower or "blocked" in d_lower:
        osi_layer = "Layer 4 - Transport"
        confidence = schemas.ConfidenceLevel.HIGH
        iface_str = primary_iface or "GigabitEthernet0/1"
        root_cause = f"Access Control List (ACL) traffic drop: {topo or desc}. An access-list applied on {iface_str} matches and denies traffic due to implicit deny or missing permit rule."
        next_cmds = [
            "show access-lists",
            f"show ip interface {iface_str}",
            f"show running-config interface {iface_str}"
        ]
        fix_steps = [
            "Inspect access-list hit counters: `show access-lists`",
            f"Verify ACL interface binding and direction: `show ip interface {iface_str}`",
            "Update ACL permit statements to allow the required source/destination IP and transport ports.",
            "Clear counters (`clear access-list counters`) and verify traffic flow."
        ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN H: NAT / PAT
    # -------------------------------------------------------------------------
    if "nat" in c_lower or "nat" in f_lower or "pat" in f_lower:
        osi_layer = "Layer 4 - Transport"
        confidence = schemas.ConfidenceLevel.HIGH
        root_cause = f"Network Address Translation (NAT/PAT) failure: {topo or desc}. Missing `ip nat inside/outside` configuration or misconfigured NAT translation pool."
        next_cmds = [
            "show ip nat translations",
            "show ip nat statistics",
            "show access-lists",
            "show ip interface brief"
        ]
        fix_steps = [
            "Check active NAT translation table: `show ip nat translations`",
            "Verify internal interfaces have `ip nat inside` and egress interface has `ip nat outside`.",
            "Verify NAT overload ACL matches intended source subnets.",
            "Test outbound connectivity and verify translation creation."
        ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # DOMAIN I: PHYSICAL / INTERFACE DOWN / WIRELESS
    # -------------------------------------------------------------------------
    if "down" in f_lower or "down" in t_lower or "down" in d_lower or "interface" in c_lower or "wireless" in c_lower:
        osi_layer = "Layer 1 - Physical"
        confidence = schemas.ConfidenceLevel.HIGH
        iface_str = primary_iface or "GigabitEthernet0/1"
        root_cause = f"Physical / Link layer operational failure on {iface_str}: {topo or desc}."
        next_cmds = [
            f"show interfaces {iface_str} status",
            f"show interfaces {iface_str}",
            f"show running-config interface {iface_str}"
        ]
        fix_steps = [
            f"Enter interface configuration: `interface {iface_str}`",
            "Bring interface up: `no shutdown`",
            "Verify cable connectivity and speed/duplex negotiation.",
            f"Verify interface status is UP/UP: `show interfaces {iface_str} status`"
        ]
        return schemas.AIDiagnosisBase(
            root_cause=root_cause,
            osi_layer=osi_layer,
            confidence=confidence,
            evidence=evidence_list,
            next_commands=next_cmds,
            fix_steps=fix_steps
        )

    # -------------------------------------------------------------------------
    # GENERAL METADATA SYNTHESIS FALLBACK
    # -------------------------------------------------------------------------
    osi_layer = "Layer 3 - Network"
    if osi_in:
        osi_layer = osi_in
    if topo:
        root_cause = f"Network configuration issue identified from topology: {topo}."
    elif desc:
        root_cause = f"Network connectivity fault reported: {desc}."
    elif fault:
        root_cause = f"Network fault detected on {host or 'device'}: {fault}."
    else:
        root_cause = "General network anomaly detected across reporting device interfaces."

    if is_host_device:
        next_cmds = [
            "ipconfig /all",
            "ping 127.0.0.1",
            "tracert <remote_destination>"
        ]
        fix_steps = [
            "Run `ipconfig /all` to inspect host adapter settings.",
            "Test local loopback with `ping 127.0.0.1` to confirm TCP/IP stack functionality.",
            "Verify network cable and gateway reachability."
        ]
    else:
        next_cmds = [
            "show ip interface brief",
            "show ip route",
            "show interfaces status",
            "show running-config"
        ]
        fix_steps = [
            "Inspect device interface states: `show ip interface brief`",
            "Inspect device routing table: `show ip route`",
            "Check device running configuration for syntax or parameter errors.",
            "Test end-to-end ping reachability."
        ]

    return schemas.AIDiagnosisBase(
        root_cause=root_cause,
        osi_layer=osi_layer,
        confidence=schemas.ConfidenceLevel.MEDIUM,
        evidence=evidence_list,
        next_commands=next_cmds,
        fix_steps=fix_steps
    )
