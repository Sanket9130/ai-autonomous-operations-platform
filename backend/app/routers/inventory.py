"""
Inventory Router.
Provides endpoints to query warehouse spare parts inventory and stock levels.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.inventory import Inventory
from backend.app.schemas.inventory import InventoryItemResponse

router = APIRouter(prefix="/api/inventory", tags=["Inventory & Warehouse"])


@router.get("", response_model=List[InventoryItemResponse], summary="List all inventory spare parts")
async def get_inventory(db: Session = Depends(get_db)):
    """List all spare parts and stock levels."""
    parts = db.query(Inventory).order_by(Inventory.part_id.asc()).all()
    return parts


@router.get("/{part_id}", response_model=InventoryItemResponse, summary="Get inventory item by part ID")
async def get_item(part_id: str, db: Session = Depends(get_db)):
    """Retrieve stock and lead time for a specific spare part."""
    item = db.query(Inventory).filter(Inventory.part_id == part_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Part '{part_id}' not found in inventory.",
        )
    return item
