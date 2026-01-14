import streamlit as st
import pandas as pd
from modules.core.db_manager import load_fuel_inventory

def render_fuel_sovereignty():
    """
    EXPLICIT ENTRY POINT: Matches Master Router (app.py).
    Fixed to resolve 'ImportError' and Architectural Drift.
    """
    st.markdown("## ⛽ Fuel Sovereignty | Strategic Reserve")
    st.caption("Energy Custody & Consumption Analytics (Hardened Kernel)")
    st.divider()

    # 1. Pull Live Data from the Hardened Kernel
    df_fuel = load_fuel_inventory()
    
    # 2. Render Metrics
    if not df_fuel.empty:
        total_reserve = df_fuel['current_liters'].sum() if 'current_liters' in df_fuel.columns else 0
        st.metric("Total Strategic Reserve", f"{total_reserve:,.0f} L", "Sovereign")
        st.dataframe(df_fuel, width='stretch', hide_index=True) # Fixed UI Deprecation
    else:
        st.info("⚠️ Strategic Reserve Empty. Initialize via Admin Core.")
