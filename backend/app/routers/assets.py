"""
Assets Router.
Provides endpoints to list and inspect assets & telemetry from the database.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.app.database import get_asset_by_id, list_all_assets
from backend.app.schemas import AssetResponse

router = APIRouter(prefix="/api/assets", tags=["Assets & Telemetry"])


@router.get("", response_model=List[AssetResponse], summary="List all facility assets")
async def get_assets():
    """List all assets stored in the operations database."""
    return list_all_assets()


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get asset by ID")
async def get_asset(asset_id: str):
    """Retrieve details and sensor telemetry for a specific asset."""
    asset = get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found.",
        )
    return asset
