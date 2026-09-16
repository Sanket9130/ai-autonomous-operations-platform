"""
Preprocessing and feature engineering for HVAC telemetry and asset data.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

FEATURE_COLUMNS: List[str] = [
    "vibration_mm_s",
    "operating_temp_c",
    "ambient_temp_c",
    "power_kw",
    "runtime_hours",
    "last_maintenance_days",
    "temp_diff",
    "thermal_stress_index",
]

TARGET_COLUMN = "failure_within_7d"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive physics-informed thermal and stress indicators for Dubai FM operations."""
    data = df.copy()
    data["temp_diff"] = data["operating_temp_c"] - data["ambient_temp_c"]
    data["thermal_stress_index"] = (data["operating_temp_c"] / 100.0) * (data["ambient_temp_c"] / 45.0)
    return data


def clean_sensor_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean telemetry: drop exact duplicates, fill or drop NaNs."""
    if df.empty:
        return df
    cleaned = df.drop_duplicates().copy()
    cleaned = cleaned.ffill().bfill()
    return cleaned


def preprocess_dataframe(
    df: pd.DataFrame,
    is_training: bool = False,
) -> Union[Tuple[pd.DataFrame, pd.Series], pd.DataFrame]:
    """Prepare feature matrix and optional target series from DataFrame."""
    cleaned = clean_sensor_data(df)
    featured = engineer_features(cleaned)

    # Ensure all required features are present
    missing_cols = [col for col in FEATURE_COLUMNS if col not in featured.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    X = featured[FEATURE_COLUMNS]

    if is_training:
        if TARGET_COLUMN not in featured.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found in training DataFrame.")
        y = featured[TARGET_COLUMN].astype(int)
        return X, y

    return X


def _safe_float(val: Any, default: float) -> float:
    """Helper to convert value to float, using default if val is None or invalid."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def preprocess_single_payload(payload: Dict[str, Any]) -> pd.DataFrame:
    """Convert a single telemetry record dictionary into a 1-row feature DataFrame."""
    vibration = payload.get("vibration_mm_s") if payload.get("vibration_mm_s") is not None else payload.get("vibration_level")
    operating_temp = payload.get("operating_temp_c") if payload.get("operating_temp_c") is not None else payload.get("operating_temperature_c")
    ambient_temp = payload.get("ambient_temp_c") if payload.get("ambient_temp_c") is not None else payload.get("ambient_temperature_c")
    power = payload.get("power_kw") if payload.get("power_kw") is not None else payload.get("power_consumption_kw")
    runtime = payload.get("runtime_hours")
    last_maint = payload.get("last_maintenance_days") if payload.get("last_maintenance_days") is not None else payload.get("last_maintenance_days_ago")

    row = {
        "vibration_mm_s": _safe_float(vibration, 2.0),
        "operating_temp_c": _safe_float(operating_temp, 50.0),
        "ambient_temp_c": _safe_float(ambient_temp, 40.0),
        "power_kw": _safe_float(power, 50.0),
        "runtime_hours": _safe_float(runtime, 2000.0),
        "last_maintenance_days": _safe_float(last_maint, 30.0),
    }
    df = pd.DataFrame([row])
    featured = engineer_features(df)
    return featured[FEATURE_COLUMNS]

