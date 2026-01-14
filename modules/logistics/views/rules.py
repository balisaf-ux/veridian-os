# modules/logistics/rules.py
import pandas as pd
from modules.logistics.db_utils import load_data


# =========================================================
# PHYSICAL CAPABILITIES
# =========================================================

def get_physics_from_type(truck_type):
    """
    Returns the physical capabilities based on the trailer configuration.
    """
    t = str(truck_type).lower()

    # LOGIC: Define Tonnage
    max_tons = 14  # Default
    if "interlink" in t:
        max_tons = 36
    elif "tri-axle" in t:
        max_tons = 28
    elif "tautliner" in t:
        max_tons = 34
    elif "rigid" in t:
        max_tons = 8
    elif "tipper" in t:
        max_tons = 34
    elif "flat deck" in t:
        max_tons = 30

    # LOGIC: Define Hazchem Compliance
    is_hazchem = True if ("tautliner" in t or "rigid" in t) else False

    return max_tons, is_hazchem


# =========================================================
# AVAILABILITY FORECAST
# =========================================================

def calculate_availability(status):
    """
    Predicts availability based on current status.
    """
    s = str(status).lower()
    if "idle" in s:
        return "🟢 IMMEDIATELY"
    if "active" in s:
        return "🔴 +4 Hours"
    if "en route" in s:
        return "🟡 +6 Hours"
    if "at site" in s:
        return "🔵 +2 Hours"
    if "maintenance" in s:
        return "⚙️ +24 Hours"
    return "⚫ Unknown"


# =========================================================
# STATUS EMOJIS
# =========================================================

def status_emoji(status):
    s = str(status).lower()
    if "idle" in s:
        return "🟢 Idle"
    if "active" in s:
        return "🔴 Active"
    if "en route" in s:
        return "🟡 En Route"
    if "at site" in s:
        return "🔵 At Site"
    if "maintenance" in s:
        return "⚙️ Maintenance"
    return "⚫ Unknown"


# =========================================================
# MISSION CONTEXT ENRICHMENT
# =========================================================

def attach_mission_context(df):
    """
    Attaches mission context to each vehicle:
    - current mission
    - mission status
    - mission client
    - mission start time
    - mission driver
    - last 3 missions (history)
    """
    if df.empty:
        # Make sure columns still exist on empty frames
        df["current_mission"] = None
        df["mission_status"] = None
        df["mission_client"] = None
        df["mission_start"] = None
        df["mission_driver"] = None
        df["mission_history"] = None
        return df

    enriched_rows = []

    for _, row in df.iterrows():
        reg = row.get("reg_number")

        # Guard against missing reg_number
        if not reg:
            row["current_mission"] = None
            row["mission_status"] = None
            row["mission_client"] = None
            row["mission_start"] = None
            row["mission_driver"] = None
            row["mission_history"] = pd.DataFrame()
            enriched_rows.append(row)
            continue

        # Latest mission for this vehicle
        mission_df = load_data(
            """
            SELECT *
            FROM log_missions
            WHERE reg_number = :r
            ORDER BY id DESC
            LIMIT 1
            """,
            {"r": reg},
        )

        if mission_df.empty:
            row["current_mission"] = None
            row["mission_status"] = None
            row["mission_client"] = None
            row["mission_start"] = None
            row["mission_driver"] = None
        else:
            m = mission_df.iloc[0]
            row["current_mission"] = m.get("mission_name")
            row["mission_status"] = m.get("status")
            # For now mission_client == mission_name (no separate client field yet)
            row["mission_client"] = m.get("mission_name")
            row["mission_start"] = m.get("start_time")
            row["mission_driver"] = m.get("driver_name")

        # Last 3 missions for this vehicle
        history_df = load_data(
            """
            SELECT mission_name, status, start_time, end_time
            FROM log_missions
            WHERE reg_number = :r
            ORDER BY id DESC
            LIMIT 3
            """,
            {"r": reg},
        )
        row["mission_history"] = history_df

        enriched_rows.append(row)

    return pd.DataFrame(enriched_rows)


# =========================================================
# LOCATION INTELLIGENCE
# =========================================================

def clean_location(loc):
    if not loc or str(loc).strip() == "":
        return "Unknown"
    loc = str(loc)
    if "Yard" in loc:
        return loc
    if "Depot" in loc:
        return loc
    if "Port" in loc:
        return loc
    if "Site" in loc:
        return loc
    return loc


# =========================================================
# MASTER ENRICHMENT FUNCTION
# =========================================================

def enrich_fleet_data(df):
    """
    Unified enrichment layer for:
    - Fleet Registry
    - Driver Portal
    - Dispatch
    - Route Planner
    - Risk & Fuel

    Guarantees presence of:
    - status_signal, mission_client, mission_status, mission_driver
    - location_clean, is_idle, is_active, is_enroute, is_atsite
    - availability_forecast, max_tons, hazchem_compliant, mission_history
    """
    # Ensure we have a DataFrame
    if df is None:
        df = pd.DataFrame()

    if df.empty:
        # Still guarantee presence of expected columns
        for col in [
            "status_signal",
            "mission_client",
            "mission_status",
            "mission_driver",
            "current_mission",
            "mission_start",
            "location_clean",
            "is_idle",
            "is_active",
            "is_enroute",
            "is_atsite",
            "availability_forecast",
            "max_tons",
            "hazchem_compliant",
            "mission_history",
        ]:
            df[col] = None
        return df

    df = df.copy()

    # Ensure columns exist before we derive from them
    if "type" not in df.columns:
        df["type"] = "Interlink"  # safe default

    if "status" not in df.columns:
        df["status"] = "Idle"

    if "location" not in df.columns:
        df["location"] = "Unknown"

    # -----------------------------------------
    # 1. Physics
    # -----------------------------------------
    physics = df["type"].apply(get_physics_from_type)
    df["max_tons"] = [p[0] for p in physics]
    df["hazchem_compliant"] = [p[1] for p in physics]

    # -----------------------------------------
    # 2. Availability
    # -----------------------------------------
    df["availability_forecast"] = df["status"].apply(calculate_availability)

    # -----------------------------------------
    # 3. Status Emojis (signal)
    # -----------------------------------------
    df["status_signal"] = df["status"].apply(status_emoji)

    # Boolean flags for quick filtering
    s_lower = df["status"].astype(str).str.lower()
    df["is_idle"] = s_lower == "idle"
    df["is_active"] = s_lower == "active"
    df["is_enroute"] = s_lower.str.contains("en route")
    df["is_atsite"] = s_lower.str.contains("at site")

    # -----------------------------------------
    # 4. Location Intelligence
    # -----------------------------------------
    df["location_clean"] = df["location"].apply(clean_location)

    # -----------------------------------------
    # 5. Mission Context
    # -----------------------------------------
    df = attach_mission_context(df)

    # Final safety: ensure all expected columns exist
    for col in [
        "status_signal",
        "mission_client",
        "mission_status",
        "mission_driver",
        "current_mission",
        "mission_start",
        "location_clean",
        "is_idle",
        "is_active",
        "is_enroute",
        "is_atsite",
        "availability_forecast",
        "max_tons",
        "hazchem_compliant",
        "mission_history",
    ]:
        if col not in df.columns:
            df[col] = None

    return df
