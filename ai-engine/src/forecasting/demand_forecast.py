"""
Demand forecasting, stockout risk, overstock risk, safety stock, and reorder point calculations.
"""

from typing import Any, Dict, List, Optional
import math


def forecast_spare_part_demand(
    part_id: str,
    historical_daily_demand: List[float],
    forecast_days: int = 30,
    current_stock: float = 0.0,
    lead_time_days: float = 14.0,
    service_level_z: float = 1.65,  # 95% cycle service level
) -> Dict[str, Any]:
    """
    Generate statistical demand forecast (7, 30, 90 days), safety stock, ROP, and stockout risk.
    """
    if not historical_daily_demand:
        historical_daily_demand = [1.0]

    n = len(historical_daily_demand)
    avg_daily_demand = float(sum(historical_daily_demand) / n)

    # Calculate demand variance & standard deviation
    variance = sum((x - avg_daily_demand) ** 2 for x in historical_daily_demand) / max(1, n - 1)
    daily_std = math.sqrt(variance) if variance > 0 else (avg_daily_demand * 0.3)

    # 1. Predicted demand over requested horizon (7, 30, 90 days)
    predicted_demand = round(avg_daily_demand * forecast_days, 2)

    # 2. Safety Stock = Z * sigma_D * sqrt(Lead_Time)
    safety_stock = round(service_level_z * daily_std * math.sqrt(max(1.0, lead_time_days)), 2)

    # 3. Reorder Point = (Average Daily Demand * Lead Time) + Safety Stock
    reorder_point = round((avg_daily_demand * lead_time_days) + safety_stock, 2)

    # 4. Stockout Risk Assessment
    if current_stock <= 0:
        stockout_risk = "CRITICAL"
    elif current_stock < reorder_point:
        stockout_risk = "HIGH"
    elif current_stock < (reorder_point * 1.25):
        stockout_risk = "MEDIUM"
    else:
        stockout_risk = "LOW"

    # 5. Recommended Order Quantity
    if current_stock < reorder_point:
        recommended_order_quantity = max(0.0, round((reorder_point * 1.5) - current_stock, 0))
    else:
        recommended_order_quantity = 0.0

    return {
        "part_id": part_id,
        "forecast_days": forecast_days,
        "average_daily_demand": round(avg_daily_demand, 3),
        "predicted_demand": predicted_demand,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "current_stock": float(current_stock),
        "stockout_risk": stockout_risk,
        "recommended_order_quantity": recommended_order_quantity,
    }



def calculate_safety_stock(
    service_factor_z: float,
    lead_time_std: float,
    demand_mean: float,
    demand_std: float,
    lead_time_mean: float,
) -> float:
    """
    Calculate safety stock using standard statistical inventory formula:
    SS = Z * sqrt( (LT_mean * sigma_D^2) + (D_mean^2 * sigma_LT^2) )
    """
    variance = (lead_time_mean * (demand_std ** 2)) + ((demand_mean ** 2) * (lead_time_std ** 2))
    return round(service_factor_z * math.sqrt(variance), 2)


def calculate_reorder_point(
    demand_mean_daily: float,
    lead_time_days: float,
    safety_stock: float,
) -> float:
    """
    Calculate reorder point:
    ROP = (Average Daily Demand * Average Lead Time) + Safety Stock
    """
    return round((demand_mean_daily * lead_time_days) + safety_stock, 2)


def predict_stockout_risk(
    current_stock: float,
    projected_demand: float,
    reorder_point: float,
) -> Dict[str, Any]:
    """
    Assess probability and severity of running out of stock before next replenishment.
    """
    risk_level = "LOW"
    if current_stock <= 0:
        risk_level = "CRITICAL"
    elif current_stock < reorder_point:
        risk_level = "HIGH"
    elif current_stock < (reorder_point * 1.2):
        risk_level = "MEDIUM"

    return {
        "risk_level": risk_level,
        "current_stock": current_stock,
        "reorder_point": reorder_point,
        "stockout_probability": 0.95 if risk_level == "CRITICAL" else (0.75 if risk_level == "HIGH" else 0.15),
    }


def predict_overstock_risk(
    current_stock: float,
    projected_monthly_demand: float,
    holding_cost_rate: float = 0.15,
) -> Dict[str, Any]:
    """
    Assess financial locking and overstock risk (inventory holding > 6 months demand).
    """
    months_of_inventory = (
        current_stock / projected_monthly_demand
        if projected_monthly_demand > 0
        else 999.0
    )
    is_overstocked = months_of_inventory > 6.0
    return {
        "is_overstocked": is_overstocked,
        "months_of_inventory": round(months_of_inventory, 1),
        "overstock_risk_level": "HIGH" if months_of_inventory > 9.0 else ("MEDIUM" if is_overstocked else "LOW"),
    }
