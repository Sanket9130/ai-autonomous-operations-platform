"""
Operations Orchestration Service Compatibility Layer.
Connects database entities with AI Engine and operation orchestrator.
"""

from typing import Any, Dict, Optional
from backend.app.core.database import SessionLocal
from backend.app.services.operation_orchestrator import orchestrate_autonomous_operation
from backend.app.services.ai_client import ai_client


class OperationsOrchestrator:
    async def execute_autonomous_workflow(
        self,
        asset_id: str,
        vibration_override: Optional[float] = None,
        operating_temp_override: Optional[float] = None,
        ambient_temp_override: Optional[float] = None,
        sla_deadline_hours: float = 3.0,
    ) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            res = await orchestrate_autonomous_operation(
                asset_id=asset_id,
                db=db,
                client=ai_client,
                vibration_override=vibration_override,
                operating_temp_override=operating_temp_override,
                ambient_temp_override=ambient_temp_override,
                sla_deadline_hours=sla_deadline_hours,
            )
            return res.model_dump()
        finally:
            db.close()


operations_orchestrator = OperationsOrchestrator()
