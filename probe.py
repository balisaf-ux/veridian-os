import sqlite3
import pandas as pd
import os

# --- CONFIGURATION ---
DB_NAME = "veridian_cortex.db"

def run_diagnostic():
    print(f"🔎 PROBE LAUNCHED: Targeting {DB_NAME}...")
    
    if not os.path.exists(DB_NAME):
        print(f"❌ CRITICAL ERROR: Database file '{DB_NAME}' not found in {os.getcwd()}")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. CHECK TABLE EXISTENCE
    print("\n--- 1. SCHEMA SCAN ---")
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in c.fetchall()]
    
    if "virtual_stockpiles" in tables:
        print("✅ Table 'virtual_stockpiles' EXISTS.")
    else:
        print("❌ Table 'virtual_stockpiles' MISSING.")
        print("   🛠️  REPAIRING SCHEMA...")
        c.execute('''CREATE TABLE virtual_stockpiles (
            stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_ref TEXT, product TEXT, tonnage_on_floor REAL, 
            value_per_ton REAL, last_audit TEXT)''')
        conn.commit()
        print("   ✅ Table Created.")

    # 2. CHECK DATA CONTENT
    print("\n--- 2. DATA DENSITY SCAN ---")
    try:
        df = pd.read_sql_query("SELECT * FROM virtual_stockpiles", conn)
        print(f"📊 Row Count: {len(df)}")
        
        if df.empty:
            print("❌ Table is EMPTY. Dashboard has nothing to display.")
            print("   💉 INJECTING STRATEGIC DATA...")
            stocks = [
                ("PPC Cement Hercules", "Cement (CEM II)", 1500, 1250.00),
                ("Khwezela Colliery", "Thermal Coal (RB1)", 34000, 950.00),
                ("Sturrock & Robson", "Industrial Components", 200, 45000.00)
            ]
            for s in stocks:
                c.execute("INSERT INTO virtual_stockpiles (source_ref, product, tonnage_on_floor, value_per_ton, last_audit) VALUES (?, ?, ?, ?, '2025-01-01')", s)
            conn.commit()
            print("   ✅ Data Injected.")
        else:
            print("✅ Data Detected:")
            print(df[['source_ref', 'tonnage_on_floor']].to_string(index=False))
            
    except Exception as e:
        print(f"❌ DATA READ ERROR: {e}")

    # 3. CHECK COLUMN INTEGRITY
    print("\n--- 3. COLUMN INTEGRITY ---")
    c.execute("PRAGMA table_info(virtual_stockpiles)")
    cols = [row[1] for row in c.fetchall()]
    print(f"Columns Found: {cols}")
    
    required = ['source_ref', 'product', 'tonnage_on_floor']
    missing = [x for x in required if x not in cols]
    
    if missing:
        print(f"❌ CRITICAL SCHEMA MISMATCH. Missing: {missing}")
    else:
        print("✅ Schema Integrity: 100%")

    conn.close()
    print("\n🔎 PROBE COMPLETE.")

if __name__ == "__main__":
    run_diagnostic()
