from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.asset import Asset
from backend.app.models.telemetry import Telemetry
from backend.app.schemas.asset import AssetResponse, AssetDetailResponse, TelemetryResponse

router = APIRouter(prefix="/api/assets", tags=["Assets"])


@router.get("", response_model=List[AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    """
    Retrieve all monitored industrial assets with their telemetry and maintenance records.
    Database-driven, no hardcoded values.
    """
    assets = db.query(Asset).all()
    return assets


@router.get("/{asset_id}", response_model=AssetDetailResponse)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single asset by its unique asset_id.
    """
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found."
        )

    # Attach latest telemetry
    latest_telemetry = (
        db.query(Telemetry)
        .filter(Telemetry.asset_id == asset_id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )

    response_data = AssetDetailResponse.model_validate(asset)
    if latest_telemetry:
        response_data.latest_telemetry = TelemetryResponse.model_validate(latest_telemetry)

    return response_data
