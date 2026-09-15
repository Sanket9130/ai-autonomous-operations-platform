"""
Tests for risk engine calculations.
"""

from src.risk_engine.risk_score import (
    calculate_asset_risk_score,
    calculate_inventory_risk_score,
    compute_composite_facility_risk,
)


def test_calculate_asset_risk_score_critical():
    result = calculate_asset_risk_score(
        asset_id="PUMP-01",
        failure_probability=0.9,
        criticality_weight=1.0,
        age_years=8.0,
        ambient_temp_stress=1.0,
    )
    assert result["risk_score"] >= 80
    assert result["risk_category"] == "CRITICAL"


def test_calculate_inventory_risk_score():
    result = calculate_inventory_risk_score(
        part_id="VALVE-01",
        stockout_probability=0.8,
        lead_time_days=45.0,
    )
    assert "risk_score" in result
    assert result["risk_score"] > 0


def test_compute_composite_facility_risk():
    result = compute_composite_facility_risk(
        asset_risk_scores=[80.0, 60.0],
        inventory_risk_scores=[40.0, 50.0],
    )
    assert "composite_facility_risk" in result
    assert 50.0 <= result["composite_facility_risk"] <= 70.0
