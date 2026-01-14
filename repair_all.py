import sqlite3
import os

DB_NAME = "veridian_cortex.db"

def repair_full_chain():
    print(f"🔧 STARTING FULL INDUSTRIAL CHAIN REPAIR on {DB_NAME}...")
    
    if not os.path.exists(DB_NAME):
        print("❌ DB File not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. REPAIR 'industrial_sources' (The Parent)
    # If this is missing, Stockpiles have no "Source" to link to, causing crashes.
    print("\n--- CHECKING: INDUSTRIAL SOURCES ---")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='industrial_sources';")
    if not c.fetchone():
        print("❌ MISSING. Creating table...")
        c.execute('''CREATE TABLE industrial_sources (
            source_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, type TEXT, location TEXT, product TEXT, 
            contract_status TEXT, capacity_per_month REAL)''')
        # Seed Data
        sources = [
            ("PPC Cement Hercules", "Factory", "Pretoria West", "Cement (CEM II)", 45000),
            ("Khwezela Colliery", "Mine", "Emalahleni", "Thermal Coal (RB1)", 60000),
            ("Sturrock & Robson", "Warehouse", "East Rand", "Industrial Components", 5000),
            ("Durban Paints", "Factory", "Mobeni KZN", "Paints & Solvents", 12000)
        ]
        for s in sources:
            c.execute("INSERT INTO industrial_sources (name, type, location, product, contract_status, capacity_per_month) VALUES (?, ?, ?, ?, 'Active', ?)", s)
        print("✅ REPAIRED & SEEDED.")
    else:
        print("✅ EXISTS.")

    # 2. REPAIR 'subcontractor_registry' (The Fleet)
    print("\n--- CHECKING: SUB-CONTRACTORS ---")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subcontractor_registry';")
    if not c.fetchone():
        print("❌ MISSING. Creating table...")
        c.execute('''CREATE TABLE subcontractor_registry (
            sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT, fleet_size INTEGER, rate_per_ton REAL, 
            status TEXT, payment_terms TEXT)''')
        # Seed Data
        subbies = [
            ("Makhado Logistics", 15, 650.00),
            ("Super Group Sub-Div", 40, 1800.00)
        ]
        for s in subbies:
            c.execute("INSERT INTO subcontractor_registry (company_name, fleet_size, rate_per_ton, status, payment_terms) VALUES (?, ?, ?, 'Vetted', '30 Days')", s)
        print("✅ REPAIRED & SEEDED.")
    else:
        print("✅ EXISTS.")

    # 3. VERIFY 'virtual_stockpiles' (The Target)
    print("\n--- CHECKING: VIRTUAL STOCKPILES ---")
    c.execute("SELECT count(*) FROM virtual_stockpiles")
    count = c.fetchone()[0]
    print(f"✅ EXISTS with {count} rows.")

    conn.commit()
    conn.close()
    print("\n✨ CHAIN REPAIR COMPLETE. RESTART YOUR APP.")

if __name__ == "__main__":
    repair_full_chain()
