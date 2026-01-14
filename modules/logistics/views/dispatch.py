import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- ROBUST IMPORTS ---
try:
    from .db_utils import load_data, run_query
except ImportError:
    try:
        from ..db_utils import load_data, run_query
    except ImportError:
        from modules.logistics.db_utils import load_data, run_query

# Import Service / Logic Modules
try:
    from modules.logistics.models import inject_sovereign_data
    from modules.logistics.services import validate_physics_handshake, generate_dispatch_docs
    from modules.logistics.rules import enrich_fleet_data
except ImportError:
    # Fallback/Mock for standalone testing
    def inject_sovereign_data(): st.warning("Mock Injection")
    def validate_physics_handshake(*args): return True
    def enrich_fleet_data(df): return df
    def generate_dispatch_docs(trip): return b"%PDF-1.4\n% Placeholder Dispatch Pack\n"

# -------------------------------------------------------------------
# MAIN DISPATCH CONSOLE
# -------------------------------------------------------------------

st.write("RFQs in DB:", load_data("SELECT * FROM ind_rfqs").shape)
st.dataframe(load_data("SELECT * FROM ind_rfqs"))

def render_dispatch_console(df_orders, df_fleet):

    st.subheader("🏭 Live Operations & Weighbridge Console")

    # Enrich fleet with physics, availability, status signals, mission context, etc.
    df_rich = enrich_fleet_data(df_fleet.copy()) if not df_fleet.empty else df_fleet

    # Optional: quick operational snapshot for the dispatcher
    if not df_rich.empty:
        with st.expander("📍 Live Fleet Snapshot"):
            snapshot_cols = [
                "reg_number",
                "make_model",
                "status_signal",
                "location_clean",
                "availability_forecast",
                "max_tons",
                "hazchem_compliant",
            ]
            # Defensive: ensure columns exist before display
            valid_cols = [c for c in snapshot_cols if c in df_rich.columns]
            
            st.dataframe(
                df_rich[valid_cols],
                use_container_width=True,
                hide_index=True,
            )

    # Load active trips
    # Ensure table exists (Self-Healing)
    run_query("""
        CREATE TABLE IF NOT EXISTS log_dispatch_journal (
            trip_id TEXT PRIMARY KEY, rfq_ref TEXT, truck_reg TEXT, 
            driver TEXT, status TEXT, start_time DATETIME, 
            tare_weight REAL, gross_weight REAL, net_weight REAL, ticket_no TEXT, end_time DATETIME
        )
    """)

    df_active_trips = load_data(
        "SELECT * FROM log_dispatch_journal WHERE status != 'DISPATCHED'"
    )
    # Debug: check DB write mode
    st.write(run_query("PRAGMA journal_mode"))

    # Empty console
    if st.button("Inject Simulation Data"):
        success = inject_sovereign_data()
        if success:
            st.cache_data.clear()      # Clears cached DB reads
            st.success("Simulation data injected.")
            st.rerun()                 # Modern Streamlit rerun
        else:
            st.error("Injection failed.")

    col_queue, col_process = st.columns([1, 2])
    

    # =========================================================
    # LEFT: QUEUE
    # =========================================================
    with col_queue:
        st.markdown("##### 📋 Pending Queue")

        if df_orders.empty:
            st.info("No Pending Orders")
        else:
            # Enumerate to create unique keys if IDs are duplicates
            for idx, row in df_orders.iterrows():
                # Flexible schema handling (supports 'rfq_id' or 'id')
                rfq_id = row.get('rfq_id', row.get('id', f'UNK-{idx}'))
                client = row.get('client', 'Unknown Client')
                product = row.get('commodity', row.get('product', 'General Cargo'))
                volume = row.get('tons', row.get('volume', 0))
                route = row.get('route', f"{row.get('origin','?')} -> {row.get('destination','?')}")

                with st.expander(f"{client} ({product})"):
                    st.caption(f"Route: {route} | Vol: {volume}t")

                    if df_rich.empty:
                        st.warning("No fleet data available.")
                        continue

                    # Filter suitable vehicles: idle + enough capacity
                    if "is_idle" not in df_rich.columns:
                        df_rich["is_idle"] = df_rich["status"] == "Idle"
                    if "max_tons" not in df_rich.columns:
                        df_rich["max_tons"] = 34.0

                    suitable = df_rich[
                        (df_rich["is_idle"]) &
                        (df_rich["max_tons"] >= volume)
                    ]

                    if suitable.empty:
                        st.warning("No suitable idle vehicles.")
                        continue

                    truck_assign = st.selectbox(
                        "Assign Truck",
                        suitable["reg_number"].unique(),
                        key=f"t_{rfq_id}_{idx}" # Unique key
                    )

                    # Auto-fill driver if available
                    current_truck_drivers = suitable[suitable["reg_number"] == truck_assign]["driver_name"]
                    default_driver = current_truck_drivers.iloc[0] if not current_truck_drivers.empty else ""
                    
                    driver_assign = st.text_input(
                        "Driver Name",
                        value=default_driver if default_driver else "Driver",
                        key=f"d_{rfq_id}_{idx}" # Unique key
                    )

                    # Physics validation (using enriched suitable DF)
                    if st.button(f"Initiate Load {rfq_id}", key=f"init_{rfq_id}_{idx}"):
                        if not validate_physics_handshake(row, truck_assign, suitable):
                            st.error("❌ Physics Mismatch: Load exceeds truck capability.")
                            st.stop()

                        trip_id = f"TRIP-{int(time.time())}"

                        # 1) Create dispatch journal entry
                        run_query(
                            """
                            INSERT INTO log_dispatch_journal
                            (trip_id, rfq_ref, truck_reg, driver, status, start_time)
                            VALUES (:id, :rfq, :trk, :drv, 'GATE_IN', CURRENT_TIMESTAMP)
                            """,
                            {
                                "id": trip_id,
                                "rfq": str(rfq_id),
                                "trk": truck_assign,
                                "drv": driver_assign
                            }
                        )

                        # 2) Mark RFQ as processing
                        # Handle varied ID column name in SQL
                        id_col = 'rfq_id' if 'rfq_id' in df_orders.columns else 'id'
                        run_query(
                            f"UPDATE ind_rfqs SET status='Processing' WHERE {id_col}=:id",
                            {"id": rfq_id}
                        )

                        # 3) Create a staged mission
                        mission_name = f"{client} - {product}"
                        run_query(
                            """
                            INSERT INTO log_missions (mission_name, reg_number, driver_name, start_time, status)
                            VALUES (:m, :r, :d, CURRENT_TIMESTAMP, 'Staged')
                            """,
                            {
                                "m": mission_name,
                                "r": truck_assign,
                                "d": driver_assign,
                            }
                        )

                        st.success(f"Trip {trip_id} Initiated and Mission Staged.")
                        st.rerun()

    # =========================================================
    # RIGHT: WORKFLOW
    # =========================================================
    with col_process:
        st.markdown("##### ⚙️ Active Loading Bays")

        if df_active_trips.empty:
            st.info("No active trucks in bay.")
            return

        trip_sel = st.selectbox(
            "Select Active Operation",
            df_active_trips["trip_id"].unique()
        )

        curr_trip = df_active_trips[
            df_active_trips["trip_id"] == trip_sel
        ].iloc[0]

        # Progress bar
        stages = {
            "GATE_IN": 25,
            "WEIGH_IN": 50,
            "LOADING": 75,
            "WEIGH_OUT": 90,
            "DOCUMENTATION": 100
        }

        st.progress(stages.get(curr_trip["status"], 0))
        st.caption(
            f"Status: **{curr_trip['status']}** | Asset: {curr_trip['truck_reg']}"
        )
        st.divider()

        # -------------------------
        # STEP 1: GATE IN
        # -------------------------
        if curr_trip["status"] == "GATE_IN":
            st.info("🔹 STEP 1: WEIGHBRIDGE IN (TARE)")
            tare = st.number_input("Tare Weight (kg)", value=14500)

            if st.button("Confirm Tare"):
                run_query(
                    """
                    UPDATE log_dispatch_journal
                    SET status='LOADING', tare_weight=:w
                    WHERE trip_id=:id
                    """,
                    {"w": tare, "id": trip_sel}
                )

                _update_latest_mission_status(curr_trip["truck_reg"], "Loading")
                st.rerun()

        # -------------------------
        # STEP 2: LOADING
        # -------------------------
        elif curr_trip["status"] == "LOADING":
            st.info("🔹 STEP 2: LOADING BAY")

            if st.button("Loading Complete"):
                run_query(
                    """
                    UPDATE log_dispatch_journal
                    SET status='WEIGH_OUT'
                    WHERE trip_id=:id
                    """,
                    {"id": trip_sel}
                )

                _update_latest_mission_status(curr_trip["truck_reg"], "Weigh Out")
                st.rerun()

        # -------------------------
        # STEP 3: WEIGH OUT
        # -------------------------
        elif curr_trip["status"] == "WEIGH_OUT":
            st.info("🔹 STEP 3: WEIGHBRIDGE OUT (GROSS)")
            gross = st.number_input("Gross Weight (kg)", value=48500)
            ticket = st.text_input("Ticket #", "WB-001")

            # Handle Null/None in tare safely
            tare_val = curr_trip["tare_weight"] if pd.notnull(curr_trip["tare_weight"]) else 0
            net = gross - tare_val
            st.metric("Net Payload", f"{net} kg")

            if st.button("Finalize Weights"):
                run_query(
                    """
                    UPDATE log_dispatch_journal
                    SET status='DOCUMENTATION',
                        gross_weight=:g,
                        net_weight=:n,
                        ticket_no=:t
                    WHERE trip_id=:id
                    """,
                    {"g": gross, "n": net, "t": ticket, "id": trip_sel}
                )

                _update_latest_mission_status(curr_trip["truck_reg"], "Documentation")
                st.rerun()

        # -------------------------
        # STEP 4: DOCUMENTATION
        # -------------------------
        elif curr_trip["status"] == "DOCUMENTATION":
            st.success("✅ READY FOR DISPATCH")

            if st.button("📄 Generate Docs & Close"):
                pdf_data = generate_dispatch_docs(curr_trip)

                # 1) Close dispatch journal
                run_query(
                    """
                    UPDATE log_dispatch_journal
                    SET status='DISPATCHED', end_time=CURRENT_TIMESTAMP
                    WHERE trip_id=:id
                    """,
                    {"id": trip_sel}
                )

                # 2) Activate mission (Driver Portal sees it as Active)
                _activate_staged_mission(curr_trip["truck_reg"], curr_trip["driver"])

                st.download_button(
                    "⬇️ Download Dispatch Pack",
                    data=pdf_data,
                    file_name=f"Dispatch_{trip_sel}.pdf",
                    mime="application/pdf"
                )


# =========================================================
# INTERNAL HELPERS — MISSION SYNC (Aligned with OS v16)
# =========================================================

def _update_latest_mission_status(reg_number, new_status):
    """Updates the most recent non-closed mission."""
    mission_df = load_data(
        "SELECT id FROM log_missions WHERE reg_number = :r AND status != 'Closed' ORDER BY id DESC LIMIT 1",
        {"r": reg_number},
    )

    if mission_df.empty:
        return

    mid = mission_df.iloc[0]["id"]

    run_query(
        "UPDATE log_missions SET status = :s WHERE id = :id",
        {"s": new_status, "id": mid},
    )
    run_query(
        "UPDATE log_vehicles SET status = :s WHERE reg_number = :r",
        {"s": new_status, "r": reg_number},
    )


def _activate_staged_mission(reg_number, driver_name):
    """Activates the latest staged mission."""
    mission_df = load_data(
        """
        SELECT id FROM log_missions
        WHERE reg_number = :r AND status IN ('Staged', 'Loading', 'Weigh Out', 'Documentation')
        ORDER BY id DESC LIMIT 1
        """,
        {"r": reg_number},
    )

    if mission_df.empty:
        return

    mid = mission_df.iloc[0]["id"]

    run_query(
        "UPDATE log_missions SET status = 'Active', driver_name = :d, start_time = COALESCE(start_time, CURRENT_TIMESTAMP) WHERE id = :id",
        {"d": driver_name, "id": mid},
    )
    run_query(
        "UPDATE log_vehicles SET status = 'Active', driver_name = :d WHERE reg_number = :r",
        {"d": driver_name, "r": reg_number},
    )
