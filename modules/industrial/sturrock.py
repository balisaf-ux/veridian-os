import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import vas_kernel as vk

def render_sturrock_dashboard():
    """
    V2.1: THE FEDERAL CONSOLE.
    Full implementation of the 'Holding Company' Product Definition.
    """
    vk.init_sr_data()
    
    # --- HEADER: THE HOLDING COMPANY VIEW ---
    st.markdown("## 🦅 Sturrock & Robson Group | Federal Console")
    st.caption("Governance: Federal Model | HQ: London / Johannesburg")

    # 1. TOP LEVEL STRATEGY
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.metric("Portfolio Balance", "60/40", "Defensive / Growth")
    with c2:
        st.metric("Engagement Score", "90%", "+16% (Cultural Turnaround)")
    with c3:
        st.metric("Global Revenue", "£ 245M", "GBP / USD / ZAR Hedged")

    # 2. GEOGRAPHIC HEDGING (The Resilience Layer)
    with st.expander("🌍 Geographic Revenue Hedge (Currency Resilience)", expanded=False):
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
            st.info("ℹ️ **ZAR/AUD Ops:** High-yield commodity exposure.")

    st.divider()

    # --- DIVISIONAL NAVIGATION (5 TABS) ---
    tab_mining, tab_marine, tab_tech, tab_infra, tab_green = st.tabs([
        "⛏️ Martin & Robson", 
        "⚓ Shand (Marine)", 
        "⛽ LAS (Tech)", 
        "🚆 Infra (Pandrol)",
        "♻️ Secorra (Green)"
    ])

    # === TAB 1: MARTIN & ROBSON ===
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
            st.warning("⚠️ Mackay Port: Re-order point reached.")
        with c_kpi:
            st.markdown("**🧪 Process Efficiency**")
            st.metric("SG Control (Rheology)", "99.8%", "Target Met")
            st.info("High switching costs established.")

    # === TAB 2: SHAND ENGINEERING ===
    with tab_marine:
        st.subheader("Shand Engineering | Critical Connections")
        st.caption("Value Prop: Compliance & Strategic Diversification")
        s1, s2, s3 = st.columns(3)
        s1.metric("Compliance (OCIMF)", "PASS", "Audit Ready")
        s2.metric("Mfg Load (Grimsby)", "92%", "CNC/Welding")
        s3.metric("Diversification", "Healthcare", "New Vertical")
        st.divider()
        c_proj, c_chart = st.columns(2)
        with c_proj:
            st.markdown("#### 🏥 Project Pivot: GHA Chemotherapy")
            st.write("Site: **Gibraltar Health Authority**")
            st.success("✅ HVAC Integration: Complete")
            st.caption("Leveraging precision engineering for healthcare.")
        with c_chart:
            st.markdown("#### 🌊 Subsea Stress Monitor")
            st.line_chart(pd.DataFrame(np.random.randn(20, 1) + 100, columns=['Bar']), height=150)

    # === TAB 3: LAS (TECH) ===
    with tab_tech:
        st.subheader("Liquid Automation | Chain of Custody")
        col_flow, col_sars = st.columns(2)
        with col_flow:
            st.markdown("**⛽ Reconciliation Engine**")
            st.metric("Variance", "-0.37%", "Within Tolerance")
            st.progress(99, text="Chain of Custody Integrity")
        with col_sars:
            st.markdown("**🇿🇦 SARS Compliance Log**")
            st.info("Automated Diesel Rebate Report")
            st.dataframe(pd.DataFrame({'Claim_ID': ['RB-2025-01', 'RB-2025-02'], 'Status': ['Ready', 'Processing']}), hide_index=True)
        st.divider()
        st.markdown("**✈️ Aviation Innovation: DeiceCube**")
        st.metric("Glycol Mix Ratio", "45:55", "Optimized for -2°C")

    # === TAB 4: INFRASTRUCTURE ===
    with tab_infra:
        st.subheader("Infrastructure | Anti-Sabotage Systems")
        i1, i2 = st.columns(2)
        with i1:
            st.markdown("**🚆 Pandrol (Rail)**")
            st.error("🚨 ALERT: Clip Tampering (Sector 4)")
            st.map(pd.DataFrame({'lat': [-26.1], 'lon': [28.0]}), zoom=10)
        with i2:
            st.markdown("**🔥 SigmaHLR (Wellhead)**")
            st.metric("Hydraulic Pressure", "320 Bar", "Stable")
            st.success("✅ Fusible Loop: ARMED")

    # === TAB 5: SECORRA / REDS (GREEN PIVOT) ===
    with tab_green:
        st.subheader("Secorra & REDS | The Growth Engine")
        st.caption("Value Prop: Offshore Wind O&M & Automation Transition")
        st.markdown("**🌬️ O&M Scheduler (London Array)**")
        st.dataframe(pd.DataFrame({'Turbine_ID': ['WTG-04', 'WTG-09'], 'Status': ['Maintenance Required', 'Operational'], 'Team': ['ROV-Alpha', 'None']}), use_container_width=True, hide_index=True)
        st.divider()
        st.markdown("#### 🤖 Tech Transition: Diver vs. ROV Hours")
        trans_data = pd.DataFrame({'Year': ['2023', '2024', '2025 (Est)'], 'Diver Hours': [1200, 800, 400], 'ROV Hours': [200, 900, 1600]})
        st.bar_chart(trans_data.set_index('Year'), color=["#C0392B", "#27AE60"])
