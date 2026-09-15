from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class AIEngineTelemetry(BaseModel):
    vibration_rms: float
    bearing_temperature: float
    coolant_pressure: float
    power_kw: float
    operating_hours: float
    additional_metrics: Optional[Dict[str, Any]] = None


class AIEngineMaintenance(BaseModel):
    last_serviced: Optional[str] = None
    past_failures_count: int = 0


class AIEngineSparePart(BaseModel):
    part_id: str
    part_name: str
    category: str
    current_stock: int
    minimum_stock: int
    lead_time: int
    unit_cost: float


class AIEngineRequest(BaseModel):
    asset_id: str
    asset_type: str
    telemetry: AIEngineTelemetry
    maintenance_history: Optional[AIEngineMaintenance] = None
    spare_parts: List[AIEngineSparePart] = Field(default_factory=list)


class AIEngineResponse(BaseModel):
    failure_probability: float
    asset_risk: str  # HIGH, MEDIUM, LOW, CRITICAL
    RUL: float  # Remaining Useful Life in hours
    recommended_action: str
    stock_status: str
    reorder_quantity: int = 0
    preventive_cost: float = 0.0
    failure_cost: float = 0.0
    estimated_savings: float = 0.0
    required_skills: List[str] = Field(default_factory=list)
    required_parts: List[str] = Field(default_factory=list)
    priority: str = "HIGH"
    autonomous_decision: str = "SCHEDULE_DISPATCH"
