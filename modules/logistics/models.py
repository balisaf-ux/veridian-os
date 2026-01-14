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
    "Anglo American": {
        "commodities": ["Coal", "Ore", "Concentrate"],
        "tons_range": (28, 34),
    },
    "Shoprite DC": {
        "commodities": ["FMCG", "Chilled Goods", "Dry Goods"],
        "tons_range": (12, 28),
    },
    "Massmart": {
        "commodities": ["FMCG", "Electronics", "Bulk Retail"],
        "tons_range": (18, 32),
    },
    "Glencore": {
        "commodities": ["Coal", "Metals"],
        "tons_range": (28, 34),
    },
    "Sasol": {
        "commodities": ["Chemicals", "Fuels"],
        "tons_range": (20, 32),
    },
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
    if month in (12, 1, 2):
        return "Summer"
    if month in (3, 4, 5):
        return "Autumn"
    if month in (6, 7, 8):
        return "Winter"
    return "Spring"


def derive_tonnage(client: str, season: str) -> float:
    profile = CLIENT_PROFILES.get(client, {"tons_range": (18, 32)})
    base_min, base_max = profile["tons_range"]

    # Seasonal modulation
    if season in ("Summer", "Spring") and "FMCG" in profile.get("commodities", []):
        base_min += 2
        base_max += 2
    if season == "Winter" and client in ("Anglo American", "Glencore"):
        base_min += 2
        base_max += 2

    return random.randint(base_min, base_max)


def pick_commodity(client: str, season: str) -> str:
    profile = CLIENT_PROFILES.get(client)
    if profile:
        candidates = profile["commodities"]
    else:
        candidates = ["General Cargo", "FMCG", "Coal", "Chemicals"]

    # Seasonal bias
    if season in ("Spring", "Summer") and "FMCG" in candidates:
        weights = [2 if c == "FMCG" else 1 for c in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]

    return random.choice(candidates)


def route_difficulty(distance_km: int, corridor_type: str) -> str:
    score = 0
    if distance_km > 800:
        score += 2
    elif distance_km > 400:
        score += 1

    if corridor_type == "Hazchem Corridor":
        score += 2
    elif corridor_type == "Industrial":
        score += 1

    if score >= 3:
        return "High"
    if score == 2:
        return "Medium"
    return "Low"


# ---------------------------------------------------------
# MAIN SIMULATION ENGINE
# ---------------------------------------------------------

def inject_sovereign_data():
    """
    Injects synthetic simulation data.
    Fully compatible with 'fleet_data.db' schema (Text IDs).
    NOW INCLUDES: Force-Creation of Tables to prevent 'Missing Table' errors.
    """
    
    # ---------------------------------------------------------
    # 0. FORCE-CREATE TABLES (The Critical Fix)
    # ---------------------------------------------------------
    # Ensure RFQ table exists
    run_query("""
        CREATE TABLE IF NOT EXISTS ind_rfqs (
            rfq_id TEXT PRIMARY KEY,
            client TEXT,
            origin TEXT,
            destination TEXT,
            tons REAL,
            commodity TEXT,
            status TEXT,
            created_at DATETIME
        );
    """)
    
    # Ensure Vehicle table exists
    run_query("""
        CREATE TABLE IF NOT EXISTS log_vehicles (
            reg_number TEXT PRIMARY KEY,
            type TEXT,
            make_model TEXT,
            fuel_rating REAL,
            status TEXT DEFAULT 'Idle',
            driver_name TEXT,
            location TEXT DEFAULT 'Depot'
        );
    """)

    season = pick_season()

    # ---------------------------------------------------------
    # 1. FLEET INJECTION (Cold Start Protection)
    # ---------------------------------------------------------
    existing_fleet = load_data("SELECT count(*) as cnt FROM log_vehicles")
    if existing_fleet.empty or existing_fleet.iloc[0]['cnt'] == 0:
        fleet = [
            ("TRK-001", "Interlink", "Volvo FH 540", 38.5, "Idle", "Solomon M.", "Depot"),
            ("TRK-002", "Interlink", "Scania R560", 36.2, "Idle", "David K.", "Depot"),
            ("TRK-003", "Tautliner", "Mercedes Actros", 35.0, "Idle", "Thomas Z.", "JHB Yard"),
            ("VAN-105", "Rigid", "Isuzu NPR 400", 18.0, "Idle", "Samson J.", "Depot"),
            ("FLT-200", "Flat Deck", "MAN TGS", 37.5, "Idle", "Michael B.", "Richards Bay"),
        ]
        
        for truck in fleet:
            run_query(
                """
                INSERT INTO log_vehicles (reg_number, type, make_model, fuel_rating, status, driver_name, location)
                VALUES (:r, :t, :m, :f, :s, :d, :l)
                """,
                {
                    "r": truck[0], "t": truck[1], "m": truck[2], 
                    "f": truck[3], "s": truck[4], "d": truck[5], "l": truck[6]
                }
            )

    # ---------------------------------------------------------
    # 2. RFQ GENERATION (Seasonal + Profiled)
    # ---------------------------------------------------------
    for _ in range(5):
        client = random.choice(list(CLIENT_PROFILES.keys()))
        origin, dest, dist, corridor = random.choice(ROUTES)

        commodity = pick_commodity(client, season)
        tons = derive_tonnage(client, season)
        # difficulty = route_difficulty(dist, corridor) # Reserved for Risk Module

        rfq_id = f"RFQ-{str(uuid.uuid4())[:8].upper()}"

        run_query(
            """
            INSERT INTO ind_rfqs (rfq_id, client, origin, destination, tons, commodity, status, created_at)
            VALUES (:id, :c, :o, :d, :t, :comm, 'Pending', :ts)
            """,
            {
                "id": rfq_id,
                "c": f"{client}",
                "o": origin,
                "d": dest,
                "t": tons,
                "comm": commodity,
                "ts": datetime.now().isoformat(),
            }
        )

    # ---------------------------------------------------------
    # 3. RESET STATUS (Ensure availability)
    # ---------------------------------------------------------
    run_query(
        "UPDATE log_vehicles SET status='Idle' WHERE reg_number IN ('TRK-002', 'VAN-105')"
    )

    return True
