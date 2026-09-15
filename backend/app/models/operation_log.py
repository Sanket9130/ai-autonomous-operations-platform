from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    operation_id = Column(String(64), primary_key=True, index=True)
    asset_id = Column(String(64), ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    failure_probability = Column(Float, nullable=False)
    asset_risk = Column(String(32), nullable=False)
    RUL = Column(Float, nullable=False)
    stock_status = Column(String(64), nullable=False)
    reorder_quantity = Column(Integer, nullable=False, default=0)
    technician_id = Column(String(64), ForeignKey("technicians.technician_id", ondelete="SET NULL"), nullable=True)
    ETA = Column(Float, nullable=False)  # in minutes
    SLA_status = Column(String(32), nullable=False)  # WITHIN_SLA, AT_RISK, SLA_BREACH_RISK
    preventive_cost = Column(Float, nullable=False, default=0.0)
    failure_cost = Column(Float, nullable=False, default=0.0)
    estimated_savings = Column(Float, nullable=False, default=0.0)
    final_action = Column(String(64), nullable=False)
    raw_ai_response = Column(JSON, nullable=True)

    asset = relationship("Asset", back_populates="operation_logs")
    technician = relationship("Technician", back_populates="operation_logs")
