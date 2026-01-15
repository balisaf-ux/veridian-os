import pandas as pd
import numpy as np

# ---------------------------------------------------------
# ROBUST IMPORTS
# ---------------------------------------------------------
try:
    from modules.logistics.db_utils import load_data
except ImportError:
    from .db_utils import load_data

try:
    from modules.logistics.services import calculate_asset_availability
except ImportError:
    # Safe fallback if services is not available
    def calculate_asset_availability(status):
        return "Unknown"


def _fetch_latest_mission(reg_number: str) -> dict:
    df = load_data(
        """
        SELECT mission_name, driver_name, status, start_time
        FROM log_missions
        WHERE reg_number = :r
        ORDER BY id DESC
        LIMIT 1
        """,
        {"r": reg_number},
    )
    if df.empty:
        return {
            "mission_name": None,
            "mission_driver": None,
            "mission_status": "Unassigned",
            "mission_start": None,
            "mission_client": None,
        }

    row = df.iloc[0]
    # mission_client can be inferred from mission_name pattern "Client - Product"
    mission_name = row.get("mission_name")
    mission_client = None
    if isinstance(mission_name, str) and " - " in mission_name:
        mission_client = mission_name.split(" - ", 1)[0]

    return {
        "mission_name": mission_name,
        "mission_driver": row.get("driver_name"),
        "mission_status": row.get("status", "Unknown"),
        "mission_start": row.get("start_time"),
        "mission_client": mission_client,
    }


def _fetch_mission_history(reg_number: str) -> pd.DataFrame | None:
    df = load_data(
        """
        SELECT mission_name, status, start_time, end_time
        FROM log_missions
        WHERE reg_number = :r
        ORDER BY id DESC
        LIMIT 3
        """,
        {"r": reg_number},
    )
    if df.empty:
        return None
    return df


def _fetch_latest_gps(reg_number: str) -> dict:
    df = load_data(
        """
        SELECT latitude, longitude, speed, heading, ignition, signal_quality
        FROM gps_pings
        WHERE reg_number = :r
        ORDER BY id DESC
        LIMIT 1
        """,
        {"r": reg_number},
    )
    if df.empty:
        return {
            "last_lat": None,
            "last_lon": None,
            "speed": None,
            "heading": None,
            "ignition": None,
            "signal_quality": None,
            "movement_status": "Unknown",
        }

    row = df.iloc[0]
    speed = row.get("speed", 0) or 0
    ignition = row.get("ignition", 1)

    if ignition == 0:
        movement_status = "Parked"
    elif speed > 5:
        movement_status = "In Transit"
    elif 0 <= speed <= 5:
        movement_status = "Stationary"
    else:
        movement_status = "Unknown"

    return {
        "last_lat": row.get("latitude"),
        "last_lon": row.get("longitude"),
        "speed": speed,
        "heading": row.get("heading"),
        "ignition": ignition,
        "signal_quality": row.get("signal_quality"),
        "movement_status": movement_status,
    }


def enrich_fleet_data(df_fleet: pd.DataFrame) -> pd.DataFrame:
    """
    Sovereign enrichment engine for fleet data.
    Ensures all downstream modules receive a complete, enriched dataset:
    - mission context (live + history)
    - GPS context (movement + coordinates)
    - availability forecast
    - physics placeholders
    """
    if df_fleet.empty:
        return df_fleet

    df = df_fleet.copy()

    # -----------------------------------------------------
    # 1. LOCATION NORMALISATION
    # -----------------------------------------------------
    if "location" in df.columns:
        df["location_clean"] = df["location"].fillna("Unknown")
    else:
        df["location_clean"] = "Unknown"

    # -----------------------------------------------------
    # 2. STATUS + IDLE FLAG + MISSION STATUS
    # -----------------------------------------------------
    if "status" in df.columns:
        df["status_signal"] = df["status"].fillna("Unknown")
        df["is_idle"] = df["status"] == "Idle"
        df["mission_status"] = df["status"]
    else:
        df["status_signal"] = "Unknown"
        df["is_idle"] = False
        df["mission_status"] = "Unknown"

    # -----------------------------------------------------
    # 3. DRIVER + BASE MISSION CONTEXT PLACEHOLDERS
    # -----------------------------------------------------
    if "driver_name" not in df.columns:
        df["driver_name"] = None

    if "mission_client" not in df.columns:
        df["mission_client"] = "Unassigned"

    if "mission_driver" not in df.columns:
        df["mission_driver"] = df["driver_name"]

    if "mission_start" not in df.columns:
        df["mission_start"] = None

    if "mission_history" not in df.columns:
        df["mission_history"] = None

    # -----------------------------------------------------
    # 4. CAPACITY + COMPLIANCE + AVAILABILITY
    # -----------------------------------------------------
    if "max_tons" not in df.columns:
        df["max_tons"] = 34.0  # Default interlink capacity

    if "hazchem_compliant" not in df.columns:
        df["hazchem_compliant"] = False

    # Availability forecast using sovereign logic
    df["availability_forecast"] = df["status_signal"].apply(
        lambda s: calculate_asset_availability(s)
    )

    # -----------------------------------------------------
    # 5. PHYSICS PLACEHOLDERS
    # -----------------------------------------------------
    if "physics_ok" not in df.columns:
        df["physics_ok"] = True

    if "load_rating" not in df.columns:
        df["load_rating"] = df["max_tons"]

    # -----------------------------------------------------
    # 6. GPS + MISSION ENRICHMENT (PER VEHICLE)
    # -----------------------------------------------------
    # Ensure reg_number exists
    if "reg_number" not in df.columns:
        return df  # Cannot enrich without a key

    enriched_rows = []

    for _, row in df.iterrows():
        reg = row.get("reg_number")

        # Mission context
        mission_ctx = _fetch_latest_mission(reg)
        history_df = _fetch_mission_history(reg)

        # GPS context
        gps_ctx = _fetch_latest_gps(reg)

        enriched_row = row.copy()

        # Mission fields
        enriched_row["mission_client"] = mission_ctx["mission_client"] or row.get(
            "mission_client", "Unassigned"
        )
        enriched_row["mission_driver"] = mission_ctx["mission_driver"] or row.get(
            "driver_name"
        )
        enriched_row["mission_status"] = mission_ctx["mission_status"] or row.get(
            "mission_status", "Unknown"
        )
        enriched_row["mission_start"] = mission_ctx["mission_start"]
        enriched_row["mission_history"] = history_df

        # GPS fields
        # Prefer GPS last_lat/last_lon, fall back to existing columns if present
        enriched_row["last_lat"] = gps_ctx["last_lat"] if gps_ctx["last_lat"] is not None else row.get(
            "last_lat"
        )
        enriched_row["last_lon"] = gps_ctx["last_lon"] if gps_ctx["last_lon"] is not None else row.get(
            "last_lon"
        )
        enriched_row["speed"] = gps_ctx["speed"]
        enriched_row["heading"] = gps_ctx["heading"]
        enriched_row["ignition"] = gps_ctx["ignition"]
        enriched_row["signal_quality"] = gps_ctx["signal_quality"]
        enriched_row["movement_status"] = gps_ctx["movement_status"]

        enriched_rows.append(enriched_row)

    df_enriched = pd.DataFrame(enriched_rows)

    return df_enriched

