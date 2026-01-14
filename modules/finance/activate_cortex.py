import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. SETUP PATHS
sys.path.append(os.getcwd())

# 2. IMPORT THE NEW BRAIN
from modules.finance.models import Base, Client
from modules.finance.settlement import SettlementEngine

def activate_system():
    print("\n⚠️  INITIATING MAGISTERIAL CORTEX ACTIVATION sequence...")
    
    # 3. CONNECT TO REALITY (The Live Database)
    # We are connecting to the actual file on your disk now.
    db_path = 'sqlite:///cortex_live.db'
    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f"   > Connected to: {db_path}")

    # 4. DEPLOY ARCHITECTURE (Create Tables)
    # This checks if the new tables exist. If not, it builds them.
    print("   > Deploying SQL Tables (Invoices, Clients, Ledger)...")
    Base.metadata.create_all(engine)
    print("   > Architecture: STABLE")

    # 5. ONBOARD CLIENT
    client_id = "ORION_ENERGY"
    existing_client = session.query(Client).filter_by(id=client_id).first()
    
    if not existing_client:
        print(f"   > Onboarding Client: {client_id}...")
        new_client = Client(
            id=client_id, 
            name="Orion Energy Ltd.", 
            credit_limit=1500000.00, # R 1.5m Limit
            current_debt=0.00
        )
        session.add(new_client)
        session.commit()
    else:
        print(f"   > Client {client_id} already exists.")

    # 6. LIVE FIRE TEST (The Transaction)
    print("   > Injecting Live Transaction...")
    cortex = SettlementEngine(session)
    
    payload = {
        "client_id": "ORION_ENERGY",
        "qty": 4500,        
        "rate": 22.50,      
        "ref": "LIVE_ACTIVATION_001",
        "desc": "Heavy Fuel Oil (HFO) - System Activation Batch"
    }
    
    result = cortex.capitalize_event("SYSTEM_ACTIVATION", payload)
    
    if result['status'] == 'SETTLED':
        print(f"\n✅ SYSTEM ACTIVE. Transaction Settled.")
        print(f"   > Invoice: {result['invoice_number']}")
        print(f"   > Revenue: R {result['total_due']}")
    else:
        print(f"\n❌ ACTIVATION FAILED: {result.get('reason')}")

if __name__ == "__main__":
    activate_system()
