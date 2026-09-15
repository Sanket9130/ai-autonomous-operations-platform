from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.operation_log import OperationLog
from backend.app.schemas.operation import OperationResponse
from backend.app.services.operation_orchestrator import orchestrate_autonomous_operation

router = APIRouter(prefix="/api/operations", tags=["Operations"])


@router.post("/trigger/{asset_id}", response_model=OperationResponse)
async def trigger_operation(asset_id: str, db: Session = Depends(get_db)):
    """
    Trigger end-to-end autonomous operations for a specified asset:
      1. Validate asset
      2. Fetch telemetry & maintenance
      3. Fetch spare parts inventory
      4. Fetch available technicians
      5. Call AI Engine /autonomous-operation
      6. Rank technicians deterministically
      7. Calculate Haversine distance, speed, and ETA
      8. Calculate SLA compliance
      9. Persist operation log & work order
      10. Return clean frontend response
    """
    return await orchestrate_autonomous_operation(asset_id=asset_id, db=db)


@router.get("/logs", response_model=List[dict])
def get_operation_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve historical autonomous operation logs.
    """
    logs = db.query(OperationLog).order_by(OperationLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "operation_id": log.operation_id,
            "asset_id": log.asset_id,
            "timestamp": log.timestamp.isoformat(),
            "failure_probability": log.failure_probability,
            "asset_risk": log.asset_risk,
            "RUL": log.RUL,
            "stock_status": log.stock_status,
            "reorder_quantity": log.reorder_quantity,
            "technician_id": log.technician_id,
            "ETA": log.ETA,
            "SLA_status": log.SLA_status,
            "preventive_cost": log.preventive_cost,
            "failure_cost": log.failure_cost,
            "estimated_savings": log.estimated_savings,
            "final_action": log.final_action,
        }
        for log in logs
    ]


@router.get("/logs/{operation_id}", response_model=dict)
def get_operation_log(operation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single operation log by operation_id.
    """
    log = db.query(OperationLog).filter(OperationLog.operation_id == operation_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation log '{operation_id}' not found."
        )
    return {
        "operation_id": log.operation_id,
        "asset_id": log.asset_id,
        "timestamp": log.timestamp.isoformat(),
        "failure_probability": log.failure_probability,
        "asset_risk": log.asset_risk,
        "RUL": log.RUL,
        "stock_status": log.stock_status,
        "reorder_quantity": log.reorder_quantity,
        "technician_id": log.technician_id,
        "ETA": log.ETA,
        "SLA_status": log.SLA_status,
        "preventive_cost": log.preventive_cost,
        "failure_cost": log.failure_cost,
        "estimated_savings": log.estimated_savings,
        "final_action": log.final_action,
        "raw_ai_response": log.raw_ai_response,
    }
