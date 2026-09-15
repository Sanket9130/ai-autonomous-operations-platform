from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.app.models.asset import Asset
from backend.app.models.telemetry import Telemetry
from backend.app.models.inventory import Inventory
from backend.app.models.technician import Technician
from backend.app.models.maintenance import Maintenance


def seed_database(db: Session):
    """
    Seeds initial enterprise data including CHILLER-MARINA-101, telemetry,
    spare parts, and certified technicians.
    Idempotent: skips seeding if assets already exist.
    """
    existing_asset = db.query(Asset).filter(Asset.asset_id == "CHILLER-MARINA-101").first()
    if existing_asset:
        return

    now = datetime.now(timezone.utc)

    # 1. Primary Test Asset: CHILLER-MARINA-101
    chiller = Asset(
        asset_id="CHILLER-MARINA-101",
        name="Chiller Unit Marina 101",
        asset_type="HVAC_CHILLER",
        location="Dubai Marina 101 Tower, Basement Level 2",
        latitude=25.0889,
        longitude=55.1458,
        criticality="CRITICAL",
        status="OPERATIONAL",
        created_at=now - timedelta(days=365),
    )
    db.add(chiller)

    # Secondary Asset for multi-asset queries
    pump = Asset(
        asset_id="PUMP-DOWNTOWN-202",
        name="Cooling Water Booster Pump 2",
        asset_type="WATER_PUMP",
        location="Downtown Facility Room 4",
        latitude=25.1972,
        longitude=55.2744,
        criticality="HIGH",
        status="OPERATIONAL",
        created_at=now - timedelta(days=200),
    )
    db.add(pump)
    db.flush()

    # 2. Telemetry records for CHILLER-MARINA-101
    t1 = Telemetry(
        asset_id="CHILLER-MARINA-101",
        timestamp=now - timedelta(hours=2),
        vibration_rms=4.10,
        bearing_temperature=84.2,
        coolant_pressure=3.2,
        power_kw=41.5,
        operating_hours=14198.0,
    )
    t2 = Telemetry(
        asset_id="CHILLER-MARINA-101",
        timestamp=now,
        vibration_rms=4.82,
        bearing_temperature=88.5,
        coolant_pressure=3.1,
        power_kw=42.0,
        operating_hours=14200.0,
    )
    db.add_all([t1, t2])

    # 3. Maintenance history
    m1 = Maintenance(
        asset_id="CHILLER-MARINA-101",
        serviced_at=now - timedelta(days=90),
        past_failures_count=2,
        notes="Q2 quarterly maintenance. Slight vibration increase logged.",
    )
    db.add(m1)

    # 4. Inventory Spare Parts
    parts = [
        Inventory(
            part_id="PART-BRG-7701",
            part_name="Ceramic Ball Bearing Assembly",
            category="Bearings",
            current_stock=2,
            minimum_stock=3,
            lead_time=4,
            unit_cost=450.00,
            supplier="SKF Industrial Middle East",
            asset_type="HVAC_CHILLER",
        ),
        Inventory(
            part_id="PART-CMP-402",
            part_name="Scroll Compressor Valve Kit",
            category="Compressors",
            current_stock=5,
            minimum_stock=2,
            lead_time=7,
            unit_cost=820.00,
            supplier="Carrier Commercial Service",
            asset_type="HVAC_CHILLER",
        ),
        Inventory(
            part_id="PART-SEN-108",
            part_name="Piezoelectric Vibration Sensor",
            category="Sensors",
            current_stock=8,
            minimum_stock=4,
            lead_time=2,
            unit_cost=120.00,
            supplier="Honeywell Automation",
            asset_type="HVAC_CHILLER",
        ),
        Inventory(
            part_id="PART-SEAL-901",
            part_name="Mechanical Shaft Seal Kit",
            category="Seals",
            current_stock=1,
            minimum_stock=3,
            lead_time=3,
            unit_cost=95.00,
            supplier="Flowserve Corp",
            asset_type="WATER_PUMP",
        ),
    ]
    db.add_all(parts)

    # 5. Field Technicians
    techs = [
        Technician(
            technician_id="TECH-DXB-01",
            name="Ahmed Mansoor",
            skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL", "VIBRATION_ANALYSIS"],
            certifications=["EPA_UNIVERSAL", "CAT_IV_VIBRATION"],
            experience=8.5,
            current_latitude=25.0772,  # ~1.8 km from Marina 101
            current_longitude=55.1325,
            availability=True,
            status="AVAILABLE",
        ),
        Technician(
            technician_id="TECH-DXB-02",
            name="Rashid Al-Falasi",
            skills=["HVAC_CERTIFIED", "ELECTRICAL_DIAGNOSTICS"],
            certifications=["EPA_UNIVERSAL"],
            experience=5.0,
            current_latitude=25.1120,  # ~6.5 km from Marina 101
            current_longitude=55.2010,
            availability=True,
            status="AVAILABLE",
        ),
        Technician(
            technician_id="TECH-DXB-03",
            name="Vikram Mehta",
            skills=["HVAC_CERTIFIED", "BEARING_OVERHAUL", "COMPRESSOR_REPAIR"],
            certifications=["EPA_UNIVERSAL", "ISO_VIBRATION_CAT3"],
            experience=12.0,
            current_latitude=25.1972,  # Downtown Dubai (~20 km)
            current_longitude=55.2744,
            availability=False,  # Currently on active work order
            status="ON_DUTY",
        ),
        Technician(
            technician_id="TECH-DXB-04",
            name="Carlos Santos",
            skills=["PLUMBING", "PIPE_FITTING"],
            certifications=["SAFETY_OSHA"],
            experience=4.0,
            current_latitude=25.0800,  # ~1.2 km from Marina 101
            current_longitude=55.1400,
            availability=True,
            status="AVAILABLE",
        ),
    ]
    db.add_all(techs)

    db.commit()
