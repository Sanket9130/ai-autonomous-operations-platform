from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    timestamp: Optional[datetime] = None
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
    vibration_mm_s: Optional[float] = None
    operating_temp_c: Optional[float] = None
    ambient_temp_c: Optional[float] = None
    power_kw: Optional[float] = None
    runtime_hours: Optional[float] = None
    last_maintenance_days: Optional[int] = None
    required_spare_part_id: Optional[str] = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = None
    latest_telemetry: Optional[TelemetryResponse] = None
    telemetry: Optional[List[TelemetryResponse]] = None
    maintenance: Optional[List[MaintenanceResponse]] = None


class AssetDetailResponse(AssetResponse):
    pass
