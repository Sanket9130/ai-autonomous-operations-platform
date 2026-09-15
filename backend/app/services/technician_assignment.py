from typing import List, Dict, Any, Optional, Tuple
from backend.app.models.technician import Technician
from backend.app.models.asset import Asset
from backend.app.services.routing import get_route_info
from backend.app.services.sla import evaluate_sla_status, SLA_WITHIN, SLA_AT_RISK, SLA_BREACH


def score_technician(
    technician: Technician,
    asset: Asset,
    required_skills: List[str],
    speed_kmh: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes a deterministic score for an individual technician based on:
      1. Required skill & certification match (40%)
      2. Distance and proximity to asset (30%)
      3. Years of field experience (15%)
      4. SLA compliance (15%)
    """
    route = get_route_info(
        origin_lat=technician.current_latitude,
        origin_lon=technician.current_longitude,
        dest_lat=asset.latitude,
        dest_lon=asset.longitude,
        speed_kmh=speed_kmh,
    )

    distance_km = route["distance_km"]
    eta_minutes = route["eta_minutes"]
    eta_hours = route["eta_hours"]

    sla_info = evaluate_sla_status(eta_hours, asset.criticality)

    # 1. Skill Match Score (0.0 to 1.0)
    tech_skills = {s.strip().upper() for s in (technician.skills or [])}
    tech_certs = {c.strip().upper() for c in (technician.certifications or [])}
    combined_qualifications = tech_skills.union(tech_certs)

    if required_skills:
        req_set = {s.strip().upper() for s in required_skills}
        matched = combined_qualifications.intersection(req_set)
        skill_ratio = len(matched) / len(req_set)
    else:
        skill_ratio = 1.0

    skill_score = skill_ratio * 40.0  # Max 40 points

    # 2. Proximity Score (Max 30 points)
    # Closer distance yields higher score; decays smoothly
    # 0 km = 30 pts, 15 km = 15 pts, 30+ km = 0 pts
    proximity_points = max(0.0, 30.0 - (distance_km * 1.0))

    # 3. Experience Score (Max 15 points, normalized to 15 years)
    experience_years = max(0.0, float(technician.experience or 0))
    experience_points = min(15.0, (experience_years / 15.0) * 15.0)

    # 4. SLA Compliance Score (Max 15 points)
    if sla_info["sla_status"] == SLA_WITHIN:
        sla_points = 15.0
    elif sla_info["sla_status"] == SLA_AT_RISK:
        sla_points = 7.5
    else:
        sla_points = -20.0  # Penalty for breach risk

    total_score = round(max(0.0, skill_score + proximity_points + experience_points + sla_points), 2)

    return {
        "technician": technician,
        "score": total_score,
        "skill_ratio": skill_ratio,
        "distance_km": distance_km,
        "eta_minutes": eta_minutes,
        "eta_hours": eta_hours,
        "sla": sla_info,
        "route": route,
    }


def rank_technicians(
    technicians: List[Technician],
    asset: Asset,
    required_skills: List[str] = None,
    speed_kmh: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Ranks available technicians deterministically.
    Filters out unavailable technicians.
    Sorts by total_score DESC, distance_km ASC, technician_id ASC.
    """
    req_skills = required_skills or []
    available_techs = [t for t in technicians if t.availability is True]

    scored = [
        score_technician(tech, asset, req_skills, speed_kmh=speed_kmh)
        for tech in available_techs
    ]

    # Deterministic sorting
    scored.sort(
        key=lambda item: (
            -item["score"],
            item["distance_km"],
            item["technician"].technician_id,
        )
    )

    return scored
