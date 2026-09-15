from typing import Optional
from pydantic import BaseModel, ConfigDict


class InventoryBase(BaseModel):
    part_id: str
    part_name: str
    category: str
    current_stock: int
    minimum_stock: int
    lead_time: int
    unit_cost: float
    supplier: str
    asset_type: Optional[str] = None


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)
