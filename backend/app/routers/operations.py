"""
Operations Router.
Provides endpoints to trigger autonomous operational workflows and query execution audit logs.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from backend.app.database import list_operation_logs
from backend.app.schemas import AutonomousOperationBackendResponse, TriggerOperationRequest
from backend.app.services.operations_service import operations_orchestrator

router = APIRouter(prefix="/api/operations", tags=["Autonomous Operations"])


@router.post(
    "/trigger/{asset_id}",
    response_model=AutonomousOperationBackendResponse,
    summary="Trigger Autonomous Workflow for an Asset",
)
async def trigger_operation_by_asset(
    asset_id: str,
    vibration_override: Optional[float] = Query(default=None, description="Optional vibration override"),
    operating_temp_override: Optional[float] = Query(default=None, description="Optional operating temp override"),
    ambient_temp_override: Optional[float] = Query(default=None, description="Optional ambient temp override"),
    sla_deadline_hours: float = Query(default=3.0, description="SLA window in hours"),
):
    """
    Triggers the end-to-end autonomous operations flow:
    1. Reads asset telemetry from database
    2. Reads current inventory stock & lead time
    3. Reads available certified technicians
    4. Calls AI Engine (/autonomous-operation)
    5. Saves operation audit log in database
    6. Returns unified intelligence decision
    """
    result = await operations_orchestrator.execute_autonomous_workflow(
        asset_id=asset_id,
        vibration_override=vibration_override,
        operating_temp_override=operating_temp_override,
        ambient_temp_override=ambient_temp_override,
        sla_deadline_hours=sla_deadline_hours,
    )
    return result


@router.post(
    "/evaluate",
    response_model=AutonomousOperationBackendResponse,
    summary="Evaluate Autonomous Workflow with Custom Request Body",
)
async def evaluate_operation(request: TriggerOperationRequest):
    """
    Alternative POST endpoint accepting a JSON body with optional sensor overrides.
    """
    result = await operations_orchestrator.execute_autonomous_workflow(
        asset_id=request.asset_id,
        vibration_override=request.vibration_override,
        operating_temp_override=request.operating_temp_override,
        ambient_temp_override=request.ambient_temp_override,
        sla_deadline_hours=request.sla_deadline_hours or 3.0,
    )
    return result


@router.get(
    "/logs",
    summary="Get Autonomous Operation Audit Logs",
)
async def get_operation_logs(limit: int = Query(default=50, ge=1, le=200)):
    """Retrieve history of executed autonomous operations and audit logs."""
    return list_operation_logs(limit=limit)
