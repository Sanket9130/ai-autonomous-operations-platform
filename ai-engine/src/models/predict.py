"""
Inference and risk calculation module using the trained model artifact.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from src.models.model_utils import load_metadata, load_model
from src.preprocessing.preprocess import preprocess_single_payload
from src.recommendations.recommendation_engine import generate_maintenance_recommendations
from src.risk_engine.risk_score import calculate_asset_risk_score

# Cache loaded model in memory
_CACHED_MODEL: Optional[Any] = None


def get_model() -> Optional[Any]:
    """Retrieve cached model instance or load from disk."""
    global _CACHED_MODEL
    if _CACHED_MODEL is None:
        _CACHED_MODEL = load_model()
    return _CACHED_MODEL


def predict_asset_failure(
    asset_id: str,
    telemetry_features: Dict[str, Any],
    asset_type: str = "HVAC_CHILLER",
    model: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Compute real model-driven failure probability, operational risk score, and prescriptive actions.
    """
    active_model = model or get_model()
    if active_model is None:
        raise RuntimeError(
            "Trained model artifact 'best_hvac_model.joblib' is unavailable. "
            "Please train the model by running 'python scripts/train_model.py' before serving inference."
        )

    X_input = preprocess_single_payload(telemetry_features)

    if hasattr(active_model, "predict_proba"):
        prob_failure = float(active_model.predict_proba(X_input)[0, 1])
    elif hasattr(active_model, "predict"):
        prob_failure = float(active_model.predict(X_input)[0])
    else:
        raise RuntimeError("Loaded model object does not implement predict or predict_proba interface.")

    prob_failure = round(prob_failure, 4)

    # Ambient thermal stress and runtime factors from preprocessed DataFrame
    ambient_temp = float(X_input["ambient_temp_c"].iloc[0])
    runtime_hours = float(X_input["runtime_hours"].iloc[0])
    ambient_stress = max(0.0, (ambient_temp - 38.0) / 12.0)

    # Asset risk score calculation
    risk_info = calculate_asset_risk_score(
        asset_id=asset_id,
        failure_probability=prob_failure,
        criticality_weight=1.0,
        age_years=runtime_hours / 2500.0,
        ambient_temp_stress=ambient_stress,
    )

    risk_score = risk_info["risk_score"]
    risk_category = risk_info["risk_category"]

    # Status classification
    if risk_score >= 75 or prob_failure >= 0.70:
        status = "CRITICAL"
        estimated_rul_days = round(max(1.0, (1.0 - prob_failure) * 10), 1)
    elif risk_score >= 45 or prob_failure >= 0.35:
        status = "WARNING"
        estimated_rul_days = round(max(7.0, (1.0 - prob_failure) * 30), 1)
    else:
        status = "HEALTHY"
        estimated_rul_days = round(max(30.0, (1.0 - prob_failure) * 90), 1)

    # Prescriptive recommendations
    recommendations = generate_maintenance_recommendations(
        asset_id=asset_id,
        asset_type=asset_type,
        risk_score=risk_score,
        telemetry_summary=telemetry_features,
    )

    return {
        "asset_id": asset_id,
        "failure_probability": prob_failure,
        "predicted_status": status,
        "estimated_rul_days": estimated_rul_days,
        "risk_score": risk_score,
        "risk_category": risk_category,
        "recommendations": recommendations,
    }


def predict_remaining_useful_life(
    asset_id: str,
    telemetry_features: Dict[str, Any],
) -> Dict[str, Any]:
    """Estimate RUL days for asset."""
    result = predict_asset_failure(asset_id=asset_id, telemetry_features=telemetry_features)
    return {
        "asset_id": asset_id,
        "estimated_rul_days": result["estimated_rul_days"],
        "predicted_status": result["predicted_status"],
    }

