import random
from datetime import datetime
from modules.logistics.db_utils import run_query, load_data


# ---------------------------------------------------------
# 1. GPS TABLE INITIALIZATION
# ---------------------------------------------------------

def ensure_gps_table():
    run_query("""
        CREATE TABLE IF NOT EXISTS gps_pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_number TEXT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL,
            speed REAL,
            heading REAL,
            ignition INTEGER,
            signal_quality REAL,
            source TEXT
        )
    """)
    return True


# ---------------------------------------------------------
# 2. SYNTHETIC GPS GENERATOR
# ---------------------------------------------------------

def generate_synthetic_gps(reg_number, lat, lon):
    drift_lat = random.uniform(-0.0008, 0.0008)
    drift_lon = random.uniform(-0.0008, 0.0008)

    new_lat = lat + drift_lat
    new_lon = lon + drift_lon

    return {
        "reg_number": reg_number,
        "timestamp": datetime.now().isoformat(),
        "latitude": new_lat,
        "longitude": new_lon,
        "speed": random.uniform(20, 80),
        "heading": random.uniform(0, 360),
        "ignition": 1,
        "signal_quality": random.uniform(0.8, 1.0),
        "source": "synthetic"
    }


# ---------------------------------------------------------
# 3. GPS INGESTION LOOP
# ---------------------------------------------------------

def ingest_synthetic_gps():
    ensure_gps_table()

    fleet = load_data("""
        SELECT reg_number, last_lat, last_lon 
        FROM log_vehicles
    """)

    if fleet.empty:
        return False

    for _, row in fleet.iterrows():
        ping = generate_synthetic_gps(
            row["reg_number"],
            row["last_lat"],
            row["last_lon"]
        )

        # Insert GPS ping
        run_query("""
            INSERT INTO gps_pings 
            (reg_number, timestamp, latitude, longitude, speed, heading, ignition, signal_quality, source)
            VALUES (:reg_number, :timestamp, :latitude, :longitude, :speed, :heading, :ignition, :signal_quality, :source)
        """, ping)

        # Update live fleet position
        run_query("""
            UPDATE log_vehicles
            SET last_lat = :latitude,
                last_lon = :longitude
            WHERE reg_number = :reg_number
        """, ping)

    return True


# ---------------------------------------------------------
# 4. PUBLIC ENTRYPOINT
# ---------------------------------------------------------

def run_gps_simulation():
    """
    Call this from Streamlit or any service.
    It injects one round of GPS updates for all vehicles.
    """
    return ingest_synthetic_gps()
