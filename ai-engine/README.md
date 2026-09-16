# AI Autonomous Operations Engine — Backend Integration & API Reference

> **Dubai Facility & Property Management Decision Intelligence Core**  
> High-throughput, stateless AI/ML microservice providing predictive maintenance, statistical spare-part forecasting, technician dispatch routing, SLA risk detection, and operational cost optimization.

---

## 🚀 1. How to Start the AI API

### Prerequisites & Installation
```bash
# Navigate to the AI module directory
cd ai-engine

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Ensure model artifact is trained and ready
python scripts/train_model.py
```

### Start Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

* **API Base URL**: `http://localhost:8000`
* **Interactive OpenAPI Swagger Docs**: `http://localhost:8000/docs`
* **ReDoc Interactive Reference**: `http://localhost:8000/redoc`

---

## 🌟 2. Primary Integration Endpoint

### `POST /autonomous-operation` (or `POST /api/v1/autonomous-operation`)

This is the **primary integration endpoint** for backend microservices and workflow engines. It takes asset sensor telemetry and inventory/technician parameters, executes the complete intelligence pipeline in one shot, and returns a unified operational action.

#### Pipeline Flow:
$$\text{Sensor Telemetry} \longrightarrow \text{ML Failure Prob} \longrightarrow \text{Asset Risk} \longrightarrow \text{Spare-Part Forecast} \longrightarrow \text{Stockout Risk} \longrightarrow \text{Technician Route \& ETA} \longrightarrow \text{SLA Margin} \longrightarrow \text{Cost Optimization} \longrightarrow \text{Unified Action}$$

---

## 📋 3. Request & Response Specification

### Request Example (`POST /autonomous-operation`)
```json
{
  "asset_id": "CHILLER-MARINA-101",
  "asset_type": "HVAC_CHILLER",
  "asset_location": "MARINA",
  "vibration_mm_s": 7.8,
  "operating_temp_c": 87.0,
  "ambient_temp_c": 48.0,
  "power_kw": 128.0,
  "runtime_hours": 9400.0,
  "last_maintenance_days": 88,
  "asset_criticality": "CRITICAL",
  "required_spare_part": "CHILLER_EXPANSION_VALVE",
  "current_stock": 0.0,
  "lead_time_days": 14.0,
  "forecast_days": 30,
  "spare_part_cost": 500.0,
  "sla_deadline_hours": 3.0,
  "estimated_repair_duration_hours": 1.5,
  "candidate_technicians": [
    {
      "technician_id": "TECH-DXB-042 (Senior HVAC Specialist)",
      "skills": ["HVAC_CHILLER_SPECIALIST", "ELECTROMECHANICAL"],
      "availability": true,
      "current_location": "DOWNTOWN",
      "technician_workload": 1
    }
  ]
}
```

### Response Example (`200 OK`)
```json
{
  "asset_id": "CHILLER-MARINA-101",
  "failure_prediction": {
    "failure_probability": 0.9757,
    "predicted_status": "CRITICAL",
    "risk_score": 90.9,
    "estimated_rul_days": 1.0
  },
  "inventory_intelligence": {
    "spare_part": "CHILLER_EXPANSION_VALVE",
    "current_stock": 0.0,
    "predicted_demand_30d": 36.17,
    "safety_stock": 7.49,
    "reorder_point": 24.37,
    "stockout_risk": "CRITICAL",
    "recommended_order_quantity": 37.0
  },
  "technician_dispatch": {
    "selected_technician": "TECH-DXB-042 (Senior HVAC Specialist)",
    "technician_score": 86.5,
    "distance_km": 24.36,
    "estimated_eta_minutes": 41.5,
    "sla_status": "WITHIN_SLA"
  },
  "cost_optimization": {
    "preventive_total_cost": 725.0,
    "failure_total_cost": 6820.0,
    "estimated_savings": 5929.27
  },
  "unified_action": "URGENT_MAINTENANCE_AND_REORDER",
  "operational_summary": "High failure risk (0.98) with critical stockout vulnerability for CHILLER_EXPANSION_VALVE. Emergency parts reorder (37.0 units) and technician dispatch initiated. Net expected savings: 5929.27 AED."
}
```

---

## 💻 4. Backend Integration Code Examples

### Python (`httpx` or `requests`)
```python
import requests

AI_ENGINE_URL = "http://localhost:8000/autonomous-operation"

payload = {
    "asset_id": "CHILLER-MARINA-101",
    "asset_type": "HVAC_CHILLER",
    "asset_location": "MARINA",
    "vibration_mm_s": 7.8,
    "operating_temp_c": 87.0,
    "ambient_temp_c": 48.0,
    "power_kw": 128.0,
    "runtime_hours": 9400.0,
    "last_maintenance_days": 88,
    "asset_criticality": "CRITICAL",
    "required_spare_part": "CHILLER_EXPANSION_VALVE",
    "current_stock": 0.0,
    "lead_time_days": 14.0,
    "spare_part_cost": 500.0,
    "sla_deadline_hours": 3.0,
}

response = requests.post(AI_ENGINE_URL, json=payload, timeout=5.0)
response.raise_for_status()
result = response.json()

print(f"Action: {result['unified_action']}")
print(f"Summary: {result['operational_summary']}")
print(f"Savings: {result['cost_optimization']['estimated_savings']} AED")
```

### Node.js / Express / NestJS
```javascript
const axios = require('axios');

async function triggerAutonomousOperation(telemetry) {
  const url = 'http://localhost:8000/autonomous-operation';
  try {
    const { data } = await axios.post(url, telemetry, { timeout: 5000 });
    console.log(`Action: ${data.unified_action}`);
    return data;
  } catch (error) {
    console.error('AI Engine Error:', error.response?.data || error.message);
    throw error;
  }
}
```

### cURL
```bash
curl -X POST "http://localhost:8000/autonomous-operation" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "CHILLER-MARINA-101",
    "vibration_mm_s": 7.8,
    "operating_temp_c": 87.0,
    "ambient_temp_c": 48.0,
    "power_kw": 128.0,
    "runtime_hours": 9400.0,
    "last_maintenance_days": 88,
    "asset_criticality": "CRITICAL",
    "required_spare_part": "CHILLER_EXPANSION_VALVE",
    "current_stock": 0.0,
    "lead_time_days": 14.0
  }'
```

---

## 🛠 5. Additional Modular Endpoints

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/health` | `GET` | Readiness and active model status probe |
| `/predict` | `POST` | ML asset failure probability & RUL estimation |
| `/forecast-demand` | `POST` | Statistical spare-part demand forecasting (7/30/90 days) |
| `/operations-decision`| `POST` | Combined asset risk & inventory reorder calculation |
| `/dispatch-technician`| `POST` | Technician candidate scoring, Dubai route distance & ETA |
| `/optimize-operation` | `POST` | Cost-benefit tradeoff & downtime savings optimization |

---

## 🧪 6. Testing & Quality Assurance
Run the complete automated test suite:
```bash
pytest tests/ -v
```
