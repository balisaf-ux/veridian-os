import pandas as pd
import numpy as np

def enrich_fleet_data(df_fleet):
    """
    Applies business rules to the raw fleet dataframe.
    Ensures all downstream modules receive a complete, safe, enriched dataset.
    """

    if df_fleet.empty:
        return df_fleet

    df = df_fleet.copy()

    # =========================================================
    # 1. LOCATION NORMALIZATION
    # =========================================================
    if "location" in df.columns:
        df["location_clean"] = df["location"].fillna("Unknown")
    else:
        df["location_clean"] = "Unknown"

    # =========================================================
    # 2. STATUS SIGNAL + IDLE FLAG + MISSION STATUS
    # =========================================================
    if "status" in df.columns:
        df["status_signal"] = df["status"].fillna("Unknown")
        df["is_idle"] = df["status"] == "Idle"
        df["mission_status"] = df["status"]
    else:
        df["status_signal"] = "Unknown"
        df["is_idle"] = False
        df["mission_status"] = "Unknown"

    # =========================================================
    # 3. DRIVER + MISSION CONTEXT
    # =========================================================
    if "driver_name" not in df.columns:
        df["driver_name"] = None

    if "mission_client" not in df.columns:
        df["mission_client"] = "Unassigned"

    if "mission_driver" not in df.columns:
        df["mission_driver"] = df["driver_name"]

    # =========================================================
    # 4. FORECASTING + CAPACITY + COMPLIANCE
    # =========================================================
    if "availability_forecast" not in df.columns:
        df["availability_forecast"] = "Now"

    if "max_tons" not in df.columns:
        df["max_tons"] = 34.0  # Default interlink capacity

    if "hazchem_compliant" not in df.columns:
        df["hazchem_compliant"] = False

    # =========================================================
    # 5. MISSION HISTORY PLACEHOLDER
    # =========================================================
    if "mission_history" not in df.columns:
        df["mission_history"] = None

    # =========================================================
    # 6. MISSION START PLACEHOLDER
    # =========================================================
    if "mission_start" not in df.columns:
        df["mission_start"] = None
    if "mission_history" not in df.columns:
        df["mission_history"] = None # Mission Start Placeholder
    if "mission_start" not in df.columns:
        df["mission_start"] = None

    # =========================================================
    # 7. PHYSICS PLACEHOLDERS (Future Integration)
    # =========================================================
    if "physics_ok" not in df.columns:
        df["physics_ok"] = True

    if "load_rating" not in df.columns:
        df["load_rating"] = df["max_tons"]

    return df
