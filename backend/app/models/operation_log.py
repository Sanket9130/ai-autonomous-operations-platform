from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    operation_id = Column(String(64), primary_key=True, index=True)
    asset_id = Column(String(64), ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    failure_probability = Column(Float, nullable=False, default=0.0)
    asset_risk = Column(String(32), nullable=False, default="LOW")
    RUL = Column(Float, nullable=False, default=0.0)
    stock_status = Column(String(64), nullable=False, default="OPTIMAL")
    reorder_quantity = Column(Integer, nullable=False, default=0)
    technician_id = Column(String(64), ForeignKey("technicians.technician_id", ondelete="SET NULL"), nullable=True)
    ETA = Column(Float, nullable=False, default=0.0)  # in minutes
    SLA_status = Column(String(32), nullable=False, default="WITHIN_SLA")  # WITHIN_SLA, AT_RISK, SLA_BREACH_RISK
    preventive_cost = Column(Float, nullable=False, default=0.0)
    failure_cost = Column(Float, nullable=False, default=0.0)
    estimated_savings = Column(Float, nullable=False, default=0.0)
    final_action = Column(String(64), nullable=False, default="MONITOR")
    raw_ai_response = Column(JSON, nullable=True)

    # Extended audit fields for frontend table & API contract
    unified_action = Column(String(64), nullable=True)
    risk_score = Column(Float, nullable=True, default=0.0)
    selected_technician = Column(String(255), nullable=True)
    technician_eta_minutes = Column(Float, nullable=True, default=0.0)
    estimated_savings_aed = Column(Float, nullable=True, default=0.0)
    operational_summary = Column(String(1000), nullable=True)

    asset = relationship("Asset", back_populates="operation_logs")
    technician = relationship("Technician", back_populates="operation_logs")

    @property
    def id(self) -> str:
        return self.operation_id

    @property
    def executed_at(self) -> str:
        return self.timestamp.isoformat() if self.timestamp else ""
