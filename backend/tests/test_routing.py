import pytest
from backend.app.services.routing import calculate_haversine_distance, calculate_eta, get_route_info
from backend.app.services.sla import evaluate_sla_status, SLA_WITHIN, SLA_AT_RISK, SLA_BREACH
from backend.app.services.technician_assignment import score_technician, rank_technicians
from backend.app.models.technician import Technician
from backend.app.models.asset import Asset


def test_haversine_distance_calculation():
    """
    Test Haversine distance between two known geographic points in Dubai:
      Point A (Dubai Marina 101): 25.0889, 55.1458
      Point B (JBR nearby): 25.0772, 55.1325
      Expected distance: ~1.8 - 2.0 km
    """
    dist = calculate_haversine_distance(25.0889, 55.1458, 25.0772, 55.1325)
    assert 1.5 < dist < 2.5
    assert isinstance(dist, float)


def test_haversine_same_point():
    """Distance between identical coordinates must be 0.0."""
    dist = calculate_haversine_distance(25.0889, 55.1458, 25.0889, 55.1458)
    assert dist == 0.0


def test_calculate_eta():
    """Test ETA calculation for 15 km at 30 km/h = 30 minutes (0.5 hours)."""
    eta_min, eta_hours = calculate_eta(15.0, speed_kmh=30.0)
    assert eta_min == 30.0
    assert eta_hours == 0.5


def test_get_route_info():
    """Test full route info structure."""
    route = get_route_info(25.0772, 55.1325, 25.0889, 55.1458, speed_kmh=30.0)
    assert "distance_km" in route
    assert "eta_minutes" in route
    assert "eta_hours" in route
    assert "average_speed_kmh" in route
    assert route["average_speed_kmh"] == 30.0
    assert route["distance_km"] > 0


def test_sla_evaluation_statuses():
    """
    Critical SLA is 2.0 hours:
      eta <= 1.4h -> WITHIN_SLA
      1.4h < eta <= 2.0h -> AT_RISK
      eta > 2.0h -> SLA_BREACH_RISK
    """
    # 0.5 hours on Critical asset (2.0h limit)
    sla_within = evaluate_sla_status(0.5, "CRITICAL")
    assert sla_within["sla_status"] == SLA_WITHIN
    assert sla_within["sla_hours"] == 2.0

    # 1.6 hours on Critical asset -> AT_RISK
    sla_at_risk = evaluate_sla_status(1.6, "CRITICAL")
    assert sla_at_risk["sla_status"] == SLA_AT_RISK

    # 2.5 hours on Critical asset -> SLA_BREACH_RISK
    sla_breach = evaluate_sla_status(2.5, "CRITICAL")
    assert sla_breach["sla_status"] == SLA_BREACH


def test_technician_ranking_deterministic():
    """
    Test that technician ranking prioritizes:
      1. Skills match
      2. Distance/Proximity
      3. Experience
      Filters out unavailable technicians.
    """
    asset = Asset(
        asset_id="TEST-ASSET",
        name="Test Chiller",
        asset_type="HVAC_CHILLER",
        location="Marina",
        latitude=25.0889,
        longitude=55.1458,
        criticality="CRITICAL",
        status="OPERATIONAL",
    )

    t1_skilled_close = Technician(
        technician_id="T1",
        name="Close Skilled",
        skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL"],
        certifications=["EPA_UNIVERSAL"],
        experience=8.0,
        current_latitude=25.0772,  # Close (~1.8 km)
        current_longitude=55.1325,
        availability=True,
    )

    t2_skilled_far = Technician(
        technician_id="T2",
        name="Far Skilled",
        skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL"],
        certifications=["EPA_UNIVERSAL"],
        experience=10.0,
        current_latitude=25.2500,  # Far (~25 km)
        current_longitude=55.3000,
        availability=True,
    )

    t3_unskilled_close = Technician(
        technician_id="T3",
        name="Close Unskilled",
        skills=["PLUMBING"],
        certifications=[],
        experience=2.0,
        current_latitude=25.0800,  # Very close (~1 km)
        current_longitude=55.1400,
        availability=True,
    )

    t4_unavailable = Technician(
        technician_id="T4",
        name="Unavailable Tech",
        skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL"],
        certifications=["EPA_UNIVERSAL"],
        experience=15.0,
        current_latitude=25.0889,
        current_longitude=55.1458,
        availability=False,  # Not available
    )

    ranked = rank_technicians(
        [t1_skilled_close, t2_skilled_far, t3_unskilled_close, t4_unavailable],
        asset=asset,
        required_skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL"],
        speed_kmh=30.0,
    )

    # Verify t4_unavailable was filtered out
    ranked_ids = [item["technician"].technician_id for item in ranked]
    assert "T4" not in ranked_ids

    # Verify T1 is ranked first (has both required skills AND is close)
    assert ranked[0]["technician"].technician_id == "T1"
    assert ranked[0]["score"] > ranked[1]["score"]
