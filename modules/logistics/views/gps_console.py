import streamlit as st
from modules.logistics.gps_engine import run_gps_simulation
from modules.logistics.db_utils import load_data

def render_gps_console():
    st.subheader("GPS Engine Console")
    st.markdown("This module simulates GPS movement and updates fleet positions in real time.")

    if st.button("Run GPS Simulation"):
        run_gps_simulation()
        st.success("GPS updated.")
        st.rerun()

    st.markdown("### Live Fleet Coordinates")
    df = load_data("SELECT reg_number, last_lat, last_lon FROM log_vehicles")
    st.dataframe(df)
    df = load_data("SELECT reg_number, last_lat, last_lon FROM log_vehicles")
    st.write(df)
