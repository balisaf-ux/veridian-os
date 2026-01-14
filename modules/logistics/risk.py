import streamlit as st
import pandas as pd

def render_risk_tabs():
    # Note: We group these two into sub-tabs here for cleaner organization
    tab_fuel, tab_comp = st.tabs(["⛽ Fuel Risk", "🪪 Compliance"])
    
    # --- FUEL FORENSICS ---
    with tab_fuel:
        st.subheader("⛽ Fuel Forensics | TTE-07")
        c_fuel, c_alert = st.columns([3, 1])
        with c_fuel:
            fuel_hours = [f"{i}:00" for i in range(24)]
            # The specific logic for the 'Drop' at 08:00
            fuel_levels = [900 - (i*10) if i != 8 else 900-(i*10)-50 for i in range(24)] 
            st.line_chart(pd.DataFrame({'Time': fuel_hours, 'Level': fuel_levels}).set_index('Time'), color="#C0392B")
        with c_alert:
            st.error("🚨 **THEFT EVENT**")
            st.markdown("08:00 AM • **-50L Drop**")
            st.button("👮 Log Incident")

    # --- COMPLIANCE VAULT ---
    with tab_comp:
        st.subheader("🪪 Compliance Vault")
        st.success("✅ Company Reg: Verified (2024/0056/07)")
        st.success("✅ Tax Clearance: Verified (Good Standing)")
        st.warning("⚠️ Public Liability: Pending Renewal (Nov 2024)")
        st.info("ℹ️ GIT Insurance: Covered via Santam")
