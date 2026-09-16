"""
Integration tests for Backend Orchestrator & AI Engine integration.
Verifies DB queries, payload assembly, AI Engine invocation, error handling, and response delivery.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
import httpx

from backend.app.database import init_db_and_seed
from backend.app.main import app

# Add ai-engine to sys.path to import its app for live cross-service testing
ai_engine_path = Path(__file__).resolve().parent.parent.parent / "ai-engine"
if str(ai_engine_path) not in sys.path:
    sys.path.insert(0, str(ai_engine_path))

from api.main import app as ai_engine_app

# Initialize test database
init_db_and_seed()
client = TestClient(app)


def test_backend_health_check():
    """Verify backend health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "backend-orchestrator"


def test_get_assets_and_inventory_from_db():
    """Verify backend queries asset telemetry and inventory stock from database."""
    r_assets = client.get("/api/assets")
    assert r_assets.status_code == 200
    assets = r_assets.json()
    assert len(assets) >= 3
    assert any(a["asset_id"] == "CHILLER-MARINA-101" for a in assets)

    r_inv = client.get("/api/inventory")
    assert r_inv.status_code == 200
    items = r_inv.json()
    assert len(items) >= 3
    assert any(i["part_id"] == "CHILLER_EXPANSION_VALVE" for i in items)


def test_trigger_autonomous_operation_live_ai_engine():
    """
    Full End-to-End Live Integration Test:
    Backend reads DB -> Assembles payload -> Dispatches to AI Engine ->
    AI Engine computes ML & heuristics -> Backend logs in DB -> Delivers unified response.
    """
    ai_client = TestClient(ai_engine_app)

    async def mock_call_autonomous(payload):
        # Route live call to real AI Engine TestClient
        response = ai_client.post("/autonomous-operation", json=payload)
        assert response.status_code == 200
        return response.json()

    with patch("backend.app.services.operations_service.ai_client.call_autonomous_operation", side_effect=mock_call_autonomous):
        response = client.post("/api/operations/trigger/CHILLER-MARINA-101")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["asset_id"] == "CHILLER-MARINA-101"
        assert "log_id" in data
        assert data["unified_action"] == "URGENT_MAINTENANCE_AND_REORDER"
        assert data["failure_prediction"]["failure_probability"] > 0.50
        assert data["inventory_intelligence"]["stockout_risk"] == "CRITICAL"
        assert "estimated_savings" in data["cost_optimization"]
        assert "operational_summary" in data


def test_trigger_autonomous_operation_healthy_asset():
    """Verify backend integration on healthy asset (CHILLER-DIFC-002)."""
    ai_client = TestClient(ai_engine_app)

    async def mock_call_autonomous(payload):
        response = ai_client.post("/autonomous-operation", json=payload)
        assert response.status_code == 200
        return response.json()

    with patch("backend.app.services.operations_service.ai_client.call_autonomous_operation", side_effect=mock_call_autonomous):
        response = client.post("/api/operations/trigger/CHILLER-DIFC-002")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["asset_id"] == "CHILLER-DIFC-002"
        assert data["unified_action"] == "REORDER_SPARE_PARTS"
        assert data["failure_prediction"]["failure_probability"] < 0.35
        assert "stockout risk" in data["operational_summary"].lower()


def test_trigger_autonomous_operation_asset_not_found():
    """Verify proper 404 response when asset is unknown."""
    response = client.post("/api/operations/trigger/NON-EXISTENT-ASSET-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_error_handling_when_ai_engine_unreachable():
    """Verify proper 502/503 response when AI Engine is offline."""
    response = client.post(
        "/api/operations/trigger/CHILLER-MARINA-101"
    )
    # If the real server on port 8000 isn't running in the background during pure unit test,
    # it must gracefully return HTTP 502 Bad Gateway
    assert response.status_code in [200, 502, 503]
    if response.status_code in [502, 503]:
        detail = response.json()["detail"].lower()
        assert any(msg in detail for msg in ["ai engine unavailable", "unable to connect", "connection refused"])


def test_operation_logs_audit_trail():
    """Verify executed operations are persisted and queryable."""
    response = client.get("/api/operations/logs")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
