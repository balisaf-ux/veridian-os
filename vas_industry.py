import streamlit as st
import pandas as pd
import vas_kernel as vk

# ==========================================
# 1. INDUSTRIAL CLOUD (S&R) - FULLY RESTORED
# ==========================================

def render_liquid_module():
    vk.init_sr_data()
    st.markdown("## 💧 Veridian Industrial Cloud | Liquid Automation")
    st.caption("Site: Germiston Plant A • Status: **NOMINAL**")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Current Flow Rate", "1,240 L/min", "+2.4%")
    k2.metric("Pump Efficiency", "94.2%", "-0.5%")
    k3.metric("Active Alerts", "0", "All Clear")
    k4.metric("Next Maintenance", "14 Days", "Pump B-12")
    st.divider()
    
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1:
        st.subheader("24-Hour Flow Stability")
        chart_data = st.session_state.sr_liquid
        st.line_chart(chart_data.set_index('Time')[['Flow Efficiency (%)']], color="#0056b3")
        st.caption("Real-time telemetry from SCADA Node 4.")
    with c2:
        st.subheader("Asset Health")
        st.markdown("**Pump Station Alpha**")
        st.progress(0.94, text="Efficiency: 94%")
        st.markdown("**Pump Station Beta**")
        st.progress(0.88, text="Efficiency: 88%")
        st.markdown("**Filtration Unit**")
        st.progress(0.99, text="Efficiency: 99%")
        st.info("ℹ️ **Optimization:** Beta pump is consuming 4% more energy than baseline.")

def render_safety_module():
    vk.init_sr_data()
    st.markdown("## 🛡️ Veridian Industrial Cloud | Safety Overlay")
    st.caption("Group-Wide Incident Tracking & Risk Heatmap")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #EAFAF1; border: 1px solid #27AE60; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: #186A3B; font-size: 3rem; margin: 0;">412 DAYS</h1>
        <h3 style="color: #27AE60; margin: 0;">WITHOUT LOST TIME INJURY (LTI)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("Incident Categorization (YTD)")
        df = st.session_state.sr_safety
        st.bar_chart(df.set_index('Category')['Incidents'], color="#C0392B")
    with c2:
        st.subheader("Risk Action Items")
        st.checkbox("Review Site B PPE Protocols", value=True)
        st.checkbox("Certify new forklift operators (JHB)", value=False)
        st.checkbox("Update Thermal Division Fire Suppression", value=False)
        st.warning("⚠️ **Compliance Alert:** 3 certifications expiring in < 7 days.")

def render_energy_module():
    vk.init_sr_data()
    st.markdown("## ⚡ Veridian Industrial Cloud | EnergyShield")
    st.caption("PPA Performance & Liability Transfer Monitor")
    
    f1, f2, f3 = st.columns(3)
    f1.metric("Grid Reliance", "42%", "-18% YoY")
    f2.metric("PPA Production", "14.2 MWh", "Target Met")
    f3.metric("Est. Savings (Dec)", "R 45,200", "Cumulative")
    st.divider()
    
    col_chart, col_stat = st.columns([3, 1], gap="medium")
    with col_chart:
        st.subheader("Supply Mix: Grid vs. Veridian PPA")
        energy_df = st.session_state.sr_energy.set_index('Date')
        st.line_chart(energy_df, color=["#C0392B", "#27AE60"])
    with col_stat:
        st.subheader("System Status")
        st.markdown("**Battery State of Charge**")
        st.progress(0.85, text="85% Charged")
        st.markdown("**Inverter Load**")
        st.progress(0.60, text="60% Capacity")
        st.markdown("---")
        st.success("✅ **Sovereignty Check:** System mitigated 4 hours of Load Shedding.")

# ==========================================
# 2. AGRI CLOUD (BONNYVALE) - FULLY RESTORED
# ==========================================

def render_bonnyvale_module():
    vk.init_bonnyvale_data()
    st.markdown("## 🍍 Veridian Agri Cloud | Bonnyvale Estates")
    st.caption("Region: East London (Sunshine Coast) • Crop: **Pineapple (Cayenne/Queen)**")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Season Yield Target", "18,500 Tons", "Forecast")
    k2.metric("Harvest Progress", "12.4%", "+2% vs Schedule")
    k3.metric("Avg Brix (Sugar)", "14.6°", "Premium Grade")
    k4.metric("Active Fleet", "3/4 Trucks", "Logistics Active")

    st.divider()

    st.subheader("Yield Map & Block Status")
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        df_map = st.session_state.agri_harvest
        st.map(df_map, latitude='lat', longitude='lon', zoom=13, use_container_width=True)
        st.caption("📍 GPS Telemetry: Active Production Blocks (BV-01 to BV-05)")
    with c2:
        st.markdown("**Block Readiness Index**")
        df_blocks = st.session_state.agri_harvest
        for index, row in df_blocks.iterrows():
            st.progress(row['Readiness'], text=f"{row['Block_ID']} ({row['Status']})")

    st.divider()
    
    st.subheader("🚛 Logistics Chain (Field to Factory)")
    c_log1, c_log2 = st.columns([2, 1], gap="large")
    with c_log1:
        def highlight_status(val):
            color = '#eafaf1' if val == 'On Time' or val == 'Active' else '#f8d7da' if val == 'Delayed' else ''
            return f'background-color: {color}'
        st.dataframe(st.session_state.agri_fleet.style.applymap(highlight_status, subset=['Status']), use_container_width=True, hide_index=True)
    with c_log2:
        st.markdown("**Live Dispatch Notes**")
        st.info("ℹ️ **Co-op Alert:** Summerpride facility is experiencing high traffic. 45 min delay expected for TRK-02.")
        st.success("✅ **Optimization:** Back-haul opportunity identified for TRK-03.")
