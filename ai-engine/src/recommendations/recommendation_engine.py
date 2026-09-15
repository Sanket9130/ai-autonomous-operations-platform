"""
Prescriptive AI Recommendation Engine for Facility Managers & Maintenance Engineers.
Generates automated work orders, preventive inspection suggestions, and dynamic replenishment actions.
"""

from typing import Any, Dict, List, Optional, Union


def generate_maintenance_recommendations(
    asset_id: str,
    asset_type: str,
    risk_score: float,
    telemetry_summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Produce actionable maintenance recommendations based on risk scores and operational anomalies.
    """
    recommendations = []
    if risk_score >= 80:
        recommendations.append({
            "asset_id": asset_id,
            "priority": "P1_URGENT",
            "action": "Immediate Inspection & Filter/Motor Bearing Diagnostic",
            "reason": f"High risk score ({risk_score}/100) indicates imminent failure vulnerability under current thermal load.",
            "suggested_role": "Senior HVAC / Electromechanical Technician",
        })
    elif risk_score >= 60:
        recommendations.append({
            "asset_id": asset_id,
            "priority": "P2_HIGH",
            "action": "Schedule Preventive Service Within 48 Hours",
            "reason": f"Elevated operational strain detected (risk score {risk_score}/100).",
            "suggested_role": "Maintenance Technician",
        })
    return recommendations


def evaluate_decision_intelligence(
    failure_probability: float,
    risk_level: str,
    asset_criticality: str = "HIGH",
    required_spare_part: Optional[str] = None,
    current_stock: float = 0.0,
    minimum_stock: float = 0.0,
    lead_time_days: float = 0.0,
) -> Dict[str, Any]:
    """
    Synthesize asset failure risk and spare-part availability into deterministic operational decisions.
    """
    # 1. Determine Stock Status
    if current_stock <= 0:
        stock_status = "OUT_OF_STOCK"
    elif current_stock < minimum_stock:
        stock_status = "LOW"
    elif current_stock <= (minimum_stock * 2.5):
        stock_status = "OPTIMAL"
    else:
        stock_status = "EXCESS"

    # 2. Determine Maintenance Priority
    crit_upper = str(asset_criticality).upper()
    is_high_crit = crit_upper in ["CRITICAL", "HIGH", "1", "1.0"]

    if failure_probability >= 0.70 or risk_level.upper() in ["CRITICAL", "HIGH"]:
        priority = "P1" if is_high_crit or failure_probability >= 0.80 else "P2"
    elif failure_probability >= 0.35 or risk_level.upper() in ["WARNING", "MEDIUM"]:
        priority = "P2" if is_high_crit else "P3"
    elif failure_probability >= 0.15:
        priority = "P3"
    else:
        priority = "P4"

    # 3. Formulate Action & Reason Matrix
    is_urgent_risk = priority in ["P1", "P2"] or failure_probability >= 0.50
    is_stock_deficient = stock_status in ["OUT_OF_STOCK", "LOW"]

    if is_urgent_risk and is_stock_deficient:
        action = "Schedule preventive maintenance and reorder spare part"
        reason = "High failure risk with insufficient spare-part stock"
    elif is_urgent_risk and not is_stock_deficient:
        action = "Dispatch technician for preventive maintenance with in-stock spare part"
        reason = "High failure risk detected; replacement spare parts are ready in inventory"
    elif not is_urgent_risk and is_stock_deficient:
        action = f"Initiate spare-part replenishment for {required_spare_part or 'component'}"
        reason = f"Asset condition stable, but inventory is below minimum safety threshold ({current_stock}/{minimum_stock})"
    else:
        action = "Maintain standard inspection and preventive maintenance schedule"
        reason = "Asset operating normally and inventory levels are sufficient"

    return {
        "failure_probability": round(float(failure_probability), 2),
        "risk_level": risk_level.upper(),
        "maintenance_priority": priority,
        "stock_status": stock_status,
        "recommended_action": action,
        "reason": reason,
    }


def evaluate_unified_operations_decision(
    asset_id: str,
    telemetry_features: Dict[str, Any],
    asset_type: str = "HVAC_CHILLER",
    asset_criticality: str = "HIGH",
    required_spare_part: str = "CHILLER_EXPANSION_VALVE",
    current_stock: float = 0.0,
    lead_time_days: float = 14.0,
    historical_daily_demand: Optional[List[float]] = None,
    forecast_days: int = 30,
) -> Dict[str, Any]:
    """
    Unified operations decision engine combining asset failure ML inference,
    risk scoring, spare-part demand forecasting, and inventory optimization.
    """
    from src.forecasting.demand_forecast import forecast_spare_part_demand
    from src.models.predict import predict_asset_failure

    # 1. Asset Failure & Risk ML Prediction
    pred = predict_asset_failure(
        asset_id=asset_id,
        telemetry_features=telemetry_features,
        asset_type=asset_type,
    )
    fail_prob = pred["failure_probability"]
    asset_risk = pred["predicted_status"]

    # 2. Spare Part Demand Forecasting
    demand_res = forecast_spare_part_demand(
        part_id=required_spare_part,
        historical_daily_demand=historical_daily_demand or [1.2, 1.0, 1.5, 0.8, 1.3, 1.1, 0.9, 1.4, 1.6, 1.0],
        forecast_days=forecast_days,
        current_stock=current_stock,
        lead_time_days=lead_time_days,
    )

    # 3. Decision Matrix & Action Formulation
    decision = evaluate_decision_intelligence(
        failure_probability=fail_prob,
        risk_level=asset_risk,
        asset_criticality=asset_criticality,
        required_spare_part=required_spare_part,
        current_stock=current_stock,
        minimum_stock=demand_res["safety_stock"],
        lead_time_days=lead_time_days,
    )

    # Standardized action code mapping
    maint_prio = decision["maintenance_priority"]
    stock_stat = decision["stock_status"]

    if maint_prio in ["P1", "P2"] and stock_stat in ["OUT_OF_STOCK", "LOW"]:
        action_code = "URGENT_PREVENTIVE_MAINTENANCE_AND_REORDER"
        reason = f"High failure risk ({fail_prob:.2f}) with critical/low spare-part inventory ({current_stock} units on hand vs ROP {demand_res['reorder_point']})"
    elif maint_prio in ["P1", "P2"] and stock_stat in ["OPTIMAL", "EXCESS"]:
        action_code = "DISPATCH_PREVENTIVE_MAINTENANCE_IN_STOCK"
        reason = f"High failure risk ({fail_prob:.2f}) detected; {required_spare_part} is available in stock ({current_stock} units)"
    elif maint_prio in ["P3", "P4"] and stock_stat in ["OUT_OF_STOCK", "LOW"]:
        action_code = "REORDER_SPARE_PARTS"
        reason = f"Asset condition stable, but inventory ({current_stock}) has breached reorder point ({demand_res['reorder_point']})"
    else:
        action_code = "MAINTAIN_STANDARD_SCHEDULE"
        reason = f"Asset telemetry normal and spare-part buffer is healthy ({current_stock} units on hand)"

    return {
        "failure_probability": fail_prob,
        "asset_risk": asset_risk,
        "maintenance_priority": maint_prio,
        "spare_part": required_spare_part,
        "stockout_risk": demand_res["stockout_risk"],
        "predicted_demand": demand_res["predicted_demand"],
        "reorder_point": demand_res["reorder_point"],
        "recommended_order_quantity": demand_res["recommended_order_quantity"],
        "recommended_action": action_code,
        "reason": reason,
    }


def execute_autonomous_operations_pipeline(
    asset_id: str,
    telemetry_features: Dict[str, Any],
    asset_type: str = "HVAC_CHILLER",
    asset_location: Union[Dict[str, float], str] = "MARINA",
    asset_criticality: str = "HIGH",
    required_spare_part: str = "CHILLER_EXPANSION_VALVE",
    current_stock: float = 0.0,
    lead_time_days: float = 14.0,
    forecast_days: int = 30,
    spare_part_cost: Optional[float] = 450.0,
    sla_deadline_hours: float = 3.0,
    estimated_repair_duration_hours: float = 1.5,
    candidate_technicians: Optional[List[Dict[str, Any]]] = None,
    historical_daily_demand: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    End-to-End Autonomous Operations Pipeline connecting telemetry, ML failure prediction,
    statistical inventory demand forecasting, technician routing, SLA margin assessment,
    and financial cost optimization into a single unified operational decision.
    """
    from src.forecasting.demand_forecast import forecast_spare_part_demand
    from src.models.predict import predict_asset_failure
    from src.recommendations.technician_router import select_best_technician
    from src.risk_engine.cost_optimizer import optimize_operational_decision

    # 1. Telemetry -> ML Asset Failure Prediction
    prediction = predict_asset_failure(
        asset_id=asset_id,
        telemetry_features=telemetry_features,
        asset_type=asset_type,
    )
    fail_prob = prediction["failure_probability"]
    asset_risk = prediction["predicted_status"]

    # 2. Spare-Part Demand Forecasting & Inventory Risk
    demand_forecast = forecast_spare_part_demand(
        part_id=required_spare_part,
        historical_daily_demand=historical_daily_demand or [1.2, 1.0, 1.5, 0.8, 1.3, 1.1, 0.9, 1.4, 1.6, 1.0],
        forecast_days=forecast_days,
        current_stock=current_stock,
        lead_time_days=lead_time_days,
    )

    # 3. Decision Matrix Synthesis
    decision = evaluate_decision_intelligence(
        failure_probability=fail_prob,
        risk_level=asset_risk,
        asset_criticality=asset_criticality,
        required_spare_part=required_spare_part,
        current_stock=current_stock,
        minimum_stock=demand_forecast["safety_stock"],
        lead_time_days=lead_time_days,
    )

    # 4. Technician Dispatch & Route ETA Selection
    technician_decision = select_best_technician(
        candidates=candidate_technicians or [{
            "technician_id": "TECH-DXB-042 (Senior HVAC Specialist)",
            "skills": ["HVAC_CHILLER_SPECIALIST", "ELECTROMECHANICAL"],
            "availability": True,
            "current_location": "DOWNTOWN",
            "technician_workload": 1,
        }],
        required_skill="HVAC_CHILLER_SPECIALIST" if "CHILLER" in asset_type.upper() else "HVAC_GENERAL",
        asset_location=asset_location,
        sla_deadline_hours=sla_deadline_hours,
        estimated_repair_duration_hours=estimated_repair_duration_hours,
    )

    # 5. Cost & SLA Optimization
    cost_opt = optimize_operational_decision(
        failure_probability=fail_prob,
        asset_criticality=asset_criticality,
        maintenance_priority=decision["maintenance_priority"],
        stock_status=decision["stock_status"],
        selected_technician=technician_decision["selected_technician"],
        technician_eta_minutes=technician_decision["estimated_eta"],
        sla_status=technician_decision["sla_status"],
        spare_part_cost=spare_part_cost,
        current_stock=current_stock,
        reorder_point=demand_forecast["reorder_point"],
    )

    # 6. Pipeline Unified Action & Operational Summary
    sla_status = technician_decision["sla_status"]
    is_critical = fail_prob >= 0.65 or decision["maintenance_priority"] in ["P1", "P2"]
    is_stock_low = decision["stock_status"] in ["OUT_OF_STOCK", "LOW"]

    if is_critical and sla_status == "SLA_BREACH_RISK":
        unified_action = "SLA_ESCALATION_REQUIRED"
        summary = (
            f"CRITICAL ALERT: Imminent failure risk ({fail_prob:.2f}) on {asset_id}. "
            f"Technician ETA ({technician_decision['estimated_eta']}m) threatens SLA deadline ({sla_deadline_hours}h). "
            f"Immediate supervisor escalation and priority re-route required."
        )
    elif is_critical and is_stock_low:
        unified_action = "URGENT_MAINTENANCE_AND_REORDER"
        summary = (
            f"High failure risk ({fail_prob:.2f}) with critical stockout vulnerability for {required_spare_part}. "
            f"Emergency parts reorder ({demand_forecast['recommended_order_quantity']} units) and technician dispatch initiated. "
            f"Net expected savings: {cost_opt['estimated_savings']} AED."
        )
    elif is_critical:
        unified_action = "URGENT_MAINTENANCE"
        summary = (
            f"Critical degradation detected ({fail_prob:.2f}). Spare part in stock. "
            f"Dispatched {technician_decision['selected_technician']} (ETA {technician_decision['estimated_eta']}m). "
            f"Estimated savings: {cost_opt['estimated_savings']} AED."
        )
    elif is_stock_low:
        if fail_prob < 0.25:
            unified_action = "REORDER_SPARE_PARTS"
            summary = (
                f"Asset {asset_id} operating in normal health ({fail_prob:.2f} failure probability, RUL {prediction['estimated_rul_days']}d). "
                f"However, critical stockout risk detected for {required_spare_part} ({current_stock} on hand vs ROP {demand_forecast['reorder_point']}). "
                f"Routine monitoring active; replenishment of {demand_forecast['recommended_order_quantity']} units recommended."
            )
        else:
            unified_action = "PROCEED_PREVENTIVE_MAINTENANCE_AND_REORDER"
            summary = (
                f"Moderate risk observed ({fail_prob:.2f}) and inventory is below reorder point ({current_stock}/{demand_forecast['reorder_point']}). "
                f"Parts replenishment ({demand_forecast['recommended_order_quantity']} units) and preventive service recommended."
            )
    elif fail_prob < 0.25:
        unified_action = "MONITOR"
        summary = (
            f"Asset {asset_id} operating in normal health ({fail_prob:.2f} failure probability). "
            f"Inventory buffer ({current_stock} units) and SLA margins are optimal. Standard monitoring active."
        )
    else:
        unified_action = "PROCEED_PREVENTIVE_MAINTENANCE"
        summary = (
            f"Moderate risk observed ({fail_prob:.2f}). Spare part in stock ({current_stock} units). "
            f"Preventive service recommended to capture {cost_opt['estimated_savings']} AED in avoided failure costs."
        )

    return {
        "asset_id": asset_id,
        "failure_prediction": {
            "failure_probability": fail_prob,
            "predicted_status": asset_risk,
            "risk_score": prediction["risk_score"],
            "estimated_rul_days": prediction["estimated_rul_days"],
        },
        "inventory_intelligence": {
            "spare_part": required_spare_part,
            "current_stock": current_stock,
            "predicted_demand_30d": demand_forecast["predicted_demand"],
            "safety_stock": demand_forecast["safety_stock"],
            "reorder_point": demand_forecast["reorder_point"],
            "stockout_risk": demand_forecast["stockout_risk"],
            "recommended_order_quantity": demand_forecast["recommended_order_quantity"],
        },
        "technician_dispatch": {
            "selected_technician": technician_decision["selected_technician"],
            "technician_score": technician_decision["technician_score"],
            "distance_km": technician_decision["distance"],
            "estimated_eta_minutes": technician_decision["estimated_eta"],
            "sla_status": technician_decision["sla_status"],
        },
        "cost_optimization": {
            "preventive_total_cost": cost_opt["preventive_total_cost"],
            "failure_total_cost": cost_opt["failure_total_cost"],
            "estimated_savings": cost_opt["estimated_savings"],
        },
        "unified_action": unified_action,
        "operational_summary": summary,
    }

