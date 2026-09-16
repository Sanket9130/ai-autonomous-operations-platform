"""
Synthetic Dubai Facility-Management Demonstration Dataset Generator.
Provides realistic, deterministic synthetic FM operational data across major Dubai zones.

NOTE:
This dataset is strictly synthetic demonstration data generated for product evaluation
and pitching to Dubai facility management / property management operators.
No records represent real customer operational data or proprietary facility information.
"""

import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.asset import Asset
from backend.app.models.telemetry import Telemetry
from backend.app.models.inventory import Inventory
from backend.app.models.technician import Technician
from backend.app.models.maintenance import Maintenance
from backend.app.models.work_order import WorkOrder


# Synthetic Dubai Zones and Geographic Hubs
DUBAI_FACILITIES = [
    # (Zone Name, Facility Name, Latitude, Longitude)
    ("DOWNTOWN", "Downtown Business Tower A", 25.1972, 55.2744),
    ("DOWNTOWN", "Downtown Plaza Mixed-Use Complex", 25.1950, 55.2780),
    ("DOWNTOWN", "Boulevard Financial Center", 25.2010, 55.2720),
    ("MARINA", "Dubai Marina 101 Tower", 25.0889, 55.1458),
    ("MARINA", "Marina Waterfront Heights", 25.0820, 55.1410),
    ("MARINA", "Marina Hospitality Center", 25.0760, 55.1330),
    ("DIFC", "DIFC Gate Precinct", 25.2048, 55.2708),
    ("DIFC", "DIFC Fintech Plaza", 25.2085, 55.2755),
    ("DIFC", "DIFC Commercial Center A", 25.2120, 55.2810),
    ("BUSINESS_BAY", "Business Bay Executive Tower", 25.1837, 55.2665),
    ("BUSINESS_BAY", "Business Bay Mixed Use Tower", 25.1870, 55.2620),
    ("BUSINESS_BAY", "Bay View Commercial Hub", 25.1810, 55.2690),
    ("JUMEIRAH", "Jumeirah Coastal Resort", 25.1412, 55.1853),
    ("JUMEIRAH", "Jumeirah Community Center", 25.1480, 55.1920),
    ("JLT", "JLT Corporate Plaza Tower 1", 25.0754, 55.1458),
    ("JLT", "JLT Commercial Tower 2", 25.0720, 55.1420),
    ("SILICON_OASIS", "Silicon Oasis Technology Park", 25.1224, 55.3776),
    ("SILICON_OASIS", "Silicon Tech Center Phase 2", 25.1260, 55.3810),
    ("HEALTHCARE_CITY", "Healthcare District Facility A", 25.2345, 55.3218),
    ("HEALTHCARE_CITY", "Medical Science Center B", 25.2380, 55.3250),
    ("AL_QUOZ", "Al Quoz Operations Center", 25.1432, 55.2389),
    ("AL_QUOZ", "Al Quoz Industrial Logistics Hub", 25.1390, 55.2340),
    ("DEIRA", "Deira Commerce Tower", 25.2697, 55.3095),
    ("DEIRA", "Deira Central Plaza", 25.2650, 55.3120),
    ("BUR_DUBAI", "Bur Dubai Administrative Center", 25.2532, 55.2974),
    ("BUR_DUBAI", "Heritage Business Center", 25.2500, 55.2930),
    ("DIP", "Dubai Investment Park Warehouse Hub", 24.9925, 55.1824),
    ("DIP", "DIP Logistics Park Facility 4", 24.9880, 55.1790),
    ("FESTIVAL_CITY", "Festival City Corporate Center", 25.2223, 55.3512),
    ("DUBAI_HILLS", "Dubai Hills Residential Complex", 25.1158, 55.2476),
    ("DUBAI_HILLS", "Dubai Hills Executive Suites", 25.1190, 55.2510),
    ("PALM_JUMEIRAH", "Palm Jumeirah Resort", 25.1124, 55.1390),
    ("PALM_JUMEIRAH", "Palm Seaside Residences", 25.1180, 55.1350),
]


def seed_database(db: Session):
    """
    Seeds complete synthetic Dubai FM operational dataset.
    Deterministic execution via fixed seed (42).
    Preserves existing key demo assets and test expectations.
    """
    now = datetime.now(timezone.utc)
    rng = random.Random(42)

    # =========================================================================
    # 1. INVENTORY: 50 Spare Parts (8 preserved baseline + 42 synthetic)
    # =========================================================================
    inventory_data: List[Dict[str, Any]] = [
        # Preserved baseline parts
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
        # 42 Additional synthetic Dubai FM parts
        {
            "part_id": "PART-HVAC-EXV-02",
            "part_name": "Thermostatic Expansion Valve TE5",
            "category": "HVAC_COMPONENTS",
            "current_stock": 4,
            "minimum_stock": 6,
            "lead_time": 10,
            "unit_cost": 620.00,
            "supplier": "Danfoss Middle East",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-HVAC-FLT-01",
            "part_name": "Liquid Line Filter Drier DCL 305",
            "category": "FILTRATION",
            "current_stock": 18,
            "minimum_stock": 8,
            "lead_time": 4,
            "unit_cost": 145.00,
            "supplier": "Emerson Commercial",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-HVAC-CMP-02",
            "part_name": "Screw Compressor Overhaul Gasket Set",
            "category": "Compressors",
            "current_stock": 2,
            "minimum_stock": 2,
            "lead_time": 12,
            "unit_cost": 1150.00,
            "supplier": "Bitzer Middle East",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-HVAC-OIL-01",
            "part_name": "Polyolester Refrigerant Lubricant 5L",
            "category": "CONSUMABLES",
            "current_stock": 12,
            "minimum_stock": 6,
            "lead_time": 3,
            "unit_cost": 280.00,
            "supplier": "Mobil Industrial Lubricants",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-HVAC-PRX-01",
            "part_name": "Dual High/Low Pressure Switch",
            "category": "Sensors",
            "current_stock": 6,
            "minimum_stock": 4,
            "lead_time": 5,
            "unit_cost": 190.00,
            "supplier": "Johnson Controls Middle East",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-HVAC-VLV-01",
            "part_name": "3-Way Modulating Water Valve DN65",
            "category": "Valves",
            "current_stock": 3,
            "minimum_stock": 3,
            "lead_time": 9,
            "unit_cost": 890.00,
            "supplier": "Belimo Controls UAE",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-HVAC-SEN-02",
            "part_name": "Chilled Water Immersion Temp Sensor",
            "category": "Sensors",
            "current_stock": 14,
            "minimum_stock": 5,
            "lead_time": 2,
            "unit_cost": 135.00,
            "supplier": "Siemens Building Technologies",
            "asset_type": "HVAC_CHILLER",
        },
        {
            "part_id": "PART-AHU-BLT-01",
            "part_name": "Heavy-Duty Cogged V-Belt B68",
            "category": "Mechanical",
            "current_stock": 24,
            "minimum_stock": 10,
            "lead_time": 2,
            "unit_cost": 65.00,
            "supplier": "Gates Middle East",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-AHU-MTR-01",
            "part_name": "7.5kW Premium Efficiency IE3 Motor",
            "category": "Motors",
            "current_stock": 1,
            "minimum_stock": 2,
            "lead_time": 14,
            "unit_cost": 2100.00,
            "supplier": "ABB UAE",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-AHU-ACT-01",
            "part_name": "Air Damper Spring Return Actuator 20Nm",
            "category": "Actuators",
            "current_stock": 7,
            "minimum_stock": 4,
            "lead_time": 4,
            "unit_cost": 410.00,
            "supplier": "Belimo Controls UAE",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-AHU-PRE-01",
            "part_name": "Pleated Panel Pre-Filter G4 24x24x2",
            "category": "FILTRATION",
            "current_stock": 60,
            "minimum_stock": 30,
            "lead_time": 2,
            "unit_cost": 42.00,
            "supplier": "Camfil Middle East",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-AHU-BAG-01",
            "part_name": "Synthetic Pocket Bag Filter F7",
            "category": "FILTRATION",
            "current_stock": 32,
            "minimum_stock": 15,
            "lead_time": 3,
            "unit_cost": 95.00,
            "supplier": "AAF International ME",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-AHU-PUL-01",
            "part_name": "Cast Iron Dual-Groove Drive Pulley",
            "category": "Mechanical",
            "current_stock": 6,
            "minimum_stock": 3,
            "lead_time": 5,
            "unit_cost": 160.00,
            "supplier": "Fenner Power Transmission",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-AHU-SEN-01",
            "part_name": "Duct Static Differential Pressure Transmitter",
            "category": "Sensors",
            "current_stock": 9,
            "minimum_stock": 4,
            "lead_time": 3,
            "unit_cost": 210.00,
            "supplier": "Dwyer Instruments ME",
            "asset_type": "AHU",
        },
        {
            "part_id": "PART-FCU-MTR-01",
            "part_name": "3-Speed Fan Coil Motor 120W",
            "category": "Motors",
            "current_stock": 11,
            "minimum_stock": 6,
            "lead_time": 4,
            "unit_cost": 320.00,
            "supplier": "Ebm-papst Middle East",
            "asset_type": "FCU",
        },
        {
            "part_id": "PART-FCU-VLV-01",
            "part_name": "2-Way Fan Coil Zone Valve 1/2-Inch",
            "category": "Valves",
            "current_stock": 20,
            "minimum_stock": 10,
            "lead_time": 3,
            "unit_cost": 175.00,
            "supplier": "Honeywell Middle East",
            "asset_type": "FCU",
        },
        {
            "part_id": "PART-FCU-FLT-01",
            "part_name": "Washable Aluminum Mesh Filter",
            "category": "FILTRATION",
            "current_stock": 50,
            "minimum_stock": 25,
            "lead_time": 1,
            "unit_cost": 28.00,
            "supplier": "Universal Filter Gulf",
            "asset_type": "FCU",
        },
        {
            "part_id": "PART-FCU-THM-01",
            "part_name": "BACnet Modulating Room Thermostat",
            "category": "Controls",
            "current_stock": 8,
            "minimum_stock": 5,
            "lead_time": 5,
            "unit_cost": 240.00,
            "supplier": "Johnson Controls Middle East",
            "asset_type": "FCU",
        },
        {
            "part_id": "PART-CT-NOZ-01",
            "part_name": "Cooling Tower Spray Distribution Nozzle",
            "category": "Plumbing",
            "current_stock": 35,
            "minimum_stock": 20,
            "lead_time": 3,
            "unit_cost": 45.00,
            "supplier": "SPX Marley ME",
            "asset_type": "COOLING_TOWER",
        },
        {
            "part_id": "PART-CT-BLT-01",
            "part_name": "Cooling Tower Fan Drive Poly-V Belt",
            "category": "Mechanical",
            "current_stock": 8,
            "minimum_stock": 4,
            "lead_time": 4,
            "unit_cost": 185.00,
            "supplier": "Optibelt ME",
            "asset_type": "COOLING_TOWER",
        },
        {
            "part_id": "PART-CT-DRV-01",
            "part_name": "Right-Angle Fan Reduction Gearbox",
            "category": "Gearbox",
            "current_stock": 1,
            "minimum_stock": 1,
            "lead_time": 21,
            "unit_cost": 5400.00,
            "supplier": "Amarillo Gear Company",
            "asset_type": "COOLING_TOWER",
        },
        {
            "part_id": "PART-PMP-IMP-01",
            "part_name": "Bronze Centrifugal Pump Impeller 200mm",
            "category": "Hydraulics",
            "current_stock": 2,
            "minimum_stock": 2,
            "lead_time": 10,
            "unit_cost": 750.00,
            "supplier": "Grundfos Gulf",
            "asset_type": "WATER_PUMP",
        },
        {
            "part_id": "PART-PMP-SEL-02",
            "part_name": "Silicon Carbide Cartridge Mechanical Seal",
            "category": "Seals",
            "current_stock": 5,
            "minimum_stock": 4,
            "lead_time": 5,
            "unit_cost": 310.00,
            "supplier": "EagleBurgmann Middle East",
            "asset_type": "WATER_PUMP",
        },
        {
            "part_id": "PART-PMP-BRG-01",
            "part_name": "Double-Row Angular Contact Pump Bearing",
            "category": "Bearings",
            "current_stock": 6,
            "minimum_stock": 3,
            "lead_time": 4,
            "unit_cost": 260.00,
            "supplier": "NSK Bearings Gulf",
            "asset_type": "WATER_PUMP",
        },
        {
            "part_id": "PART-PMP-CPG-01",
            "part_name": "Flexible Elastomer Coupling Insert",
            "category": "Mechanical",
            "current_stock": 14,
            "minimum_stock": 6,
            "lead_time": 2,
            "unit_cost": 90.00,
            "supplier": "Rexnord Middle East",
            "asset_type": "WATER_PUMP",
        },
        {
            "part_id": "PART-PMP-MTR-01",
            "part_name": "15kW Submersible Pump Drive Motor",
            "category": "Motors",
            "current_stock": 1,
            "minimum_stock": 1,
            "lead_time": 14,
            "unit_cost": 3400.00,
            "supplier": "Siemens UAE",
            "asset_type": "WATER_PUMP",
        },
        {
            "part_id": "PART-ELEC-CNT-01",
            "part_name": "3-Pole 40A Heavy Duty Magnetic Contactor",
            "category": "Electrical",
            "current_stock": 16,
            "minimum_stock": 8,
            "lead_time": 2,
            "unit_cost": 110.00,
            "supplier": "Schneider Electric UAE",
            "asset_type": "ELECTRICAL_PANEL",
        },
        {
            "part_id": "PART-ELEC-RLY-01",
            "part_name": "Electronic Thermal Overload Relay 18-25A",
            "category": "Electrical",
            "current_stock": 9,
            "minimum_stock": 4,
            "lead_time": 3,
            "unit_cost": 145.00,
            "supplier": "Siemens Sirius ME",
            "asset_type": "ELECTRICAL_PANEL",
        },
        {
            "part_id": "PART-ELEC-BRK-01",
            "part_name": "Molded Case Circuit Breaker 250A 3P",
            "category": "Electrical",
            "current_stock": 3,
            "minimum_stock": 2,
            "lead_time": 7,
            "unit_cost": 1450.00,
            "supplier": "ABB SACE Middle East",
            "asset_type": "ELECTRICAL_PANEL",
        },
        {
            "part_id": "PART-ELEC-CAP-01",
            "part_name": "Power Factor Correction Capacitor 25kVAR",
            "category": "Electrical",
            "current_stock": 7,
            "minimum_stock": 3,
            "lead_time": 5,
            "unit_cost": 380.00,
            "supplier": "Epcos TDK Middle East",
            "asset_type": "ELECTRICAL_PANEL",
        },
        {
            "part_id": "PART-ELEC-FUS-01",
            "part_name": "High-Rupture Capacity Industrial Fuse 100A",
            "category": "Electrical",
            "current_stock": 25,
            "minimum_stock": 10,
            "lead_time": 1,
            "unit_cost": 35.00,
            "supplier": "Bussmann Eaton ME",
            "asset_type": "ELECTRICAL_PANEL",
        },
        {
            "part_id": "PART-ELEC-VFD-01",
            "part_name": "VFD Cooling Fan Internal Assembly",
            "category": "Electronics",
            "current_stock": 5,
            "minimum_stock": 3,
            "lead_time": 6,
            "unit_cost": 290.00,
            "supplier": "Danfoss Drives UAE",
            "asset_type": "ELECTRICAL_PANEL",
        },
        {
            "part_id": "PART-UPS-BAT-01",
            "part_name": "Sealed Lead-Acid VRLA Battery 12V 100Ah",
            "category": "Batteries",
            "current_stock": 12,
            "minimum_stock": 8,
            "lead_time": 5,
            "unit_cost": 650.00,
            "supplier": "CSB Battery Middle East",
            "asset_type": "UPS",
        },
        {
            "part_id": "PART-UPS-FAN-01",
            "part_name": "High-CFM Server UPS Exhaust Fan 120mm",
            "category": "Electronics",
            "current_stock": 10,
            "minimum_stock": 4,
            "lead_time": 2,
            "unit_cost": 85.00,
            "supplier": "Sanyo Denki Gulf",
            "asset_type": "UPS",
        },
        {
            "part_id": "PART-GEN-FLT-01",
            "part_name": "Heavy Diesel Fuel/Water Separator Filter",
            "category": "FILTRATION",
            "current_stock": 14,
            "minimum_stock": 6,
            "lead_time": 3,
            "unit_cost": 125.00,
            "supplier": "Fleetguard Middle East",
            "asset_type": "GENERATOR",
        },
        {
            "part_id": "PART-GEN-OIL-01",
            "part_name": "High-Capacity Spin-On Engine Lube Filter",
            "category": "FILTRATION",
            "current_stock": 15,
            "minimum_stock": 6,
            "lead_time": 3,
            "unit_cost": 95.00,
            "supplier": "Donaldson Filtration ME",
            "asset_type": "GENERATOR",
        },
        {
            "part_id": "PART-GEN-BAT-01",
            "part_name": "Generator Cranking Starter Battery 12V 200Ah",
            "category": "Batteries",
            "current_stock": 4,
            "minimum_stock": 3,
            "lead_time": 4,
            "unit_cost": 890.00,
            "supplier": "Exide Middle East",
            "asset_type": "GENERATOR",
        },
        {
            "part_id": "PART-FIRE-SEL-01",
            "part_name": "UL/FM Certified Fire Pump Packing Seal",
            "category": "Life_Safety",
            "current_stock": 6,
            "minimum_stock": 3,
            "lead_time": 5,
            "unit_cost": 210.00,
            "supplier": "Patterson Pump ME",
            "asset_type": "FIRE_PUMP",
        },
        {
            "part_id": "PART-FIRE-PRS-01",
            "part_name": "Fire Sprinkler Mainline Pressure Relief Valve",
            "category": "Life_Safety",
            "current_stock": 2,
            "minimum_stock": 2,
            "lead_time": 10,
            "unit_cost": 1350.00,
            "supplier": "Cla-Val Middle East",
            "asset_type": "FIRE_PUMP",
        },
        {
            "part_id": "PART-FIRE-BAT-01",
            "part_name": "Fire Alarm Control Panel Backup Battery 24V",
            "category": "Life_Safety",
            "current_stock": 8,
            "minimum_stock": 4,
            "lead_time": 3,
            "unit_cost": 280.00,
            "supplier": "Notifier Honeywell ME",
            "asset_type": "FIRE_ALARM",
        },
        {
            "part_id": "PART-FIRE-SEN-01",
            "part_name": "Addressable Photoelectric Smoke Sensor Head",
            "category": "Life_Safety",
            "current_stock": 35,
            "minimum_stock": 15,
            "lead_time": 2,
            "unit_cost": 85.00,
            "supplier": "Simplex Middle East",
            "asset_type": "FIRE_ALARM",
        },
        {
            "part_id": "PART-ELEV-BRK-01",
            "part_name": "Heavy Elevator Traction Machine Brake Lining",
            "category": "Vertical_Transport",
            "current_stock": 3,
            "minimum_stock": 2,
            "lead_time": 8,
            "unit_cost": 1650.00,
            "supplier": "Otis Commercial Gulf",
            "asset_type": "ELEVATOR",
        },
        {
            "part_id": "PART-ELEV-RLR-01",
            "part_name": "Elevator Car Guide Shoe Roller Assembly 150mm",
            "category": "Vertical_Transport",
            "current_stock": 8,
            "minimum_stock": 4,
            "lead_time": 5,
            "unit_cost": 340.00,
            "supplier": "KONE Middle East",
            "asset_type": "ELEVATOR",
        },
        {
            "part_id": "PART-ELEV-DRV-01",
            "part_name": "Cabin Door Operator Belt & Sensor Assembly",
            "category": "Vertical_Transport",
            "current_stock": 5,
            "minimum_stock": 3,
            "lead_time": 4,
            "unit_cost": 490.00,
            "supplier": "Fermator ME",
            "asset_type": "ELEVATOR",
        },
    ]

    for inv_dict in inventory_data:
        existing_part = db.query(Inventory).filter(Inventory.part_id == inv_dict["part_id"]).first()
        if existing_part:
            for k, v in inv_dict.items():
                setattr(existing_part, k, v)
        else:
            db.add(Inventory(**inv_dict))

    db.flush()

    # =========================================================================
    # 2. TECHNICIANS: 20 Technicians (4 preserved baseline + 16 synthetic)
    # =========================================================================
    techs_data: List[Dict[str, Any]] = [
        # Preserved baseline technicians
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
        # 16 Additional synthetic technicians stationed across Dubai
        {
            "technician_id": "TECH-DXB-05",
            "name": "Tariq Al-Nuaimi",
            "skills": ["ELECTRICAL", "HIGH_VOLTAGE", "PANEL_MAINTENANCE", "TRANSFORMER_SAFETY"],
            "certifications": ["DEWA_CERTIFIED", "NFPA_70E"],
            "experience": 9.0,
            "current_latitude": 25.1837,
            "current_longitude": 55.2665,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "BUSINESS_BAY",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-06",
            "name": "Omar Al-Ketbi",
            "skills": ["HVAC_CERTIFIED", "SCREW_COMPRESSOR", "REFRIGERATION"],
            "certifications": ["EPA_UNIVERSAL"],
            "experience": 11.5,
            "current_latitude": 25.0754,
            "current_longitude": 55.1458,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "JLT",
            "active_workload": 2,
        },
        {
            "technician_id": "TECH-DXB-07",
            "name": "Joseph Fernandes",
            "skills": ["BMS", "CONTROLS_CALIBRATION", "ELECTRICAL_DIAGNOSTICS", "SENSOR_INTEGRATION"],
            "certifications": ["BACNET_PROFESSIONAL", "TRIDIUM_NIAGARA_4"],
            "experience": 8.0,
            "current_latitude": 25.2048,
            "current_longitude": 55.2708,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "DIFC",
            "active_workload": 0,
        },
        {
            "technician_id": "TECH-DXB-08",
            "name": "Zaid Farooqi",
            "skills": ["WATER_PUMP", "SHAFT_ALIGNMENT", "MECHANICAL_SEAL_OVERHAUL", "BEARING_OVERHAUL"],
            "certifications": ["ISO_VIBRATION_CAT2", "OSHA_SAFETY"],
            "experience": 7.5,
            "current_latitude": 25.1432,
            "current_longitude": 55.2389,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "AL_QUOZ",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-09",
            "name": "Fahad Al-Blooshi",
            "skills": ["FIRE_PUMP", "FIRE_ALARM", "SPRINKLER_HYDRAULICS", "LIFE_SAFETY"],
            "certifications": ["NFPA_CERTIFIED", "CIVIL_DEFENSE_APPROVED"],
            "experience": 10.0,
            "current_latitude": 25.1972,
            "current_longitude": 55.2744,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "DOWNTOWN",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-10",
            "name": "Rajesh Pillai",
            "skills": ["DIESEL_GENERATOR", "UPS_SYSTEMS", "ELECTRICAL_SWITCHGEAR", "HIGH_VOLTAGE"],
            "certifications": ["CATERPILLAR_CERTIFIED", "DEWA_APPROVED"],
            "experience": 14.0,
            "current_latitude": 24.9925,
            "current_longitude": 55.1824,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "DIP",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-11",
            "name": "Bilal Hammoud",
            "skills": ["HVAC", "AHU", "V_BELT_ALIGNMENT", "AIR_BALANCING"],
            "certifications": ["HVAC_EXCELLENCE"],
            "experience": 4.5,
            "current_latitude": 25.1158,
            "current_longitude": 55.2476,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "DUBAI_HILLS",
            "active_workload": 0,
        },
        {
            "technician_id": "TECH-DXB-12",
            "name": "Chen Wei",
            "skills": ["ELEVATOR_MAINTENANCE", "TRACTION_MACHINES", "DOOR_OPERATOR", "SAFETY_INSPECTION"],
            "certifications": ["TUV_ELEVATOR_SAFETY"],
            "experience": 13.0,
            "current_latitude": 25.2106,
            "current_longitude": 55.2801,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "DIFC",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-13",
            "name": "Salem Al-Marri",
            "skills": ["HVAC_CERTIFIED", "REFRIGERATION_CYCLE", "ELECTRICAL_DIAGNOSTICS"],
            "certifications": ["EPA_UNIVERSAL"],
            "experience": 6.0,
            "current_latitude": 25.1224,
            "current_longitude": 55.3776,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "SILICON_OASIS",
            "active_workload": 0,
        },
        {
            "technician_id": "TECH-DXB-14",
            "name": "Sunita Nair",
            "skills": ["VIBRATION_ANALYSIS", "DYNAMIC_BALANCING", "ULTRASONIC_INSPECTION", "THERMOGRAPHY"],
            "certifications": ["ISO_VIBRATION_CAT3", "LEVEL_II_THERMOGRAPHY"],
            "experience": 10.5,
            "current_latitude": 25.2345,
            "current_longitude": 55.3218,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "HEALTHCARE_CITY",
            "active_workload": 2,
        },
        {
            "technician_id": "TECH-DXB-15",
            "name": "Kevin O'Connor",
            "skills": ["HVAC_CHILLER_SPECIALIST", "CENTRIFUGAL_COMPRESSOR", "BEARING_OVERHAUL"],
            "certifications": ["CARRIER_CERTIFIED", "TRANE_CERTIFIED"],
            "experience": 15.0,
            "current_latitude": 25.2697,
            "current_longitude": 55.3095,
            "availability": False,
            "status": "OFF_DUTY",
            "current_location": "DEIRA",
            "active_workload": 0,
        },
        {
            "technician_id": "TECH-DXB-16",
            "name": "Hamdan Al-Shamsi",
            "skills": ["COOLING_TOWER", "WATER_PUMP", "PIPE_FITTING", "MECHANICAL_MAINTENANCE"],
            "certifications": ["SAFETY_OSHA"],
            "experience": 5.5,
            "current_latitude": 25.2223,
            "current_longitude": 55.3512,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "FESTIVAL_CITY",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-17",
            "name": "Arun Kumar",
            "skills": ["ELEVATOR_MAINTENANCE", "HYDRAULIC_LIFTS", "SAFETY_GEAR"],
            "certifications": ["ELEVATOR_CODE_A17"],
            "experience": 8.0,
            "current_latitude": 25.0889,
            "current_longitude": 55.1458,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "MARINA",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-18",
            "name": "Mahmoud Ghazal",
            "skills": ["UPS_SYSTEMS", "BATTERY_IMPEDANCE", "ELECTRICAL_SAFETY", "INVERTER_MAINTENANCE"],
            "certifications": ["SCHNEIDER_CERTIFIED"],
            "experience": 7.0,
            "current_latitude": 25.2532,
            "current_longitude": 55.2974,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "BUR_DUBAI",
            "active_workload": 0,
        },
        {
            "technician_id": "TECH-DXB-19",
            "name": "Ali Al-Zaabi",
            "skills": ["FIRE_PUMP", "SPRINKLER_HYDRAULICS", "PRESSURE_VESSELS"],
            "certifications": ["NFPA_20", "CIVIL_DEFENSE_APPROVED"],
            "experience": 9.5,
            "current_latitude": 25.1432,
            "current_longitude": 55.2389,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "AL_QUOZ",
            "active_workload": 1,
        },
        {
            "technician_id": "TECH-DXB-20",
            "name": "Mikhail Volkov",
            "skills": ["COOLING_TOWER", "GEAR_DRIVE", "FAN_BALANCING", "CHEMICAL_DOSING"],
            "certifications": ["CTI_CERTIFIED"],
            "experience": 6.5,
            "current_latitude": 25.1124,
            "current_longitude": 55.1390,
            "availability": True,
            "status": "AVAILABLE",
            "current_location": "PALM_JUMEIRAH",
            "active_workload": 0,
        },
    ]

    for t_dict in techs_data:
        existing_tech = db.query(Technician).filter(Technician.technician_id == t_dict["technician_id"]).first()
        if existing_tech:
            for k, v in t_dict.items():
                setattr(existing_tech, k, v)
        else:
            db.add(Technician(**t_dict))

    db.flush()

    # =========================================================================
    # 3. ASSETS: 100 Hard-FM Assets (5 preserved baseline + 95 synthetic)
    # =========================================================================
    assets_data: List[Dict[str, Any]] = [
        # Preserved baseline assets
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

    # Deterministic generation of 95 synthetic assets
    asset_configs = [
        # (asset_type, prefix, count, part_id, power_range, base_name)
        ("HVAC_CHILLER", "CHILLER-DXB", 15, "PART-BRG-7701", (60.0, 160.0), "Central Water-Cooled Chiller"),
        ("AHU", "AHU-DXB", 17, "PART-AHU-BLT-01", (15.0, 45.0), "Air Handling Unit Plant"),
        ("FCU", "FCU-DXB", 10, "PART-FCU-VLV-01", (1.2, 3.5), "Commercial Fan Coil Unit"),
        ("COOLING_TOWER", "CT-DXB", 7, "PART-CT-NOZ-01", (30.0, 75.0), "Induced Draft Cooling Tower"),
        ("WATER_PUMP", "PUMP-DXB", 11, "PART-PMP-SEL-02", (18.0, 55.0), "Secondary Chilled Water Circulation Pump"),
        ("COMPRESSOR", "COMP-DXB", 5, "PART-CMP-402", (45.0, 110.0), "Heavy Duty Screw Refrigeration Compressor"),
        ("GENERATOR", "GEN-DXB", 6, "PART-GEN-FLT-01", (120.0, 450.0), "Emergency Standby Diesel Generator"),
        ("UPS", "UPS-DXB", 5, "PART-UPS-BAT-01", (25.0, 80.0), "Online Double-Conversion Industrial UPS"),
        ("ELECTRICAL_PANEL", "PANEL-DXB", 4, "PART-ELEC-CNT-01", (10.0, 30.0), "Main Low-Voltage Distribution Switchboard"),
        ("TRANSFORMER", "XFRM-DXB", 2, "PART-ELEC-BRK-01", (15.0, 50.0), "Cast Resin Step-Down Power Transformer"),
        ("FIRE_PUMP", "FIRE-PUMP-DXB", 5, "PART-FIRE-SEL-01", (75.0, 180.0), "UL/FM Certified Main Fire Suppression Pump"),
        ("FIRE_ALARM", "FIRE-ALM-DXB", 4, "PART-FIRE-BAT-01", (0.5, 2.0), "Intelligent Addressable Fire Alarm Panel"),
        ("ELEVATOR", "ELEV-DXB", 4, "PART-ELEV-BRK-01", (22.0, 55.0), "High-Speed Passenger Traction Elevator"),
    ]

    # Target condition distribution across the 95 new assets:
    # 65% Normal (62 items), 20% Warning (19 items), 10% Degraded (10 items), 5% Critical (4 items)
    condition_deck = (
        ["NORMAL"] * 62 +
        ["WARNING"] * 19 +
        ["DEGRADED"] * 10 +
        ["CRITICAL"] * 4
    )
    rng.shuffle(condition_deck)

    # Criticality distribution:
    # 15% CRITICAL, 30% HIGH, 40% MEDIUM, 15% LOW
    crit_deck = (
        ["CRITICAL"] * 14 +
        ["HIGH"] * 29 +
        ["MEDIUM"] * 38 +
        ["LOW"] * 14
    )
    rng.shuffle(crit_deck)

    deck_idx = 0
    facility_idx = 0

    for a_type, prefix, count, default_part, power_range, base_name in asset_configs:
        for i in range(1, count + 1):
            asset_id = f"{prefix}-{i:03d}"
            condition = condition_deck[deck_idx]
            criticality = crit_deck[deck_idx]
            deck_idx += 1

            fac_zone, fac_name, fac_lat, fac_lng = DUBAI_FACILITIES[facility_idx % len(DUBAI_FACILITIES)]
            facility_idx += 1

            # Realistic sensor values according to condition
            if condition == "NORMAL":
                vib = round(rng.uniform(0.8, 2.4), 2)
                op_temp = round(rng.uniform(42.0, 62.0), 1)
                runtime = round(rng.uniform(1200.0, 4800.0), 1)
                maint_days = rng.randint(8, 45)
                status_str = "OPERATIONAL"
            elif condition == "WARNING":
                vib = round(rng.uniform(2.5, 4.4), 2)
                op_temp = round(rng.uniform(63.0, 74.0), 1)
                runtime = round(rng.uniform(4900.0, 7200.0), 1)
                maint_days = rng.randint(45, 75)
                status_str = "OPERATIONAL"
            elif condition == "DEGRADED":
                vib = round(rng.uniform(4.5, 6.4), 2)
                op_temp = round(rng.uniform(75.0, 82.0), 1)
                runtime = round(rng.uniform(7300.0, 9500.0), 1)
                maint_days = rng.randint(75, 110)
                status_str = "DEGRADED"
            else:  # CRITICAL
                vib = round(rng.uniform(6.5, 8.8), 2)
                op_temp = round(rng.uniform(83.0, 93.0), 1)
                runtime = round(rng.uniform(9600.0, 14000.0), 1)
                maint_days = rng.randint(110, 160)
                status_str = "FAILURE_RISK" if rng.random() > 0.3 else "DEGRADED"

            ambient = round(rng.uniform(36.0, 47.0), 1)
            power = round(rng.uniform(power_range[0], power_range[1]), 1)
            created_days_ago = rng.randint(120, 500)

            assets_data.append({
                "asset_id": asset_id,
                "name": f"{fac_name} - {base_name} #{i}",
                "asset_type": a_type,
                "location": f"{fac_name}, {fac_zone}",
                "latitude": round(fac_lat + rng.uniform(-0.003, 0.003), 4),
                "longitude": round(fac_lng + rng.uniform(-0.003, 0.003), 4),
                "criticality": criticality,
                "status": status_str,
                "vibration_mm_s": vib,
                "operating_temp_c": op_temp,
                "ambient_temp_c": ambient,
                "power_kw": power,
                "runtime_hours": runtime,
                "last_maintenance_days": maint_days,
                "required_spare_part_id": default_part,
                "created_at": now - timedelta(days=created_days_ago),
            })

    for a_dict in assets_data:
        existing_asset = db.query(Asset).filter(Asset.asset_id == a_dict["asset_id"]).first()
        if existing_asset:
            for k, v in a_dict.items():
                setattr(existing_asset, k, v)
        else:
            db.add(Asset(**a_dict))

    db.flush()

    # =========================================================================
    # 4. TELEMETRY: Stream readings for all 100 assets
    # =========================================================================
    # Preserve exact baseline telemetry for key demo assets
    baseline_telem = [
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

    for bt in baseline_telem:
        existing = (
            db.query(Telemetry)
            .filter(
                Telemetry.asset_id == bt["asset_id"],
                Telemetry.vibration_rms == bt["vibration_rms"],
            )
            .first()
        )
        if not existing:
            db.add(Telemetry(**bt))

    # Add telemetry streams for remaining assets
    for a in assets_data:
        if a["asset_id"] in ["CHILLER-MARINA-101", "CHILLER-DIFC-002"]:
            continue
        existing_t = db.query(Telemetry).filter(Telemetry.asset_id == a["asset_id"]).first()
        if not existing_t:
            db.add(Telemetry(
                asset_id=a["asset_id"],
                timestamp=now - timedelta(minutes=rng.randint(2, 60)),
                vibration_rms=float(a["vibration_mm_s"] or 1.5),
                bearing_temperature=float(a["operating_temp_c"] or 55.0),
                coolant_pressure=round(rng.uniform(2.8, 4.5), 1),
                power_kw=float(a["power_kw"] or 35.0),
                operating_hours=float(a["runtime_hours"] or 3000.0),
            ))

    db.flush()

    # =========================================================================
    # 5. MAINTENANCE: 110+ Records (2 baseline preserved + 108 synthetic)
    # =========================================================================
    # Preserve baseline maintenance records
    existing_m1 = db.query(Maintenance).filter(Maintenance.asset_id == "CHILLER-MARINA-101").first()
    if not existing_m1:
        db.add(
            Maintenance(
                asset_id="CHILLER-MARINA-101",
                serviced_at=now - timedelta(days=90),
                past_failures_count=2,
                notes="Q2 quarterly maintenance. Slight vibration increase logged.",
            )
        )

    existing_m2 = db.query(Maintenance).filter(Maintenance.asset_id == "CHILLER-DIFC-002").first()
    if not existing_m2:
        db.add(
            Maintenance(
                asset_id="CHILLER-DIFC-002",
                serviced_at=now - timedelta(days=10),
                past_failures_count=0,
                notes="Routine quarterly check passed.",
            )
        )

    maintenance_notes_templates = [
        "Quarterly preventive maintenance completed. Filter change and electrical inspection passed.",
        "Routine dynamic balance check and lubricant replenishment completed.",
        "Semi-annual statutory safety valve certification and pressure test passed.",
        "Drive belt alignment calibrated; motor thermal profile within manufacturer envelope.",
        "Replaced mechanical seal and conducted leak integrity inspection.",
        "Emergency corrective service: bearing vibration damper tightened and calibrated.",
        "Full seasonal summer prep inspection; cooling coil chemical flush performed.",
        "Annual infrared thermography scan of electrical connections completed with zero hot spots.",
        "Replaced worn suction expansion valve and verified superheat delta.",
        "Routine lubrication of bearings and check of safety interlocks.",
    ]

    existing_maint_count = db.query(Maintenance).count()
    if existing_maint_count < 110:
        for idx, a in enumerate(assets_data):
            # Generate 1 or 2 historical maintenance records per asset
            recs_for_asset = 2 if idx < 15 else 1
            for r in range(recs_for_asset):
                days_ago = a["last_maintenance_days"] + (r * rng.randint(60, 120))
                db.add(
                    Maintenance(
                        asset_id=a["asset_id"],
                        serviced_at=now - timedelta(days=max(5, days_ago)),
                        past_failures_count=rng.choice([0, 0, 0, 1, 1, 2]),
                        notes=rng.choice(maintenance_notes_templates),
                    )
                )

    db.flush()

    # =========================================================================
    # 6. WORK ORDERS: 110+ Records (Routine & historical operational dispatch)
    # =========================================================================
    existing_wo_count = db.query(WorkOrder).count()
    if existing_wo_count < 110:
        wo_statuses = ["COMPLETED"] * 55 + ["IN_PROGRESS"] * 25 + ["ASSIGNED"] * 18 + ["OPEN"] * 12
        wo_priorities = ["CRITICAL"] * 15 + ["HIGH"] * 35 + ["MEDIUM"] * 45 + ["LOW"] * 15

        for i in range(1, 115):
            wo_id = f"WO-DXB-{i:04d}"
            target_asset = assets_data[(i - 1) % len(assets_data)]
            assigned_tech = techs_data[(i - 1) % len(techs_data)] if i <= 98 else None
            status_choice = wo_statuses[(i - 1) % len(wo_statuses)]
            priority_choice = wo_priorities[(i - 1) % len(wo_priorities)]

            created_days = rng.randint(1, 120) if status_choice == "COMPLETED" else rng.randint(0, 3)
            created_time = now - timedelta(days=created_days, hours=rng.randint(1, 8))
            sla_hours = 2.0 if priority_choice == "CRITICAL" else (4.0 if priority_choice == "HIGH" else 8.0)
            sla_deadline = created_time + timedelta(hours=sla_hours)

            notes_msg = (
                f"Synthetic routine work order #{i} for {target_asset['name']}. "
                f"Status: {status_choice}."
            )

            existing_wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
            if not existing_wo:
                db.add(WorkOrder(
                    id=wo_id,
                    operation_id=None,
                    asset_id=target_asset["asset_id"],
                    technician_id=assigned_tech["technician_id"] if assigned_tech else None,
                    status=status_choice,
                    priority=priority_choice,
                    notes=notes_msg,
                    created_at=created_time,
                    sla_deadline=sla_deadline,
                ))

    db.commit()
