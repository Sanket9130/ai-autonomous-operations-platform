from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.inventory import Inventory
from backend.app.schemas.inventory import InventoryResponse

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    """
    Retrieve all inventory spare parts.
    Database-driven, strictly raw inventory data (no duplicate demand forecasting).
    """
    items = db.query(Inventory).all()
    return items


@router.get("/{part_id}", response_model=InventoryResponse)
def get_inventory_part(part_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific spare part by part_id.
    """
    item = db.query(Inventory).filter(Inventory.part_id == part_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory part '{part_id}' not found."
        )
    return item
