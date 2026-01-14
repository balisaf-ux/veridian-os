import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())
from modules.mercantile.models import Base, SovereignAsset

def commission_magisterial_mercantile():
    print("\n🏛️ COMMISSIONING MAGISTERIAL MERCANTILE...")
    
    db_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Build the Vaults
    Base.metadata.create_all(engine)
    print("   > Asset & Position Ledgers Constructed.")

    # 2. Seed Sovereign Assets (The Wealth)
    assets = [
        # The Fuel Fortress (Import Strategy)
        {"id": "TNK-DSL-01", "name": "JHB Depot Main Tank", "type": "LIQUID", "cap": 25000, "curr": 12500, "cost": 20.50, "loc": "City Deep Yard"},
        # The Export Stockpile (Commodity Strategy)
        {"id": "STK-COAL-01", "name": "RBCT Bonded Stockpile", "type": "SOLID", "cap": 50000, "curr": 10000, "cost": 1450.00, "loc": "Richards Bay"}
    ]

    count = 0
    for a in assets:
        exists = session.query(SovereignAsset).filter_by(asset_id=a['id']).first()
        if not exists:
            new_asset = SovereignAsset(
                asset_id=a['id'], name=a['name'], type=a['type'],
                capacity=a['cap'], current_level=a['curr'],
                avg_cost_price=a['cost'], location=a['loc']
            )
            session.add(new_asset)
            count += 1
    
    session.commit()
    print(f"   > {count} Sovereign Assets Capitalized.")
    print("✅ MAGISTERIAL MERCANTILE OPEN FOR BUSINESS.")

if __name__ == "__main__":
    commission_magisterial_mercantile()
