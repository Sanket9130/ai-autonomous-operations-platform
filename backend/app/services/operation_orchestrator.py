import uuid
from datetime import datetime, timezone
from typing import Optional
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
) -> OperationResponse:
    """
    Executes the complete end-to-end autonomous operations pipeline:
      1. Validate asset in DB
      2. Fetch latest telemetry
      3. Fetch compatible spare parts / inventory
      4. Fetch available technicians
      5. Build AI Engine request payload
      6. POST /autonomous-operation to AI Engine with timeout and error handling
      7. Validate AI response (do not fabricate if unavailable)
      8. Deterministically rank and select qualified technician
      9. Calculate Haversine distance, speed, and ETA
      10. Evaluate SLA compliance (WITHIN_SLA, AT_RISK, SLA_BREACH_RISK)
      11. Persist operation log & work order in PostgreSQL
      12. Return clean unified response for the frontend
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

    telemetry_data = AIEngineTelemetry(
        vibration_rms=latest_telemetry.vibration_rms if latest_telemetry else 1.0,
        bearing_temperature=latest_telemetry.bearing_temperature if latest_telemetry else 65.0,
        coolant_pressure=latest_telemetry.coolant_pressure if latest_telemetry else 4.0,
        power_kw=latest_telemetry.power_kw if latest_telemetry else 30.0,
        operating_hours=latest_telemetry.operating_hours if latest_telemetry else 5000.0,
    )

    # 3. Fetch maintenance history
    maintenance_rec: Optional[Maintenance] = (
        db.query(Maintenance)
        .filter(Maintenance.asset_id == asset_id)
        .order_by(Maintenance.serviced_at.desc())
        .first()
    )

    maintenance_history = AIEngineMaintenance(
        last_serviced=maintenance_rec.serviced_at.isoformat() if maintenance_rec else None,
        past_failures_count=maintenance_rec.past_failures_count if maintenance_rec else 0,
    )

    # 4. Fetch compatible inventory spare parts
    db_parts = (
        db.query(Inventory)
        .filter((Inventory.asset_type == asset.asset_type) | (Inventory.asset_type.is_(None)))
        .all()
    )
    if not db_parts:
        db_parts = db.query(Inventory).all()

    spare_parts = [
        AIEngineSparePart(
            part_id=p.part_id,
            part_name=p.part_name,
            category=p.category,
            current_stock=p.current_stock,
            minimum_stock=p.minimum_stock,
            lead_time=p.lead_time,
            unit_cost=p.unit_cost,
        )
        for p in db_parts
    ]

    # 5. Fetch available technicians
    available_technicians = (
        db.query(Technician)
        .filter(Technician.availability.is_(True))
        .all()
    )

    # 6. Build AI Engine request
    ai_request = AIEngineRequest(
        asset_id=asset.asset_id,
        asset_type=asset.asset_type,
        telemetry=telemetry_data,
        maintenance_history=maintenance_history,
        spare_parts=spare_parts,
    )

    # 7. POST /autonomous-operation to AI Engine
    ai_response: AIEngineResponse = await ai_client.call_autonomous_operation(ai_request)

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

    # 9. Find relevant inventory part from AI response
    matched_inventory = None
    target_part_id = ai_response.required_parts[0] if ai_response.required_parts else (
        db_parts[0].part_id if db_parts else None
    )

    if target_part_id:
        target_part = next((p for p in db_parts if p.part_id == target_part_id), None)
        if not target_part:
            target_part = db.query(Inventory).filter(Inventory.part_id == target_part_id).first()

        if target_part:
            matched_inventory = OperationInventory(
                part_id=target_part.part_id,
                part_name=target_part.part_name,
                stock_status=ai_response.stock_status,
                current_stock=target_part.current_stock,
                minimum_stock=target_part.minimum_stock,
                reorder_quantity=ai_response.reorder_quantity,
            )

    # 10. Generate Operation ID & Log Entry
    operation_id = f"op-{uuid.uuid4().hex[:12]}"
    now_utc = datetime.now(timezone.utc)

    op_log = OperationLog(
        operation_id=operation_id,
        asset_id=asset.asset_id,
        timestamp=now_utc,
        failure_probability=ai_response.failure_probability,
        asset_risk=ai_response.asset_risk,
        RUL=ai_response.RUL,
        stock_status=ai_response.stock_status,
        reorder_quantity=ai_response.reorder_quantity,
        technician_id=selected_tech.technician_id if selected_tech else None,
        ETA=route_info["eta_minutes"] if route_info else 0.0,
        SLA_status=sla_info["sla_status"] if sla_info else "N/A",
        preventive_cost=ai_response.preventive_cost,
        failure_cost=ai_response.failure_cost,
        estimated_savings=ai_response.estimated_savings,
        final_action=ai_response.autonomous_decision or ai_response.recommended_action,
        raw_ai_response=ai_response.model_dump(),
    )

    db.add(op_log)

    # If technician assigned, create WorkOrder record
    if selected_tech:
        work_order = WorkOrder(
            id=f"wo-{uuid.uuid4().hex[:8]}",
            operation_id=operation_id,
            asset_id=asset.asset_id,
            technician_id=selected_tech.technician_id,
            status="DISPATCHED",
            created_at=now_utc,
        )
        db.add(work_order)

    # Commit operation log and work order to DB
    db.commit()

    # 11. Compose Human-Readable Summary
    tech_str = (
        f"Dispatched {selected_tech.name} (ETA: {route_info['eta_minutes']} mins, {sla_info['sla_status']})"
        if selected_tech and route_info and sla_info
        else "No available technician found"
    )
    part_str = (
        f"Reorder {ai_response.reorder_quantity} units of {matched_inventory.part_name} ({matched_inventory.part_id})"
        if matched_inventory and ai_response.reorder_quantity > 0
        else "Parts stock adequate"
    )
    summary = (
        f"Autonomous Operation triggered for {asset.name} ({asset.asset_id}): "
        f"{ai_response.asset_risk} Risk ({round(ai_response.failure_probability * 100, 1)}% failure prob, RUL: {ai_response.RUL}h). "
        f"Action: {ai_response.recommended_action}. {tech_str}. {part_str}."
    )

    # 12. Build clean response matching frontend expectations
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
            final_action=ai_response.autonomous_decision or ai_response.recommended_action,
            priority=ai_response.priority,
            autonomous_decision=ai_response.autonomous_decision,
        ),
        summary=summary,
    )
