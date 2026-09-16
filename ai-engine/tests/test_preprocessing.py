"""
Unit tests for data preprocessing and feature engineering.
"""

import pandas as pd
from src.preprocessing.preprocess import (
    FEATURE_COLUMNS,
    clean_sensor_data,
    engineer_features,
    preprocess_dataframe,
    preprocess_single_payload,
)


def test_clean_sensor_data_handles_duplicates_and_nans():
    df = pd.DataFrame({
        "vibration_mm_s": [2.0, 2.0, None],
        "operating_temp_c": [50.0, 50.0, 52.0],
    })
    cleaned = clean_sensor_data(df)
    assert len(cleaned) == 2
    assert not cleaned.isna().any().any()


def test_engineer_features_adds_temp_diff_and_stress():
    df = pd.DataFrame({
        "operating_temp_c": [65.0],
        "ambient_temp_c": [45.0],
    })
    featured = engineer_features(df)
    assert "temp_diff" in featured.columns
    assert "thermal_stress_index" in featured.columns
    assert featured["temp_diff"].iloc[0] == 20.0
    assert featured["thermal_stress_index"].iloc[0] == 0.65


def test_preprocess_single_payload():
    payload = {
        "asset_id": "HVAC-001",
        "vibration_mm_s": 3.5,
        "operating_temp_c": 58.0,
        "ambient_temp_c": 42.0,
        "power_kw": 65.0,
        "runtime_hours": 3200.0,
        "last_maintenance_days": 45,
    }
    X = preprocess_single_payload(payload)
    assert isinstance(X, pd.DataFrame)
    assert list(X.columns) == FEATURE_COLUMNS
    assert len(X) == 1
