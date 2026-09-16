from sqlalchemy import Column, String, Float, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Technician(Base):
    __tablename__ = "technicians"

    technician_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    skills = Column(JSON, nullable=False, default=list)  # List[str]
    certifications = Column(JSON, nullable=False, default=list)  # List[str]
    experience = Column(Float, nullable=False, default=1.0)  # Years of experience
    current_latitude = Column(Float, nullable=False, default=25.0772)
    current_longitude = Column(Float, nullable=False, default=55.1325)
    availability = Column(Boolean, nullable=False, default=True, index=True)
    status = Column(String(32), nullable=False, default="AVAILABLE")  # AVAILABLE, ON_DUTY, OFF_DUTY
    current_location = Column(String(128), nullable=True, default="MARINA")
    active_workload = Column(Integer, nullable=False, default=0)

    operation_logs = relationship("OperationLog", back_populates="technician")

    @property
    def technician_workload(self) -> int:
        return self.active_workload or 0
