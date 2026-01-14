import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

# ==========================================
# 1. ARCHITECTURAL BRIDGE
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../")) # Up 3 levels to project_cortex
sys.path.append(root_dir)

# ==========================================
# 2. MODULAR IMPORTS (FIXED)
# ==========================================
try:
    import vas_kernel as vk
    # FIXED: Pointing to the local Sturrock package
    from modules.industrial.Sturrock_Vertical import models 
    from modules.industrial.Sturrock_Vertical import services
except ImportError as e:
    st.error(f"⚠️ Architecture Error: {e}")
    st.info("Ensure this file is in 'project_cortex/modules/industrial/Sturrock_Vertical/'")
    st.stop()

def render_sturrock_dashboard():
    """
    V2.1: THE FEDERAL CONSOLE.
    Full implementation of the 'Holding Company' Product Definition.
    """
    
    # 3. SYSTEM BOOT
    vk.boot_system()
    models.init_industrial_db()  # Initialize Asset Registry
    
    # --- HEADER: THE HOLDING COMPANY VIEW ---
    st.markdown("## 🦅 Sturrock & Robson Group | Federal Console")
    st.caption("Governance: Federal Model | HQ: London / Johannesburg")

    # TOP LEVEL STRATEGY
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.metric("Portfolio Balance", "60/40", "Defensive / Growth")
    with c2:
        st.metric("Engagement Score", "90%", "+16% (Cultural Turnaround)")
    with c3:
        st.metric("Global Revenue", "£ 245M", "GBP / USD / ZAR Hedged")

    # GEOGRAPHIC HEDGING
    with st.expander("🌍 Geographic Revenue Hedge (Currency Resilience)", expanded=False):
        geo_data = pd.DataFrame({
            'Region': ['UK/Europe (GBP)', 'Americas (USD)', 'Africa/Aus (ZAR/AUD)'],
            'Revenue': [45, 30, 25]
        })
        fig = px.pie(geo_data, values='Revenue', names='Region', hole=0.4, 
                     color_discrete_sequence=['#2C3E50', '#27AE60', '#C0392B'])
        fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        c_chart, c_txt = st.columns([1, 2])
        with c_chart:
            st.plotly_chart(fig, use_container_width=True)
        with c_txt:
            st.markdown("### Currency Arbitrage Strategy")
            st.success("✅ **GBP Base:** Stable capital allocation.")
            st.info("ℹ️ **ZAR/AUD Ops:** High-yield commodity exposure.")

    st.divider()

    # --- DIVISIONAL NAVIGATION (6 TABS) ---
    tab_mining, tab_marine, tab_tech, tab_infra, tab_green, tab_admin = st.tabs([
        "⛏️ Martin & Robson", 
        "⚓ Shand (Marine)", 
        "⛽ LAS (Tech)", 
        "🚆 Infra (Pandrol)",
        "♻️ Secorra (Green)",
        "🛠️ Asset Registry"
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
        with c_kpi:
            st.markdown("**🧪 Process Efficiency**")
            st.metric("SG Control (Rheology)", "99.8%", "Target Met")

    # === TAB 2: SHAND ENGINEERING ===
    with tab_marine:
        st.subheader("Shand Engineering | Critical Connections")
        s1, s2, s3 = st.columns(3)
        s1.metric("Compliance (OCIMF)", "PASS", "Audit Ready")
        s2.metric("Mfg Load (Grimsby)", "92%", "CNC/Welding")
        s3.metric("Diversification", "Healthcare", "New Vertical")
        st.divider()
        st.markdown("#### 🏥 Project Pivot: GHA Chemotherapy")
        st.success("✅ HVAC Integration: Complete")

    # === TAB 3: LAS (TECH) ===
    with tab_tech:
        st.subheader("Liquid Automation | Chain of Custody")
        col_flow, col_sars = st.columns(2)
        with col_flow:
            st.markdown("**⛽ Reconciliation Engine**")
            st.metric("Variance", "-0.37%", "Within Tolerance")
        with col_sars:
            st.markdown("**🇿🇦 SARS Compliance Log**")
            st.dataframe(pd.DataFrame({'Claim_ID': ['RB-2025-01'], 'Status': ['Ready']}), hide_index=True)

    # === TAB 4: INFRASTRUCTURE ===
    with tab_infra:
        st.subheader("Infrastructure | Anti-Sabotage Systems")
        i1, i2 = st.columns(2)
        with i1:
            st.markdown("**🚆 Pandrol (Rail)**")
            st.error("🚨 ALERT: Clip Tampering (Sector 4)")
        with i2:
            st.markdown("**🔥 SigmaHLR (Wellhead)**")
            st.metric("Hydraulic Pressure", "320 Bar", "Stable")

    # === TAB 5: SECORRA / REDS ===
    with tab_green:
        st.subheader("Secorra & REDS | The Growth Engine")
        st.caption("Value Prop: Offshore Wind O&M & Automation Transition")
        st.dataframe(pd.DataFrame({'Turbine_ID': ['WTG-04', 'WTG-09'], 'Status': ['Maintenance Required', 'Operational']}), use_container_width=True, hide_index=True)

    # === TAB 6: BACKEND ADMIN (INTEGRATION VIEW) ===
    with tab_admin:
        st.subheader("The Iron Vault | Backend Data View")
        st.info("Visualizes data from `modules.industrial.Sturrock_Vertical.models`")
        
        c_sim, c_data = st.columns([1, 2])
        
        with c_sim:
            st.markdown("**Simulation Controls**")
            if st.button("➕ Register Test Asset"):
                # Uses models.py logic
                rfq_id = f"RFQ-{np.random.randint(100,999)}"
                new_id = models.register_asset({
                    'Product': 'High-Pressure Valve', 
                    'Client': 'Sasol', 
                    'RFQ_ID': rfq_id
                }, location="Secunda")
                st.toast(f"Registered: {new_id}")
            
            if st.button("📄 Attach Compliance Doc"):
                # Uses services.py logic
                if not st.session_state.asset_registry.empty:
                    tgt_asset = st.session_state.asset_registry.iloc[0]['Asset_ID']
                    services.attach_compliance_doc(tgt_asset, "ISO-9001")
                    st.toast(f"Doc attached to {tgt_asset}")
                else:
                    st.error("Registry Empty")

        with c_data:
            st.caption("Live `asset_registry` Table")
            if 'asset_registry' in st.session_state and not st.session_state.asset_registry.empty:
                st.dataframe(st.session_state.asset_registry, use_container_width=True)
            else:
                st.write("No assets registered yet.")
