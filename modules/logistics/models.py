import pandas as pd
import random
import uuid
from datetime import datetime

# ---------------------------------------------------------
# DIRECT, SAFE IMPORT (NO FALLBACKS)
# ---------------------------------------------------------
try:
    from .db_utils import run_query, load_data
except ImportError:
    try:
        from ..db_utils import run_query, load_data
    except ImportError:
        from modules.logistics.db_utils import run_query, load_data


# ---------------------------------------------------------
# SEASONAL + CLIENT PROFILE + ROUTE MODELS
# ---------------------------------------------------------

SEASONS = ["Summer", "Autumn", "Winter", "Spring"]

CLIENT_PROFILES = {
    "Anglo American": {"commodities": ["Coal", "Ore", "Concentrate"], "tons_range": (28, 34)},
    "Shoprite DC": {"commodities": ["FMCG", "Chilled Goods", "Dry Goods"], "tons_range": (12, 28)},
    "Massmart": {"commodities": ["FMCG", "Electronics", "Bulk Retail"], "tons_range": (18, 32)},
    "Glencore": {"commodities": ["Coal", "Metals"], "tons_range": (28, 34)},
    "Sasol": {"commodities": ["Chemicals", "Fuels"], "tons_range": (20, 32)},
}

ROUTES = [
    ("JHB City Deep", "Durban Port", 570, "Corridor"),
    ("Richards Bay", "Witbank", 420, "Industrial"),
    ("Cape Town", "JHB", 1400, "Linehaul"),
    ("Polokwane", "Musina", 200, "Regional"),
    ("Secunda", "Richards Bay", 500, "Hazchem Corridor"),
]


# ---------------------------------------------------------
# SEASONAL + PROFILED HELPERS
# ---------------------------------------------------------

def pick_season():
    month = datetime.now().month
    if month in (12, 1, 2): return "Summer"
    if month in (3, 4, 5): return "Autumn"
    if month in (6, 7, 8): return "Winter"
    return "Spring"

def derive_tonnage(client: str, season: str) -> float:
    profile = CLIENT_PROFILES.get(client, {"tons_range": (18, 32)})
    base_min, base_max = profile["tons_range"]
    if season in ("Summer", "Spring") and "FMCG" in profile.get("commodities", []):
        base_min += 2; base_max += 2
    if season == "Winter" and client in ("Anglo American", "Glencore"):
        base_min += 2; base_max += 2
    return random.randint(base_min, base_max)

def pick_commodity(client: str, season: str) -> str:
    profile = CLIENT_PROFILES.get(client)
    candidates = profile["commodities"] if profile else ["General Cargo", "FMCG", "Coal", "Chemicals"]
    if season in ("Spring", "Summer") and "FMCG" in candidates:
        weights = [2 if c == "FMCG" else 1 for c in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]
    return random.choice(candidates)


# ---------------------------------------------------------
# MAIN SIMULATION ENGINE
# ---------------------------------------------------------

def inject_sovereign_data():
    """
    Injects synthetic simulation data into the sovereign logistics DB.
    Fully aligned with init_db() schema.
    Includes diagnostic output for debugging and confirmation.
    """

    print("[SIMULATION] Sovereign injector triggered")

    # ---------------------------------------------------------
    # 0. ENSURE TABLES EXIST
    # ---------------------------------------------------------
    run_query("""CREATE TABLE IF NOT EXISTS ind_rfqs (
        rfq_id TEXT PRIMARY KEY, client TEXT, origin TEXT, destination TEXT,
        tons REAL, commodity TEXT, status TEXT, created_at DATETIME
    );""")

    run_query("""CREATE TABLE IF NOT EXISTS log_vehicles (
        reg_number TEXT PRIMARY KEY, type TEXT, make_model TEXT, fuel_rating REAL,
        status TEXT DEFAULT 'Idle', driver_name TEXT, location TEXT DEFAULT 'Depot',
        last_lat REAL, last_lon REAL
    );""")

    run_query("""CREATE TABLE IF NOT EXISTS gps_pings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, reg_number TEXT, timestamp TEXT,
        latitude REAL, longitude REAL, speed REAL, heading REAL,
        ignition INTEGER, signal_quality REAL, source TEXT
    );""")

    season = pick_season()
    print(f"[SIMULATION] Season detected: {season}")

    # ---------------------------------------------------------
    # 1. FLEET INJECTION
    # ---------------------------------------------------------
    fleet = [
        ("TRK-001", "Interlink", "Volvo FH 540", 38.5, "Idle", "Solomon M.", "Depot", -26.2041, 28.0473),
        ("TRK-002", "Interlink", "Scania R560", 36.2, "Idle", "David K.", "Depot", -26.2041, 28.0473),
        ("TRK-003", "Tautliner", "Mercedes Actros", 35.0, "Idle", "Thomas Z.", "JHB Yard", -26.1929, 28.0305),
        ("TRK-004", "Rigid", "Isuzu NPR 400", 18.0, "Idle", "Samson J.", "Depot", -26.2041, 28.0473),
        ("TRK-005", "Flat Deck", "MAN TGS", 37.5, "Idle", "Michael B.", "Richards Bay", -28.7830, 32.0377),
    ]

    for truck in fleet:
        result = run_query("""
            INSERT OR IGNORE INTO log_vehicles (
                reg_number, type, make_model, fuel_rating,
                status, driver_name, location, last_lat, last_lon
            ) VALUES (:r, :t, :m, :f, :s, :d, :l, :lat, :lon)
        """, {
            "r": truck[0], "t": truck[1], "m": truck[2], "f": truck[3],
            "s": truck[4], "d": truck[5], "l": truck[6], "lat": truck[7], "lon": truck[8]
        })
        print(f"[FLEET] Injected {truck[0]}: {result}")

    # ---------------------------------------------------------
    # 2. GPS PINGS
    # ---------------------------------------------------------
    for truck in fleet:
        result = run_query("""
            INSERT INTO gps_pings (
                reg_number, timestamp, latitude, longitude,
                speed, heading, ignition, signal_quality, source
            ) VALUES (:r, :ts, :lat, :lon, 0, 0, 1, 1.0, 'SIM')
        """, {
            "r": truck[0], "ts": datetime.now().isoformat(),
            "lat": truck[7], "lon": truck[8]
        })
        print(f"[GPS] Pinged {truck[0]}: {result}")

    # ---------------------------------------------------------
    # 3. RFQ INJECTION
    # ---------------------------------------------------------
    df_rfqs = load_data("SELECT COUNT(*) AS cnt FROM ind_rfqs")
    current_count = df_rfqs.iloc[0]["cnt"] if not df_rfqs.empty else 0
    needed = max(0, 10 - current_count)
    print(f"[RFQ] Current count: {current_count} | Injecting: {needed}")

    for _ in range(needed):
        client = random.choice(list(CLIENT_PROFILES.keys()))
        origin, dest, _, _ = random.choice(ROUTES)
        rfq_id = f"RFQ-{str(uuid.uuid4())[:8].upper()}"

        result = run_query("""
            INSERT INTO ind_rfqs (
                rfq_id, client, origin, destination,
                tons, commodity, status, created_at
            ) VALUES (:id, :client, :origin, :dest, :tons, :comm, 'Pending', :ts)
        """, {
            "id": rfq_id,
            "client": client,
            "origin": origin,
            "dest": dest,
            "tons": derive_tonnage(client, season),
            "comm": pick_commodity(client, season),
            "ts": datetime.now().isoformat()
        })
        print(f"[RFQ] Injected {rfq_id}: {result}")

    print("[SIMULATION] Injection complete.")
    return True


