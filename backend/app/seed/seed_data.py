from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.app.models.asset import Asset
from backend.app.models.telemetry import Telemetry
from backend.app.models.inventory import Inventory
from backend.app.models.technician import Technician
from backend.app.models.maintenance import Maintenance


def seed_database(db: Session):
    """
    Seeds initial operational data including CHILLER-MARINA-101, CHILLER-DIFC-002, telemetry,
    spare parts, and certified technicians.
    Upserts records so existing databases stay up-to-date and consistent.
    """
    now = datetime.now(timezone.utc)

    # 1. Assets
    assets_data = [
        {
            "asset_id": "CHILLER-MARINA-101",
            "name": "Chiller Unit Marina 101",
            "asset_type": "HVAC_CHILLER",
            "location": "Dubai Marina 101 Tower, Basement Level 2",
            "latitude": 25.0889,
            "longitude": 55.1458,
            "criticality": "CRITICAL",
            "status": "OPERATIONAL",
            "vibration_mm_s": 7.8,
            "operating_temp_c": 87.0,
            "ambient_temp_c": 48.0,
            "power_kw": 128.0,
            "runtime_hours": 9400.0,
            "last_maintenance_days": 88,
            "required_spare_part_id": "CHILLER_EXPANSION_VALVE",
            "created_at": now - timedelta(days=365),
        },
        {
            "asset_id": "CHILLER-DIFC-002",
            "name": "DIFC Gate Precinct Chiller #2",
            "asset_type": "HVAC_CHILLER",
            "location": "DIFC",
            "latitude": 25.2048,
            "longitude": 55.2708,
            "criticality": "MEDIUM",
            "status": "OPERATIONAL",
            "vibration_mm_s": 1.2,
            "operating_temp_c": 52.0,
            "ambient_temp_c": 32.0,
            "power_kw": 45.0,
            "runtime_hours": 1200.0,
            "last_maintenance_days": 10,
            "required_spare_part_id": "CHILLER_EXPANSION_VALVE",
            "created_at": now - timedelta(days=120),
        },
        {
            "asset_id": "PUMP-DOWNTOWN-202",
            "name": "Cooling Water Booster Pump 2",
            "asset_type": "WATER_PUMP",
            "location": "Downtown Facility Room 4",
            "latitude": 25.1972,
            "longitude": 55.2744,
            "criticality": "HIGH",
            "status": "OPERATIONAL",
            "vibration_mm_s": 5.8,
            "operating_temp_c": 78.0,
            "ambient_temp_c": 44.0,
            "power_kw": 38.0,
            "runtime_hours": 6800.0,
            "last_maintenance_days": 62,
            "required_spare_part_id": "PART-SEAL-901",
            "created_at": now - timedelta(days=200),
        },
        {
            "asset_id": "AHU-DOWNTOWN-005",
            "name": "Burj Area Commercial AHU-05",
            "asset_type": "AHU",
            "location": "DOWNTOWN",
            "latitude": 25.1972,
            "longitude": 55.2744,
            "criticality": "HIGH",
            "status": "OPERATIONAL",
            "vibration_mm_s": 5.8,
            "operating_temp_c": 78.0,
            "ambient_temp_c": 44.0,
            "power_kw": 38.0,
            "runtime_hours": 6800.0,
            "last_maintenance_days": 62,
            "required_spare_part_id": "AHU_MOTOR_BEARING",
            "created_at": now - timedelta(days=150),
        },
        {
            "asset_id": "CHILLER-PALM-999",
            "name": "Palm Jumeirah Resort Chiller #9",
            "asset_type": "HVAC_CHILLER",
            "location": "PALM_JUMEIRAH",
            "latitude": 25.1124,
            "longitude": 55.1390,
            "criticality": "CRITICAL",
            "status": "OPERATIONAL",
            "vibration_mm_s": 8.5,
            "operating_temp_c": 92.0,
            "ambient_temp_c": 49.0,
            "power_kw": 135.0,
            "runtime_hours": 9800.0,
            "last_maintenance_days": 90,
            "required_spare_part_id": "CHILLER_EXPANSION_VALVE",
            "created_at": now - timedelta(days=250),
        },
    ]

    for a_dict in assets_data:
        existing = db.query(Asset).filter(Asset.asset_id == a_dict["asset_id"]).first()
        if existing:
            for k, v in a_dict.items():
                setattr(existing, k, v)
        else:
            db.add(Asset(**a_dict))

    db.flush()

    # 2. Telemetry
    telem_data = [
        {
            "asset_id": "CHILLER-MARINA-101",
            "timestamp": now - timedelta(hours=2),
            "vibration_rms": 4.10,
            "bearing_temperature": 84.2,
            "coolant_pressure": 3.2,
            "power_kw": 41.5,
            "operating_hours": 14198.0,
        },
        {
            "asset_id": "CHILLER-MARINA-101",
            "timestamp": now,
            "vibration_rms": 4.82,
            "bearing_temperature": 88.5,
            "coolant_pressure": 3.1,
            "power_kw": 42.0,
            "operating_hours": 14200.0,
        },
        {
            "asset_id": "CHILLER-DIFC-002",
            "timestamp": now,
            "vibration_rms": 1.20,
            "bearing_temperature": 52.0,
            "coolant_pressure": 4.0,
            "power_kw": 45.0,
            "operating_hours": 1200.0,
        },
    ]

    existing_telem = db.query(Telemetry).count()
    if existing_telem == 0:
        for t in telem_data:
            db.add(Telemetry(**t))

    # 3. Maintenance
    existing_maint = db.query(Maintenance).count()
    if existing_maint == 0:
        db.add(
            Maintenance(
                asset_id="CHILLER-MARINA-101",
                serviced_at=now - timedelta(days=90),
                past_failures_count=2,
                notes="Q2 quarterly maintenance. Slight vibration increase logged.",
            )
        )
        db.add(
            Maintenance(
                asset_id="CHILLER-DIFC-002",
                serviced_at=now - timedelta(days=10),
                past_failures_count=0,
                notes="Routine quarterly check passed.",
            )
        )

    # 4. Inventory
    inventory_data = [
        {
            "part_id": "PART-BRG-7701",
            "part_name": "Ceramic Ball Bearing Assembly",
            "category": "Bearings",
            "current_stock": 2,
            "minimum_stock": 3,
            "lead_time": 4,
            "unit_cost": 450.00,
            "supplier": "SKF Industrial Middle East",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "CHILLER_EXPANSION_VALVE",
            "part_name": "Electronic Chiller Expansion Valve",
            "category": "HVAC_COMPONENTS",
            "current_stock": 0,
            "minimum_stock": 8,
            "lead_time": 14,
            "unit_cost": 500.00,
            "supplier": "Danfoss Middle East",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-CMP-402",
            "part_name": "Scroll Compressor Valve Kit",
            "category": "Compressors",
            "current_stock": 5,
            "minimum_stock": 2,
            "lead_time": 7,
            "unit_cost": 820.00,
            "supplier": "Carrier Commercial Service",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-SEN-108",
            "part_name": "Piezoelectric Vibration Sensor",
            "category": "Sensors",
            "current_stock": 8,
            "minimum_stock": 4,
            "lead_time": 2,
            "unit_cost": 120.00,
            "supplier": "Honeywell Automation",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-SEAL-901",
            "part_name": "Mechanical Shaft Seal Kit",
            "category": "Seals",
            "current_stock": 1,
            "minimum_stock": 3,
            "lead_time": 3,
            "unit_cost": 95.00,
            "supplier": "Flowserve Corp",
            "asset_type": "WATER_PUMP",
        },
        {
            "part_id": "AHU_MOTOR_BEARING",
            "part_name": "High-Load Ceramic Motor Bearing",
            "category": "ROTATING_EQUIPMENT",
            "current_stock": 15,
            "minimum_stock": 5,
            "lead_time": 7,
            "unit_cost": 180.00,
            "supplier": "SKF Industrial Middle East",
            "asset_type": "AHU",
        },
        {
            "part_id": "HVAC_AIR_FILTER_HEPA",
            "part_name": "Industrial HEPA Air Filter Grade H13",
            "category": "FILTRATION",
            "current_stock": 45,
            "minimum_stock": 20,
            "lead_time": 3,
            "unit_cost": 85.00,
            "supplier": "Camfil Middle East",
            "asset_type": "AHU",
        },
        {
            "part_id": "REFRIGERANT_R134A_CYLINDER",
            "part_name": "Eco-Refrigerant R134a 13.6kg",
            "category": "CONSUMABLES",
            "current_stock": 8,
            "minimum_stock": 4,
            "lead_time": 5,
            "unit_cost": 420.00,
            "supplier": "National Refrigerants",
            "asset_type": "HVAC_CHILLER",
        },
    ]

    for inv_dict in inventory_data:
        existing = db.query(Inventory).filter(Inventory.part_id == inv_dict["part_id"]).first()
        if existing:
            for k, v in inv_dict.items():
                setattr(existing, k, v)
        else:
            db.add(Inventory(**inv_dict))

    # 5. Technicians
    techs_data = [
        {
            "technician_id": "TECH-DXB-01",
            "name": "Ahmed Mansoor",
            "skills": ["HVAC_CERTIFIED", "BEARING_OVERHAUL", "VIBRATION_ANALYSIS", "HVAC_CHILLER_SPECIALIST"],
            "certifications": ["EPA_UNIVERSAL", "CAT_IV_VIBRATION"],
            "experience": 8.5,
            "current_latitude": 25.0772,
            "current_longitude": 55.1325,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "MARINA",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-02",
            "name": "Rashid Al-Falasi",
            "skills": ["HVAC_CERTIFIED", "ELECTRICAL_DIAGNOSTICS", "HVAC_CHILLER_SPECIALIST"],
            "certifications": ["EPA_UNIVERSAL"],
            "experience": 5.0,
            "current_latitude": 25.1120,
            "current_longitude": 55.2010,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "DOWNTOWN",
            "active_workload": 0,
        },
        {
            "technician_id": "TECH-DXB-03",
            "name": "Vikram Mehta",
            "skills": ["HVAC_CERTIFIED", "BEARING_OVERHAUL", "COMPRESSOR_REPAIR", "ELECTROMECHANICAL"],
            "certifications": ["EPA_UNIVERSAL", "ISO_VIBRATION_CAT3"],
            "experience": 12.0,
            "current_latitude": 25.1972,
            "current_longitude": 55.2744,
            "availability": False,
            "status": "ON_DUTY",
            "current_location": "DEIRA",
            "active_workload": 3,
        },
        {
            "technician_id": "TECH-DXB-04",
            "name": "Carlos Santos",
            "skills": ["PLUMBING", "PIPE_FITTING"],
            "certifications": ["SAFETY_OSHA"],
            "experience": 4.0,
            "current_latitude": 25.0800,
            "current_longitude": 55.1400,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "MARINA",
            "active_workload": 0,
        },
    ]

    for t_dict in techs_data:
        existing = db.query(Technician).filter(Technician.technician_id == t_dict["technician_id"]).first()
        if existing:
            for k, v in t_dict.items():
                setattr(existing, k, v)
        else:
            db.add(Technician(**t_dict))

    db.commit()
