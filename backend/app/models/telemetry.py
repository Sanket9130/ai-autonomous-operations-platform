from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(64), ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    vibration_rms = Column(Float, nullable=False)
    bearing_temperature = Column(Float, nullable=False)
    coolant_pressure = Column(Float, nullable=False)
    power_kw = Column(Float, nullable=False)
    operating_hours = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=True)

    asset = relationship("Asset", back_populates="telemetry")
