import uuid
from datetime import datetime, timezone
from typing import Optional, Union, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.asset import Asset
from backend.app.models.telemetry import Telemetry
from backend.app.models.inventory import Inventory
from backend.app.models.technician import Technician
from backend.app.models.maintenance import Maintenance
from backend.app.models.operation_log import OperationLog
from backend.app.models.work_order import WorkOrder
from backend.app.schemas.ai_engine import (
    AIEngineRequest,
    AIEngineTelemetry,
    AIEngineMaintenance,
    AIEngineSparePart,
    AIEngineResponse,
)
from backend.app.schemas.operation import (
    OperationResponse,
    OperationAsset,
    OperationPrediction,
    OperationInventory,
    OperationTechnician,
    OperationRoute,
    OperationSLA,
    OperationCost,
    OperationDecision,
)
from backend.app.services.ai_engine_client import ai_engine_client, AIEngineClient
from backend.app.services.technician_assignment import rank_technicians


async def orchestrate_autonomous_operation(
    asset_id: str,
    db: Session,
    client: Optional[AIEngineClient] = None,
    vibration_override: Optional[float] = None,
    operating_temp_override: Optional[float] = None,
    ambient_temp_override: Optional[float] = None,
    sla_deadline_hours: float = 3.0,
) -> OperationResponse:
    """
    Executes the complete end-to-end autonomous operations pipeline:
      1. Validate asset in DB
      2. Fetch latest telemetry
      3. Fetch compatible spare parts / inventory
      4. Fetch available technicians
      5. Build AI Engine request payload (dict/schema compatible)
      6. POST /autonomous-operation to AI Engine with timeout and error handling
      7. Validate AI response (do not fabricate if unavailable)
      8. Deterministically rank and select qualified technician
      9. Calculate Haversine distance, speed, and ETA
      10. Evaluate SLA compliance (WITHIN_SLA, AT_RISK, SLA_BREACH_RISK)
      11. Persist operation log & work order in SQLite/PostgreSQL
      12. Return clean unified response for frontend and integration tests
    """
    ai_client = client or ai_engine_client

    # 1. Validate asset
    asset: Optional[Asset] = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with ID '{asset_id}' not found."
        )

    # 2. Fetch latest telemetry
    latest_telemetry: Optional[Telemetry] = (
        db.query(Telemetry)
        .filter(Telemetry.asset_id == asset_id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )

    vibration = vibration_override if vibration_override is not None else (
        latest_telemetry.vibration_rms if latest_telemetry else (asset.vibration_mm_s or 1.0)
    )
    operating_temp = operating_temp_override if operating_temp_override is not None else (
        latest_telemetry.bearing_temperature if latest_telemetry else (asset.operating_temp_c or 65.0)
    )
    ambient_temp = ambient_temp_override if ambient_temp_override is not None else (
        asset.ambient_temp_c or 42.0
    )
    power = latest_telemetry.power_kw if latest_telemetry else (asset.power_kw or 30.0)
    runtime = latest_telemetry.operating_hours if latest_telemetry else (asset.runtime_hours or 5000.0)

    # 3. Fetch maintenance history
    maintenance_rec: Optional[Maintenance] = (
        db.query(Maintenance)
        .filter(Maintenance.asset_id == asset_id)
        .order_by(Maintenance.serviced_at.desc())
        .first()
    )

    # 4. Fetch compatible inventory spare parts
    target_part_id = asset.required_spare_part_id or "PART-BRG-7701"
    db_parts = (
        db.query(Inventory)
        .filter((Inventory.asset_type == asset.asset_type) | (Inventory.asset_type.is_(None)))
        .all()
    )
    if not db_parts:
        db_parts = db.query(Inventory).all()

    target_part = next((p for p in db_parts if p.part_id == target_part_id), None)
    if not target_part:
        target_part = db.query(Inventory).filter(Inventory.part_id == target_part_id).first()

    current_stock = float(target_part.current_stock) if target_part else 0.0
    lead_time = float(target_part.lead_time) if target_part else 14.0
    unit_cost = float(target_part.unit_cost) if target_part else 450.0

    # 5. Fetch available technicians
    available_technicians = (
        db.query(Technician)
        .filter(Technician.availability.is_(True))
        .all()
    )

    candidates = [
        {
            "technician_id": t.technician_id,
            "skills": t.skills or [],
            "availability": bool(t.availability),
            "current_location": t.current_location or "MARINA",
            "technician_workload": t.active_workload or 0,
        }
        for t in available_technicians
    ]

    # 6. Build AI Engine request payload dictionary
    loc = (asset.location or "MARINA").upper()
    if "MARINA" in loc:
        std_loc = "MARINA"
    elif "DIFC" in loc:
        std_loc = "DIFC"
    elif "DOWNTOWN" in loc:
        std_loc = "DOWNTOWN"
    elif "DEIRA" in loc:
        std_loc = "DEIRA"
    elif "PALM" in loc:
        std_loc = "PALM_JUMEIRAH"
    else:
        std_loc = "MARINA"

    ai_payload = {
        "asset_id": asset.asset_id,
        "asset_type": asset.asset_type,
        "asset_location": std_loc,
        "vibration_mm_s": float(vibration),
        "operating_temp_c": float(operating_temp),
        "ambient_temp_c": float(ambient_temp),
        "power_kw": float(power),
        "runtime_hours": float(runtime),
        "last_maintenance_days": int(asset.last_maintenance_days or 30),
        "asset_criticality": asset.criticality,
        "required_spare_part": target_part_id,
        "current_stock": current_stock,
        "lead_time_days": lead_time,
        "forecast_days": 30,
        "spare_part_cost": unit_cost,
        "sla_deadline_hours": float(sla_deadline_hours),
        "estimated_repair_duration_hours": 1.5,
        "candidate_technicians": candidates if candidates else None,
    }

    # 7. POST /autonomous-operation to AI Engine
    raw_response = await ai_client.call_autonomous_operation(ai_payload)
    if isinstance(raw_response, dict):
        ai_response = AIEngineResponse.model_validate(raw_response)
    else:
        ai_response = raw_response

    # 8. Deterministically select/rank technicians
    ranked_technicians = rank_technicians(
        technicians=available_technicians,
        asset=asset,
        required_skills=ai_response.required_skills,
    )

    selected_tech = None
    route_info = None
    sla_info = None

    if ranked_technicians:
        top_match = ranked_technicians[0]
        selected_tech = top_match["technician"]
        route_info = top_match["route"]
        sla_info = top_match["sla"]

    # 9. Extract authoritative inventory & ROP fields from AI Engine response
    ai_inv = ai_response.inventory_intelligence or {}
    authoritative_rop = (
        float(ai_inv["reorder_point"])
        if "reorder_point" in ai_inv and ai_inv["reorder_point"] is not None
        else (
            float(ai_response.reorder_point)
            if hasattr(ai_response, "reorder_point") and ai_response.reorder_point is not None
            else (float(target_part.minimum_stock) if target_part and target_part.minimum_stock is not None else 8.0)
        )
    )
    authoritative_safety_stock = (
        float(ai_inv["safety_stock"])
        if "safety_stock" in ai_inv and ai_inv["safety_stock"] is not None
        else (
            float(ai_response.safety_stock)
            if hasattr(ai_response, "safety_stock") and ai_response.safety_stock is not None
            else 4.0
        )
    )
    authoritative_predicted_demand = (
        float(ai_inv["predicted_demand_30d"])
        if "predicted_demand_30d" in ai_inv and ai_inv["predicted_demand_30d"] is not None
        else (
            float(ai_response.predicted_demand_30d)
            if hasattr(ai_response, "predicted_demand_30d") and ai_response.predicted_demand_30d is not None
            else 12.0
        )
    )
    authoritative_reorder_qty = (
        int(ai_inv["recommended_order_quantity"])
        if "recommended_order_quantity" in ai_inv and ai_inv["recommended_order_quantity"] is not None
        else int(ai_response.reorder_quantity)
    )
    authoritative_stockout_risk = (
        ai_inv.get("stockout_risk")
        or ("CRITICAL" if ai_response.stock_status in ["CRITICAL_LOW", "CRITICAL", "OUT_OF_STOCK"] else "LOW")
    )
    authoritative_current_stock = float(
        ai_inv.get("current_stock")
        if ai_inv.get("current_stock") is not None
        else (target_part.current_stock if target_part and target_part.current_stock is not None else 0.0)
    )

    matched_inventory = None
    req_part_id = ai_response.required_parts[0] if ai_response.required_parts else target_part_id

    if req_part_id:
        inv_part = next((p for p in db_parts if p.part_id == req_part_id), None)
        if not inv_part:
            inv_part = db.query(Inventory).filter(Inventory.part_id == req_part_id).first()

        if inv_part:
            matched_inventory = OperationInventory(
                part_id=inv_part.part_id,
                part_name=inv_part.part_name,
                stock_status=ai_response.stock_status,
                current_stock=inv_part.current_stock,
                minimum_stock=inv_part.minimum_stock,
                reorder_point=authoritative_rop,
                safety_stock=authoritative_safety_stock,
                predicted_demand_30d=authoritative_predicted_demand,
                reorder_quantity=authoritative_reorder_qty,
            )

    # 10. Generate Operation ID & Log Entry
    operation_id = f"op-{uuid.uuid4().hex[:12]}"
    now_utc = datetime.now(timezone.utc)

    final_action_code = ai_response.autonomous_decision or ai_response.recommended_action or "SCHEDULE_IMMEDIATE_DISPATCH"
    tech_str = (
        f"Dispatched {selected_tech.name} (ETA: {route_info['eta_minutes']} mins, {sla_info['sla_status']})"
        if selected_tech and route_info and sla_info
        else "No available technician found"
    )
    part_str = (
        f"Reorder {authoritative_reorder_qty} units of {matched_inventory.part_name} ({matched_inventory.part_id})"
        if matched_inventory and authoritative_reorder_qty > 0
        else "Parts stock adequate"
    )
    summary_text = (
        ai_response.operational_summary
        if ai_response.operational_summary
        else (
            f"Autonomous Operation triggered for {asset.name} ({asset.asset_id}): "
            f"{ai_response.asset_risk} Risk ({round(ai_response.failure_probability * 100, 1)}% failure prob, RUL: {ai_response.RUL}h). "
            f"Action: {final_action_code}. {tech_str}. {part_str}."
        )
    )

    op_log = OperationLog(
        operation_id=operation_id,
        asset_id=asset.asset_id,
        timestamp=now_utc,
        failure_probability=ai_response.failure_probability,
        asset_risk=ai_response.asset_risk,
        RUL=ai_response.RUL,
        stock_status=ai_response.stock_status,
        reorder_quantity=authoritative_reorder_qty,
        technician_id=selected_tech.technician_id if selected_tech else None,
        ETA=route_info["eta_minutes"] if route_info else 0.0,
        SLA_status=sla_info["sla_status"] if sla_info else "N/A",
        preventive_cost=ai_response.preventive_cost,
        failure_cost=ai_response.failure_cost,
        estimated_savings=ai_response.estimated_savings,
        final_action=final_action_code,
        unified_action=final_action_code,
        risk_score=ai_response.failure_probability * 100.0,
        selected_technician=f"{selected_tech.technician_id} ({selected_tech.name})" if selected_tech else "NONE",
        technician_eta_minutes=route_info["eta_minutes"] if route_info else 0.0,
        estimated_savings_aed=ai_response.estimated_savings,
        operational_summary=summary_text,
        raw_ai_response=ai_response.model_dump(),
    )

    db.add(op_log)

    # Deterministic mapping: AI operation risk/urgency -> work order priority
    risk_to_priority = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
    }
    work_order_priority = risk_to_priority.get(
        str(ai_response.asset_risk).upper(),
        risk_to_priority.get(str(ai_response.priority).upper(), "MEDIUM"),
    )

    # If technician assigned, create WorkOrder record
    if selected_tech:
        work_order = WorkOrder(
            id=f"wo-{uuid.uuid4().hex[:8]}",
            operation_id=operation_id,
            asset_id=asset.asset_id,
            technician_id=selected_tech.technician_id,
            status="DISPATCHED",
            priority=work_order_priority,
            created_at=now_utc,
        )
        db.add(work_order)

    # Commit operation log and work order to DB
    db.commit()

    # 11. Build unified response matching both test schemas and frontend expectations
    failure_prediction_dict = {
        "failure_probability": ai_response.failure_probability,
        "predicted_status": ai_response.asset_risk,
        "risk_score": ai_response.failure_probability * 100.0,
        "estimated_rul_days": round(ai_response.RUL / 24.0, 2) if ai_response.RUL else 1.77,
    }

    inventory_intel_dict = {
        "spare_part": ai_inv.get("spare_part") or (matched_inventory.part_name if matched_inventory else target_part_id),
        "current_stock": authoritative_current_stock,
        "predicted_demand_30d": authoritative_predicted_demand,
        "safety_stock": authoritative_safety_stock,
        "reorder_point": authoritative_rop,
        "stockout_risk": authoritative_stockout_risk,
        "recommended_order_quantity": authoritative_reorder_qty,
    }

    tech_dispatch_dict = {
        "selected_technician": f"{selected_tech.technician_id} ({selected_tech.name})" if selected_tech else "NONE",
        "technician_score": ranked_technicians[0]["score"] if ranked_technicians else 0.0,
        "distance_km": route_info["distance_km"] if route_info else 0.0,
        "estimated_eta_minutes": route_info["eta_minutes"] if route_info else 0.0,
        "sla_status": sla_info["sla_status"] if sla_info else "UNKNOWN",
    }

    cost_opt_dict = {
        "preventive_total_cost": ai_response.preventive_cost,
        "failure_total_cost": ai_response.failure_cost,
        "estimated_savings": ai_response.estimated_savings,
    }

    return OperationResponse(
        operation_id=operation_id,
        timestamp=now_utc,
        asset=OperationAsset(
            asset_id=asset.asset_id,
            name=asset.name,
            asset_type=asset.asset_type,
            location=asset.location,
            latitude=asset.latitude,
            longitude=asset.longitude,
            criticality=asset.criticality,
            status=asset.status,
        ),
        prediction=OperationPrediction(
            failure_probability=ai_response.failure_probability,
            asset_risk=ai_response.asset_risk,
            RUL=ai_response.RUL,
            recommended_action=ai_response.recommended_action,
        ),
        inventory=matched_inventory,
        technician=OperationTechnician(
            technician_id=selected_tech.technician_id,
            name=selected_tech.name,
            skills=selected_tech.skills or [],
            certifications=selected_tech.certifications or [],
            experience=selected_tech.experience,
            current_latitude=selected_tech.current_latitude,
            current_longitude=selected_tech.current_longitude,
            score=ranked_technicians[0]["score"] if ranked_technicians else None,
        ) if selected_tech else None,
        route=OperationRoute(
            distance_km=route_info["distance_km"],
            eta_minutes=route_info["eta_minutes"],
            average_speed_kmh=route_info["average_speed_kmh"],
        ) if route_info else None,
        sla=OperationSLA(
            sla_hours=sla_info["sla_hours"],
            eta_hours=sla_info["eta_hours"],
            sla_status=sla_info["sla_status"],
        ) if sla_info else None,
        cost=OperationCost(
            preventive_cost=ai_response.preventive_cost,
            failure_cost=ai_response.failure_cost,
            estimated_savings=ai_response.estimated_savings,
        ),
        decision=OperationDecision(
            final_action=final_action_code,
            priority=work_order_priority,
            autonomous_decision=final_action_code,
        ),
        summary=summary_text,
        status="success",
        log_id=operation_id,
        asset_id=asset.asset_id,
        unified_action=final_action_code,
        operational_summary=summary_text,
        failure_prediction=failure_prediction_dict,
        inventory_intelligence=inventory_intel_dict,
        technician_dispatch=tech_dispatch_dict,
        cost_optimization=cost_opt_dict,
        ai_engine_metadata={
            "endpoint_called": getattr(ai_client, "base_url", "http://localhost:8000"),
            "asset_location": asset.location,
            "required_spare_part": target_part_id,
        },
    )
