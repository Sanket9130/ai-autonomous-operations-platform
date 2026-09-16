"""
Pydantic Schemas for AI Engine REST API request & response payloads.
Standardized for Frontend and Backend Integration.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Health & Status Schemas
# ---------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service operational status")
    service: str = Field(default="ai-engine", description="Service identifier")
    version: str = Field(default="1.0.0", description="Service semantic version")
    model_loaded: bool = Field(..., description="True if trained ML model artifact is loaded and ready")
    selected_model: Optional[str] = Field(default=None, description="Active serialized model name")


# ---------------------------------------------------------
# 1. Predictive Maintenance Schemas
# ---------------------------------------------------------
class AssetTelemetryInput(BaseModel):
    asset_id: str = Field(..., description="Unique Asset ID (e.g. HVAC-DXB-001)")
    asset_type: str = Field(default="HVAC_CHILLER", description="Asset type (e.g. HVAC_CHILLER, AHU, ELEVATOR)")
    vibration_mm_s: Optional[float] = Field(default=None, description="Vibration velocity in mm/s")
    vibration_level: Optional[float] = Field(default=None, description="Alias for vibration in mm/s")
    operating_temp_c: Optional[float] = Field(default=None, description="Operating temperature in Celsius")
    operating_temperature_c: Optional[float] = Field(default=None, description="Alias for operating temperature in Celsius")
    ambient_temp_c: Optional[float] = Field(default=42.0, description="Dubai ambient temperature in Celsius")
    ambient_temperature_c: Optional[float] = Field(default=None, description="Alias for ambient temperature in Celsius")
    power_kw: Optional[float] = Field(default=None, description="Power consumption in kW")
    power_consumption_kw: Optional[float] = Field(default=None, description="Alias for power consumption in kW")
    runtime_hours: float = Field(default=1500.0, description="Cumulative machine runtime hours")
    last_maintenance_days: Optional[int] = Field(default=None, description="Days elapsed since last maintenance inspection")
    last_maintenance_days_ago: Optional[int] = Field(default=None, description="Alias for days since last service")


class AssetFailurePredictionResponse(BaseModel):
    asset_id: str = Field(..., description="Unique Asset ID")
    failure_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted probability of failure (0.0 to 1.0)")
    predicted_status: str = Field(..., description="Asset condition: CRITICAL, WARNING, HEALTHY")
    estimated_rul_days: float = Field(..., description="Estimated Remaining Useful Life in days")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite operational risk score (0 to 100)")
    risk_category: str = Field(..., description="Risk category: CRITICAL, HIGH, MEDIUM, LOW")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Prescriptive maintenance actions")


# ---------------------------------------------------------
# 2. Decision Intelligence Schemas
# ---------------------------------------------------------
class DecisionIntelligenceInput(BaseModel):
    failure_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted failure probability (0.0 to 1.0)")
    asset_risk_level: str = Field(default="CRITICAL", description="Asset risk level: CRITICAL, WARNING, HEALTHY")
    asset_criticality: str = Field(default="HIGH", description="Asset operational criticality: CRITICAL, HIGH, MEDIUM, LOW")
    required_spare_part: Optional[str] = Field(default=None, description="Spare part identifier / name")
    current_stock: float = Field(default=0.0, ge=0.0, description="Current warehouse available stock")
    minimum_stock: float = Field(default=0.0, ge=0.0, description="Minimum safety stock threshold")
    lead_time_days: float = Field(default=7.0, ge=0.0, description="Supplier lead time in days")


class DecisionIntelligenceResponse(BaseModel):
    failure_probability: float = Field(..., description="Evaluated failure probability")
    risk_level: str = Field(..., description="Risk level (CRITICAL, WARNING, HEALTHY)")
    maintenance_priority: str = Field(..., description="Assigned priority code: P1, P2, P3, P4")
    stock_status: str = Field(..., description="Stock status: OPTIMAL, LOW, OUT_OF_STOCK, EXCESS")
    recommended_action: str = Field(..., description="Prescriptive recommendation text")
    reason: str = Field(..., description="Deterministic decision rationale")


# ---------------------------------------------------------
# 3. Demand Forecasting Schemas
# ---------------------------------------------------------
class DemandForecastInput(BaseModel):
    part_id: str = Field(..., description="Unique spare part identifier")
    forecast_days: int = Field(default=30, description="Forecast horizon in days (e.g. 7, 30, 90)")
    historical_daily_demand: Optional[List[float]] = Field(
        default=None,
        description="Historical daily consumption records. If omitted, default historical profile is used.",
    )
    current_stock: float = Field(default=0.0, ge=0.0, description="Current warehouse on-hand stock")
    lead_time_days: float = Field(default=14.0, ge=1.0, description="Supplier replenishment lead time in days")


class DemandForecastResponse(BaseModel):
    part_id: str = Field(..., description="Spare part identifier")
    forecast_days: int = Field(..., description="Forecast horizon in days")
    predicted_demand: float = Field(..., description="Total projected demand over horizon")
    safety_stock: float = Field(..., description="Calculated statistical safety buffer")
    reorder_point: float = Field(..., description="Calculated reorder trigger point")
    current_stock: float = Field(..., description="Current on-hand inventory")
    stockout_risk: str = Field(..., description="Stockout risk category: CRITICAL, ELEVATED, LOW")
    recommended_order_quantity: float = Field(..., description="Recommended order batch quantity")


# ---------------------------------------------------------
# 4. Unified Operations Decision Schemas
# ---------------------------------------------------------
class UnifiedOperationsDecisionInput(BaseModel):
    asset_id: str = Field(..., description="Unique Asset ID (e.g. HVAC-DXB-001)")
    asset_type: str = Field(default="HVAC_CHILLER", description="Asset type")
    vibration_mm_s: float = Field(..., description="Vibration level in mm/s")
    operating_temp_c: float = Field(..., description="Operating temperature in Celsius")
    ambient_temp_c: float = Field(default=42.0, description="Ambient temperature in Celsius")
    power_kw: float = Field(default=50.0, description="Power consumption in kW")
    runtime_hours: float = Field(default=2000.0, description="Cumulative runtime hours")
    last_maintenance_days: int = Field(default=30, description="Days since last maintenance")
    asset_criticality: str = Field(default="HIGH", description="Asset criticality: CRITICAL, HIGH, MEDIUM, LOW")
    required_spare_part: str = Field(default="CHILLER_EXPANSION_VALVE", description="Linked spare part identifier")
    current_stock: float = Field(default=0.0, ge=0.0, description="Current stock in warehouse")
    lead_time_days: float = Field(default=14.0, ge=1.0, description="Supplier lead time in days")
    forecast_days: int = Field(default=30, description="Demand forecast horizon in days")
    historical_daily_demand: Optional[List[float]] = Field(default=None, description="Optional historical consumption series")


class UnifiedOperationsDecisionResponse(BaseModel):
    failure_probability: float = Field(..., description="Predicted failure probability")
    asset_risk: str = Field(..., description="Asset risk status")
    maintenance_priority: str = Field(..., description="Assigned priority code")
    spare_part: str = Field(..., description="Linked spare part identifier")
    stockout_risk: str = Field(..., description="Stockout vulnerability status")
    predicted_demand: float = Field(..., description="Predicted spare-part demand")
    reorder_point: float = Field(..., description="Inventory reorder trigger point")
    recommended_order_quantity: float = Field(..., description="Recommended reorder quantity")
    recommended_action: str = Field(..., description="Standardized operation action code")
    reason: str = Field(..., description="Operational rationale")


# ---------------------------------------------------------
# 5. Technician Dispatch Schemas
# ---------------------------------------------------------
class TechnicianDispatchInput(BaseModel):
    technician_id: Optional[str] = Field(default="TECH-DXB-042", description="Technician ID or Name")
    technician_skills: List[str] = Field(
        default=["HVAC_CHILLER_SPECIALIST", "ELECTROMECHANICAL"],
        description="List of certified technician skills",
    )
    technician_availability: bool = Field(default=True, description="Current shift availability")
    technician_current_location: Union[Dict[str, float], str] = Field(
        default="DOWNTOWN",
        description="Current location as Dubai area name or {'lat': float, 'lng': float}",
    )
    asset_location: Union[Dict[str, float], str] = Field(
        default="MARINA",
        description="Target asset building location as Dubai area name or {'lat': float, 'lng': float}",
    )
    estimated_repair_duration_hours: float = Field(default=1.5, ge=0.25, description="Estimated work duration in hours")
    technician_workload: int = Field(default=1, ge=0, description="Current count of queued tasks")
    sla_deadline_hours: float = Field(default=3.0, ge=0.1, description="SLA response/resolution deadline in hours")
    required_skill: Optional[str] = Field(default="HVAC_CHILLER_SPECIALIST", description="Required diagnostic skill")
    candidates: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional list of candidate technicians to rank")


class TechnicianDispatchResponse(BaseModel):
    selected_technician: str = Field(..., description="Selected technician ID / name")
    technician_score: float = Field(..., description="Suitability score (0 - 100)")
    distance: float = Field(..., description="Geodesic travel distance in km")
    estimated_eta: float = Field(..., description="Estimated travel ETA in minutes")
    sla_status: str = Field(..., description="SLA compliance status: WITHIN_SLA, AT_RISK, SLA_BREACH_RISK")
    reason: str = Field(..., description="Technician selection rationale")


# ---------------------------------------------------------
# 6. Cost & SLA Optimization Schemas
# ---------------------------------------------------------
class OptimizeOperationInput(BaseModel):
    failure_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted asset failure probability")
    asset_criticality: str = Field(default="HIGH", description="Asset criticality (CRITICAL, HIGH, MEDIUM, LOW)")
    maintenance_priority: str = Field(default="P1", description="Assigned maintenance priority (P1, P2, P3, P4)")
    stock_status: str = Field(default="OPTIMAL", description="Spare part stock status (OPTIMAL, LOW, OUT_OF_STOCK, EXCESS)")
    selected_technician: str = Field(default="TECH-DXB-042 (Senior Specialist)", description="Designated field technician")
    technician_eta_minutes: float = Field(default=15.0, description="Estimated travel ETA in minutes")
    sla_status: str = Field(default="WITHIN_SLA", description="SLA compliance status (WITHIN_SLA, AT_RISK, SLA_BREACH_RISK)")
    spare_part_cost: Optional[float] = Field(default=450.0, ge=0.0, description="Cost of replacement spare part in AED")
    current_stock: float = Field(default=2.0, ge=0.0, description="Current on-hand spare parts")
    reorder_point: float = Field(default=10.0, ge=0.0, description="Inventory reorder point")


class OptimizeOperationResponse(BaseModel):
    preventive_total_cost: float = Field(..., description="Total cost of proactive preventive maintenance in AED")
    failure_total_cost: float = Field(..., description="Projected cost of breakdown failure in AED")
    estimated_savings: float = Field(..., description="Net expected financial savings in AED")
    sla_risk: str = Field(..., description="Assessed SLA compliance status")
    final_recommended_action: str = Field(..., description="Optimal operational recommendation code")
    reason: str = Field(..., description="Financial optimization rationale")


# ---------------------------------------------------------
# 7. End-to-End Autonomous Operation Schemas (Primary Endpoint)
# ---------------------------------------------------------
class FailurePredictionSummary(BaseModel):
    failure_probability: float = Field(..., description="ML predicted failure probability (0.0 to 1.0)")
    predicted_status: str = Field(..., description="Asset condition: CRITICAL, WARNING, HEALTHY")
    risk_score: float = Field(..., description="Composite risk index (0 to 100)")
    estimated_rul_days: float = Field(..., description="Estimated Remaining Useful Life in days")


class InventoryIntelligenceSummary(BaseModel):
    spare_part: str = Field(..., description="Target spare part identifier")
    current_stock: float = Field(..., description="Current on-hand warehouse stock")
    predicted_demand_30d: float = Field(..., description="Forecast demand over 30 days")
    safety_stock: float = Field(..., description="Recommended safety buffer stock")
    reorder_point: float = Field(..., description="Calculated reorder trigger point")
    stockout_risk: str = Field(..., description="Stockout risk category: CRITICAL, ELEVATED, LOW")
    recommended_order_quantity: float = Field(..., description="Recommended replenishment quantity")


class TechnicianDispatchSummary(BaseModel):
    selected_technician: str = Field(..., description="Selected technician ID and designation")
    technician_score: float = Field(..., description="Technician suitability score (0 to 100)")
    distance_km: float = Field(..., description="Estimated road travel distance in km")
    estimated_eta_minutes: float = Field(..., description="Estimated travel time in minutes")
    sla_status: str = Field(..., description="SLA status: WITHIN_SLA, AT_RISK, SLA_BREACH_RISK")


class CostOptimizationSummary(BaseModel):
    preventive_total_cost: float = Field(..., description="Total cost of proactive maintenance in AED")
    failure_total_cost: float = Field(..., description="Total cost of breakdown failure & downtime in AED")
    estimated_savings: float = Field(..., description="Net expected financial savings in AED")


class AutonomousOperationInput(BaseModel):
    asset_id: str = Field(..., description="Unique Asset ID (e.g. HVAC-DXB-001)")
    asset_type: str = Field(default="HVAC_CHILLER", description="Asset type (HVAC_CHILLER, AHU, PUMP, ELEVATOR)")
    asset_location: Union[Dict[str, float], str] = Field(default="MARINA", description="Asset facility location (Dubai district name or lat/lng dict)")
    vibration_mm_s: float = Field(..., description="Vibration level in mm/s")
    operating_temp_c: float = Field(..., description="Operating temperature in Celsius")
    ambient_temp_c: float = Field(default=42.0, description="Dubai ambient temperature in Celsius")
    power_kw: float = Field(default=50.0, description="Power consumption in kW")
    runtime_hours: float = Field(default=2000.0, description="Cumulative runtime hours")
    last_maintenance_days: int = Field(default=30, description="Days since last maintenance service")
    asset_criticality: str = Field(default="HIGH", description="Asset operational criticality: CRITICAL, HIGH, MEDIUM, LOW")
    required_spare_part: str = Field(default="CHILLER_EXPANSION_VALVE", description="Required replacement spare part identifier")
    current_stock: float = Field(default=0.0, ge=0.0, description="Current stock in warehouse")
    lead_time_days: float = Field(default=14.0, ge=1.0, description="Supplier lead time in days")
    forecast_days: int = Field(default=30, description="Forecast horizon in days")
    spare_part_cost: Optional[float] = Field(default=450.0, ge=0.0, description="Spare part unit cost in AED")
    sla_deadline_hours: float = Field(default=3.0, ge=0.1, description="SLA response deadline in hours")
    estimated_repair_duration_hours: float = Field(default=1.5, ge=0.1, description="Estimated work duration in hours")
    candidate_technicians: Optional[List[Dict[str, Any]]] = Field(default=None, description="Available technician candidates list")
    historical_daily_demand: Optional[List[float]] = Field(default=None, description="Optional historical consumption records")


class AutonomousOperationResponse(BaseModel):
    asset_id: str = Field(..., description="Asset identifier")
    failure_prediction: FailurePredictionSummary = Field(..., description="ML failure prediction and RUL estimation")
    inventory_intelligence: InventoryIntelligenceSummary = Field(..., description="Spare-part demand forecast and stockout risk")
    technician_dispatch: TechnicianDispatchSummary = Field(..., description="Technician suitability scoring and ETA/SLA status")
    cost_optimization: CostOptimizationSummary = Field(..., description="Financial cost-benefit tradeoff and savings")
    unified_action: str = Field(..., description="Primary autonomous decision code (e.g. URGENT_MAINTENANCE_AND_REORDER, MONITOR, SLA_ESCALATION_REQUIRED)")
    operational_summary: str = Field(..., description="Plain-language executive summary of the autonomous action")
