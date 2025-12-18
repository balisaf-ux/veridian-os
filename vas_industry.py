import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import vas_kernel as vk

# ==========================================
# 1. STURROCK & ROBSON GROUP (V2.1 FEDERAL CONSOLE)
# ==========================================
def render_sturrock_robson_module():
    """
    V2.1: THE FEDERAL CONSOLE.
    Full implementation of the 'Holding Company' Product Definition.
    """
    # --- HEADER: THE HOLDING COMPANY VIEW ---
    st.markdown("## 🦅 Sturrock & Robson Group | Federal Console")
    st.caption("Governance: Federal Model | HQ: London / Johannesburg")

    # 1. TOP LEVEL STRATEGY (Barbell & Human Capital)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.metric("Portfolio Balance", "60/40", "Defensive / Growth")
    with c2:
        # Engagement Score Highlight
        st.metric("Engagement Score", "90%", "+16% (Cultural Turnaround)")
    with c3:
        st.metric("Global Revenue", "£ 245M", "GBP / USD / ZAR Hedged")

    # 2. GEOGRAPHIC HEDGING (The Resilience Layer)
    with st.expander("🌍 Geographic Revenue Hedge (Currency Resilience)", expanded=False):
        # Simple dataframe to visualize the currency split
        geo_data = pd.DataFrame({
            'Region': ['UK/Europe (GBP)', 'Americas (USD)', 'Africa/Aus (ZAR/AUD)'],
            'Revenue': [45, 30, 25]
        })
        fig = px.pie(geo_data, values='Revenue', names='Region', hole=0.4, color_discrete_sequence=['#2C3E50', '#27AE60', '#C0392B'])
        fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        c_chart, c_txt = st.columns([1, 2])
        with c_chart:
            st.plotly_chart(fig, use_container_width=True)
        with c_txt:
            st.markdown("### Currency Arbitrage Strategy")
            st.success("✅ **GBP Base:** Stable capital allocation.")
            st.info("ℹ️ **ZAR/AUD Ops:** High-yield commodity exposure (Coal/Iron Ore).")

    st.divider()

    # --- DIVISIONAL NAVIGATION (5 TABS) ---
    tab_mining, tab_marine, tab_tech, tab_infra, tab_green = st.tabs([
        "⛏️ Martin & Robson", 
        "⚓ Shand (Marine)", 
        "⛽ LAS (Tech)", 
        "🚆 Infra (Pandrol)",
        "♻️ Secorra (Green)"
    ])

    # === TAB 1: MARTIN & ROBSON (CASH COW) ===
    with tab_mining:
        st.subheader("Martin & Robson | Magnetite Solutions")
        st.caption("Value Prop: Logistics Reliability & Technical Rheology")
        
        c_map, c_kpi = st.columns([2, 1])
        
        with c_map:
            st.markdown("**🚢 Global Logistics Corridor (Witbank ➝ Indonesia)**")
            st.progress(85, text="Shipment MR-402: En Route to Indonesia (ETA: 4 Days)")
            st.progress(30, text="Shipment MR-405: Loading at Richards Bay Coal Terminal")
            st.markdown("---")
            st.markdown("**📦 Vendor Managed Inventory (Mackay, Aus)**")
            st.bar_chart(pd.DataFrame({'Stock Level': [85, 12]}, index=['Witbank (SA)', 'Mackay (AUS)']), color=["#27AE60"])
            st.warning("⚠️ Mackay Port: Re-order point reached.")
        
        with c_kpi:
            st.markdown("**🧪 Process Efficiency**")
            st.metric("SG Control (Rheology)", "99.8%", "Target Met")
            st.caption("Technical support lock-in active.")
            st.info("High switching costs established via proprietary SG algorithms.")

    # === TAB 2: SHAND ENGINEERING (NICHE LEADER) ===
    with tab_marine:
        st.subheader("Shand Engineering | Critical Connections")
        st.caption("Value Prop: Compliance & Strategic Diversification")
        
        s1, s2, s3 = st.columns(3)
        s1.metric("Compliance (OCIMF)", "PASS", "Audit Ready")
        s2.metric("Mfg Load (Grimsby)", "92%", "CNC/Welding/Test")
        s3.metric("Diversification", "Healthcare", "New Vertical")

        st.markdown("---")
        
        c_proj, c_chart = st.columns(2)
        with c_proj:
            st.markdown("#### 🏥 Project Pivot: GHA Chemotherapy")
            st.write("Site: **Gibraltar Health Authority**")
            st.success("✅ HVAC Integration: Complete")
            st.success("✅ Clean Room Certification: Pending")
            st.caption("Leveraging precision engineering for healthcare infrastructure.")
            
        with c_chart:
            st.markdown("#### 🌊 Subsea Stress Monitor")
            chart_data = pd.DataFrame(np.random.randn(20, 1) + 100, columns=['Bar'])
            st.line_chart(chart_data, height=150)

    # === TAB 3: LAS (THE INNOVATOR) ===
    with tab_tech:
        st.subheader("Liquid Automation | Chain of Custody")
        st.caption("Value Prop: Theft Prevention & Financial Recovery")
        
        # 1. RECONCILIATION ENGINE
        col_flow, col_sars = st.columns(2)
        with col_flow:
            st.markdown("**⛽ Tank-to-Nozzle Reconciliation**")
            st.metric("Variance (ATG vs Dispense)", "-0.37%", "Within Tolerance")
            st.progress(99, text="Chain of Custody Integrity")
            
        with col_sars:
            st.markdown("**🇿🇦 SARS Compliance Log**")
            st.info("Automated Diesel Rebate Report")
            st.dataframe(pd.DataFrame({
                'Claim_ID': ['RB-2025-01', 'RB-2025-02'],
                'Liters': [45000, 32000],
                'Status': ['Ready for Filing', 'Processing']
            }), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("**✈️ Aviation Innovation: DeiceCube**")
        st.metric("Glycol Mix Ratio", "45:55", "Optimized for -2°C")

    # === TAB 4: INFRASTRUCTURE (SAFETY) ===
    with tab_infra:
        st.subheader("Infrastructure | Anti-Sabotage Systems")
        st.caption("Value Prop: Rail Integrity & Wellhead Fail-Safe")
        
        i1, i2 = st.columns(2)
        with i1:
            st.markdown("**🚆 Pandrol (Rail Integrity)**")
            st.error("🚨 ALERT: Clip Tampering (Sector 4)")
            st.map(pd.DataFrame({'lat': [-26.1], 'lon': [28.0]}), zoom=10) # Simple Map
            st.caption("Track Geometry Defect detected at Km 45.")
        
        with i2:
            st.markdown("**🔥 SigmaHLR (Wellhead Safety)**")
            st.metric("Hydraulic Pressure", "320 Bar", "Stable")
            st.success("✅ Fusible Loop: ARMED (ESD Active)")
            st.metric("System Status", "Fail-Safe Mode", "Ready")

    # === TAB 5: SECORRA / REDS (THE GREEN PIVOT) ===
    with tab_green:
        st.subheader("Secorra & REDS | The Growth Engine")
        st.caption("Value Prop: Offshore Wind O&M & Automation Transition")
        
        # O&M SCHEDULER
        st.markdown("**🌬️ O&M Scheduler (London Array)**")
        st.dataframe(pd.DataFrame({
            'Turbine_ID': ['WTG-04', 'WTG-09', 'WTG-12'],
            'Status': ['Maintenance Required', 'Operational', 'Inspection Due'],
            'Team': ['ROV-Alpha', 'None', 'Diver Team 4']
        }), use_container_width=True, hide_index=True)
        
        st.divider()
        
        # TECH TRANSITION VISUAL
        st.markdown("#### 🤖 Tech Transition: Diver vs. ROV Hours")
        st.caption("Shift to automated inspection reduces risk and cost.")
        
        # Comparative Chart
        trans_data = pd.DataFrame({
            'Year': ['2023', '2024', '2025 (Est)'],
            'Diver Hours': [1200, 800, 400],
            'ROV Hours': [200, 900, 1600]
        })
        st.bar_chart(trans_data.set_index('Year'), color=["#C0392B", "#27AE60"]) # Red for Divers (Risk), Green for ROV (Safe)

# ==========================================
# 2. AGRI CLOUD (BONNYVALE) - PRESERVED
# ==========================================
def render_bonnyvale_module():
    vk.init_bonnyvale_data()
    st.markdown("## 🍍 Veridian Agri Cloud | Bonnyvale Estates")
    # ... (Rest of Bonnyvale code remains unchanged - preserved for stability)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Season Yield Target", "18,500 Tons", "Forecast")
    k2.metric("Harvest Progress", "12.4%", "+2% vs Schedule")
    k3.metric("Avg Brix (Sugar)", "14.6°", "Premium Grade")
    k4.metric("Active Fleet", "3/4 Trucks", "Logistics Active")
    st.divider()
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        st.map(st.session_state.agri_harvest, latitude='lat', longitude='lon', zoom=13, use_container_width=True)
    with c2:
        st.markdown("**Block Readiness Index**")
        for index, row in st.session_state.agri_harvest.iterrows():
            st.progress(row['Readiness'], text=f"{row['Block_ID']} ({row['Status']})")
    st.divider()
    c_log1, c_log2 = st.columns([2, 1], gap="large")
    with c_log1:
        st.dataframe(st.session_state.agri_fleet, use_container_width=True, hide_index=True)
    with c_log2:
        st.info("ℹ️ **Co-op Alert:** Summerpride facility is experiencing high traffic.")
