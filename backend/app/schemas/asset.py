from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    timestamp: datetime
    vibration_rms: float
    bearing_temperature: float
    coolant_pressure: float
    power_kw: float
    operating_hours: float
    metrics: Optional[Any] = None


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    serviced_at: datetime
    past_failures_count: int
    notes: Optional[str] = None


class AssetBase(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    location: str
    latitude: float
    longitude: float
    criticality: str
    status: str


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = None
    telemetry: Optional[List[TelemetryResponse]] = None
    maintenance: Optional[List[MaintenanceResponse]] = None


class AssetDetailResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = None
    latest_telemetry: Optional[TelemetryResponse] = None
    telemetry: Optional[List[TelemetryResponse]] = None
    maintenance: Optional[List[MaintenanceResponse]] = None
