"""
Cost & SLA Optimization Engine for Dubai Facility Management Operations.
Performs financial comparison between preventive interventions vs. catastrophic failure downtime costs.
"""

from typing import Any, Dict, List, Optional, Union

# Transparent Baseline Cost Configuration (AED - UAE Dirhams)
DEFAULT_COST_CONFIG: Dict[str, Any] = {
    "technician_hourly_rate_aed": 150.0,
    "emergency_rate_multiplier": 2.2,
    "default_spare_part_cost_aed": 450.0,
    "rush_procurement_multiplier": 1.4,
    "criticality_downtime_hourly_rates": {
        "CRITICAL": 1200.0,
        "HIGH": 750.0,
        "MEDIUM": 350.0,
        "LOW": 150.0,
    },
    "default_sla_penalty_aed": 1500.0,
    "standard_pm_duration_hours": 1.5,
    "emergency_repair_duration_hours": 4.0,
}


def calculate_maintenance_costs(
    failure_probability: float,
    asset_criticality: str = "HIGH",
    spare_part_cost: Optional[float] = None,
    custom_cost_config: Optional[Dict[str, Any]] = None,
    sla_breach_expected: bool = False,
) -> Dict[str, Any]:
    """
    Compute structured preventive vs. emergency failure costs and net expected financial savings.
    """
    cfg = {**DEFAULT_COST_CONFIG, **(custom_cost_config or {})}
    crit_key = str(asset_criticality).upper()
    downtime_rate = cfg["criticality_downtime_hourly_rates"].get(crit_key, 500.0)

    part_cost = float(spare_part_cost if spare_part_cost is not None else cfg["default_spare_part_cost_aed"])

    # 1. Preventive Maintenance Cost Model
    pm_labor_cost = cfg["technician_hourly_rate_aed"] * cfg["standard_pm_duration_hours"]
    pm_parts_cost = part_cost
    preventive_total_cost = round(pm_labor_cost + pm_parts_cost, 2)

    # 2. Emergency Failure Cost Model (Breakdown scenario)
    em_labor_cost = (
        cfg["technician_hourly_rate_aed"]
        * cfg["emergency_rate_multiplier"]
        * cfg["emergency_repair_duration_hours"]
    )
    em_parts_cost = part_cost * cfg["rush_procurement_multiplier"]
    em_downtime_cost = downtime_rate * cfg["emergency_repair_duration_hours"]
    em_sla_penalty = cfg["default_sla_penalty_aed"] if sla_breach_expected else 0.0

    failure_total_cost = round(
        em_labor_cost + em_parts_cost + em_downtime_cost + em_sla_penalty, 2
    )

    # 3. Expected Value Savings Calculation
    expected_failure_impact = failure_probability * failure_total_cost
    estimated_savings = round(max(0.0, expected_failure_impact - preventive_total_cost), 2)
    direct_avoided_cost = round(max(0.0, failure_total_cost - preventive_total_cost), 2)

    return {
        "preventive_total_cost": preventive_total_cost,
        "preventive_breakdown": {
            "labor_cost": round(pm_labor_cost, 2),
            "spare_part_cost": round(pm_parts_cost, 2),
        },
        "failure_total_cost": failure_total_cost,
        "failure_breakdown": {
            "emergency_labor_cost": round(em_labor_cost, 2),
            "emergency_parts_cost": round(em_parts_cost, 2),
            "downtime_cost": round(em_downtime_cost, 2),
            "sla_penalty": round(em_sla_penalty, 2),
        },
        "expected_failure_impact": round(expected_failure_impact, 2),
        "estimated_savings": estimated_savings,
        "direct_avoided_cost": direct_avoided_cost,
    }


def optimize_operational_decision(
    failure_probability: float,
    asset_criticality: str = "HIGH",
    maintenance_priority: str = "P1",
    stock_status: str = "OPTIMAL",
    selected_technician: str = "TECH-DXB-042",
    technician_eta_minutes: float = 15.0,
    sla_status: str = "WITHIN_SLA",
    spare_part_cost: Optional[float] = None,
    current_stock: float = 0.0,
    reorder_point: float = 10.0,
) -> Dict[str, Any]:
    """
    Synthesize predictive failure, technician availability, SLA status, and cost optimization
    into a single high-level operational recommendation.
    """
    sla_breach_expected = sla_status == "SLA_BREACH_RISK"

    costs = calculate_maintenance_costs(
        failure_probability=failure_probability,
        asset_criticality=asset_criticality,
        spare_part_cost=spare_part_cost,
        sla_breach_expected=sla_breach_expected,
    )

    # Decision Matrix for Final Recommended Action
    is_critical_risk = failure_probability >= 0.65 or maintenance_priority in ["P1", "P2"]
    is_stock_ready = stock_status in ["OPTIMAL", "EXCESS"] or current_stock >= 1.0

    if is_critical_risk and is_stock_ready:
        final_action = "URGENT_MAINTENANCE"
        reason = (
            f"High failure risk ({failure_probability:.2f}) with expected downtime cost of {costs['failure_total_cost']} AED. "
            f"Dispatching {selected_technician} (ETA {technician_eta_minutes}m) generates estimated savings of {costs['estimated_savings']} AED."
        )
    elif is_critical_risk and not is_stock_ready:
        final_action = "REORDER_AND_SCHEDULE"
        reason = (
            f"High failure risk ({failure_probability:.2f}) but spare parts are below threshold ({current_stock}/{reorder_point}). "
            f"Immediate parts requisition required before scheduling technician dispatch."
        )
    elif failure_probability >= 0.30 and not is_stock_ready:
        final_action = "PREVENTIVE_MAINTENANCE_AND_REORDER"
        reason = (
            f"Moderate risk detected ({failure_probability:.2f}) and spare parts are below threshold ({current_stock}/{reorder_point}). "
            f"Replenishment and preventive scheduling recommended to capture {costs['estimated_savings']} AED."
        )
    elif failure_probability >= 0.30:
        final_action = "PROCEED_PREVENTIVE_MAINTENANCE"
        reason = (
            f"Moderate risk detected. Performing preventive service saves an estimated {costs['estimated_savings']} AED "
            f"vs. unplanned outage."
        )
    elif not is_stock_ready:
        final_action = "REORDER_SPARE_PARTS"
        reason = (
            f"Asset operating normally (failure probability {failure_probability:.2f}), but inventory ({current_stock}/{reorder_point}) "
            f"is below reorder threshold. Replenishment recommended while maintaining routine monitoring."
        )
    else:
        final_action = "MONITOR"
        reason = (
            f"Asset operating normally (failure probability {failure_probability:.2f}). "
            f"Continue routine telemetry monitoring; no immediate capital expenditure required."
        )

    return {
        "preventive_total_cost": costs["preventive_total_cost"],
        "failure_total_cost": costs["failure_total_cost"],
        "estimated_savings": costs["estimated_savings"],
        "sla_risk": sla_status,
        "final_recommended_action": final_action,
        "reason": reason,
        "cost_details": costs,
    }
