from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException, status
from backend.app.schemas.ai_engine import AIEngineResponse
from backend.app.models.operation_log import OperationLog
from backend.app.models.work_order import WorkOrder


@pytest.fixture
def mock_ai_response():
    return AIEngineResponse(
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


def test_successful_autonomous_operation(client, db_session, mock_ai_response):
    """
    Test end-to-end autonomous operation triggering on CHILLER-MARINA-101.
    Verifies:
      - Valid response structure
      - Technician selected and ranked
      - Haversine distance, speed, and ETA populated
      - SLA status calculated
      - Operation log saved in database
      - Work order created
    """
    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_call:
        mock_call.return_value = mock_ai_response

        response = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "operation_id" in data
        assert data["asset"]["asset_id"] == "CHILLER-MARINA-101"
        assert data["prediction"]["failure_probability"] == 0.88
        assert data["prediction"]["asset_risk"] == "HIGH"
        assert data["inventory"]["part_id"] == "PART-BRG-7701"
        assert data["inventory"]["reorder_quantity"] == 5

        # Check technician assignment
        assert data["technician"] is not None
        assert data["technician"]["technician_id"] == "TECH-DXB-01"
        assert "HVAC_CERTIFIED" in data["technician"]["skills"]

        # Check route and SLA
        assert data["route"]["distance_km"] > 0
        assert data["route"]["eta_minutes"] > 0
        assert data["sla"]["sla_status"] in ["WITHIN_SLA", "AT_RISK", "SLA_BREACH_RISK"]
        assert data["sla"]["sla_hours"] == 2.0  # Critical asset limit

        # Check cost & decision
        assert data["cost"]["preventive_cost"] == 750.00
        assert data["cost"]["estimated_savings"] == 7750.00
        assert data["decision"]["final_action"] == "SCHEDULE_IMMEDIATE_DISPATCH"
        assert "summary" in data

        # Check DB persistence
        op_id = data["operation_id"]
        saved_log = db_session.query(OperationLog).filter(OperationLog.operation_id == op_id).first()
        assert saved_log is not None
        assert saved_log.asset_id == "CHILLER-MARINA-101"
        assert saved_log.failure_probability == 0.88
        assert saved_log.technician_id == "TECH-DXB-01"

        saved_wo = db_session.query(WorkOrder).filter(WorkOrder.operation_id == op_id).first()
        assert saved_wo is not None
        assert saved_wo.technician_id == "TECH-DXB-01"
        assert saved_wo.status == "DISPATCHED"
        assert saved_wo.priority == "HIGH"


def test_operation_invalid_asset(client):
    """Test operation trigger fails with 404 for non-existent asset."""
    response = client.post("/api/operations/trigger/NON-EXISTENT-CHILLER")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_operation_ai_engine_unavailable(client):
    """
    Test system does not fabricate results when AI Engine is unreachable.
    Must return 502 Bad Gateway with meaningful error.
    """
    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_call:
        mock_call.side_effect = HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI Engine unavailable. Connection refused."
        )

        response = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert response.status_code == 502
        assert "AI Engine unavailable" in response.json()["detail"]


def test_operation_ai_engine_timeout(client):
    """
    Test system returns 504 Gateway Timeout when AI Engine times out.
    """
    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_call:
        mock_call.side_effect = HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI Engine request timed out after 15.0 seconds."
        )

        response = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()


def test_operation_logs_endpoint(client, db_session, mock_ai_response):
    """Test retrieving operation logs via API."""
    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_call:
        mock_call.return_value = mock_ai_response
        client.post("/api/operations/trigger/CHILLER-MARINA-101")

    logs_resp = client.get("/api/operations/logs")
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    assert len(logs) >= 1
    assert logs[0]["asset_id"] == "CHILLER-MARINA-101"


@pytest.mark.parametrize(
    "risk_level,expected_priority",
    [
        ("CRITICAL", "CRITICAL"),
        ("HIGH", "HIGH"),
        ("MEDIUM", "MEDIUM"),
        ("LOW", "LOW"),
    ],
)
def test_autonomous_work_order_priority_mapping(
    client, db_session, mock_ai_response, risk_level, expected_priority
):
    """
    Verify that autonomous work order priority is derived consistently
    from the operation decision / asset risk level:
      CRITICAL -> CRITICAL
      HIGH -> HIGH
      MEDIUM -> MEDIUM
      LOW -> LOW
    """
    mock_ai_response.asset_risk = risk_level
    mock_ai_response.priority = expected_priority

    with patch(
        "backend.app.services.operation_orchestrator.ai_engine_client.call_autonomous_operation",
        new_callable=AsyncMock,
    ) as mock_call:
        mock_call.return_value = mock_ai_response

        response = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert response.status_code == 200
        data = response.json()

        assert data["decision"]["priority"] == expected_priority

        op_id = data["operation_id"]
        saved_wo = db_session.query(WorkOrder).filter(WorkOrder.operation_id == op_id).first()
        assert saved_wo is not None
        assert saved_wo.priority == expected_priority

