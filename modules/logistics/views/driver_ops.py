import streamlit as st
from datetime import datetime

# Robust imports
try:
    from modules.logistics.db_utils import load_data, run_query
    from modules.logistics.rules import enrich_fleet_data
except ImportError:
    from ..db_utils import load_data, run_query
    from ..rules import enrich_fleet_data


# =========================================================
# DRIVER PORTAL (SOVEREIGN-ALIGNED)
# =========================================================

def render_driver_portal(df_fleet_raw):

    df_fleet = enrich_fleet_data(df_fleet_raw.copy())

    st.markdown("## 🚛 Driver Portal | Mission Control")

    render_availability_roster(df_fleet)

    drivers = ["Solomon M.", "David K.", "Thomas Z.", "Samson J.", "Michael B."]
    driver_id = st.selectbox("👤 Select Operator", ["-- Select --"] + drivers)

    if driver_id == "-- Select --":
        st.info("Identify yourself to continue.")
        return

    st.markdown(
        """
        **Mission Lifecycle:**  
        `Dispatch → Staged → Loading → Weigh Out → Documentation → Active → En Route → At Site → Closed`
        """
    )

    tab_mission, tab_start, tab_handover, tab_incident = st.tabs([
        "⚡ Active Mission",
        "🚀 Start Mission",
        "🔄 Handover",
        "🚨 Incident Log",
    ])

    with tab_mission:
        show_active_mission(driver_id, df_fleet)

    with tab_start:
        show_start_mission(driver_id, df_fleet)

    with tab_handover:
        show_handover(driver_id, df_fleet)

    with tab_incident:
        show_incident_logger(driver_id, df_fleet)


# =========================================================
# AVAILABILITY ROSTER
# =========================================================

def render_availability_roster(df_fleet):
    st.subheader("🧭 Live Driver & Fleet Roster")

    if df_fleet.empty:
        st.warning("Fleet registry is empty.")
        return

    roster = df_fleet.copy()
    roster["Driver"] = roster["driver_name"].fillna("—")
    roster["Vehicle"] = roster["reg_number"]
    roster["Location"] = roster["location_clean"]
    roster["Status"] = roster["status_signal"]

    st.dataframe(
        roster[["Driver", "Vehicle", "Location", "Status"]],
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# ACTIVE MISSION VIEW
# =========================================================

def show_active_mission(driver_id, df_fleet):

    active = df_fleet[
        (df_fleet["driver_name"] == driver_id) &
        (df_fleet["mission_status"].isin([
            "Staged", "Loading", "Weigh Out", "Documentation",
            "Active", "En Route", "At Site"
        ]))
    ]

    if active.empty:
        st.info("No active mission assigned.")
        return

    row = active.iloc[0]
    reg = row["reg_number"]

    st.success(f"⚡ ACTIVE MISSION | {reg} → {row['mission_client']}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Status", row["status_signal"])
    c2.metric("Movement", row["movement_status"])
    c3.metric("Vehicle", reg)

    st.caption(f"Mission Status: **{row['mission_status']}**")
    st.caption(f"Started: {row['mission_start']}")

    st.divider()

    # ARRIVAL
    if row["mission_status"] != "At Site":
        if st.button("ARRIVED AT SITE", type="primary"):
            run_query(
                "UPDATE log_vehicles SET status='At Site', location='Client Site' WHERE reg_number=:r",
                {"r": reg},
            )
            run_query(
                """
                UPDATE log_missions
                SET status='At Site', location='Client Site'
                WHERE reg_number=:r AND status!='Closed'
                """,
                {"r": reg},
            )
            st.rerun()
    else:
        st.info("Vehicle is At Site")

    # CLOSE MISSION
    pod = st.file_uploader("Upload POD (Required)", type=["jpg", "png", "pdf", "jpeg"])

    if st.button("CLOSE MISSION"):
        if pod is None:
            st.error("Upload POD first.")
        else:
            run_query(
                "UPDATE log_vehicles SET status='Idle', driver_name=NULL WHERE reg_number=:r",
                {"r": reg},
            )
            run_query(
                """
                UPDATE log_missions
                SET status='Closed', end_time=CURRENT_TIMESTAMP
                WHERE reg_number=:r AND status!='Closed'
                """,
                {"r": reg},
            )
            st.balloons()
            st.rerun()


# =========================================================
# START MISSION (PRE-TRIP)
# =========================================================

def show_start_mission(driver_id, df_fleet):

    idle = df_fleet[df_fleet["is_idle"]]["reg_number"].tolist()

    if not idle:
        st.warning("No idle vehicles available for assignment.")
        return

    st.subheader("🚀 Start Mission | Pre‑Trip Inspection")

    reg = st.selectbox("Select Vehicle", idle)
    mission_name = st.text_input("Client / Mission Name")

    # 3-layer checklist
    mech_results = render_checklist_group("mech", [
        ("Brakes", True),
        ("Tires", True),
        ("Lights", True),
        ("Fluids", True),
        ("Wipers", False),
        ("Leaks", True),
    ])

    trailer_results = render_checklist_group("trailer", [
        ("Landing legs", True),
        ("Susie cables", True),
        ("Twist locks", True),
        ("Air pressure", False),
    ])

    driver_results = render_checklist_group("driver", [
        ("License & PrDP valid", True),
        ("Logbook up to date", True),
        ("PPE in place", False),
        ("Fit to drive", True),
    ])

    all_results = mech_results + trailer_results + driver_results

    critical_missing = [label for label, checked, critical in all_results if critical and not checked]
    noncritical_missing = [label for label, checked, critical in all_results if not critical and not checked]

    if critical_missing:
        st.error("Critical items missing:\n- " + "\n- ".join(critical_missing))

    if noncritical_missing:
        st.warning("Non‑critical items missing:\n- " + "\n- ".join(noncritical_missing))

    if st.button("START MISSION", type="primary"):

        if not mission_name.strip():
            st.error("Enter a mission name.")
            return

        if critical_missing:
            log_pretrip_event(driver_id, reg, mission_name, "PRETRIP_BLOCKED", critical_missing, noncritical_missing)
            st.error("Mission blocked due to critical safety issues.")
            return

        if noncritical_missing:
            log_pretrip_event(driver_id, reg, mission_name, "PRETRIP_EXCEPTIONS", [], noncritical_missing)

        run_query(
            "UPDATE log_vehicles SET status='Active', driver_name=:d WHERE reg_number=:r",
            {"d": driver_id, "r": reg},
        )

        run_query(
            """
            INSERT INTO log_missions (mission_name, reg_number, driver_name, start_time, status)
            VALUES (:m, :r, :d, CURRENT_TIMESTAMP, 'Active')
            """,
            {"m": mission_name, "r": reg, "d": driver_id},
        )

        st.success("Mission started.")
        st.rerun()


# =========================================================
# CHECKLIST RENDERER
# =========================================================

def render_checklist_group(prefix, items):
    results = []
    cols = st.columns(2)

    for idx, (label, critical) in enumerate(items):
        col = cols[idx % 2]
        with col:
            checked = st.checkbox(f"{label}" + (" *" if critical else ""), key=f"{prefix}_{label}")
            results.append((label, checked, critical))

    st.caption("_Items marked with * are critical._")
    return results


# =========================================================
# PRETRIP EVENT LOGGER
# =========================================================

def log_pretrip_event(driver_id, reg, mission_name, event_type, critical_missing, noncritical_missing):

    details = (
        f"[{event_type}] Driver: {driver_id} | Vehicle: {reg} | Mission: {mission_name}\n"
        f"Critical missing: {', '.join(critical_missing) if critical_missing else 'None'}\n"
        f"Non‑critical missing: {', '.join(noncritical_missing) if noncritical_missing else 'None'}"
    )

    run_query(
        """
        INSERT INTO log_incidents (driver, reg_number, details, timestamp)
        VALUES (:d, :r, :det, :ts)
        """,
        {"d": driver_id, "r": reg, "det": details, "ts": datetime.now()},
    )


# =========================================================
# HANDOVER VIEW
# =========================================================

def show_handover(driver_id, df_fleet):

    st.subheader("🔄 Dual‑Driver Handover")

    active = df_fleet[
        (df_fleet["mission_status"].isin([
            "Staged", "Loading", "Weigh Out", "Documentation",
            "Active", "En Route", "At Site"
        ])) &
        (df_fleet["driver_name"] != driver_id)
    ]

    if active.empty:
        st.info("No active convoys available for handover.")
        return

    active["label"] = active["reg_number"] + " (" + active["driver_name"].astype(str) + ")"
    selection = st.selectbox("Select Unit", active["label"])

    reg = selection.split(" ")[0]

    if st.button(f"TAKE CONTROL OF {reg}"):

        run_query(
            "UPDATE log_vehicles SET driver_name=:d WHERE reg_number=:r",
            {"d": driver_id, "r": reg},
        )

        run_query(
            """
            UPDATE log_missions
            SET driver_name=:d
            WHERE reg_number=:r AND status!='Closed'
            """,
            {"d": driver_id, "r": reg},
        )

        st.success("Handover complete.")
        st.rerun()


# =========================================================
# INCIDENT LOGGER
# =========================================================

def show_incident_logger(driver_id, df_fleet):

    st.subheader("🚨 Incident Logging")

    current = df_fleet[df_fleet["driver_name"] == driver_id]
    default_reg = current.iloc[0]["reg_number"] if not current.empty else "UNKNOWN"

    reg = st.text_input("Vehicle (reg number)", value=default_reg)
    incident_type = st.selectbox(
        "Incident Type",
        ["Traffic Fine", "Breakdown", "Accident", "Delay", "Pre‑Trip Exception", "Other"],
    )
    issue = st.text_area("Incident Details")

    if st.button("Log Incident"):

        details = f"[{incident_type}] {issue}"

        run_query(
            """
            INSERT INTO log_incidents (driver, reg_number, details, timestamp)
            VALUES (:d, :r, :det, :ts)
            """,
            {"d": driver_id, "r": reg, "det": details, "ts": datetime.now()},
        )

        st.success("Incident logged.")
