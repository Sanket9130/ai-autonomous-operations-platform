"""
Generate realistic synthetic HVAC telemetry dataset for Dubai FM facilities.
Simulates multi-mode physical failure mechanisms with realistic stochasticity,
sensor noise, and unobserved environmental factors (no deterministic linear leakage).
"""

from pathlib import Path
import numpy as np
import pandas as pd


def generate_hvac_telemetry_data(num_samples: int = 2000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)

    asset_types = ["HVAC_CHILLER", "AIR_HANDLING_UNIT", "ROOFTOP_PACKAGED", "FAN_COIL_UNIT"]
    locations = ["DOWNTOWN", "MARINA", "BUSINESS_BAY", "DIFC", "JBR", "PALM_JUMEIRAH"]

    data = []
    for i in range(num_samples):
        atype = np.random.choice(asset_types)
        loc = np.random.choice(locations)
        asset_id = f"{atype[:3]}-{loc[:3]}-{(i % 80) + 1:03d}"

        # Ambient conditions (Dubai climate distribution)
        ambient_temp = np.random.uniform(30.0, 49.5)
        runtime_hours = np.random.exponential(scale=3500.0) + 200.0
        runtime_hours = min(runtime_hours, 15000.0)
        last_maintenance_days = int(np.random.exponential(scale=40.0)) + 1
        last_maintenance_days = min(last_maintenance_days, 180)

        # Baseline physical behavior with realistic variance
        base_vibration = np.random.gamma(shape=3.0, scale=0.7)  # Mean ~2.1 mm/s
        base_operating_temp = ambient_temp + np.random.normal(18.0, 5.0)
        base_power = np.random.normal(55.0, 18.0)

        # Failure modes simulation (physical failure mechanisms)
        mode = "NORMAL"
        roll = np.random.rand()
        if roll < 0.08:
            # Mode A: Mechanical / Bearing degradation
            mode = "BEARING_WEAR"
            base_vibration += np.random.uniform(2.5, 5.0)
            base_operating_temp += np.random.uniform(5.0, 12.0)
        elif roll < 0.15:
            # Mode B: Thermal overload & condenser fouling under Dubai heat
            mode = "THERMAL_OVERLOAD"
            base_operating_temp += np.random.uniform(15.0, 30.0)
            base_power += np.random.uniform(25.0, 55.0)
        elif roll < 0.19:
            # Mode C: Overdue maintenance / lubrication starvation
            mode = "LUBRICATION_STARVATION"
            base_vibration += np.random.uniform(1.8, 3.5)
            base_operating_temp += np.random.uniform(8.0, 18.0)

        # Add realistic sensor measurement noise (jitter)
        vibration = max(0.4, round(float(base_vibration + np.random.normal(0, 0.25)), 2))
        operating_temp = max(32.0, round(float(base_operating_temp + np.random.normal(0, 1.2)), 1))
        ambient_temp = round(float(ambient_temp), 1)
        power_kw = max(12.0, round(float(base_power + np.random.normal(0, 3.0)), 1))
        runtime_hours = round(float(runtime_hours), 1)

        # Non-linear failure risk calculation
        temp_delta = max(0.0, operating_temp - ambient_temp)
        bearing_risk = 1.0 / (1.0 + np.exp(-1.5 * (vibration - 4.2)))
        thermal_risk = 1.0 / (1.0 + np.exp(-0.15 * (operating_temp - 72.0))) if ambient_temp > 38.0 else 0.05
        aging_risk = min(runtime_hours / 12000.0, 1.0) * min(last_maintenance_days / 90.0, 1.5) * 0.35

        # Compound failure risk probability
        combined_prob = 0.45 * bearing_risk + 0.35 * thermal_risk + 0.20 * aging_risk

        # Unobserved random shocks (electrical surges, refrigerant leaks: ~3%)
        if np.random.rand() < 0.03:
            combined_prob = max(combined_prob, 0.75)

        # False alarms / resilient assets (~4% do not fail despite warning readings)
        if np.random.rand() < 0.04:
            combined_prob = min(combined_prob, 0.15)

        combined_prob = float(np.clip(combined_prob, 0.01, 0.95))

        # Stochastic binary outcome (not deterministic threshold)
        failure_within_7d = int(np.random.binomial(n=1, p=combined_prob))

        data.append({
            "asset_id": asset_id,
            "asset_type": atype,
            "vibration_mm_s": vibration,
            "operating_temp_c": operating_temp,
            "ambient_temp_c": ambient_temp,
            "power_kw": power_kw,
            "runtime_hours": runtime_hours,
            "last_maintenance_days": last_maintenance_days,
            "failure_within_7d": failure_within_7d,
        })

    df = pd.DataFrame(data)
    return df


def generate_spare_parts_demand_data(days: int = 180, random_seed: int = 42) -> pd.DataFrame:
    """Generate realistic daily spare part consumption series for FM operations."""
    np.random.seed(random_seed)
    parts = [
        {"part_id": "CHILLER_EXPANSION_VALVE", "base_daily": 0.8, "summer_multiplier": 2.2, "lead_time_days": 14},
        {"part_id": "AHU_V_BELT_B56", "base_daily": 2.5, "summer_multiplier": 1.6, "lead_time_days": 7},
        {"part_id": "MOTOR_BEARING_6208", "base_daily": 1.2, "summer_multiplier": 2.0, "lead_time_days": 21},
        {"part_id": "HVAC_AIR_FILTER_MERV13", "base_daily": 6.0, "summer_multiplier": 1.8, "lead_time_days": 5},
        {"part_id": "REFRIGERANT_R134A_CYLINDER", "base_daily": 1.5, "summer_multiplier": 2.5, "lead_time_days": 10},
    ]

    records = []
    for day in range(days):
        # Summer peak simulation (middle 90 days represent peak heat)
        is_summer = 45 <= day <= 135
        for p in parts:
            rate = p["base_daily"] * (p["summer_multiplier"] if is_summer else 1.0)
            daily_demand = int(np.random.poisson(lam=rate))
            records.append({
                "day_index": day,
                "part_id": p["part_id"],
                "daily_demand": daily_demand,
                "lead_time_days": p["lead_time_days"],
                "is_summer_peak": int(is_summer),
            })
    return pd.DataFrame(records)


def main():
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. Telemetry Data
    hvac_path = raw_dir / "hvac_sensor_data.csv"
    df_hvac = generate_hvac_telemetry_data(num_samples=2000, random_seed=42)
    df_hvac.to_csv(hvac_path, index=False)
    print(f"Generated {len(df_hvac)} telemetry records at: {hvac_path}")

    # 2. Spare Parts Historical Demand Data
    parts_path = raw_dir / "spare_parts_demand.csv"
    df_parts = generate_spare_parts_demand_data(days=180, random_seed=42)
    df_parts.to_csv(parts_path, index=False)
    print(f"Generated {len(df_parts)} spare-part daily demand logs at: {parts_path}")


if __name__ == "__main__":
    main()

