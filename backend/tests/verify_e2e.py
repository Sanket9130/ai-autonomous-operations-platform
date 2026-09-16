#!/usr/bin/env python3
"""
End-to-End Live Verification Script for Developer 3 Scope:
AI Autonomous Operations Intelligence Platform
"""

import sys
from pathlib import Path
root_path = str(Path(__file__).resolve().parent.parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.models.operation_log import OperationLog
from backend.app.models.work_order import WorkOrder
from backend.app.seed.seed_data import seed_database
from backend.app.schemas.ai_engine import AIEngineResponse
from backend.app.main import app

def run_e2e_verification():
    print("=" * 70)
    print("AI AUTONOMOUS OPERATIONS PLATFORM — END-TO-END VERIFICATION")
    print("=" * 70)

    # 1. Database Setup
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    seed_database(session)

    def override_get_db():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # 2. Verify Health
    print("\n[STEP 1] Testing Health Endpoint...")
    health_resp = client.get("/health")
    assert health_resp.status_code == 200, f"Health failed: {health_resp.text}"
    print(f" -> PASS: {health_resp.json()}")

    # 3. Verify Assets API & CHILLER-MARINA-101
    print("\n[STEP 2] Testing Assets API...")
    assets_resp = client.get("/api/assets")
    assert assets_resp.status_code == 200
    assets = assets_resp.json()
    assert any(a["asset_id"] == "CHILLER-MARINA-101" for a in assets)
    print(f" -> PASS: Found {len(assets)} assets in DB.")

    chiller_resp = client.get("/api/assets/CHILLER-MARINA-101")
    assert chiller_resp.status_code == 200
    chiller_data = chiller_resp.json()
    assert chiller_data["criticality"] == "CRITICAL"
    assert chiller_data["latest_telemetry"]["vibration_rms"] == 4.82
    print(f" -> PASS: CHILLER-MARINA-101 details verified: Lat={chiller_data['latitude']}, Lon={chiller_data['longitude']}, Vibration={chiller_data['latest_telemetry']['vibration_rms']}")

    # 4. Verify Inventory API
    print("\n[STEP 3] Testing Inventory API...")
    inv_resp = client.get("/api/inventory")
    assert inv_resp.status_code == 200
    inv = inv_resp.json()
    assert any(p["part_id"] == "PART-BRG-7701" for p in inv)
    print(f" -> PASS: Found {len(inv)} inventory items in DB.")

    # 5. Verify Technicians API
    print("\n[STEP 4] Testing Technicians API...")
    tech_resp = client.get("/api/technicians")
    assert tech_resp.status_code == 200
    techs = tech_resp.json()
    assert any(t["technician_id"] == "TECH-DXB-01" for t in techs)
    print(f" -> PASS: Found {len(techs)} technicians in DB.")

    # 6. End-to-End Autonomous Operation Flow
    print("\n[STEP 5] Triggering Autonomous Operation for CHILLER-MARINA-101...")
    mock_ai_data = AIEngineResponse(
        failure_probability=0.88,
        asset_risk="HIGH",
        RUL=42.5,
        recommended_action="REPLACE_BEARING",
        stock_status="CRITICAL_LOW",
        reorder_quantity=5,
        preventive_cost=750.00,
        failure_cost=8500.00,
        estimated_savings=7750.00,
        required_skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL"],
        required_parts=["PART-BRG-7701"],
        priority="HIGH",
        autonomous_decision="SCHEDULE_IMMEDIATE_DISPATCH",
    )

    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_ai_call:
        mock_ai_call.return_value = mock_ai_data

        op_resp = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert op_resp.status_code == 200, f"Trigger failed: {op_resp.text}"
        op_data = op_resp.json()

        print("\n" + "-" * 50)
        print("AUTONOMOUS OPERATION RESPONSE:")
        print(f"Operation ID:  {op_data['operation_id']}")
        print(f"Asset:         {op_data['asset']['name']} ({op_data['asset']['asset_id']})")
        print(f"Prediction:    Risk={op_data['prediction']['asset_risk']}, FailProb={op_data['prediction']['failure_probability']}, RUL={op_data['prediction']['RUL']}h")
        print(f"Inventory:     Part={op_data['inventory']['part_name']} ({op_data['inventory']['part_id']}), Stock={op_data['inventory']['current_stock']}, Reorder={op_data['inventory']['reorder_quantity']}")
        print(f"Technician:    {op_data['technician']['name']} ({op_data['technician']['technician_id']}), Score={op_data['technician']['score']}")
        print(f"Routing:       Distance={op_data['route']['distance_km']} km, ETA={op_data['route']['eta_minutes']} mins @ {op_data['route']['average_speed_kmh']} km/h")
        print(f"SLA:           Limit={op_data['sla']['sla_hours']}h, Status={op_data['sla']['sla_status']}")
        print(f"Cost & ROI:    Prev Cost=${op_data['cost']['preventive_cost']}, Fail Cost=${op_data['cost']['failure_cost']}, Savings=${op_data['cost']['estimated_savings']}")
        print(f"Decision:      {op_data['decision']['final_action']} (Priority: {op_data['decision']['priority']})")
        print(f"Summary:       {op_data['summary']}")
        print("-" * 50)

        # Assertions
        assert op_data["technician"]["technician_id"] == "TECH-DXB-01"
        assert op_data["sla"]["sla_status"] == "WITHIN_SLA"
        assert op_data["cost"]["estimated_savings"] == 7750.00

        # Verify DB Persistence
        db_log = session.query(OperationLog).filter(OperationLog.operation_id == op_data["operation_id"]).first()
        assert db_log is not None
        assert db_log.asset_id == "CHILLER-MARINA-101"
        assert db_log.technician_id == "TECH-DXB-01"
        print(" -> PASS: Operation log successfully persisted in database.")

        db_wo = session.query(WorkOrder).filter(WorkOrder.operation_id == op_data["operation_id"]).first()
        assert db_wo is not None
        assert db_wo.technician_id == "TECH-DXB-01"
        print(" -> PASS: Work order successfully created in database.")

    # 7. Verify Error Handling & No Fake AI Results
    print("\n[STEP 6] Testing AI Engine Unavailable Resiliency...")
    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_ai_fail:
        from fastapi import HTTPException
        mock_ai_fail.side_effect = HTTPException(status_code=502, detail="AI Engine unavailable. Connection refused.")
        fail_resp = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert fail_resp.status_code == 502
        print(f" -> PASS: Responded with HTTP 502 (No fake AI predictions generated): {fail_resp.json()['detail']}")

    print("\n" + "=" * 70)
    print("ALL END-TO-END CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()
