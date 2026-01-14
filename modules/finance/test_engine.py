import sys
import os

# 1. SETUP: Add the project root to python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.finance.models import Base, Client
from modules.finance.settlement import SettlementEngine

def run_simulation():
    print("\n" + "="*60)
    print("MAIS FINANCIAL CORTEX :: SYSTEM DIAGNOSTIC")
    print("="*60 + "\n")

    # 2. INITIALIZE MEMORY (In-Memory SQLite for Testing)
    print("[INIT] Booting Virtual Ledger...")
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # 3. SEED REALITY (Create a Mock Client)
    print("[INIT] Seeding Counterparty Data...")
    mock_client = Client(
        id="ORION_ENERGY", 
        name="Orion Energy Ltd.", 
        credit_limit=1000000.00, 
        current_debt=850000.00
    )
    db.add(mock_client)
    db.commit()

    # 4. INITIALIZE BRAIN
    cortex = SettlementEngine(db)

    # 5. SIMULATE TRIGGER (The Physics)
    print("\n" + "-"*30)
    print("EVENT TRIGGER: INDUSTRIAL BATCH COMPLETION")
    print("-"*30)
    
    event_payload = {
        "client_id": "ORION_ENERGY",
        "qty": 4500,        # Liters
        "rate": 22.50,      # R/Liter
        "ref": "SENSOR_901",
        "desc": "Heavy Fuel Oil (HFO) - Grade A"
    }

    # 6. EXECUTE PROTOCOL
    result = cortex.capitalize_event("INDUSTRIAL_BATCH", event_payload)

    # 7. REPORT
    if result['status'] == 'SETTLED':
        print(f"\n✅ SUCCESS: TRANSACTION SETTLED")
        print(f"   > Invoice Generated: {result['invoice_number']}")
        print(f"   > Ledger Reference:  {result['journal_ref']}")
        print(f"   > Total Capitalized: R {result['total_due']}")
    else:
        print(f"\n❌ BLOCKED: GOVERNANCE PROTOCOL")
        print(f"   > Reason: {result['reason']}")

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
