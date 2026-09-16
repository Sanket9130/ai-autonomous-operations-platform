from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TechnicianBase(BaseModel):
    technician_id: str
    name: str
    skills: List[str]
    certifications: Optional[List[str]] = []
    experience: float
    current_latitude: float
    current_longitude: float
    availability: bool
    status: Optional[str] = "AVAILABLE"
    current_location: Optional[str] = None
    technician_workload: Optional[int] = 0


class TechnicianResponse(TechnicianBase):
    model_config = ConfigDict(from_attributes=True)
    score: Optional[float] = None
    distance_km: Optional[float] = None
    eta_minutes: Optional[float] = None
