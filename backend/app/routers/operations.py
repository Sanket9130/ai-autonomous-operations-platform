"""
Operations Router.
Provides endpoints to trigger autonomous operational workflows and query execution audit logs.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.operation_log import OperationLog
from backend.app.schemas.operation import AutonomousOperationBackendResponse, OperationResponse, TriggerOperationRequest
from backend.app.services.operation_orchestrator import orchestrate_autonomous_operation

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
    db: Session = Depends(get_db),
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
    result = await orchestrate_autonomous_operation(
        asset_id=asset_id,
        db=db,
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
async def evaluate_operation(request: TriggerOperationRequest, db: Session = Depends(get_db)):
    """
    Alternative POST endpoint accepting a JSON body with optional sensor overrides.
    """
    if not request.asset_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset ID must be provided in request body."
        )
    result = await orchestrate_autonomous_operation(
        asset_id=request.asset_id,
        db=db,
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
async def get_operation_logs(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve history of executed autonomous operations and audit logs with newest first."""
    logs = (
        db.query(OperationLog)
        .order_by(OperationLog.timestamp.desc(), OperationLog.operation_id.desc())
        .limit(limit)
        .all()
    )

    formatted_logs = []
    for log in logs:
        formatted_logs.append({
            "id": log.operation_id,
            "operation_id": log.operation_id,
            "asset_id": log.asset_id,
            "executed_at": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "",
            "timestamp": log.timestamp.isoformat() if log.timestamp else "",
            "failure_probability": log.failure_probability,
            "asset_risk": log.asset_risk,
            "risk_score": log.risk_score if log.risk_score is not None else (log.failure_probability * 100.0),
            "unified_action": log.unified_action or log.final_action,
            "final_action": log.final_action,
            "selected_technician": log.selected_technician or (log.technician_id or "NONE"),
            "technician_id": log.technician_id,
            "technician_eta_minutes": log.technician_eta_minutes if log.technician_eta_minutes is not None else log.ETA,
            "ETA": log.ETA,
            "SLA_status": log.SLA_status,
            "estimated_savings_aed": log.estimated_savings_aed if log.estimated_savings_aed is not None else log.estimated_savings,
            "estimated_savings": log.estimated_savings,
            "preventive_cost": log.preventive_cost,
            "failure_cost": log.failure_cost,
            "operational_summary": log.operational_summary or "",
            "raw_ai_response": log.raw_ai_response,
        })

    return formatted_logs
