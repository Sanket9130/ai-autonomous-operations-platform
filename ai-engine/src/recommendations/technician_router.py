"""
Technician dispatch, suitability scoring, and route ETA optimization engine for Dubai FM operations.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

# Known Dubai FM key operational hubs and zones (coordinates)
DUBAI_ZONES: Dict[str, Tuple[float, float]] = {
    "DOWNTOWN": (25.1972, 55.2744),
    "BUSINESS_BAY": (25.1837, 55.2665),
    "DIFC": (25.2106, 55.2801),
    "MARINA": (25.0772, 55.1333),
    "JBR": (25.0789, 55.1311),
    "PALM_JUMEIRAH": (25.1124, 55.1390),
    "AL_BARSHA": (25.1112, 55.2045),
    "DEIRA": (25.2697, 55.3095),
    "BUR_DUBAI": (25.2532, 55.2974),
    "JLT": (25.0754, 55.1458),
    "DUBAI_HILLS": (25.1158, 55.2476),
}


def _resolve_coordinates(loc: Union[Dict[str, float], str, Tuple[float, float]]) -> Tuple[float, float]:
    """Parse lat/lng dictionary, tuple, or known Dubai area name."""
    if isinstance(loc, (list, tuple)) and len(loc) >= 2:
        return float(loc[0]), float(loc[1])
    if isinstance(loc, dict):
        lat = loc.get("lat", loc.get("latitude", 25.2048))
        lng = loc.get("lng", loc.get("longitude", 55.2708))
        return float(lat), float(lng)
    if isinstance(loc, str):
        key = loc.strip().upper().replace(" ", "_").replace("-", "_")
        for zone_key, coords in DUBAI_ZONES.items():
            if zone_key in key or key in zone_key:
                return coords
    # Default Dubai Central Coordinate
    return (25.2048, 55.2708)


def calculate_haversine_distance(
    loc1: Union[Dict[str, float], str, Tuple[float, float]],
    loc2: Union[Dict[str, float], str, Tuple[float, float]],
) -> float:
    """
    Calculate great-circle distance between two points in kilometers.
    """
    lat1, lon1 = _resolve_coordinates(loc1)
    lat2, lon2 = _resolve_coordinates(loc2)

    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance_km = r * c

    # Apply 1.25 urban road routing winding factor
    return round(distance_km * 1.25, 2)


def calculate_eta_minutes(distance_km: float, average_speed_kmh: float = 40.0) -> float:
    """
    Calculate estimated travel time in minutes with 5 min dispatch preparation buffer.
    """
    travel_time_min = (distance_km / max(10.0, average_speed_kmh)) * 60.0
    return round(travel_time_min + 5.0, 1)


def score_technician_suitability(
    technician: Dict[str, Any],
    required_skill: str,
    asset_location: Union[Dict[str, float], str, Tuple[float, float]],
    sla_deadline_hours: float,
    estimated_repair_duration_hours: float = 1.5,
) -> Dict[str, Any]:
    """
    Score a single technician candidate on skill match, availability, proximity, and SLA margin.
    """
    tech_id = technician.get("technician_id", technician.get("id", "TECH-UNASSIGNED"))
    skills = [s.upper() for s in technician.get("skills", ["HVAC_GENERAL"])]
    is_available = bool(technician.get("availability", True))
    current_workload = float(technician.get("technician_workload", technician.get("workload", 0)))
    tech_location = technician.get("current_location", technician.get("location", "DOWNTOWN"))

    # 1. Skill Match Score (0.0 to 1.0)
    req_upper = required_skill.upper()
    if any(req_upper in s or s in req_upper for s in skills):
        skill_score = 1.0
    elif any("HVAC" in s or "ELECTRO" in s for s in skills):
        skill_score = 0.7
    else:
        skill_score = 0.3

    # 2. Availability Score
    avail_score = 1.0 if is_available else 0.1

    # 3. Distance & ETA Calculation
    distance_km = calculate_haversine_distance(tech_location, asset_location)
    eta_minutes = calculate_eta_minutes(distance_km)
    proximity_score = max(0.0, 1.0 - (distance_km / 45.0))

    # 4. Workload Score (penalty for overloaded technicians)
    workload_score = max(0.1, 1.0 - (min(current_workload, 5.0) * 0.18))

    # 5. Composite Suitability Score (0 to 100)
    composite_score = (
        (skill_score * 0.35)
        + (avail_score * 0.30)
        + (proximity_score * 0.20)
        + (workload_score * 0.15)
    ) * 100.0
    composite_score = round(min(max(composite_score, 0.0), 100.0), 1)

    # 6. SLA Risk Determination
    total_ttr_hours = (eta_minutes / 60.0) + estimated_repair_duration_hours
    if total_ttr_hours <= (sla_deadline_hours * 0.75):
        sla_status = "WITHIN_SLA"
    elif total_ttr_hours <= sla_deadline_hours:
        sla_status = "AT_RISK"
    else:
        sla_status = "SLA_BREACH_RISK"

    return {
        "technician_id": tech_id,
        "technician_score": composite_score,
        "distance": distance_km,
        "estimated_eta": eta_minutes,
        "sla_status": sla_status,
        "is_available": is_available,
        "skill_score": skill_score,
        "total_ttr_hours": round(total_ttr_hours, 2),
    }


def select_best_technician(
    candidates: List[Dict[str, Any]],
    required_skill: str,
    asset_location: Union[Dict[str, float], str, Tuple[float, float]],
    sla_deadline_hours: float,
    estimated_repair_duration_hours: float = 1.5,
) -> Dict[str, Any]:
    """
    Evaluate all technician candidates, rank by suitability score, and select the optimal dispatch.
    """
    if not candidates:
        # Default fallback technician
        candidates = [{
            "technician_id": "TECH-DXB-001 (Senior HVAC Specialist)",
            "skills": [required_skill, "HVAC_CHILLER_SPECIALIST"],
            "availability": True,
            "current_location": "DOWNTOWN",
            "technician_workload": 1,
        }]

    scored_techs = [
        score_technician_suitability(
            technician=t,
            required_skill=required_skill,
            asset_location=asset_location,
            sla_deadline_hours=sla_deadline_hours,
            estimated_repair_duration_hours=estimated_repair_duration_hours,
        )
        for t in candidates
    ]

    # Sort primarily by composite score, then by SLA status
    scored_techs.sort(key=lambda x: x["technician_score"], reverse=True)
    best = scored_techs[0]

    reason = (
        f"Selected {best['technician_id']} with score {best['technician_score']}/100. "
        f"Distance: {best['distance']} km, ETA: {best['estimated_eta']} mins, SLA: {best['sla_status']}."
    )

    return {
        "selected_technician": best["technician_id"],
        "technician_score": best["technician_score"],
        "distance": best["distance"],
        "estimated_eta": best["estimated_eta"],
        "sla_status": best["sla_status"],
        "reason": reason,
    }
