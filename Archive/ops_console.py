import streamlit as st
import pandas as pd
from modules.core.db_manager import load_fleet_to_dataframe

def render_ops_console():
    """
    LOGISTICS CLOUD: The Physics Engine.
    Reads fleet_registry to manage tonnage and hazchem compliance.
    """
    st.markdown("## 🚛 Logistics Cloud | Fleet Control Tower")
    st.caption("Live Telematics & Asset Dispatch")
    
    # 1. Pull Live Fleet Data
    df_fleet = load_fleet_to_dataframe()
    
    if df_fleet.empty:
        st.warning("⚠️ Fleet Registry Empty. Initialize assets in Admin Core.")
        return

    # 2. Physics Metrics
    total_tons = df_fleet['max_tons'].sum()
    active_trucks = len(df_fleet[df_fleet['status'] == 'Active'])
    hazchem_ready = len(df_fleet[df_fleet['hazchem_compliant'] == 1])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Lift Capacity", f"{total_tons:,.0f} Tons")
    c2.metric("Active Fleet", f"{active_trucks} / {len(df_fleet)}")
    c3.metric("Hazchem Compliant", hazchem_ready, delta="Critical for Iron Oxide")
    
    st.divider()

    # 3. The Dispatch Board
    st.markdown("### 📋 Fleet Registry")
    
    # Visual Polish: Highlight Hazchem Trucks
    st.dataframe(
        df_fleet, 
        width='stretch',
        hide_index=True,
        column_config={
            "hazchem_compliant": st.column_config.CheckboxColumn("Hazchem?", disabled=True),
            "status": st.column_config.SelectboxColumn("Asset Status", options=["Active", "Maintenance", "En Route"])
        }
    )
    
    # 4. Simulation Button (The "Go" Signal)
    if st.button("🔄 Optimize Route Planning"):
        st.toast("Calculating optimal routes based on tonnage...", icon="🛣️")
