"""
Asset and Inventory Risk Scoring Algorithms tailored for Dubai Facility Management operations.
Factors include extreme ambient temperature impacts, criticality, asset age, and stock availability.
"""

from typing import Any, Dict, List, Optional


def calculate_asset_risk_score(
    asset_id: str,
    failure_probability: float,
    criticality_weight: float = 1.0,
    age_years: float = 1.0,
    ambient_temp_stress: float = 1.0,
) -> Dict[str, Any]:
    """
    Compute 0-100 Asset Risk Index combining failure prob, equipment criticality, and ambient heat load.
    """
    raw_score = (failure_probability * 50.0) + (criticality_weight * 30.0) + (min(age_years / 10.0, 1.0) * 10.0) + (min(ambient_temp_stress, 1.0) * 10.0)
    final_score = min(max(round(raw_score, 1), 0.0), 100.0)

    category = "LOW"
    if final_score >= 80:
        category = "CRITICAL"
    elif final_score >= 60:
        category = "HIGH"
    elif final_score >= 35:
        category = "MEDIUM"

    return {
        "asset_id": asset_id,
        "risk_score": final_score,
        "risk_category": category,
        "criticality_weight": criticality_weight,
    }


def calculate_inventory_risk_score(
    part_id: str,
    stockout_probability: float,
    lead_time_days: float,
    asset_criticality_linked: float = 1.0,
) -> Dict[str, Any]:
    """
    Compute 0-100 Inventory Risk Index based on stockout probability, lead time friction, and asset dependency.
    """
    lead_time_factor = min(lead_time_days / 60.0, 1.0) * 30.0
    stockout_factor = stockout_probability * 50.0
    criticality_factor = min(asset_criticality_linked, 1.0) * 20.0

    final_score = min(max(round(lead_time_factor + stockout_factor + criticality_factor, 1), 0.0), 100.0)

    category = "LOW"
    if final_score >= 80:
        category = "CRITICAL"
    elif final_score >= 60:
        category = "HIGH"
    elif final_score >= 35:
        category = "MEDIUM"

    return {
        "part_id": part_id,
        "risk_score": final_score,
        "risk_category": category,
    }


def compute_composite_facility_risk(
    asset_risk_scores: List[float],
    inventory_risk_scores: List[float],
) -> Dict[str, Any]:
    """
    Compute composite operational risk score for an entire facility or property building.
    """
    avg_asset_risk = sum(asset_risk_scores) / len(asset_risk_scores) if asset_risk_scores else 0.0
    avg_inv_risk = sum(inventory_risk_scores) / len(inventory_risk_scores) if inventory_risk_scores else 0.0
    composite_score = round((0.65 * avg_asset_risk) + (0.35 * avg_inv_risk), 1)

    return {
        "composite_facility_risk": composite_score,
        "avg_asset_risk": round(avg_asset_risk, 1),
        "avg_inventory_risk": round(avg_inv_risk, 1),
    }
