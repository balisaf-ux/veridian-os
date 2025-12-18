import streamlit as st
import pandas as pd
import numpy as np
import time
import vas_kernel as vk

def render_tte_dashboard():
    vk.init_logistics_data()
    vk.init_bonnyvale_data()
    st.markdown("## 🚛 Veridian Logistics Cloud")
    st.caption("Tenant: **Travel & Transport Entity (TTE)**")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fleet Utilization", "82%", "+12%")
    k2.metric("Active Loads", "4", "On Route")
    k3.metric("Revenue (MTD)", "R 425,000", "DealStream")
    k4.metric("Fuel Efficiency", "38L/100km", "Alert: Truck 07")
    st.divider()

    tab_rev, tab_ops, tab_risk, tab_admin = st.tabs(["💰 DealStream", "🌍 Fleet Command", "⛽ Fuel", "🪪 Compliance"])

    # TAB 1: REVENUE
    with tab_rev:
        st.markdown("#### ⚡ Active Load Marketplace")
        df_market = st.session_state.logistics_marketplace
        for index, row in df_market.iterrows():
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**{row['Origin']} ➝ {row['Destination']}**")
            c2.caption(f"{row['Cargo']}")
            c3.markdown(f"**R {row['Rate (ZAR)']:,.0f}**")
            if c4.button("ACCEPT", key=f"btn_{row['Load_ID']}"):
                st.toast("Load Secured!")
            st.divider()

    # TAB 2: OPS & REGISTRY (RESTORED)
    with tab_ops:
        st.subheader("🌍 Fleet Command & Registry")
        ops_view, ops_input = st.tabs(["📍 Live Tracking", "➕ Registry (Input)"])
        
        with ops_view:
            st.map(st.session_state.agri_harvest, zoom=12)
            st.markdown("#### ⏱️ Smart Availability Engine")
            def calculate_availability(row):
                if row['Status'] == 'Idle': return "✅ IMMEDIATELY"
                elif row['Status'] == 'Active': return "🕒 +4 Hours"
                elif row['Status'] == 'Delayed': return "⚠️ +12 Hours"
                else: return "Unknown"
            df_display = st.session_state.agri_fleet.copy()
            df_display['Forecast'] = df_display.apply(calculate_availability, axis=1)
            st.dataframe(df_display[['Truck_ID', 'Status', 'Forecast']], use_container_width=True)

        with ops_input:
            st.markdown("#### 🚛 Onboard New Asset")
            with st.form("fleet_input"):
                v_reg = st.text_input("Registration (e.g., CA 123-456)")
                v_type = st.selectbox("Type", ["Interlink", "Tautliner"])
                if st.form_submit_button("💾 Register"):
                    new_truck = pd.DataFrame({'Truck_ID': [v_reg], 'Type': [v_type], 'Status': ['Idle'], 'Location': ['Depot'], 'Load_Tons': [0], 'Driver': ['New']})
                    st.session_state.agri_fleet = pd.concat([st.session_state.agri_fleet, new_truck], ignore_index=True)
                    st.success("Asset Registered!")
                    time.sleep(1); st.rerun()

    # TAB 3: RISK
    with tab_risk:
        st.subheader("⛽ Fuel Forensics | TTE-07")
        c_fuel, c_alert = st.columns([3, 1])
        with c_fuel:
            fuel_hours = [f"{i}:00" for i in range(24)]
            fuel_levels = [900 - (i*10) if i != 8 else 900-(i*10)-50 for i in range(24)] 
            st.line_chart(pd.DataFrame({'Time': fuel_hours, 'Level': fuel_levels}).set_index('Time'), color="#C0392B")
        with c_alert:
            st.error("🚨 **THEFT EVENT**")
            st.button("👮 Log Incident")

    # TAB 4: COMPLIANCE
    with tab_admin:
        st.success("✅ Company Reg: Verified")
        st.success("✅ Tax Clearance: Verified")
        st.warning("⚠️ Public Liability: Pending")
