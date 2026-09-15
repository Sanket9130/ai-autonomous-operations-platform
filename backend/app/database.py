"""
Database Access Layer for Facility Operations Backend.
Manages relational entities for Assets, Telemetry, Inventory, Technicians, and Operation Logs.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.app.config import settings


def get_db_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database with dict row factory."""
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed baseline operational data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Assets & Telemetry Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        asset_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        asset_type TEXT NOT NULL,
        location TEXT NOT NULL,
        criticality TEXT NOT NULL,
        vibration_mm_s REAL NOT NULL,
        operating_temp_c REAL NOT NULL,
        ambient_temp_c REAL NOT NULL,
        power_kw REAL NOT NULL,
        runtime_hours REAL NOT NULL,
        last_maintenance_days INTEGER NOT NULL,
        required_spare_part_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Inventory / Spare Parts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        part_id TEXT PRIMARY KEY,
        part_name TEXT NOT NULL,
        category TEXT NOT NULL,
        current_stock REAL NOT NULL,
        unit_cost_aed REAL NOT NULL,
        lead_time_days REAL NOT NULL,
        min_safety_stock REAL NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Technicians Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS technicians (
        technician_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        skills_json TEXT NOT NULL,
        is_available INTEGER NOT NULL,
        current_location TEXT NOT NULL,
        active_workload INTEGER NOT NULL,
        shift_status TEXT DEFAULT 'ACTIVE'
    );
    """)

    # 4. Autonomous Operations Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id TEXT NOT NULL,
        unified_action TEXT NOT NULL,
        failure_probability REAL NOT NULL,
        risk_score REAL NOT NULL,
        selected_technician TEXT NOT NULL,
        technician_eta_minutes REAL NOT NULL,
        estimated_savings_aed REAL NOT NULL,
        operational_summary TEXT NOT NULL,
        full_response_json TEXT NOT NULL,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Seed initial test data if assets table is empty
    cursor.execute("SELECT COUNT(*) FROM assets")
    count = cursor.fetchone()[0]
    if count == 0:
        _seed_initial_data(cursor)
        conn.commit()

    conn.close()


def _seed_initial_data(cursor: sqlite3.Cursor):
    """Seed realistic operational records for Dubai facilities."""
    # Seed Assets
    assets = [
        (
            "CHILLER-MARINA-101",
            "Marina Bay Tower Main Chiller #1",
            "HVAC_CHILLER",
            "MARINA",
            "CRITICAL",
            7.8,
            87.0,
            48.0,
            128.0,
            9400.0,
            88,
            "CHILLER_EXPANSION_VALVE",
        ),
        (
            "CHILLER-DIFC-002",
            "DIFC Gate Precinct Chiller #2",
            "HVAC_CHILLER",
            "DIFC",
            "MEDIUM",
            1.2,
            52.0,
            32.0,
            45.0,
            1200.0,
            10,
            "CHILLER_EXPANSION_VALVE",
        ),
        (
            "AHU-DOWNTOWN-005",
            "Burj Area Commercial AHU-05",
            "AHU",
            "DOWNTOWN",
            "HIGH",
            5.8,
            78.0,
            44.0,
            38.0,
            6800.0,
            62,
            "AHU_MOTOR_BEARING",
        ),
        (
            "CHILLER-PALM-999",
            "Palm Jumeirah Resort Chiller #9",
            "HVAC_CHILLER",
            "PALM_JUMEIRAH",
            "CRITICAL",
            8.5,
            92.0,
            49.0,
            135.0,
            9800.0,
            90,
            "CHILLER_EXPANSION_VALVE",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO assets (
            asset_id, name, asset_type, location, criticality,
            vibration_mm_s, operating_temp_c, ambient_temp_c, power_kw,
            runtime_hours, last_maintenance_days, required_spare_part_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        assets,
    )

    # Seed Inventory
    inventory = [
        ("CHILLER_EXPANSION_VALVE", "Electronic Chiller Expansion Valve", "HVAC_COMPONENTS", 0.0, 500.0, 14.0, 8.0),
        ("AHU_MOTOR_BEARING", "High-Load Ceramic Motor Bearing", "ROTATING_EQUIPMENT", 15.0, 180.0, 7.0, 5.0),
        ("HVAC_AIR_FILTER_HEPA", "Industrial HEPA Air Filter Grade H13", "FILTRATION", 45.0, 85.0, 3.0, 20.0),
        ("REFRIGERANT_R134A_CYLINDER", "Eco-Refrigerant R134a 13.6kg", "CONSUMABLES", 8.0, 420.0, 5.0, 4.0),
    ]
    cursor.executemany(
        """
        INSERT INTO inventory (
            part_id, part_name, category, current_stock,
            unit_cost_aed, lead_time_days, min_safety_stock
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        inventory,
    )

    # Seed Technicians
    technicians = [
        (
            "TECH-DXB-042",
            "Rashid Al-Nuaimi (Senior HVAC Specialist)",
            json.dumps(["HVAC_CHILLER_SPECIALIST", "ELECTROMECHANICAL"]),
            1,
            "DOWNTOWN",
            1,
            "ACTIVE",
        ),
        (
            "TECH-DXB-018",
            "Vikram Sharma (Electro-Mechanical Tech)",
            json.dumps(["AHU_SPECIALIST", "ELECTROMECHANICAL"]),
            1,
            "MARINA",
            0,
            "ACTIVE",
        ),
        (
            "TECH-DXB-007",
            "Ahmed Mansoor (General HVAC Tech)",
            json.dumps(["HVAC_GENERAL"]),
            1,
            "DEIRA",
            3,
            "ACTIVE",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO technicians (
            technician_id, name, skills_json, is_available,
            current_location, active_workload, shift_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        technicians,
    )


# ---------------------------------------------------------
# Query Helpers
# ---------------------------------------------------------
def get_asset_by_id(asset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve asset details and sensor telemetry by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def list_all_assets() -> List[Dict[str, Any]]:
    """List all assets with telemetry summary."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets ORDER BY asset_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_inventory_item(part_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve inventory item stock and pricing details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE part_id = ?", (part_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def list_all_inventory() -> List[Dict[str, Any]]:
    """List all inventory items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory ORDER BY part_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_candidate_technicians(only_available: bool = True) -> List[Dict[str, Any]]:
    """Fetch candidate technicians for AI dispatch ranking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if only_available:
        cursor.execute("SELECT * FROM technicians WHERE is_available = 1")
    else:
        cursor.execute("SELECT * FROM technicians")
    rows = cursor.fetchall()
    conn.close()

    candidates = []
    for r in rows:
        d = dict(r)
        candidates.append({
            "technician_id": f"{d['technician_id']} ({d['name']})",
            "skills": json.loads(d["skills_json"]),
            "availability": bool(d["is_available"]),
            "current_location": d["current_location"],
            "technician_workload": d["active_workload"],
        })
    return candidates


def save_operation_log(
    asset_id: str,
    unified_action: str,
    failure_probability: float,
    risk_score: float,
    selected_technician: str,
    technician_eta_minutes: float,
    estimated_savings_aed: float,
    operational_summary: str,
    full_response: Dict[str, Any],
) -> int:
    """Save an executed autonomous operation record into database audit trail."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO operation_logs (
            asset_id, unified_action, failure_probability, risk_score,
            selected_technician, technician_eta_minutes, estimated_savings_aed,
            operational_summary, full_response_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asset_id,
            unified_action,
            failure_probability,
            risk_score,
            selected_technician,
            technician_eta_minutes,
            estimated_savings_aed,
            operational_summary,
            json.dumps(full_response),
        ),
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def list_operation_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """List recent autonomous operations audit logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operation_logs ORDER BY executed_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
