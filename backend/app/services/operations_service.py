"""
Operations Orchestration Service.
Connects database entities (Assets, Telemetry, Inventory, Technicians) with the AI Engine microservice.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status

from backend.app.database import (
    get_asset_by_id,
    get_candidate_technicians,
    get_inventory_item,
    save_operation_log,
)
from backend.app.services.ai_client import ai_client


class OperationsOrchestrator:
    """Orchestrates operational workflows between the PostgreSQL/SQLite database and AI Engine."""

    async def execute_autonomous_workflow(
        self,
        asset_id: str,
        vibration_override: Optional[float] = None,
        operating_temp_override: Optional[float] = None,
        ambient_temp_override: Optional[float] = None,
        sla_deadline_hours: float = 3.0,
    ) -> Dict[str, Any]:
        """
        Full orchestration flow:
          1. Retrieve asset & sensor telemetry from DB
          2. Retrieve spare-part stock and lead times from DB
          3. Retrieve candidate technicians from DB
          4. Assemble standard AI request payload
          5. Dispatch to AI Engine (/autonomous-operation)
          6. Persist execution record in audit log
          7. Return unified response
        """
        # 1. Fetch Asset & Telemetry
        asset = get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset '{asset_id}' not found in operations database.",
            )

        # 2. Fetch Linked Inventory & Spare Part
        part_id = asset["required_spare_part_id"]
        inventory = get_inventory_item(part_id)
        if not inventory:
            # Safe baseline fallback if inventory record is unmapped
            current_stock = 0.0
            unit_cost = 450.0
            lead_time = 14.0
        else:
            current_stock = float(inventory["current_stock"])
            unit_cost = float(inventory["unit_cost_aed"])
            lead_time = float(inventory["lead_time_days"])

        # 3. Fetch Available Certified Technicians
        candidates = get_candidate_technicians(only_available=True)

        # 4. Assemble AI Engine Request Payload
        ai_payload = {
            "asset_id": asset["asset_id"],
            "asset_type": asset["asset_type"],
            "asset_location": asset["location"],
            "vibration_mm_s": vibration_override if vibration_override is not None else float(asset["vibration_mm_s"]),
            "operating_temp_c": operating_temp_override if operating_temp_override is not None else float(asset["operating_temp_c"]),
            "ambient_temp_c": ambient_temp_override if ambient_temp_override is not None else float(asset["ambient_temp_c"]),
            "power_kw": float(asset["power_kw"]),
            "runtime_hours": float(asset["runtime_hours"]),
            "last_maintenance_days": int(asset["last_maintenance_days"]),
            "asset_criticality": asset["criticality"],
            "required_spare_part": part_id,
            "current_stock": current_stock,
            "lead_time_days": lead_time,
            "spare_part_cost": unit_cost,
            "sla_deadline_hours": sla_deadline_hours,
            "estimated_repair_duration_hours": 1.5,
            "candidate_technicians": candidates if candidates else None,
        }

        # 5. Call AI Engine (/autonomous-operation)
        ai_response = await ai_client.call_autonomous_operation(ai_payload)

        # 6. Save Operation Audit Log
        cost_opt = ai_response.get("cost_optimization", {})
        tech_disp = ai_response.get("technician_dispatch", {})
        fail_pred = ai_response.get("failure_prediction", {})

        log_id = save_operation_log(
            asset_id=asset_id,
            unified_action=ai_response.get("unified_action", "UNKNOWN"),
            failure_probability=float(fail_pred.get("failure_probability", 0.0)),
            risk_score=float(fail_pred.get("risk_score", 0.0)),
            selected_technician=tech_disp.get("selected_technician", "NONE"),
            technician_eta_minutes=float(tech_disp.get("estimated_eta_minutes", 0.0)),
            estimated_savings_aed=float(cost_opt.get("estimated_savings", 0.0)),
            operational_summary=ai_response.get("operational_summary", ""),
            full_response=ai_response,
        )

        # 7. Formulate Final Response
        return {
            "status": "success",
            "log_id": log_id,
            "asset_id": asset_id,
            "unified_action": ai_response.get("unified_action"),
            "operational_summary": ai_response.get("operational_summary"),
            "failure_prediction": fail_pred,
            "inventory_intelligence": ai_response.get("inventory_intelligence", {}),
            "technician_dispatch": tech_disp,
            "cost_optimization": cost_opt,
            "ai_engine_metadata": {
                "endpoint_called": ai_client.endpoint_url,
                "asset_location": asset["location"],
                "required_spare_part": part_id,
            },
        }


operations_orchestrator = OperationsOrchestrator()
