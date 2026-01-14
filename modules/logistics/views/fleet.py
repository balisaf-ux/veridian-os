import streamlit as st
import pandas as pd

# --- 1. ROBUST IMPORTS ---
try:
    from .db_utils import run_query, load_data
except ImportError:
    try:
        from ..db_utils import run_query, load_data
    except ImportError:
        from modules.logistics.db_utils import run_query, load_data

# Import Rules (with fallback if missing)
try:
    from modules.logistics.rules import enrich_fleet_data
except ImportError:
    # Fallback if rules.py is missing or broken
    def enrich_fleet_data(df):
        df = df.copy()
        df["status_signal"] = df.get("status", "Unknown")
        df["location_clean"] = df.get("location", "Unknown")
        df["mission_client"] = "Unknown"
        df["mission_driver"] = df.get("driver_name", "—")
        df["mission_status"] = df.get("status", "Unknown")
        df["mission_history"] = None
        return df


def render_fleet_registry(df_fleet):
    st.markdown("## 🚛 Logistics Cloud | Fleet Control Tower")

    # Enrich with mission context, physics, availability, etc.
    df_rich = enrich_fleet_data(df_fleet.copy()) if not df_fleet.empty else df_fleet

    # Optional global refresh (useful when state changes in other tabs)
    top_cols = st.columns([4, 1])
    with top_cols[1]:
        if st.button("🔄 Refresh Fleet"):
            st.rerun()

    t_view, t_action = st.tabs(["📍 Live Fleet Board", "➕ Onboard New Asset"])

    # =========================================================
    # VIEW TAB — LIVE FLEET BOARD
    # =========================================================
    with t_view:
        if df_fleet.empty:
            st.info("Registry empty.")
        else:
            st.markdown("### 🧭 Operational Fleet Overview")

            # Sort for readability
            df_rich_sorted = df_rich.sort_values("reg_number") if "reg_number" in df_rich.columns else df_rich

            desired_cols = [
                "reg_number",
                "make_model",
                "status_signal",
                "mission_client",
                "mission_status",
                "mission_driver",
                "location_clean",
                "availability_forecast",
                "max_tons",
                "hazchem_compliant",
            ]
            display_cols = [c for c in desired_cols if c in df_rich_sorted.columns]

            st.dataframe(
                df_rich_sorted[display_cols],
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("### 📜 Mission History (Last 3 per Vehicle)")

            for _, row in df_rich_sorted.iterrows():
                reg = row.get("reg_number", "Unknown")
                model = row.get("make_model", "Unknown")

                with st.expander(f"🚛 {reg} — {model}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Status:** {row.get('status_signal', 'N/A')}")
                    c1.write(f"**Location:** {row.get('location_clean', 'N/A')}")
                    c2.write(f"**Driver:** {row.get('mission_driver', '—')}")
                    c2.write(f"**Current Mission:** {row.get('mission_client', '—')}")

                    # Handle history safely
                    if "mission_history" in row:
                        history = row["mission_history"]
                        if history is None:
                            st.info("No mission history.")
                        elif isinstance(history, pd.DataFrame):
                            if history.empty:
                                st.info("No mission history.")
                            else:
                                st.dataframe(history, hide_index=True, use_container_width=True)
                        else:
                            st.write(history)
                    else:
                        st.caption("History data unavailable.")

    # =========================================================
    # ACTION TAB — ONBOARD NEW ASSET
    # =========================================================
    with t_action:
        st.markdown("#### 🚛 Commission New Asset")

        with st.form("new_asset_form", clear_on_submit=True):
            c1, c2 = st.columns(2)

            reg = c1.text_input("Registration Number")
            make = c2.text_input("Vehicle Model")

            trailer_type = c1.selectbox(
                "Trailer Type",
                ["Interlink", "Tri-Axle", "Tautliner", "Rigid", "Flat Deck", "Tipper"],
            )
            location = c2.selectbox(
                "Depot Location",
                ["JHB Yard", "Durban Port", "Cape Town", "Richards Bay"],
            )

            submitted = st.form_submit_button("💾 Save")

            if submitted:
                if not reg or not make:
                    st.warning("Registration and Model required.")
                else:
                    # Check for duplicate registration
                    try:
                        existing = load_data(
                            "SELECT 1 FROM log_vehicles WHERE reg_number = :r",
                            {"r": reg},
                        )
                    except Exception:
                        existing = pd.DataFrame()

                    if not existing.empty:
                        st.error(f"Vehicle {reg} already exists in the fleet.")
                    else:
                        # NOTE: trailer_type is collected but only stashed logically for now.
                        # If you add `trailer_type` column to log_vehicles, include it in INSERT.
                        run_query(
                            """
                            INSERT INTO log_vehicles (reg_number, make_model, status, location, driver_name)
                            VALUES (:r, :m, 'Idle', :l, NULL)
                            """,
                            {"r": reg, "m": make, "l": location},
                        )
                        st.success(f"{reg} added to fleet.")
                        st.rerun()
