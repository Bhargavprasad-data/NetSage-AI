import re
from typing import Dict, List

def duplicate_ip_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if re.search(r"DUPADDR|duplicate|ip address conflict", output, re.IGNORECASE):
            evidence.append(f"Found Duplicate IP warning in '{cmd}'")
    return evidence

def wrong_mask_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if "255.255.255.255" in output and "Loopback" not in output:
            evidence.append(f"Possible wrong host mask (255.255.255.255 on non-loopback) in '{cmd}'")
        elif "mask mismatch" in output.lower() or "bad mask" in output.lower():
            evidence.append(f"Subnet mask mismatch detected in '{cmd}'")
    return evidence

def gateway_mismatch_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if "Gateway of last resort is not set" in output:
            evidence.append(f"Gateway of last resort not set in '{cmd}'")
    return evidence

def interface_down_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if re.search(r"administratively down|line protocol is down|err-disabled|is down,", output, re.IGNORECASE):
            evidence.append(f"Interface down / err-disabled detected in '{cmd}'")
    return evidence

def missing_vlan_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if "not found in current VLAN database" in output or "suspended" in output.lower() or "vlan does not exist" in output.lower():
            evidence.append(f"Missing, suspended, or uncreated VLAN detected in '{cmd}'")
    return evidence

def trunk_mismatch_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if re.search(r"native vlan mismatch|encapsulation mismatch|mode mismatch|negotiation of trunking: off", output, re.IGNORECASE):
            evidence.append(f"Trunk / VLAN encapsulation mismatch detected in '{cmd}'")
        elif "administrative mode: static access" in output.lower() and "trunk" in cmd.lower():
            evidence.append(f"Port configured as static access instead of trunk in '{cmd}'")
    return evidence

def missing_route_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if "Network not in table" in output or "No route to host" in output or "% Network not in table" in output:
            evidence.append(f"Missing routing entry detected in '{cmd}'")
    return evidence

def ospf_neighbor_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if "OSPF" in cmd.upper():
            if re.search(r"mismatched hello|mismatched dead|area mismatch|mtu mismatch|auth mismatch", output, re.IGNORECASE):
                evidence.append(f"OSPF adjacency parameter mismatch detected in '{cmd}'")
            elif "state down" in output.lower() or "init/" in output.lower() or "exstart/" in output.lower():
                evidence.append(f"OSPF neighbor stuck in non-FULL state in '{cmd}'")
    return evidence

def acl_drop_check(show_outputs: dict) -> list[str]:
    evidence = []
    for cmd, output in show_outputs.items():
        if not isinstance(output, str):
            continue
        if "access-list" in cmd.lower() and re.search(r"deny\s+.*\((\d+)\s+matches\)", output, re.IGNORECASE):
            evidence.append(f"Active ACL deny drops detected in '{cmd}'")
    return evidence

def run_all_rules(show_outputs: dict) -> list[str]:
    if not show_outputs or not isinstance(show_outputs, dict):
        return []
    all_evidence = []
    all_evidence.extend(duplicate_ip_check(show_outputs))
    all_evidence.extend(wrong_mask_check(show_outputs))
    all_evidence.extend(gateway_mismatch_check(show_outputs))
    all_evidence.extend(interface_down_check(show_outputs))
    all_evidence.extend(missing_vlan_check(show_outputs))
    all_evidence.extend(trunk_mismatch_check(show_outputs))
    all_evidence.extend(missing_route_check(show_outputs))
    all_evidence.extend(ospf_neighbor_check(show_outputs))
    all_evidence.extend(acl_drop_check(show_outputs))
    return all_evidence
