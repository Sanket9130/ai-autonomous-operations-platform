from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class InventoryBase(BaseModel):
    part_id: str
    part_name: str
    category: str
    current_stock: float
    minimum_stock: float
    lead_time: float
    unit_cost: float
    unit_cost_aed: Optional[float] = None
    lead_time_days: Optional[float] = None
    min_safety_stock: Optional[float] = None
    supplier: Optional[str] = "Generic Supplier"
    asset_type: Optional[str] = None

    @model_validator(mode="after")
    def populate_alias_fields(self):
        if self.unit_cost_aed is None:
            self.unit_cost_aed = self.unit_cost
        if self.lead_time_days is None:
            self.lead_time_days = self.lead_time
        if self.min_safety_stock is None:
            self.min_safety_stock = self.minimum_stock
        return self


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)


InventoryItemResponse = InventoryResponse