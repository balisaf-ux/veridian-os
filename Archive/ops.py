import streamlit as st
import pandas as pd
import time

# NEW: Import the Control Tower
from modules.logistics.ops_console import render_ops_console

def render_ops_tab():
    ops_view, ops_input = st.tabs(["📍 Live Tracking & Control", "➕ Fleet Registry"])
    
    # --- SUB-TAB 1: LIVE TRACKING & CONTROL TOWER ---
    with ops_view:
        # A. SPRINT 5.0: THE CONTROL TOWER (Added at the top)
        render_ops_console()
        
        st.divider()
        
        # B. LEGACY MAP & TRACKING (Preserved)
        st.markdown("#### 🛰️ Fleet Telematics (GPS)")
        if 'agri_harvest' in st.session_state:
            st.map(st.session_state.agri_harvest, zoom=5)
        else:
            st.info("GPS Data Offline")
            
        st.markdown("#### ⏱️ Smart Availability Engine")
        
        def calculate_availability(row):
            if row['Status'] == 'Idle': return "✅ IMMEDIATELY"
            elif row['Status'] == 'Active': return "🕒 +4 Hours"
            elif row['Status'] == 'Delayed': return "⚠️ +12 Hours"
            else: return "Unknown"

        if 'agri_fleet' in st.session_state:
            df_display = st.session_state.agri_fleet.copy()
            df_display['Forecast'] = df_display.apply(calculate_availability, axis=1)
            
            st.dataframe(
                df_display[['Truck_ID', 'Status', 'Location', 'Forecast']].style.applymap(
                    lambda x: 'background-color: #d4edda' if 'IMMEDIATELY' in x else '', subset=['Forecast']
                ), use_container_width=True
            )
        else:
            st.warning("Fleet Data Offline")

    # --- SUB-TAB 2: REGISTRY (Preserved) ---
    with ops_input:
        st.markdown("#### 🚛 Onboard New Asset")
        with st.form("fleet_input"):
            c1, c2 = st.columns(2)
            v_reg = c1.text_input("Registration (e.g., CA 123-456)")
            v_type = c2.selectbox("Type", ["Interlink", "Tautliner", "Flat Deck"])
            v_driver = c1.text_input("Assigned Driver")
            v_loc = c2.selectbox("Location", ["Depot", "Durban Port", "Cape Town"])
            
            if st.form_submit_button("💾 Register Asset"):
                # Note: In Sprint 4.1 we moved to DB persistence for this, 
                # but we keep this UI active for the 'Fleet Registry' sub-tab.
                # Ideally, this should call save_fleet_vehicle() from db_manager.
                st.success("Asset Registered (UI Simulation)")
