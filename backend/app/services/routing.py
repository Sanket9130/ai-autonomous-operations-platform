import math
from typing import Dict, Any, Tuple
from backend.app.core.config import settings

EARTH_RADIUS_KM = 6371.0


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) using Haversine formula.
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clamp 'a' to [0, 1] to prevent math domain error due to floating point inaccuracies
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance_km = EARTH_RADIUS_KM * c
    return round(distance_km, 3)


def calculate_eta(
    distance_km: float, speed_kmh: float = None
) -> Tuple[float, float]:
    """
    Calculates ETA in minutes and travel hours given distance in km and average speed in km/h.
    Returns: (eta_minutes, travel_hours)
    """
    effective_speed = speed_kmh if speed_kmh and speed_kmh > 0 else settings.AVERAGE_SPEED_KMH
    if effective_speed <= 0:
        effective_speed = 30.0

    travel_hours = distance_km / effective_speed
    eta_minutes = travel_hours * 60.0
    return round(eta_minutes, 2), round(travel_hours, 4)


def get_route_info(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    speed_kmh: float = None
) -> Dict[str, Any]:
    """
    Returns complete route details between origin and destination.
    """
    distance_km = calculate_haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    effective_speed = speed_kmh if speed_kmh and speed_kmh > 0 else settings.AVERAGE_SPEED_KMH
    eta_minutes, travel_hours = calculate_eta(distance_km, effective_speed)

    return {
        "distance_km": distance_km,
        "eta_minutes": eta_minutes,
        "eta_hours": travel_hours,
        "average_speed_kmh": effective_speed,
    }
