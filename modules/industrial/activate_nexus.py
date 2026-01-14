import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. SETUP PATHS
sys.path.append(os.getcwd())
from modules.industrial.models import Base, IndustrialOrigin

def activate_industrial_nexus():
    print("\n🏭 INITIATING INDUSTRIAL NEXUS ACTIVATION...")
    
    # 2. CONNECT TO REALITY (Hardcoded Path for Safety)
    db_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    if not os.path.exists(db_path):
        print(f"❌ CRITICAL: Database not found at {db_path}")
        return

    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f"   > Connected to Cortex Core.")

    # 3. DEPLOY ARCHITECTURE
    print("   > Deploying Industrial Tables...")
    Base.metadata.create_all(engine)

    # 4. MIGRATE SEED DATA (Your Hardcoded List)
    print("   > Migrating Origin Registry Data...")
    
    # This is the exact data from your screenshot
    seed_data = [
        {"name": "PPC Cement Hercules", "type": "Factory", "location": "Pretoria West", "product": "Cement (CEM II)", "capacity": 45000},
        {"name": "NPC Cimpor", "type": "Factory", "location": "Durban / Siyaya", "product": "Cement (Surebuild)", "capacity": 30000},
        {"name": "Sturrock & Robson", "type": "Warehouse", "location": "East Rand", "product": "Industrial Components", "capacity": 5000},
        {"name": "Durban Paints", "type": "Factory", "location": "Mobeni KZN", "product": "Paints & Solvents", "capacity": 12000},
        {"name": "Khwezela Colliery", "type": "Mine", "location": "Emalahleni", "product": "Thermal Coal (RB1)", "capacity": 60000},
    ]

    count = 0
    for item in seed_data:
        # Check if exists to avoid duplicates
        exists = session.query(IndustrialOrigin).filter_by(name=item['name']).first()
        if not exists:
            new_origin = IndustrialOrigin(
                name=item['name'],
                type=item['type'],
                location=item['location'],
                product=item['product'],
                capacity=item['capacity'],
                contract_status='Active'
            )
            session.add(new_origin)
            count += 1
    
    session.commit()
    print(f"   > Successfully Onboarded {count} Origins.")
    print("\n✅ INDUSTRIAL NEXUS ONLINE.")

if __name__ == "__main__":
    activate_industrial_nexus()
