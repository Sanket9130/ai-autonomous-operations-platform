from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, model_validator


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
    current_stock: float
    minimum_stock: float
    lead_time: float
    unit_cost: float


class AIEngineRequest(BaseModel):
    asset_id: str
    asset_type: str
    telemetry: AIEngineTelemetry
    maintenance_history: Optional[AIEngineMaintenance] = None
    spare_parts: List[AIEngineSparePart] = Field(default_factory=list)


class AIEngineResponse(BaseModel):
    failure_probability: float = 0.0
    asset_risk: str = "LOW"  # HIGH, MEDIUM, LOW, CRITICAL
    RUL: float = 0.0  # Remaining Useful Life in hours
    recommended_action: str = "MONITOR"
    stock_status: str = "OPTIMAL"
    reorder_quantity: int = 0
    reorder_point: Optional[float] = None
    safety_stock: Optional[float] = None
    predicted_demand_30d: Optional[float] = None
    preventive_cost: float = 0.0
    failure_cost: float = 0.0
    estimated_savings: float = 0.0
    required_skills: List[str] = Field(default_factory=list)
    required_parts: List[str] = Field(default_factory=list)
    priority: str = "HIGH"
    autonomous_decision: Optional[str] = "SCHEDULE_DISPATCH"

    # Nested structures if returned directly by AI Engine
    failure_prediction: Optional[Dict[str, Any]] = None
    inventory_intelligence: Optional[Dict[str, Any]] = None
    technician_dispatch: Optional[Dict[str, Any]] = None
    cost_optimization: Optional[Dict[str, Any]] = None
    unified_action: Optional[str] = None
    operational_summary: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def parse_ai_engine_payload(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If data comes from live AI Engine (/autonomous-operation)
            fp = data.get("failure_prediction") or {}
            inv = data.get("inventory_intelligence") or {}
            tech = data.get("technician_dispatch") or {}
            cost = data.get("cost_optimization") or {}
            ua = data.get("unified_action")

            if fp:
                data.setdefault("failure_probability", float(fp.get("failure_probability", 0.0)))
                data.setdefault("asset_risk", str(fp.get("predicted_status", "HIGH")))
                if "estimated_rul_days" in fp and "RUL" not in data:
                    data["RUL"] = float(fp.get("estimated_rul_days", 0.0)) * 24.0

            if inv:
                data.setdefault("stock_status", str(inv.get("stockout_risk", "OPTIMAL")))
                data.setdefault("reorder_quantity", int(inv.get("recommended_order_quantity", 0)))
                if "reorder_point" in inv and "reorder_point" not in data:
                    data["reorder_point"] = float(inv["reorder_point"])
                if "safety_stock" in inv and "safety_stock" not in data:
                    data["safety_stock"] = float(inv["safety_stock"])
                if "predicted_demand_30d" in inv and "predicted_demand_30d" not in data:
                    data["predicted_demand_30d"] = float(inv["predicted_demand_30d"])
                part = inv.get("spare_part")
                if part and "required_parts" not in data:
                    data["required_parts"] = [part]

            if cost:
                data.setdefault("preventive_cost", float(cost.get("preventive_total_cost", 0.0)))
                data.setdefault("failure_cost", float(cost.get("failure_total_cost", 0.0)))
                data.setdefault("estimated_savings", float(cost.get("estimated_savings", 0.0)))

            if ua:
                data.setdefault("recommended_action", ua)
                data.setdefault("autonomous_decision", ua)

            if "required_skills" not in data:
                data["required_skills"] = ["HVAC_CERTIFIED", "BEARING_OVERHAUL", "HVAC_CHILLER_SPECIALIST"]

        return data
