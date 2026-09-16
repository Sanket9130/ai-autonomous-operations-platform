"""
Database Access Layer Compatibility for Facility Operations Backend.
Provides compatibility helpers backed by SQLAlchemy models and session.
"""

from typing import Any, Dict, List, Optional
from backend.app.core.database import SessionLocal, init_db, get_db, Base, engine
from backend.app.models.asset import Asset
from backend.app.models.inventory import Inventory
from backend.app.models.technician import Technician
from backend.app.models.telemetry import Telemetry
from backend.app.models.operation_log import OperationLog
from backend.app.seed.seed_data import seed_database


def init_db_and_seed():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


def get_asset_by_id(asset_id: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
        if not asset:
            return None
        latest_telem = (
            db.query(Telemetry)
            .filter(Telemetry.asset_id == asset_id)
            .order_by(Telemetry.timestamp.desc())
            .first()
        )
        return {
            "asset_id": asset.asset_id,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "location": asset.location,
            "latitude": asset.latitude,
            "longitude": asset.longitude,
            "criticality": asset.criticality,
            "status": asset.status,
            "vibration_mm_s": latest_telem.vibration_rms if latest_telem else (asset.vibration_mm_s or 1.0),
            "operating_temp_c": latest_telem.bearing_temperature if latest_telem else (asset.operating_temp_c or 65.0),
            "ambient_temp_c": asset.ambient_temp_c or 42.0,
            "power_kw": latest_telem.power_kw if latest_telem else (asset.power_kw or 30.0),
            "runtime_hours": latest_telem.operating_hours if latest_telem else (asset.runtime_hours or 5000.0),
            "last_maintenance_days": asset.last_maintenance_days or 30,
            "required_spare_part_id": asset.required_spare_part_id or "PART-BRG-7701",
        }
    finally:
        db.close()


def list_all_assets() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        assets = db.query(Asset).order_by(Asset.asset_id.asc()).all()
        result = []
        for a in assets:
            latest_telem = (
                db.query(Telemetry)
                .filter(Telemetry.asset_id == a.asset_id)
                .order_by(Telemetry.timestamp.desc())
                .first()
            )
            result.append({
                "asset_id": a.asset_id,
                "name": a.name,
                "asset_type": a.asset_type,
                "location": a.location,
                "latitude": a.latitude,
                "longitude": a.longitude,
                "criticality": a.criticality,
                "status": a.status,
                "vibration_mm_s": latest_telem.vibration_rms if latest_telem else (a.vibration_mm_s or 1.0),
                "operating_temp_c": latest_telem.bearing_temperature if latest_telem else (a.operating_temp_c or 65.0),
                "ambient_temp_c": a.ambient_temp_c or 42.0,
                "power_kw": latest_telem.power_kw if latest_telem else (a.power_kw or 30.0),
                "runtime_hours": latest_telem.operating_hours if latest_telem else (a.runtime_hours or 5000.0),
                "last_maintenance_days": a.last_maintenance_days or 30,
                "required_spare_part_id": a.required_spare_part_id or "PART-BRG-7701",
            })
        return result
    finally:
        db.close()


def get_inventory_item(part_id: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        item = db.query(Inventory).filter(Inventory.part_id == part_id).first()
        if not item:
            return None
        return {
            "part_id": item.part_id,
            "part_name": item.part_name,
            "category": item.category,
            "current_stock": float(item.current_stock),
            "minimum_stock": float(item.minimum_stock),
            "lead_time": float(item.lead_time),
            "unit_cost": float(item.unit_cost),
            "unit_cost_aed": float(item.unit_cost),
            "lead_time_days": float(item.lead_time),
            "min_safety_stock": float(item.minimum_stock),
            "supplier": item.supplier,
            "asset_type": item.asset_type,
        }
    finally:
        db.close()


def list_all_inventory() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        items = db.query(Inventory).order_by(Inventory.part_id.asc()).all()
        return [
            {
                "part_id": item.part_id,
                "part_name": item.part_name,
                "category": item.category,
                "current_stock": float(item.current_stock),
                "minimum_stock": float(item.minimum_stock),
                "lead_time": float(item.lead_time),
                "unit_cost": float(item.unit_cost),
                "unit_cost_aed": float(item.unit_cost),
                "lead_time_days": float(item.lead_time),
                "min_safety_stock": float(item.minimum_stock),
                "supplier": item.supplier,
                "asset_type": item.asset_type,
            }
            for item in items
        ]
    finally:
        db.close()


def get_candidate_technicians(only_available: bool = True) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        query = db.query(Technician)
        if only_available:
            query = query.filter(Technician.availability.is_(True))
        techs = query.order_by(Technician.technician_id.asc()).all()
        return [
            {
                "technician_id": t.technician_id,
                "name": t.name,
                "skills": t.skills or [],
                "certifications": t.certifications or [],
                "experience": t.experience,
                "current_latitude": t.current_latitude,
                "current_longitude": t.current_longitude,
                "availability": t.availability,
                "status": t.status,
                "current_location": t.current_location or "MARINA",
                "technician_workload": t.active_workload or 0,
            }
            for t in techs
        ]
    finally:
        db.close()


def list_operation_logs(limit: int = 50) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        logs = (
            db.query(OperationLog)
            .order_by(OperationLog.timestamp.desc(), OperationLog.operation_id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": log.operation_id,
                "operation_id": log.operation_id,
                "asset_id": log.asset_id,
                "executed_at": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "",
                "timestamp": log.timestamp.isoformat() if log.timestamp else "",
                "failure_probability": log.failure_probability,
                "asset_risk": log.asset_risk,
                "risk_score": log.risk_score if log.risk_score is not None else (log.failure_probability * 100.0),
                "unified_action": log.unified_action or log.final_action,
                "selected_technician": log.selected_technician or (log.technician_id or "NONE"),
                "technician_eta_minutes": log.technician_eta_minutes if log.technician_eta_minutes is not None else log.ETA,
                "estimated_savings_aed": log.estimated_savings_aed if log.estimated_savings_aed is not None else log.estimated_savings,
                "operational_summary": log.operational_summary or "",
            }
            for log in logs
        ]
    finally:
        db.close()
