# AI Autonomous Operations Intelligence Platform — Backend

Backend orchestration and operations intelligence platform for predictive maintenance, technician dispatch, route optimization, and SLA enforcement.

## Team Ownership Boundaries
- **Developer 1 (Frontend):** UI, components, pages, dashboard. (Untouched)
- **Developer 2 (AI/ML):** Predictive models, RUL estimation, risk scoring, demand forecasting. (Untouched)
- **Developer 3 (Backend):** Orchestration API, PostgreSQL schema, technician assignment, Haversine routing, SLA evaluation, operations audit log, Docker setup, and tests.

---

## Architectural Flow
```text
Frontend
    ↓
Backend API (/api/operations/trigger/{asset_id})
    ↓
Database (Fetch Asset, Telemetry, Inventory, Available Techs)
    ↓
AI Engine (POST /autonomous-operation)
    ↓
Technician Assignment (Deterministic Multi-Factor Scoring)
    ↓
Haversine Route & ETA Calculation
    ↓
SLA Compliance Evaluation (WITHIN_SLA, AT_RISK, SLA_BREACH_RISK)
    ↓
Operation Log & Work Order Persistence
    ↓
Clean Backend Response
    ↓
Frontend
```

---

## Required APIs

### 1. Assets
- `GET /api/assets`: List all monitored assets with telemetry and maintenance history.
- `GET /api/assets/{asset_id}`: Single asset details (e.g. `CHILLER-MARINA-101`).

### 2. Inventory
- `GET /api/inventory`: List all spare parts, stock levels, lead times, and unit costs.
- `GET /api/inventory/{part_id}`: Single spare part details (e.g. `PART-BRG-7701`).

### 3. Technicians
- `GET /api/technicians`: List technicians (supports `?available_only=true/false`).
- `GET /api/technicians/{technician_id}`: Single technician details (e.g. `TECH-DXB-01`).

### 4. Autonomous Operations
- `POST /api/operations/trigger/{asset_id}`: Trigger end-to-end autonomous operation.
- `GET /api/operations/logs`: View historical operation execution logs.
- `GET /api/operations/logs/{operation_id}`: Single operation log details.

---

## Local Setup & Testing

### 1. Setup Virtual Environment
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Run Test Suite
```bash
pytest backend/tests -v
```

### 3. Run End-to-End Verification
```bash
python backend/tests/verify_e2e.py
```

### 4. Run Development Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 5000 --reload
```

---

## Docker Deployment
```bash
docker compose up --build
```
Services:
- **Backend**: `http://localhost:5000`
- **AI Engine**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432` (db: `autonomous_ops`)
