from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class OperationAsset(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    location: str
    latitude: float
    longitude: float
    criticality: str
    status: str


class OperationPrediction(BaseModel):
    failure_probability: float
    asset_risk: str
    RUL: float
    recommended_action: str


class OperationInventory(BaseModel):
    part_id: Optional[str] = None
    part_name: Optional[str] = None
    stock_status: str
    current_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    reorder_quantity: int = 0


class OperationTechnician(BaseModel):
    technician_id: str
    name: str
    skills: List[str]
    certifications: List[str]
    experience: float
    current_latitude: float
    current_longitude: float
    score: Optional[float] = None


class OperationRoute(BaseModel):
    distance_km: float
    eta_minutes: float
    average_speed_kmh: float


class OperationSLA(BaseModel):
    sla_hours: float
    eta_hours: float
    sla_status: str  # WITHIN_SLA, AT_RISK, SLA_BREACH_RISK


class OperationCost(BaseModel):
    preventive_cost: float
    failure_cost: float
    estimated_savings: float


class OperationDecision(BaseModel):
    final_action: str
    priority: str
    autonomous_decision: Optional[str] = None


class OperationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operation_id: str
    timestamp: datetime
    asset: OperationAsset
    prediction: OperationPrediction
    inventory: Optional[OperationInventory] = None
    technician: Optional[OperationTechnician] = None
    route: Optional[OperationRoute] = None
    sla: Optional[OperationSLA] = None
    cost: OperationCost
    decision: OperationDecision
    summary: str
