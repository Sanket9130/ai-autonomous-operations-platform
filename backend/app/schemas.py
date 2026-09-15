"""
Pydantic schemas for the Backend REST API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    location: str
    criticality: str
    vibration_mm_s: float
    operating_temp_c: float
    ambient_temp_c: float
    power_kw: float
    runtime_hours: float
    last_maintenance_days: int
    required_spare_part_id: str


class InventoryItemResponse(BaseModel):
    part_id: str
    part_name: str
    category: str
    current_stock: float
    unit_cost_aed: float
    lead_time_days: float
    min_safety_stock: float


class TechnicianResponse(BaseModel):
    technician_id: str
    name: str
    skills_json: str
    is_available: int
    current_location: str
    active_workload: int


class TriggerOperationRequest(BaseModel):
    asset_id: str = Field(..., description="Asset ID to analyze")
    # Optional telemetry overrides for simulation / manual inspection
    vibration_override: Optional[float] = Field(default=None, description="Optional vibration override (mm/s)")
    operating_temp_override: Optional[float] = Field(default=None, description="Optional operating temp override (C)")
    ambient_temp_override: Optional[float] = Field(default=None, description="Optional ambient temp override (C)")
    sla_deadline_hours: Optional[float] = Field(default=3.0, description="Target SLA resolution window (hours)")


class AutonomousOperationBackendResponse(BaseModel):
    status: str = "success"
    log_id: int
    asset_id: str
    unified_action: str
    operational_summary: str
    failure_prediction: Dict[str, Any]
    inventory_intelligence: Dict[str, Any]
    technician_dispatch: Dict[str, Any]
    cost_optimization: Dict[str, Any]
    ai_engine_metadata: Dict[str, Any]
