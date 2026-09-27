from app.core.config import get_settings
from app.db.database import Database
from app.inspections.repository import InspectionRepository
from app.inspections.schemas import InspectionCreate


SEED_DATA = [
    {
        "vehicle_id": "CAR-1001", "make": "Hyundai", "model": "Creta", "year": 2021,
        "odometer_km": 42500, "inspector": "Asha Mehta", "decision": "approved",
        "notes": "Road test passed. Routine servicing recommended.",
        "issues": [{"category": "tyres", "component": "Front tyres", "severity": "minor",
                    "description": "Tread approaching replacement threshold", "repair_cost": 12000}],
    },
    {
        "vehicle_id": "CAR-1002", "make": "Tata", "model": "Nexon", "year": 2019,
        "odometer_km": 78500, "inspector": "Vikram Singh", "decision": "rejected",
        "notes": "Unsafe to retail until powertrain defects are repaired.",
        "issues": [
            {"category": "engine", "component": "Cylinder head", "severity": "critical",
             "description": "Coolant mixing with engine oil; probable head-gasket failure", "repair_cost": 68000},
            {"category": "brakes", "component": "Rear brake discs", "severity": "major",
             "description": "Discs below service thickness", "repair_cost": 18000},
        ],
    },
    {
        "vehicle_id": "CAR-1003", "make": "Maruti Suzuki", "model": "Baleno", "year": 2022,
        "odometer_km": 21900, "inspector": "Asha Mehta", "decision": "review",
        "notes": "Body repair history requires document verification.",
        "issues": [{"category": "body", "component": "Left quarter panel", "severity": "major",
                    "description": "Structural repair and repaint detected", "repair_cost": 35000}],
    },
    {
        "vehicle_id": "CAR-1004", "make": "Honda", "model": "City", "year": 2018,
        "odometer_km": 91000, "inspector": "Neeraj Rao", "decision": "rejected",
        "notes": "Transmission repair cost exceeds acquisition threshold.",
        "issues": [{"category": "transmission", "component": "CVT assembly", "severity": "critical",
                    "description": "Severe judder and metallic debris in fluid", "repair_cost": 125000}],
    },
    {
        "vehicle_id": "CAR-1005", "make": "Mahindra", "model": "XUV300", "year": 2020,
        "odometer_km": 56300, "inspector": "Neeraj Rao", "decision": "approved",
        "notes": "Approved after battery replacement.",
        "issues": [{"category": "electrical", "component": "Battery", "severity": "minor",
                    "description": "Low cold-cranking performance", "repair_cost": 7500}],
    },
]


def main() -> None:
    database = Database(get_settings().database_path)
    database.initialize()
    repository = InspectionRepository(database)
    if repository.search({}, limit=1):
        print("Database already contains inspections; seed skipped.")
        return
    for raw in SEED_DATA:
        repository.create(InspectionCreate.model_validate(raw))
    print(f"Seeded {len(SEED_DATA)} vehicle inspections.")


if __name__ == "__main__":
    main()
