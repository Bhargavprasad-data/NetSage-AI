# 🌐 NetSage AI — Autonomous Network Intelligence & Diagnostics

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Framer Motion](https://img.shields.io/badge/Framer_Motion-12.0+-FF0055.svg?style=flat&logo=framer&logoColor=white)](https://www.framer.com/motion/)


**NetSage AI** is an end-to-end, enterprise-grade Autonomous Network Troubleshooting and Diagnostic Intelligence Platform. It combines deterministic rule engines, semantic network feature extraction, and dynamic diagnostic reasoning to analyze complex multi-vendor network anomalies across OSI Layers 1 through 7.

## 🚀 Key Features

- **🔍 Multi-Layer Network Diagnostics**:
  - **Layer 1 (Physical)**: Cable errors, interface down, err-disabled, speed/duplex mismatch.
  - **Layer 2 (Data Link)**: 802.1Q trunk/access mismatches, incorrect VLAN assignments, missing VLAN databases, STP blocking.
  - **Layer 3 (Network)**: Subnet boundary mismatches, unreachable default gateways, IP conflicts, static route blackholes, OSPF & BGP peering failures.
  - **Layer 4–7 (Transport & Application)**: ACL filtering drops, NAT/PAT translation exhaustion, DHCP scope & relay helper issues, DNS resolution failures.

- **🧠 Dynamic Reasoning Engine**:
  - Employs mathematical subnet boundary validation using Python's `ipaddress` module.
  - Context-aware command generation: outputs PC/end-host diagnostics (`ipconfig`, `ping <gateway>`, `tracert`) for endpoints and Cisco IOS CLI show commands (`show interfaces trunk`, `show ip route`) for switches and routers.
  - Strict evidence grounding to eliminate false positives.

- **🛡️ Evidence Verification & Claim Grounding**:
  - Dynamically evaluates AI diagnostic evidence claims against raw CLI `show_outputs` and tags claims as `VERIFIED` or `UNVERIFIED`.

- **👥 Human-in-the-Loop & Responsible AI Governance**:
  - Reviewers can **Accept**, **Edit**, or **Reject** diagnoses with custom feedback.
  - Automatic immutable audit logging into `responsible_ai_log` tracks AI root cause vs. human corrections.

- **📊 Real-Time Analytics Dashboard**:
  - Live backend heartbeat pulse indicator.
  - Interactive Recharts visualization (case status distribution, AI-human agreement rates).
  - Shimmer skeleton loaders for smooth loading states.

- **🌓 Dual-Theme Design System**:
  - Supports both dark mode (`#0a0a0f`) and light mode (`#f8fafc`) with dynamic CSS variables and fluid typography.

- **📥 Dataset Import & Export**:
  - Bulk CSV dataset ingestion and flat CSV report export.

---

## 🏗️ Architecture & Tech Stack

NetSage AI/
├── backend/                  # FastAPI REST API Backend
│   ├── alembic/              # Alembic database migrations
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint & CORS middleware
│   │   ├── database.py       # SQLAlchemy engine & session factory
│   │   ├── models.py         # PostgreSQL ORM models
│   │   ├── schemas.py        # Pydantic v2 schemas
│   │   ├── crud.py           # Database operations
│   │   ├── llm.py            # Dynamic Network Diagnostic Engine
│   │   ├── rules.py          # Deterministic CLI output rule engine
│   │   ├── verifier.py       # Evidence verification module
│   │   └── routers/          # API route controllers
│   └── requirements.txt      # Python dependencies
│
└── frontend/                 # React 19 + Vite + TypeScript Frontend
    ├── src/
    │   ├── components/       # Animated components (Dashboard, Cases, Detail, Sidebar, Logo)
    │   ├── ThemeContext.tsx  # Light/Dark mode state & persistence
    │   ├── transitions.ts    # Framer motion variants
    │   ├── api.ts            # Axios API client
    │   └── index.css         # Design system & CSS variables
    ├── index.html            # Application HTML shell
    └── vite.config.ts        # Vite configuration
```

---

## 📦 Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **PostgreSQL 14+**

---

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `backend/.env`:
   ```env
   PORT=8000
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=netsage_ai
   DB_USER=postgres
   DB_PASSWORD=your_password
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/netsage_ai
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *API will be live at `http://localhost:8000` (Swagger UI at `http://localhost:8000/docs`).*

---

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Frontend UI will be live at `http://localhost:5173`.*

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/cases/` | List all network troubleshooting cases |
| `POST` | `/cases/` | Create a new case with topology & symptoms |
| `GET` | `/cases/{id}` | Retrieve case details & CLI outputs |
| `POST` | `/diagnoses/case/{id}` | Run dynamic AI diagnosis engine on a case |
| `GET` | `/diagnoses/case/{id}` | Get diagnosis with evidence verification |
| `POST` | `/reviews/` | Submit human review (Accept / Edit / Reject) |
| `GET` | `/dashboard/stats` | Retrieve metrics, counts, and agreement rate |
| `POST` | `/csv/import` | Bulk import cases from CSV dataset |
| `GET` | `/csv/export` | Download flat CSV dataset report |

---

## 📄 Structured Diagnosis Schema Example

```json
{
  "root_cause": "Trunk/access mismatch: Link Gi0/24 between switches is operating in access mode instead of trunk mode, blocking VLAN 10 inter-switch forwarding.",
  "osi_layer": "Layer 2 - Data Link",
  "confidence": "HIGH",
  "evidence": [
    "Topology note indicates: SW1 and SW2 are connected by Gi0/24; the link is configured as access instead of trunk",
    "Reported symptom: Hosts on VLAN 10 lose connectivity across switches",
    "Protocol domain: VLAN"
  ],
  "next_commands": [
    "show interfaces Gi0/24 switchport",
    "show interfaces trunk",
    "show vlan brief",
    "show interfaces Gi0/24 status"
  ],
  "fix_steps": [
    "Enter interface configuration mode on SW2: `interface Gi0/24`",
    "Configure trunk encapsulation if required: `switchport trunk encapsulation dot1q`",
    "Set the switchport mode to trunk: `switchport mode trunk`",
    "Ensure VLAN 10 is allowed: `switchport trunk allowed vlan add 10`",
    "Verify trunk status using `show interfaces trunk` and test connectivity across switches."
  ]
}
```

---

## 🛡️ License

This project is distributed under the MIT License.
