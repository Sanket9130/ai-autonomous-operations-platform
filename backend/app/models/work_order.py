from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from backend.app.core.database import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(String(64), primary_key=True, index=True)
    operation_id = Column(String(64), ForeignKey("operation_logs.operation_id", ondelete="CASCADE"), nullable=True)
    asset_id = Column(String(64), ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False)
    technician_id = Column(String(64), ForeignKey("technicians.technician_id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False, default="DISPATCHED")  # DISPATCHED, IN_PROGRESS, COMPLETED, OPEN, ASSIGNED, CANCELLED
    priority = Column(String(32), nullable=True, default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    sla_deadline = Column(DateTime, nullable=True)
