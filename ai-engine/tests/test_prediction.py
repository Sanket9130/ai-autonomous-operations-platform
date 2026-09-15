"""
Unit and API integration tests for model prediction, Decision Intelligence, Demand Forecasting,
Unified Operations Decisions, Technician Dispatch Routing, and Cost & SLA Optimization.
"""

from fastapi.testclient import TestClient
from api.main import app
from src.forecasting.demand_forecast import forecast_spare_part_demand
from src.models.predict import predict_asset_failure
from src.recommendations.recommendation_engine import (
    evaluate_decision_intelligence,
    evaluate_unified_operations_decision,
)
from src.recommendations.technician_router import (
    calculate_haversine_distance,
    score_technician_suitability,
    select_best_technician,
)
from src.risk_engine.cost_optimizer import (
    calculate_maintenance_costs,
    optimize_operational_decision,
)


def test_predict_asset_failure_output_contract():
    telemetry = {
        "vibration_mm_s": 6.8,
        "operating_temp_c": 82.0,
        "ambient_temp_c": 46.0,
        "power_kw": 115.0,
        "runtime_hours": 9500.0,
        "last_maintenance_days": 90,
    }
    result = predict_asset_failure(
        asset_id="CHILLER-DXB-001",
        telemetry_features=telemetry,
        asset_type="CHILLER",
    )
    assert result["asset_id"] == "CHILLER-DXB-001"
    assert 0.0 <= result["failure_probability"] <= 1.0
    assert result["predicted_status"] in ["HEALTHY", "WARNING", "CRITICAL"]
    assert result["risk_score"] >= 0.0
    assert result["estimated_rul_days"] > 0
    assert isinstance(result["recommendations"], list)


def test_api_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-engine"
    assert "model_loaded" in data


def test_api_predict_endpoint():
    client = TestClient(app)
    payload = {
        "asset_id": "HVAC-DXB-005",
        "asset_type": "HVAC_CHILLER",
        "vibration_mm_s": 2.1,
        "operating_temp_c": 52.0,
        "ambient_temp_c": 39.0,
        "power_kw": 45.0,
        "runtime_hours": 1200.0,
        "last_maintenance_days": 15,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "HVAC-DXB-005"
    assert "failure_probability" in data
    assert "risk_category" in data
    assert len(data["recommendations"]) >= 0


def test_decision_intelligence_critical_low_stock():
    result = evaluate_decision_intelligence(
        failure_probability=0.82,
        risk_level="CRITICAL",
        asset_criticality="HIGH",
        required_spare_part="CHILLER_BEARING_6208",
        current_stock=1.0,
        minimum_stock=4.0,
        lead_time_days=14.0,
    )
    assert result["failure_probability"] == 0.82
    assert result["risk_level"] == "CRITICAL"
    assert result["maintenance_priority"] == "P1"
    assert result["stock_status"] == "LOW"
    assert "reorder" in result["recommended_action"].lower()
    assert "insufficient" in result["reason"].lower()


def test_decision_intelligence_critical_stock_available():
    result = evaluate_decision_intelligence(
        failure_probability=0.78,
        risk_level="CRITICAL",
        asset_criticality="HIGH",
        required_spare_part="AHU_V_BELT_B56",
        current_stock=10.0,
        minimum_stock=4.0,
    )
    assert result["maintenance_priority"] == "P1"
    assert result["stock_status"] == "OPTIMAL"
    assert "dispatch" in result["recommended_action"].lower()


def test_api_decision_intelligence_endpoint():
    client = TestClient(app)
    payload = {
        "failure_probability": 0.82,
        "asset_risk_level": "CRITICAL",
        "asset_criticality": "HIGH",
        "required_spare_part": "COMPRESSOR_VALVE_KIT",
        "current_stock": 2.0,
        "minimum_stock": 5.0,
        "lead_time_days": 10.0,
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["failure_probability"] == 0.82
    assert data["risk_level"] == "CRITICAL"
    assert data["maintenance_priority"] == "P1"
    assert data["stock_status"] == "LOW"
    assert "recommended_action" in data
    assert "reason" in data


def test_forecast_demand_calculation_horizons():
    history = [1.0, 2.0, 1.0, 3.0, 2.0, 1.0, 2.0, 1.0, 4.0, 1.0]

    # 7-day forecast
    f7 = forecast_spare_part_demand("PART-001", history, forecast_days=7, current_stock=2.0, lead_time_days=7.0)
    assert f7["forecast_days"] == 7
    assert f7["predicted_demand"] > 0
    assert f7["safety_stock"] > 0
    assert f7["reorder_point"] > f7["safety_stock"]
    assert f7["stockout_risk"] in ["HIGH", "CRITICAL"]

    # 30-day forecast
    f30 = forecast_spare_part_demand("PART-001", history, forecast_days=30, current_stock=50.0, lead_time_days=14.0)
    assert f30["forecast_days"] == 30
    assert f30["predicted_demand"] > f7["predicted_demand"]
    assert f30["stockout_risk"] == "LOW"
    assert f30["recommended_order_quantity"] == 0.0

    # 90-day forecast
    f90 = forecast_spare_part_demand("PART-001", history, forecast_days=90, current_stock=0.0, lead_time_days=14.0)
    assert f90["forecast_days"] == 90
    assert f90["stockout_risk"] == "CRITICAL"
    assert f90["recommended_order_quantity"] > 0


def test_api_forecast_demand_endpoint():
    client = TestClient(app)
    payload = {
        "part_id": "CHILLER_EXPANSION_VALVE",
        "forecast_days": 30,
        "historical_daily_demand": [1.0, 0.0, 2.0, 1.0, 1.0, 3.0, 2.0],
        "current_stock": 5.0,
        "lead_time_days": 14.0,
    }
    response = client.post("/forecast-demand", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["part_id"] == "CHILLER_EXPANSION_VALVE"
    assert data["forecast_days"] == 30
    assert "predicted_demand" in data
    assert "safety_stock" in data
    assert "reorder_point" in data
    assert "stockout_risk" in data
    assert "recommended_order_quantity" in data


def test_evaluate_unified_operations_decision_urgent():
    telemetry = {
        "vibration_mm_s": 7.5,
        "operating_temp_c": 86.0,
        "ambient_temp_c": 47.0,
        "power_kw": 125.0,
        "runtime_hours": 9200.0,
        "last_maintenance_days": 85,
    }
    res = evaluate_unified_operations_decision(
        asset_id="HVAC-DXB-999",
        telemetry_features=telemetry,
        asset_criticality="HIGH",
        required_spare_part="CHILLER_EXPANSION_VALVE",
        current_stock=1.0,
        lead_time_days=14.0,
    )
    assert res["failure_probability"] > 0.5
    assert res["maintenance_priority"] in ["P1", "P2"]
    assert res["spare_part"] == "CHILLER_EXPANSION_VALVE"
    assert res["recommended_action"] == "URGENT_PREVENTIVE_MAINTENANCE_AND_REORDER"
    assert "reason" in res


def test_api_operations_decision_endpoint():
    client = TestClient(app)
    payload = {
        "asset_id": "CHILLER-MARINA-101",
        "asset_type": "HVAC_CHILLER",
        "vibration_mm_s": 6.9,
        "operating_temp_c": 83.0,
        "ambient_temp_c": 46.0,
        "power_kw": 110.0,
        "runtime_hours": 8000.0,
        "last_maintenance_days": 75,
        "asset_criticality": "HIGH",
        "required_spare_part": "CHILLER_EXPANSION_VALVE",
        "current_stock": 2.0,
        "lead_time_days": 14.0,
        "forecast_days": 30,
    }
    response = client.post("/operations-decision", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "failure_probability" in data
    assert "asset_risk" in data
    assert "maintenance_priority" in data
    assert data["spare_part"] == "CHILLER_EXPANSION_VALVE"
    assert "stockout_risk" in data
    assert "predicted_demand" in data
    assert "reorder_point" in data
    assert "recommended_order_quantity" in data
    assert data["recommended_action"] == "URGENT_PREVENTIVE_MAINTENANCE_AND_REORDER"
    assert "reason" in data


def test_technician_suitability_and_selection():
    candidates = [
        {
            "technician_id": "TECH-001 (Junior Plumber)",
            "skills": ["PLUMBING"],
            "availability": True,
            "current_location": "DEIRA",
            "technician_workload": 0,
        },
        {
            "technician_id": "TECH-002 (Senior HVAC Tech)",
            "skills": ["HVAC_CHILLER_SPECIALIST", "ELECTROMECHANICAL"],
            "availability": True,
            "current_location": "DOWNTOWN",
            "technician_workload": 1,
        },
    ]
    res = select_best_technician(
        candidates=candidates,
        required_skill="HVAC_CHILLER_SPECIALIST",
        asset_location="MARINA",
        sla_deadline_hours=3.0,
        estimated_repair_duration_hours=1.5,
    )
    assert "TECH-002" in res["selected_technician"]
    assert res["technician_score"] > 70.0
    assert res["distance"] > 0
    assert res["estimated_eta"] > 0
    assert res["sla_status"] in ["WITHIN_SLA", "AT_RISK"]
    assert "reason" in res


def test_api_dispatch_technician_endpoint():
    client = TestClient(app)
    payload = {
        "technician_id": "TECH-DXB-042 (Rashid Al-Nuaimi)",
        "technician_skills": ["HVAC_CHILLER_SPECIALIST", "ELECTRICAL"],
        "technician_availability": True,
        "technician_current_location": "DOWNTOWN",
        "asset_location": "DIFC",
        "estimated_repair_duration_hours": 1.0,
        "technician_workload": 1,
        "sla_deadline_hours": 2.5,
        "required_skill": "HVAC_CHILLER_SPECIALIST",
    }
    response = client.post("/dispatch-technician", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["selected_technician"] == "TECH-DXB-042 (Rashid Al-Nuaimi)"
    assert data["technician_score"] > 80.0
    assert data["distance"] < 10.0
    assert data["estimated_eta"] < 30.0
    assert data["sla_status"] == "WITHIN_SLA"
    assert "reason" in data


def test_cost_calculation_and_optimization():
    res = optimize_operational_decision(
        failure_probability=0.88,
        asset_criticality="CRITICAL",
        maintenance_priority="P1",
        stock_status="OPTIMAL",
        selected_technician="TECH-DXB-042",
        technician_eta_minutes=12.0,
        sla_status="WITHIN_SLA",
        spare_part_cost=500.0,
        current_stock=3.0,
    )
    assert res["preventive_total_cost"] < res["failure_total_cost"]
    assert res["estimated_savings"] > 2000.0
    assert res["final_recommended_action"] == "URGENT_MAINTENANCE"
    assert "reason" in res


def test_api_optimize_operation_endpoint():
    client = TestClient(app)
    payload = {
        "failure_probability": 0.85,
        "asset_criticality": "HIGH",
        "maintenance_priority": "P1",
        "stock_status": "OPTIMAL",
        "selected_technician": "TECH-DXB-042 (Senior Specialist)",
        "technician_eta_minutes": 15.0,
        "sla_status": "WITHIN_SLA",
        "spare_part_cost": 450.0,
        "current_stock": 2.0,
        "reorder_point": 10.0,
    }
    response = client.post("/optimize-operation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["preventive_total_cost"] > 0
    assert data["failure_total_cost"] > data["preventive_total_cost"]
    assert data["estimated_savings"] > 0
    assert data["sla_risk"] == "WITHIN_SLA"
    assert data["final_recommended_action"] == "URGENT_MAINTENANCE"
    assert "reason" in data


def test_scenario_1_critical_chiller_high_failure_low_stock():
    """Scenario 1: Critical chiller + high failure probability + low stock + available specialist -> urgent maintenance + reorder"""
    client = TestClient(app)
    payload = {
        "asset_id": "CHILLER-MARINA-101",
        "asset_type": "HVAC_CHILLER",
        "vibration_mm_s": 7.8,
        "operating_temp_c": 87.0,
        "ambient_temp_c": 48.0,
        "power_kw": 128.0,
        "runtime_hours": 9400.0,
        "last_maintenance_days": 88,
        "asset_location": "MARINA",
        "asset_criticality": "CRITICAL",
        "required_spare_part": "CHILLER_EXPANSION_VALVE",
        "current_stock": 0.0,
        "lead_time_days": 14.0,
        "spare_part_cost": 500.0,
        "sla_deadline_hours": 3.0,
        "candidate_technicians": [
            {
                "technician_id": "TECH-DXB-042 (Senior HVAC Specialist)",
                "skills": ["HVAC_CHILLER_SPECIALIST", "ELECTROMECHANICAL"],
                "availability": True,
                "current_location": "DOWNTOWN",
                "technician_workload": 1,
            }
        ],
    }
    response = client.post("/autonomous-operation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "CHILLER-MARINA-101"
    assert data["failure_prediction"]["failure_probability"] > 0.50
    assert data["inventory_intelligence"]["stockout_risk"] == "CRITICAL"
    assert data["unified_action"] == "URGENT_MAINTENANCE_AND_REORDER"
    assert data["cost_optimization"]["estimated_savings"] > 0


def test_scenario_2_healthy_asset_sufficient_stock():
    """Scenario 2: Healthy asset + sufficient stock -> monitor / standard schedule"""
    client = TestClient(app)
    payload = {
        "asset_id": "CHILLER-DIFC-002",
        "asset_type": "HVAC_CHILLER",
        "vibration_mm_s": 1.2,
        "operating_temp_c": 52.0,
        "ambient_temp_c": 32.0,
        "power_kw": 45.0,
        "runtime_hours": 1200.0,
        "last_maintenance_days": 10,
        "asset_location": "DIFC",
        "asset_criticality": "MEDIUM",
        "required_spare_part": "CHILLER_EXPANSION_VALVE",
        "current_stock": 50.0,
        "lead_time_days": 14.0,
        "spare_part_cost": 450.0,
        "sla_deadline_hours": 6.0,
    }
    response = client.post("/autonomous-operation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["failure_prediction"]["failure_probability"] < 0.30
    assert data["unified_action"] == "MONITOR"


def test_scenario_3_critical_asset_sla_risk():
    """Scenario 3: Critical asset + unavailable/poor technician or SLA risk -> clearly identify the operational risk"""
    client = TestClient(app)
    payload = {
        "asset_id": "CHILLER-PALM-999",
        "asset_type": "HVAC_CHILLER",
        "vibration_mm_s": 8.5,
        "operating_temp_c": 92.0,
        "ambient_temp_c": 49.0,
        "power_kw": 135.0,
        "runtime_hours": 9800.0,
        "last_maintenance_days": 90,
        "asset_location": "PALM_JUMEIRAH",
        "asset_criticality": "CRITICAL",
        "required_spare_part": "CHILLER_EXPANSION_VALVE",
        "current_stock": 2.0,
        "lead_time_days": 14.0,
        "spare_part_cost": 600.0,
        "sla_deadline_hours": 0.25,  # 15 min SLA deadline (impossible from distant location)
        "estimated_repair_duration_hours": 1.5,
        "candidate_technicians": [
            {
                "technician_id": "TECH-DEIRA-100 (Distant Junior)",
                "skills": ["HVAC_GENERAL"],
                "availability": True,
                "current_location": "DEIRA",
                "technician_workload": 4,
            }
        ],
    }
    response = client.post("/autonomous-operation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["failure_prediction"]["failure_probability"] > 0.50
    assert data["technician_dispatch"]["sla_status"] == "SLA_BREACH_RISK"
    assert data["unified_action"] == "SLA_ESCALATION_REQUIRED"
    assert "SLA deadline" in data["operational_summary"]


def test_scenario_healthy_asset_with_critical_stockout():
    """Verify that a healthy asset with zero stock recommends parts reorder without triggering urgent maintenance."""
    client = TestClient(app)
    payload = {
        "asset_id": "CHILLER-DIFC-002",
        "asset_type": "HVAC_CHILLER",
        "vibration_mm_s": 1.2,
        "operating_temp_c": 52.0,
        "ambient_temp_c": 32.0,
        "power_kw": 45.0,
        "runtime_hours": 1200.0,
        "last_maintenance_days": 10,
        "asset_location": "DIFC",
        "asset_criticality": "MEDIUM",
        "required_spare_part": "CHILLER_EXPANSION_VALVE",
        "current_stock": 0.0,  # Zero stock
        "lead_time_days": 14.0,
        "spare_part_cost": 450.0,
        "sla_deadline_hours": 6.0,
    }
    response = client.post("/autonomous-operation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["failure_prediction"]["failure_probability"] < 0.25
    assert data["failure_prediction"]["predicted_status"] == "HEALTHY"
    assert data["inventory_intelligence"]["stockout_risk"] == "CRITICAL"
    assert data["inventory_intelligence"]["recommended_order_quantity"] > 0
    assert data["unified_action"] == "REORDER_SPARE_PARTS"
    assert "stockout risk" in data["operational_summary"].lower()
    assert "optimal" not in data["operational_summary"].lower()
    # No immediate maintenance expenditure needed
    assert data["cost_optimization"]["estimated_savings"] == 0.0


