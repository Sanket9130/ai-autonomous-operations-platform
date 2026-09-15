from typing import Dict, Any
from backend.app.core.config import settings

# SLA Status constants
SLA_WITHIN = "WITHIN_SLA"
SLA_AT_RISK = "AT_RISK"
SLA_BREACH = "SLA_BREACH_RISK"


def get_sla_limit_hours(criticality: str) -> float:
    """
    Returns the configured SLA limit in hours based on asset criticality.
    """
    crit = (criticality or "HIGH").strip().upper()
    if crit == "CRITICAL":
        return settings.SLA_HOURS_CRITICAL
    elif crit == "HIGH":
        return settings.SLA_HOURS_HIGH
    elif crit == "MEDIUM":
        return settings.SLA_HOURS_MEDIUM
    elif crit == "LOW":
        return settings.SLA_HOURS_LOW
    return settings.SLA_HOURS_HIGH


def evaluate_sla_status(eta_hours: float, criticality: str) -> Dict[str, Any]:
    """
    Determines whether the technician dispatch ETA is WITHIN_SLA, AT_RISK, or SLA_BREACH_RISK.

    Rules:
      - eta_hours <= 0.70 * SLA: WITHIN_SLA (safe margin)
      - 0.70 * SLA < eta_hours <= SLA: AT_RISK (tight margin)
      - eta_hours > SLA: SLA_BREACH_RISK (breach predicted)
    """
    sla_limit = get_sla_limit_hours(criticality)

    if eta_hours <= (0.70 * sla_limit):
        status = SLA_WITHIN
    elif eta_hours <= sla_limit:
        status = SLA_AT_RISK
    else:
        status = SLA_BREACH

    return {
        "sla_hours": sla_limit,
        "eta_hours": round(eta_hours, 3),
        "sla_status": status,
        "criticality": (criticality or "HIGH").upper(),
    }
