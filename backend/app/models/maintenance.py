from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(64), ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    serviced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    past_failures_count = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)

    asset = relationship("Asset", back_populates="maintenance")
