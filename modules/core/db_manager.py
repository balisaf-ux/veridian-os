import sqlite3

import pandas as pd

import os

import datetime

import json

import numpy as np

import time



# --- CONFIGURATION ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "veridian_cortex.db")

DB_NAME = DB_PATH



# ==========================================

# 1. SYSTEM INITIALIZATION & MIGRATION

# ==========================================



def _run_migrations(conn):

    """Auto-heals the database schema to support new features without deleting data."""

    c = conn.cursor()

    

    # MIGRATION 1: Trade Deal Columns

    try: c.execute("ALTER TABLE trade_deals ADD COLUMN stage TEXT")

    except: pass

    try: c.execute("ALTER TABLE trade_deals ADD COLUMN probability REAL")

    except: pass

    try: c.execute("ALTER TABLE trade_deals ADD COLUMN volume REAL")

    except: pass

    try: c.execute("ALTER TABLE trade_deals ADD COLUMN deal_id TEXT")

    except: pass



    # MIGRATION 2: Fleet Registry Telemetry

    try: c.execute("ALTER TABLE fleet_registry ADD COLUMN location TEXT")

    except: pass

    try: c.execute("ALTER TABLE fleet_registry ADD COLUMN current_load REAL")

    except: pass

    

    # MIGRATION 3: HAZCHEM COMPLIANCE (The Fix)

    try: c.execute("ALTER TABLE fleet_registry ADD COLUMN hazchem_compliant INTEGER DEFAULT 0")

    except: pass

    

    conn.commit()



def init_db():

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    

    # SYSTEM CONFIG

    c.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")



    # WAR ROOM

    c.execute('''CREATE TABLE IF NOT EXISTS prospects (

        id INTEGER PRIMARY KEY AUTOINCREMENT, 

        company_name TEXT, parent_company TEXT, contact_person TEXT, 

        industry TEXT, region TEXT, status TEXT, estimated_value REAL, 

        notes TEXT, focus_period TEXT)''')

        

    c.execute('''CREATE TABLE IF NOT EXISTS interaction_log (

        log_id INTEGER PRIMARY KEY AUTOINCREMENT, company_name TEXT,

        interaction_type TEXT, date TEXT, outcome TEXT, next_step TEXT)''')



    # TRADE & FINANCE

    c.execute('''CREATE TABLE IF NOT EXISTS trade_deals (

        deal_id INTEGER PRIMARY KEY AUTOINCREMENT,

        client_name TEXT, product TEXT, volume REAL, value REAL, 

        status TEXT, probability REAL, stage TEXT,

        rfq_id TEXT, qty REAL, created_at TEXT)''') 

    

    c.execute('''CREATE TABLE IF NOT EXISTS marketplace_bids (

        bid_id INTEGER PRIMARY KEY AUTOINCREMENT,

        sku TEXT, supplier TEXT, price_per_ton REAL, 

        available_qty REAL, valid_until TEXT, status TEXT)''')



    c.execute('''CREATE TABLE IF NOT EXISTS ledger_lines (

        transaction_id TEXT, date TEXT, description TEXT, 

        account_code TEXT, debit REAL, credit REAL, reference_id TEXT)''')

        

    c.execute('''CREATE TABLE IF NOT EXISTS billing_docs (

        doc_id TEXT PRIMARY KEY, client_name TEXT, doc_type TEXT, 

        date TEXT, amount REAL, status TEXT, reference_deal TEXT)''')



    # LOGISTICS KERNEL (Unified)

    # Note: We ensure all columns are present in definition for fresh installs

    c.execute('''CREATE TABLE IF NOT EXISTS fleet_registry (

        vehicle_id TEXT PRIMARY KEY, type TEXT, status TEXT, 

        max_payload_kg REAL, cpk REAL, driver TEXT,

        location TEXT, current_load REAL, hazchem_compliant INTEGER)''')



    c.execute('''CREATE TABLE IF NOT EXISTS driver_registry (

        driver_id TEXT PRIMARY KEY, name TEXT, license_code TEXT, 

        status TEXT, current_vehicle TEXT)''')



    c.execute('''CREATE TABLE IF NOT EXISTS compliance_checks (

        check_id TEXT PRIMARY KEY, vehicle_id TEXT, driver_id TEXT, 

        date TEXT, check_data TEXT, status TEXT)''')



    c.execute('''CREATE TABLE IF NOT EXISTS trip_manifests (

        trip_id TEXT PRIMARY KEY, deal_ref TEXT, vehicle_id TEXT, 

        route TEXT, status TEXT, date_dispatched TEXT, cost_impact REAL)''')

        

    c.execute('''CREATE TABLE IF NOT EXISTS trip_events (

        event_id TEXT PRIMARY KEY, trip_id TEXT, event_type TEXT, 

        weight REAL, location TEXT, timestamp TEXT, photo_hash TEXT)''')



    # PORTAL

    c.execute('''CREATE TABLE IF NOT EXISTS client_registry (

        client_id TEXT PRIMARY KEY, company_name TEXT, reg_number TEXT, 

        credit_limit REAL, credit_status TEXT, joined_date TEXT)''')



    conn.commit()

    

    # Run Safe Migrations

    _run_migrations(conn)

    conn.close()



# Initialize immediately

init_db()



# ==========================================

# 2. WAR ROOM & TARGET UTILITIES

# ==========================================



def set_annual_target(year, target):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO system_config VALUES (?, ?)", (f"target_{year}", str(target)))

    conn.commit()

    conn.close()



def get_annual_target(year):

    conn = sqlite3.connect(DB_NAME)

    try:

        df = pd.read_sql_query("SELECT value FROM system_config WHERE key = ?", conn, params=(f"target_{year}",))

        return float(df.iloc[0]['value']) if not df.empty else 0.0

    except: return 0.0

    finally: conn.close()



def save_strategic_target(company, parent, contact, industry, region, value, notes):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT INTO prospects (company_name, parent_company, contact_person, industry, region, status, estimated_value, notes, focus_period) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",

              (company, parent, contact, industry, region, "New", value, notes, "None"))

    conn.commit()

    conn.close()



def log_interaction(company, i_type, outcome, next_step):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    c.execute("INSERT INTO interaction_log (company_name, interaction_type, date, outcome, next_step) VALUES (?, ?, ?, ?, ?)",

              (company, i_type, date, outcome, next_step))

    conn.commit()

    conn.close()



def update_target_focus(company, period):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("UPDATE prospects SET focus_period = ? WHERE company_name = ?", (period, company))

    conn.commit()

    conn.close()



def load_prospects_to_dataframe():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM prospects", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def load_interaction_history(company_name):

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM interaction_log WHERE company_name = ?", conn, params=(company_name,))

    except: return pd.DataFrame()

    finally: conn.close()



# ==========================================

# 3. LOGISTICS (DRIVERS & FLEET)

# ==========================================



def load_fleet_to_dataframe():

    conn = sqlite3.connect(DB_NAME)

    try: 

        df = pd.read_sql_query("SELECT * FROM fleet_registry", conn)

        

        if not df.empty:

            # ALIASING FOR FRONTEND COMPATIBILITY (TTE uses Capitalized Keys)

            if 'vehicle_id' in df.columns: df['Truck_ID'] = df['vehicle_id']

            if 'max_payload_kg' in df.columns: df['max_tons'] = df['max_payload_kg'] / 1000.0 

            if 'status' in df.columns: df['Status'] = df['status'] 

            if 'type' in df.columns: df['Type'] = df['type']

            if 'location' in df.columns: df['Location'] = df['location'] # FIX: Map lowercase to Capital

            

            # HAZCHEM SAFETY

            if 'hazchem_compliant' not in df.columns:

                df['hazchem_compliant'] = 0

            else:

                df['hazchem_compliant'] = df['hazchem_compliant'].fillna(0).astype(int)

            

        return df

    except: return pd.DataFrame()

    finally: conn.close()



def register_vehicle_db(veh_id, v_type, payload, cpk, driver):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO fleet_registry (vehicle_id, type, status, max_payload_kg, cpk, driver, location, current_load, hazchem_compliant) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",

              (veh_id, v_type, "Idle", payload, cpk, driver, "Depot", 0.0, 0))

    conn.commit()

    conn.close()



def save_fleet_vehicle(veh_id, v_type, driver, max_tons):

    """Persistence for TTE Models."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO fleet_registry (vehicle_id, type, driver, max_payload_kg, cpk, status, location, current_load, hazchem_compliant) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",

              (veh_id, v_type, driver, max_tons * 1000, 15.0, "Idle", "Depot", 0.0, 0))

    conn.commit()

    conn.close()



def update_fleet_state(veh_id, status, location, current_load):

    """Telemetry Update."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("UPDATE fleet_registry SET status=?, location=?, current_load=? WHERE vehicle_id=?", 

              (status, location, current_load, veh_id))

    conn.commit()

    conn.close()



def create_trip(trip_data):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("SELECT cpk FROM fleet_registry WHERE vehicle_id = ?", (trip_data['vehicle_id'],))

    res = c.fetchone()

    real_cpk = res[0] if res else 12.50

    dist = 600.0

    cost = dist * real_cpk

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    

    c.execute("INSERT INTO trip_manifests VALUES (?, ?, ?, ?, ?, ?, ?)",

              (trip_data['trip_id'], trip_data['deal_ref'], trip_data['vehicle_id'], 

               trip_data['route'], trip_data['status'], date, cost))

    

    c.execute("UPDATE fleet_registry SET status = 'Active' WHERE vehicle_id = ?", (trip_data['vehicle_id'],))

    

    jrn = f"JRN-OPS-{trip_data['trip_id']}"

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)", 

              (jrn, date, f"Trip: {trip_data['vehicle_id']}", "5100-LOGISTICS", cost, 0, trip_data['trip_id']))

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)", 

              (jrn, date, "Accrual", "2000-AP", 0, cost, trip_data['trip_id']))

    conn.commit()

    conn.close()



def load_trips_to_dataframe():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM trip_manifests", conn)

    except: return pd.DataFrame()

    finally: conn.close()



# --- DRIVERS ---

def register_driver(d_id, name, license):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO driver_registry VALUES (?, ?, ?, ?, ?)",

              (d_id, name, license, "Off Duty", "None"))

    conn.commit()

    conn.close()



def get_active_drivers():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM driver_registry", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def submit_checklist(vehicle_id, driver_id, checks_json):

    c_id = f"CHK-{pd.Timestamp.now().strftime('%H%M%S')}"

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT INTO compliance_checks VALUES (?, ?, ?, ?, ?, ?)",

              (c_id, vehicle_id, driver_id, date, json.dumps(checks_json), "PASSED"))

    c.execute("UPDATE driver_registry SET status='On Duty', current_vehicle=? WHERE driver_id=?", (vehicle_id, driver_id))

    conn.commit()

    conn.close()

    return c_id



def log_trip_event(trip_id, event_type, weight, location, photo_sim):

    e_id = f"EVT-{pd.Timestamp.now().strftime('%H%M%S')}"

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT INTO trip_events VALUES (?, ?, ?, ?, ?, ?, ?)",

              (e_id, trip_id, event_type, weight, location, ts, "photo.jpg"))

    conn.commit()

    conn.close()



# ==========================================

# 4. FINANCE & BILLING

# ==========================================



def create_billing_doc(client, doc_type, amount, ref_deal):

    doc_id = f"{doc_type[:3].upper()}-{pd.Timestamp.now().strftime('%d%H%M')}"

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT INTO billing_docs VALUES (?, ?, ?, ?, ?, ?, ?)",

              (doc_id, client, doc_type, date, amount, "ISSUED", ref_deal))

    if doc_type == "INVOICE":

        jrn_id = f"JRN-REV-{doc_id}"

        c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)",

                  (jrn_id, date, f"Invoice: {client}", "1200-AR", amount, 0, doc_id))

        c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)",

                  (jrn_id, date, f"Revenue: {client}", "4000-SALES", 0, amount, doc_id))

    conn.commit()

    conn.close()

    return doc_id



def get_billing_docs():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM billing_docs", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def save_journal_entry(entry_id, date, reference, description, enriched_lines, source_module):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    for line in enriched_lines:

        c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)",

                  (entry_id, date, description, str(line['code']), line['debit'], line['credit'], reference))

    conn.commit()

    conn.close()



def get_ledger_stream():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM ledger_lines ORDER BY date DESC", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def get_financial_health():

    conn = sqlite3.connect(DB_NAME)

    try:

        df = pd.read_sql_query("SELECT * FROM ledger_lines", conn)

        if df.empty: return {"revenue": 0, "ar": 0, "cash": 0, "expense": 0}

        rev = df[df['account_code'].str.startswith('4')]['credit'].sum()

        exp = df[df['account_code'].str.startswith('5')]['debit'].sum()

        ar = df[df['account_code'].str.startswith('12')]['debit'].sum() - df[df['account_code'].str.startswith('12')]['credit'].sum()

        return {"revenue": rev, "ar": ar, "cash": rev - exp, "expense": exp}

    except: return {"revenue": 0, "ar": 0, "cash": 0, "expense": 0}

    finally: conn.close()



def init_chart_of_accounts():

    return {"1000-CASH": "Asset", "1200-AR": "Asset", "2000-AP": "Liability", "4000-SALES": "Revenue", "5100-LOGISTICS": "Expense"}



def get_trial_balance_sql():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT account_code, SUM(debit) as d, SUM(credit) as c FROM ledger_lines GROUP BY account_code", conn)

    except: return pd.DataFrame()

    finally: conn.close()



# ==========================================

# 5. TRADE CORE & FUSION

# ==========================================



def save_trade_deal(client, product, volume, value, status, stage):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    prob_map = {"Lead": 0.1, "Negotiation": 0.5, "Firm Offer": 0.8, "Signed": 1.0}

    prob = prob_map.get(stage, 0.0)

    c.execute("INSERT INTO trade_deals (client_name, product, volume, value, status, probability, stage) VALUES (?, ?, ?, ?, ?, ?, ?)",

              (client, product, volume, value, status, prob, stage))

    conn.commit()

    conn.close()



def log_supplier_bid(sku, supplier, price, qty, valid_until):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("INSERT INTO marketplace_bids (sku, supplier, price_per_ton, available_qty, valid_until, status) VALUES (?, ?, ?, ?, ?, 'Active')",

              (sku, supplier, price, qty, valid_until))

    conn.commit()

    conn.close()



def load_trades_to_dataframe():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM trade_deals", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def load_bids_to_dataframe():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM marketplace_bids WHERE status='Active'", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def load_all_bids_matrix():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT bid_id, sku as product, supplier as supplier_name, price_per_ton as bid_amount, status FROM marketplace_bids WHERE status='Active'", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def load_bids_for_rfq(rfq_id):

    return load_bids_to_dataframe() 



def get_sku_details(sku_name):

    catalog = {

        "Thermal Coal (RB1)": {"grade": "RB1 Export", "hazchem": False, "desc": "High CV (6000kcal)"},

        "Diesel 50ppm": {"grade": "Auto Diesel", "hazchem": True, "desc": "Flashpoint > 55C"},

        "Iron Oxide": {"grade": "Pigment", "hazchem": False, "desc": "Red/Black Oxide"},

        "Industrial Valves": {"grade": "Steel", "hazchem": False, "desc": "High Pressure"},

    }

    return catalog.get(sku_name, {"grade": "Standard", "hazchem": False, "desc": "General Cargo"})



def execute_deal_award(rfq_id):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    try: c.execute("UPDATE trade_deals SET status='Logistics', stage='Signed', probability=1.0 WHERE deal_id=?", (rfq_id,))

    except: pass

    conn.commit()

    conn.close()



def post_finance_entry(reference, description, amount):

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    jrn_id = f"JRN-AUTO-{int(time.time())}"

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)",

              (jrn_id, date, description, "1200-AR", amount, 0, reference))

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, ?, ?, ?, ?)",

              (jrn_id, date, description, "4000-SALES", 0, amount, reference))

    conn.commit()

    conn.close()



def mint_industrial_asset(rfq_id, client, product):

    return f"AST-{hash(str(rfq_id) + client) % 10000}"



def get_logistics_rate(weight_kg, destination):

    dist_map = {"Durban (DBN)": 580, "Cape Town (CPT)": 1400}

    dist = dist_map.get(destination, 500)

    base_rate = 22.50 

    if weight_kg < 10000: base_rate = 14.00 

    cost = dist * base_rate

    return cost, dist



# ==========================================

# 6. LOGISTICS 4PL UTILITIES

# ==========================================



def get_pending_orders():

    """Fetches orders ready for dispatch from Trade."""

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM trade_deals WHERE status IN ('Open', 'Logistics', 'Firm Offer') AND stage != 'Dispatched'", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def batch_dispatch_orders(order_ids, trip_id, vehicle_id):

    """Bundles multiple orders into a single Trip Manifest."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    deal_refs = ",".join(str(x) for x in order_ids)

    

    # Estimate cost

    c.execute("SELECT cpk FROM fleet_registry WHERE vehicle_id = ?", (vehicle_id,))

    res = c.fetchone()

    cpk = res[0] if res else 15.00

    est_cost = 500.0 * cpk 

    

    c.execute("INSERT INTO trip_manifests (trip_id, deal_ref, vehicle_id, route, status, date_dispatched, cost_impact) VALUES (?, ?, ?, ?, ?, ?, ?)",

              (trip_id, deal_refs, vehicle_id, "Milk Run", "In Transit", date, est_cost))

    

    # Update Trade Status

    for oid in order_ids:

        try: c.execute("UPDATE trade_deals SET status='Dispatched', stage='Dispatched' WHERE deal_id=?", (oid,))

        except: pass

        try: c.execute("UPDATE trade_deals SET status='Dispatched', stage='Dispatched' WHERE rfq_id=?", (oid,))

        except: pass

        

    conn.commit()

    conn.close()



# ==========================================

# 7. LEGACY SUPPORT & ALIASES

# ==========================================



def load_ledger_to_dataframe(): return get_ledger_stream()



def load_technical_skus():

    catalog = [{"sku_id": "Thermal Coal", "hazchem_mandatory": 0}, {"sku_id": "Diesel", "hazchem_mandatory": 1}]

    return pd.DataFrame(catalog)



def register_new_client(name, reg, req_credit):

    status = "APPROVED" if req_credit <= 1000000 else "PENDING"

    c_id = f"CLT-{name[:3]}-{pd.Timestamp.now().strftime('%d%H')}"

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO client_registry VALUES (?, ?, ?, ?, ?, ?)", (c_id, name, reg, req_credit if status=="APPROVED" else 0, status, "2025-01-01"))

    conn.commit(); conn.close()

    return status, c_id



def get_client_list():

    conn = sqlite3.connect(DB_NAME)

    try: return pd.read_sql_query("SELECT * FROM client_registry", conn)

    except: return pd.DataFrame()

    finally: conn.close()



def submit_portal_inquiry(client_name, product, qty, route, price):

    rfq_id = f"WEB-{pd.Timestamp.now().strftime('%H%M%S')}"

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    c.execute("INSERT INTO trade_deals (rfq_id, client_name, status, product, qty, value) VALUES (?, ?, ?, ?, ?, ?)", (rfq_id, client_name, "WON", product, qty, price))

    create_billing_doc(client_name, "PRO-FORMA", price, rfq_id)

    conn.commit(); conn.close()

    return rfq_id



def get_live_fleet_positions():

    conn = sqlite3.connect(DB_NAME)

    try: df = pd.read_sql_query("SELECT * FROM fleet_registry", conn)

    except: return pd.DataFrame()

    finally: conn.close()

    if not df.empty:

        hubs = [{"lat": -26.2041, "lon": 28.0473}, {"lat": -29.8587, "lon": 31.0218}, {"lat": -33.9249, "lon": 18.4241}]

        df['lat'] = df.index.map(lambda x: hubs[x % len(hubs)]['lat'])

        df['lon'] = df.index.map(lambda x: hubs[x % len(hubs)]['lon'])

    return df



def generate_sensor_data(id):

    return pd.DataFrame([{"Time": "10:00", "Fuel_Level": 500}])



# ==========================================

# 8. MANDLA PROTOCOL: SITE COMPLIANCE (RESTORATION)

# ==========================================



def _patch_gap_closure_schema():

    """Adds columns for Mandla's specific pain points if they are missing."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    # 1. TIME: Track site delays

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN arrival_time TEXT")

    except: pass

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN departure_time TEXT")

    except: pass

    # 2. PROOF: Digital Signature Name

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN pod_signatory TEXT")

    except: pass

    # 3. SAFETY: Route Quality

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN route_safety_score INTEGER")

    except: pass

    conn.commit()

    conn.close()



# Run patch immediately

_patch_gap_closure_schema()



def log_site_event(trip_id, event_type):

    """Logs precise timestamps for Demurrage (Waiting Time) calculations."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    col = "arrival_time" if event_type == "ARRIVAL" else "departure_time"

    c.execute(f"UPDATE trip_manifests SET {col} = ? WHERE trip_id = ?", (timestamp, trip_id))

    conn.commit()

    conn.close()

    return timestamp



def complete_pod(trip_id, signatory_name):

    """Closes the loop: No Signature = No Pay."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("UPDATE trip_manifests SET status='DELIVERED', pod_signatory=? WHERE trip_id=?", 

              (signatory_name, trip_id))

    conn.commit()

    conn.close()



    # ==========================================

# 9. INDUSTRIAL & SOURCING LOGIC (CORE)

# ==========================================



def _run_industrial_migrations():

    """Adds tables for Industrial Sourcing and Subcontractors."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    

    # 1. Industrial Sources (Mines/Factories)

    c.execute('''CREATE TABLE IF NOT EXISTS industrial_sources (

        source_id INTEGER PRIMARY KEY AUTOINCREMENT, 

        name TEXT, type TEXT, location TEXT, product TEXT, 

        contract_status TEXT, capacity_per_month REAL)''')



    # 2. Virtual Stockpiles (Inventory at Origin)

    c.execute('''CREATE TABLE IF NOT EXISTS virtual_stockpiles (

        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,

        source_ref TEXT, product TEXT, tonnage_on_floor REAL, 

        value_per_ton REAL, last_audit TEXT)''')



    # 3. Subcontractor Registry (The 'Subbie' Fleet)

    c.execute('''CREATE TABLE IF NOT EXISTS subcontractor_registry (

        sub_id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_name TEXT, fleet_size INTEGER, rate_per_ton REAL, 

        status TEXT, payment_terms TEXT)''')



    # 4. Add Subbie Reference to Manifests

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN subcontractor_ref TEXT")

    except: pass



    conn.commit()

    conn.close()



# Run industrial migration

_run_industrial_migrations()



def save_industrial_source(name, type_, loc, prod, cap):

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    c.execute("INSERT INTO industrial_sources (name, type, location, product, contract_status, capacity_per_month) VALUES (?, ?, ?, ?, 'Active', ?)",

              (name, type_, loc, prod, cap))

    c.execute("INSERT INTO virtual_stockpiles (source_ref, product, tonnage_on_floor, value_per_ton, last_audit) VALUES (?, ?, 0, 0, ?)",

              (name, prod, datetime.datetime.now().strftime("%Y-%m-%d")))

    conn.commit(); conn.close()



def load_industrial_data():

    conn = sqlite3.connect(DB_NAME)

    src = pd.read_sql_query("SELECT * FROM industrial_sources", conn)

    stk = pd.read_sql_query("SELECT * FROM virtual_stockpiles", conn)

    sub = pd.read_sql_query("SELECT * FROM subcontractor_registry", conn)

    conn.close()

    return src, stk, sub



def execute_back_to_back(deal_id, sub_name, tonnage, sub_rate, client_rate):

    """Generates AR (Income) and AP (Expense) simultaneously."""

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    trip_id = f"SUB-{int(time.time())}"

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    revenue = tonnage * client_rate

    cost = tonnage * sub_rate

    

    # 1. Log Trip

    c.execute("INSERT INTO trip_manifests (trip_id, deal_ref, vehicle_id, status, subcontractor_ref) VALUES (?, ?, 'EXTERNAL', 'In Transit', ?)",

              (trip_id, deal_id, sub_name))

    

    # 2. Post AR (Revenue)

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, '1200-AR', ?, 0, ?)", (f"JRN-AR-{trip_id}", date, f"Client Rev: {deal_id}", revenue, deal_id))

    # 3. Post AP (Cost)

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, '5100-LOGISTICS', ?, 0, ?)", (f"JRN-AP-{trip_id}", date, f"Subbie Cost: {sub_name}", cost, deal_id))

    

    conn.commit(); conn.close()

    return trip_id



# ==========================================

# 9. INDUSTRIAL & SOURCING LOGIC (RESTORED)

# ==========================================



def _run_industrial_migrations():

    """Adds tables for Industrial Sourcing and Subcontractors."""

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    

    # 1. Industrial Sources

    c.execute('''CREATE TABLE IF NOT EXISTS industrial_sources (

        source_id INTEGER PRIMARY KEY AUTOINCREMENT, 

        name TEXT, type TEXT, location TEXT, product TEXT, 

        contract_status TEXT, capacity_per_month REAL)''')



    # 2. Virtual Stockpiles

    c.execute('''CREATE TABLE IF NOT EXISTS virtual_stockpiles (

        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,

        source_ref TEXT, product TEXT, tonnage_on_floor REAL, 

        value_per_ton REAL, last_audit TEXT)''')



    # 3. Subcontractor Registry

    c.execute('''CREATE TABLE IF NOT EXISTS subcontractor_registry (

        sub_id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_name TEXT, fleet_size INTEGER, rate_per_ton REAL, 

        status TEXT, payment_terms TEXT)''')



    # 4. Manifest Update

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN subcontractor_ref TEXT")

    except: pass



    conn.commit()

    conn.close()



# Run immediately

_run_industrial_migrations()



def save_industrial_source(name, type_, loc, prod, cap):

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    c.execute("INSERT INTO industrial_sources (name, type, location, product, contract_status, capacity_per_month) VALUES (?, ?, ?, ?, 'Active', ?)",

              (name, type_, loc, prod, cap))

    c.execute("INSERT INTO virtual_stockpiles (source_ref, product, tonnage_on_floor, value_per_ton, last_audit) VALUES (?, ?, 0, 0, ?)",

              (name, prod, datetime.datetime.now().strftime("%Y-%m-%d")))

    conn.commit(); conn.close()



def load_industrial_data():

    conn = sqlite3.connect(DB_NAME)

    try:

        src = pd.read_sql_query("SELECT * FROM industrial_sources", conn)

        stk = pd.read_sql_query("SELECT * FROM virtual_stockpiles", conn)

        sub = pd.read_sql_query("SELECT * FROM subcontractor_registry", conn)

    except: 

        src, stk, sub = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    conn.close()

    return src, stk, sub



def save_subcontractor(name, size, rate):

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    c.execute("INSERT INTO subcontractor_registry (company_name, fleet_size, rate_per_ton, status, payment_terms) VALUES (?, ?, ?, 'Vetted', '30 Days')",

              (name, size, rate))

    conn.commit(); conn.close()



def execute_back_to_back(deal_id, sub_name, tonnage, sub_rate, client_rate):

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    trip_id = f"SUB-{int(time.time())}"

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    revenue = tonnage * client_rate

    cost = tonnage * sub_rate

    

    c.execute("INSERT INTO trip_manifests (trip_id, deal_ref, vehicle_id, status, subcontractor_ref) VALUES (?, ?, 'EXTERNAL', 'In Transit', ?)",

              (trip_id, deal_id, sub_name))

    

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, '1200-AR', ?, 0, ?)", (f"JRN-AR-{trip_id}", date, f"Client Rev: {deal_id}", revenue, deal_id))

    c.execute("INSERT INTO ledger_lines VALUES (?, ?, ?, '5100-LOGISTICS', ?, 0, ?)", (f"JRN-AP-{trip_id}", date, f"Subbie Cost: {sub_name}", cost, deal_id))

    

    conn.commit(); conn.close()

    return trip_id



# ==========================================

# 10. STRATEGIC DATA INJECTION (THE FLESH)

# ==========================================

def inject_industrial_muscle():

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    

    # 1. THE PRINCIPALS (Your Targets)

    principals = [

        ("PPC Cement Hercules", "Factory", "Pretoria West", "Cement (CEM II)", 45000),

        ("NPC Cimpor", "Factory", "Durban / Siyaya", "Cement (Surebuild)", 30000),

        ("Sturrock & Robson", "Warehouse", "East Rand", "Industrial Components", 5000),

        ("Durban Paints", "Factory", "Mobeni KZN", "Paints & Solvents", 12000),

        ("Khwezela Colliery", "Mine", "Emalahleni", "Thermal Coal (RB1)", 60000)

    ]

    

    # 2. THE VIRTUAL STOCKPILES (Inventory Sovereignty)

    # We simulate stock sitting on their floor that YOU control.

    stockpiles = [

        ("PPC Cement Hercules", "Cement (CEM II)", 1500, 1250.00), # 1,500 tons owned

        ("Khwezela Colliery", "Thermal Coal (RB1)", 34000, 950.00), # 34k tons (1 ship)

        ("Sturrock & Robson", "Industrial Components", 200, 45000.00) # High value

    ]

    

    # 3. THE SUB-CONTRACTOR FLEET (Elastic Capacity)

    subbies = [

        ("Makhado Logistics", 15, 650.00),   # Coal Link

        ("Super Group Sub-Div", 40, 1800.00), # Flat decks

        ("Unitrans (Spot)", 12, 850.00),      # Tautliners

        ("Local PDI Transporters", 8, 600.00) # Community trucks

    ]



    # EXECUTE INJECTION

    print("--- INJECTING INDUSTRIAL MUSCLE ---")

    

    for p in principals:

        c.execute("INSERT OR IGNORE INTO industrial_sources (name, type, location, product, contract_status, capacity_per_month) VALUES (?, ?, ?, ?, 'Target', ?)", p)

    

    for s in stockpiles:

        # Check if stockpile exists first

        c.execute("SELECT count(*) FROM virtual_stockpiles WHERE source_ref=?", (s[0],))

        if c.fetchone()[0] == 0:

            c.execute("INSERT INTO virtual_stockpiles (source_ref, product, tonnage_on_floor, value_per_ton, last_audit) VALUES (?, ?, ?, ?, '2025-01-01')", 

                      (s[0], s[1], s[2], s[3]))

            

    for sub in subbies:

        c.execute("INSERT OR IGNORE INTO subcontractor_registry (company_name, fleet_size, rate_per_ton, status, payment_terms) VALUES (?, ?, ?, 'Vetted', '30 Days')", sub)

        

    conn.commit(); conn.close()



# UNCOMMENT TO RUN ONCE, THEN RE-COMMENT

inject_industrial_muscle()



# ==========================================

# 11. LOGISTICS SUPPORT (MANDLA PROTOCOL RESTORATION)

# ==========================================



def log_site_event(trip_id, event_type):

    """

    Logs precise timestamps for Demurrage (Waiting Time) calculations.

    REQUIRED by Logistics Module.

    """

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    col = "arrival_time" if event_type == "ARRIVAL" else "departure_time"

    

    # Safety check to ensure column exists

    try:

        c.execute(f"UPDATE trip_manifests SET {col} = ? WHERE trip_id = ?", (timestamp, trip_id))

        conn.commit()

    except Exception as e:

        print(f"Schema Warning: {e}")

        

    conn.close()

    return timestamp



def complete_pod(trip_id, signatory_name):

    """

    Closes the loop: No Signature = No Pay.

    REQUIRED by Logistics Module.

    """

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("UPDATE trip_manifests SET status='DELIVERED', pod_signatory=? WHERE trip_id=?", 

              (signatory_name, trip_id))

    conn.commit()

    conn.close()



# Ensure the Schema supports these functions

def _patch_logistics_schema():

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN arrival_time TEXT")

    except: pass

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN departure_time TEXT")

    except: pass

    try: c.execute("ALTER TABLE trip_manifests ADD COLUMN pod_signatory TEXT")

    except: pass

    conn.commit(); conn.close()



_patch_logistics_schema()

# ==========================================
# SURGICAL PATCH: VIRTUAL STOCKPILES ACTIVATION
# ==========================================

def _patch_stockpile_schema():
    """Ensures the Stockpile Ledger exists without breaking existing tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Create Table if missing
    c.execute('''CREATE TABLE IF NOT EXISTS virtual_stockpiles (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_ref TEXT, product TEXT, tonnage_on_floor REAL, 
        value_per_ton REAL, last_audit TEXT)''')
    
    # 2. Check if we need to seed data (Only if empty)
    try:
        c.execute("SELECT count(*) FROM virtual_stockpiles")
        if c.fetchone()[0] == 0:
            print(">>> SEEDING VIRTUAL STOCKPILES...")
            # Inject Strategic Stockpiles (The Muscle)
            stocks = [
                ("PPC Cement Hercules", "Cement (CEM II)", 1500, 1250.00),
                ("Khwezela Colliery", "Thermal Coal (RB1)", 34000, 950.00),
                ("Sturrock & Robson", "Industrial Components", 200, 45000.00)
            ]
            for s in stocks:
                c.execute("INSERT INTO virtual_stockpiles (source_ref, product, tonnage_on_floor, value_per_ton, last_audit) VALUES (?, ?, ?, ?, ?)",
                          (s[0], s[1], s[2], s[3], datetime.datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
    except: pass
    
    conn.commit()
    conn.close()

# Run Patch Immediately
_patch_stockpile_schema()

def update_stockpile(source, tons, value):
    """Allows the Industrial Dashboard to update inventory levels."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Update logic
    c.execute("UPDATE virtual_stockpiles SET tonnage_on_floor=?, value_per_ton=? WHERE source_ref=?", 
              (tons, value, source))
    conn.commit()
    conn.close()

def load_industrial_data():
    """
    DEBUG VERSION: No Try/Except. Prints DB Path.
    """
    print(f"🔎 APP CONNECTING TO: {DB_PATH}") # Check your terminal for this line!
    
    conn = sqlite3.connect(DB_NAME)
    
    # We run these naked to force any error to appear on screen
    src = pd.read_sql_query("SELECT * FROM industrial_sources", conn)
    stk = pd.read_sql_query("SELECT * FROM virtual_stockpiles", conn)
    sub = pd.read_sql_query("SELECT * FROM subcontractor_registry", conn)
    
    conn.close()
    return src, stk, sub
