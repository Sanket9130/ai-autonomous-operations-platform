from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(64), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    criticality = Column(String(32), nullable=False, default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(32), nullable=False, default="OPERATIONAL")  # OPERATIONAL, DEGRADED, FAILURE_RISK, OFFLINE
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    telemetry = relationship("Telemetry", back_populates="asset", cascade="all, delete-orphan")
    maintenance = relationship("Maintenance", back_populates="asset", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="asset")
