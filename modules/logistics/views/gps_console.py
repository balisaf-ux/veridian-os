import streamlit as st
import pandas as pd

# Robust imports
try:
    from modules.logistics.gps_engine import run_gps_simulation
    from modules.logistics.db_utils import load_data
    from modules.logistics.rules import enrich_fleet_data
except ImportError:
    from ..gps_engine import run_gps_simulation
    from ..db_utils import load_data
    from ..rules import enrich_fleet_data


def render_gps_console():
    st.subheader("📡 GPS Engine Console")
    st.markdown("Simulates GPS movement and updates live fleet telemetry.")

    # ---------------------------------------------------------
    # Trigger GPS Simulation
    # ---------------------------------------------------------
    if st.button("Run GPS Simulation"):
        run_gps_simulation()
        st.success("GPS updated.")
        st.rerun()

    # ---------------------------------------------------------
    # Load fleet + enrich with GPS context
    # ---------------------------------------------------------
    df_raw = load_data("SELECT * FROM log_vehicles")

    if df_raw.empty:
        st.info("No fleet data available.")
        return

    df = enrich_fleet_data(df_raw)

    # ---------------------------------------------------------
    # Display Live Telemetry
    # ---------------------------------------------------------
    st.markdown("### 🚚 Live Fleet Telemetry")

    telemetry_cols = [
        "reg_number",
        "last_lat",
        "last_lon",
        "speed",
        "movement_status",
        "heading",
        "ignition",
        "signal_quality",
    ]

    valid_cols = [c for c in telemetry_cols if c in df.columns]

    st.dataframe(
        df[valid_cols],
        use_container_width=True,
        hide_index=True,
    )

    # ---------------------------------------------------------
    # Per‑Vehicle Detail
    # ---------------------------------------------------------
    st.markdown("### 🔍 Vehicle Telemetry Details")

    for _, row in df.iterrows():
        reg = row["reg_number"]
        with st.expander(f"{reg} — Telemetry"):

            st.write(f"**Latitude:** {row.get('last_lat')}")
            st.write(f"**Longitude:** {row.get('last_lon')}")
            st.write(f"**Speed:** {row.get('speed')} km/h")
            st.write(f"**Movement:** {row.get('movement_status')}")
            st.write(f"**Heading:** {row.get('heading')}")
            st.write(f"**Ignition:** {row.get('ignition')}")
            st.write(f"**Signal Quality:** {row.get('signal_quality')}")
