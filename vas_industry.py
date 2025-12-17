import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px # New dependency for V2.0
import vas_kernel as vk

# ==========================================
# 1. STURROCK & ROBSON GROUP (V2.0 FEDERAL MODEL)
# ==========================================
def render_sturrock_robson_module():
    """
    V2.0: THE CONGLOMERATE CLOUD.
    Reflecting the 'Federal Model' of Sturrock & Robson.
    """
    # --- HEADER: THE HOLDING COMPANY VIEW ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("## 🦅 Sturrock & Robson Group | Executive Console")
        st.caption("Governance: Federal Model | HQ: London / Johannesburg")
    with c2:
        # The 'Barbell Strategy' Metric
        st.metric("Portfolio Balance", "60/40", "Defensive / Growth")

    # GROUP KPI ROW (Aggregated from Subsidiaries)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Global Revenue (Est)", "£ 245M", "+12% (Renewables)")
    k2.metric("Safety (LTR)", "0.02", "Best in Class (SigmaHLR)")
    k3.metric("Engagement Score", "90%", "+16% (Have Your Say)") #
    k4.metric("Active Projects", "142", "Global Footprint")

    st.divider()

    # --- DIVISIONAL NAVIGATION (THE FEDERAL STRUCTURE) ---
    # We use Tabs to represent the distinct subsidiaries
    tab_mining, tab_marine, tab_tech, tab_infra = st.tabs([
        "⛏️ Martin & Robson", 
        "⚓ Shand Engineering", 
        "⛽ Liquid Automation", 
        "🚆 Pandrol / Sigma"
    ])

    # === TAB 1: MARTIN & ROBSON (THE CASH COW) ===
    with tab_mining:
        st.subheader("Martin & Robson | Magnetite Solutions")
        st.caption("Strategic Role: Baseload Cash Flow | Ops: Global Logistics")
        
        c_map, c_inv = st.columns([2, 1])
        
        with c_map:
            st.markdown("**🚢 Global Logistics Corridor**")
            # Simulating the Export Route: Witbank -> Richards Bay -> Indonesia
            st.progress(85, text="Shipment MR-402: En Route to Indonesia (ETA: 4 Days)")
            st.progress(30, text="Shipment MR-405: Loading at Richards Bay Coal Terminal")
        
        with c_inv:
            st.markdown("**📦 Vendor Managed Inventory**") 
            st.warning("⚠️ Mackay Port (Aus): Low Stock (12%)")
            st.success("✅ Witbank Plant: Optimal (85%)")
            st.info("ℹ️ **Insight:** Indonesia demand spiking due to thermal coal surge.")

    # === TAB 2: SHAND ENGINEERING (THE NICHE LEADER) ===
    with tab_marine:
        st.subheader("Shand Engineering | Critical Marine Infrastructure")
        st.caption("Focus: OCIMF Compliance & Hose Integrity")
        
        # Visualize "Industrial Criticality" 
        s1, s2, s3 = st.columns(3)
        s1.metric("Active Couplings", "412", "North Sea / West Africa")
        s2.metric("Compliance Rate", "100%", "OCIMF / GMPHOM ")
        s3.metric("Manufacturing", "Grimsby", "Capacity: 92%")

        st.markdown("#### 🌊 Subsea Stress Monitor (Live)")
        # Simulating a live feed from an FPSO coupling
        chart_data = pd.DataFrame(
            np.random.randn(20, 1) + 100,
            columns=['Pressure (Bar)']
        )
        st.line_chart(chart_data, height=200)
        st.info("ℹ️ **Status:** Coupling A-14 holding pressure. No seal degradation detected.")

    # === TAB 3: LIQUID AUTOMATION SYSTEMS (THE INNOVATOR) ===
    with tab_tech:
        st.subheader("LAS | Fuel Sovereignty & Aviation")
        st.caption("Focus: Chain of Custody & Theft Prevention")
        
        # The "Chain of Custody" Visualization
        col_flow, col_alert = st.columns(2)
        
        with col_flow:
            st.markdown("**⛽ Fuel Reconciliation (Daily)**")
            st.write("Target: Glencore Coal Ops")
            # Comparing Dispensed vs. Burned
            st.metric("Delivered (Tanker)", "40,000 L")
            st.metric("Dispensed (Nozzle)", "39,850 L")
            st.metric("Variance", "-0.37%", "Within Tolerance")
            
        with col_alert:
            st.markdown("**✈️ Aviation: DeiceCube**") 
            st.success("System Ready: OR Tambo Int.")
            st.metric("Glycol Mix Ratio", "45:55", "Optimized for -2°C")

    # === TAB 4: PANDROL / SIGMAHLR (INFRASTRUCTURE) ===
    with tab_infra:
        st.subheader("Infrastructure & Safety Systems")
        st.caption("Focus: Rail Integrity & Wellhead Safety")
        
        i1, i2 = st.columns(2)
        with i1:
            st.markdown("**🚆 Pandrol Rail (SA)**")
            st.write("Track Condition: **Transnet Corridor 4**")
            st.progress(78, text="Track Geometry Integrity")
            st.warning("⚠️ Theft Alert: Sector 4 (Clip Tampering Detected)")
        
        with i2:
            st.markdown("**🔥 SigmaHLR (Wellhead Safety)**")
            st.write("System: **Offshore Platform B**")
            st.success("✅ Hydraulic Pressure: Stable")
            st.metric("Fusible Loop Status", "ARMED", "Fire Safety Active")

# ==========================================
# 2. AGRI CLOUD (BONNYVALE) - PRESERVED
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
