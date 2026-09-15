"""
Inventory Router.
Provides endpoints to query warehouse spare parts inventory and stock levels.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.app.database import get_inventory_item, list_all_inventory
from backend.app.schemas import InventoryItemResponse

router = APIRouter(prefix="/api/inventory", tags=["Inventory & Warehouse"])


@router.get("", response_model=List[InventoryItemResponse], summary="List all inventory spare parts")
async def get_inventory():
    """List all spare parts and stock levels."""
    return list_all_inventory()


@router.get("/{part_id}", response_model=InventoryItemResponse, summary="Get inventory item by part ID")
async def get_item(part_id: str):
    """Retrieve stock and lead time for a specific spare part."""
    item = get_inventory_item(part_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Part '{part_id}' not found in inventory.",
        )
    return item
