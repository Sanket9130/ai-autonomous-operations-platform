"""
Assets Router.
Provides endpoints to list and inspect assets & telemetry from the database.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.asset import Asset
from backend.app.models.telemetry import Telemetry
from backend.app.schemas.asset import AssetResponse, TelemetryResponse

router = APIRouter(prefix="/api/assets", tags=["Assets & Telemetry"])


def _format_asset_response(asset: Asset, db: Session) -> AssetResponse:
    latest_telem: Telemetry = (
        db.query(Telemetry)
        .filter(Telemetry.asset_id == asset.asset_id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )

    telem_resp = None
    if latest_telem:
        telem_resp = TelemetryResponse(
            id=latest_telem.id,
            timestamp=latest_telem.timestamp,
            vibration_rms=latest_telem.vibration_rms,
            bearing_temperature=latest_telem.bearing_temperature,
            coolant_pressure=latest_telem.coolant_pressure,
            power_kw=latest_telem.power_kw,
            operating_hours=latest_telem.operating_hours,
            metrics=latest_telem.metrics,
        )

    return AssetResponse(
        asset_id=asset.asset_id,
        name=asset.name,
        asset_type=asset.asset_type,
        location=asset.location,
        latitude=asset.latitude,
        longitude=asset.longitude,
        criticality=asset.criticality,
        status=asset.status,
        vibration_mm_s=latest_telem.vibration_rms if latest_telem else (asset.vibration_mm_s or 1.0),
        operating_temp_c=latest_telem.bearing_temperature if latest_telem else (asset.operating_temp_c or 65.0),
        ambient_temp_c=asset.ambient_temp_c or 42.0,
        power_kw=latest_telem.power_kw if latest_telem else (asset.power_kw or 30.0),
        runtime_hours=latest_telem.operating_hours if latest_telem else (asset.runtime_hours or 5000.0),
        last_maintenance_days=asset.last_maintenance_days or 30,
        required_spare_part_id=asset.required_spare_part_id or "PART-BRG-7701",
        created_at=asset.created_at,
        latest_telemetry=telem_resp,
    )


@router.get("", response_model=List[AssetResponse], summary="List all facility assets")
async def get_assets(db: Session = Depends(get_db)):
    """List all assets stored in the operations database."""
    assets = db.query(Asset).order_by(Asset.asset_id.asc()).all()
    return [_format_asset_response(a, db) for a in assets]


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get asset by ID")
async def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """Retrieve details and sensor telemetry for a specific asset."""
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found.",
        )
    return _format_asset_response(asset, db)
