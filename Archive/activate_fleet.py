import sys
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Setup path
sys.path.append(os.getcwd())
# Imports from the MERGED models.py file
from modules.logistics.models import Base, Vehicle

def activate_logistics_engine():
    print("\n🚛 ACTIVATING LOGISTICS COMMAND...")
    
    # 1. Connect to Cortex DB
    # Using the absolute path to ensure connection to the Live Kernel
    db_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # 2. Build Tables (Safe Mode)
    # This will create 'log_vehicles' and 'log_trips' if they don't exist
    Base.metadata.create_all(engine)
    print("   > Fleet Tables Deployed.")

    # 3. MIGRATE BASELINE DATA
    # Preserving the specific legacy fleet from your baseline models.py
    legacy_fleet = [
        {"reg": "TRK-001 (Interlink)", "make": "Scania R500", "type": "Interlink", "fuel": 38.0, "status": "Active", "driver": "J. Sithole", "loc": "En Route (N3)"},
        {"reg": "TRK-002 (Tautliner)", "make": "Volvo FH16", "type": "Tautliner", "fuel": 36.5, "status": "Idle", "driver": "M. Nkosi", "loc": "Depot (JHB)"},
        {"reg": "TRK-003 (Flatbed)", "make": "MAN TGS", "type": "Flatbed", "fuel": 32.0, "status": "Delayed", "driver": "S. Naidoo", "loc": "Durban Port"},
        {"reg": "TRK-004 (Tipper)", "make": "Mercedes Actros", "type": "Tipper", "fuel": 42.0, "status": "Active", "driver": "P. Botha", "loc": "Richards Bay"},
    ]

    count = 0
    for truck in legacy_fleet:
        # Check if truck exists to prevent duplicates (Idempotency)
        exists = session.query(Vehicle).filter_by(reg_number=truck['reg']).first()
        if not exists:
            new_truck = Vehicle(
                reg_number=truck['reg'],
                make=truck['make'],
                type=truck['type'],
                fuel_rating=truck['fuel'],
                status=truck['status'],
                driver_name=truck['driver'],
                location=truck['loc']
            )
            session.add(new_truck)
            count += 1
    
    session.commit()
    print(f"   > Data Migration Complete: {count} Vehicles Onboarded.")
    print("✅ LOGISTICS ENGINE ONLINE.")

if __name__ == "__main__":
    activate_logistics_engine()
