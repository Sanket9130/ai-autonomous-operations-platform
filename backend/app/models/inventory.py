from sqlalchemy import Column, String, Integer, Float
from backend.app.core.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    part_id = Column(String(64), primary_key=True, index=True)
    part_name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    current_stock = Column(Integer, nullable=False, default=0)
    minimum_stock = Column(Integer, nullable=False, default=0)
    lead_time = Column(Integer, nullable=False, default=1)  # days
    unit_cost = Column(Float, nullable=False, default=0.0)
    supplier = Column(String(255), nullable=False, default="Generic Supplier")
    asset_type = Column(String(64), nullable=True)  # Associated asset type (e.g. HVAC_CHILLER)

    @property
    def unit_cost_aed(self) -> float:
        return float(self.unit_cost)

    @property
    def lead_time_days(self) -> float:
        return float(self.lead_time)

    @property
    def min_safety_stock(self) -> float:
        return float(self.minimum_stock)
