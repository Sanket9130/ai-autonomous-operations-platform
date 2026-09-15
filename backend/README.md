# Facility Operations Backend API & Orchestrator

> **Backend Data, Database, and Orchestration Microservice**  
> Connects PostgreSQL/SQLite business data, warehouse inventory, and certified field technicians with the AI Autonomous Operations Engine (`ai-engine/`).

---

## 🏗 Architecture & Flow

```text
[Frontend / Client]
       │  POST /api/operations/trigger/{asset_id}
       ▼
[Backend Orchestrator] (Port 5000)
   ├── 1. Query Asset & Sensor Telemetry from Database
   ├── 2. Query Linked Spare Part & Inventory Stock from Database
   ├── 3. Query Available Certified Technicians from Database
   ├── 4. Build AutonomousOperationInput Payload
   │
   ▼  POST /autonomous-operation (HTTP)
[AI Engine Decision Core] (Port 8000)
   ├── ML Failure Prediction (RandomForest / LogisticRegression)
   ├── Statistical Spare-Part Demand Forecasting (7/30/90d, ROP)
   ├── Technician Routing & Dubai Corridor ETA Calculation
   ├── SLA Margin Assessment
   └── Cost-Benefit Financial Optimization
   │
   ▼  Unified Response
[Backend Orchestrator]
   ├── 5. Persist Operation Audit Log in Database
   └── 6. Deliver Unified Autonomous Decision to Frontend
```

---

## 🚀 Quick Start

### 1. Installation & Environment Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Backend Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 5000 --reload
```

* **Backend Swagger Docs**: `http://localhost:5000/docs`
* **Target AI Engine**: Configured via `AI_ENGINE_URL` (default `http://localhost:8000/autonomous-operation`)

---

## 📋 Key API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `POST /api/operations/trigger/{asset_id}` | `POST` | Trigger end-to-end autonomous analysis for a specific asset |
| `POST /api/operations/evaluate` | `POST` | Trigger autonomous analysis with optional sensor overrides |
| `GET /api/operations/logs` | `GET` | Retrieve audit history of executed autonomous operations |
| `GET /api/assets` | `GET` | List all assets and telemetry in database |
| `GET /api/inventory` | `GET` | List spare-part inventory stock & lead times |
| `GET /api/technicians` | `GET` | List certified field technicians |
| `GET /health` | `GET` | Backend health & AI Engine target probe |

---

## 🧪 Tests
Run backend integration tests:
```bash
pytest backend/tests/ -v
```
