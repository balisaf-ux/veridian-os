import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Optional MAIS kernel
try:
    import vas_kernel as vk
    KERNEL_AVAILABLE = True
except ImportError:
    KERNEL_AVAILABLE = False

# Local vertical modules
from modules.industrial.Sturrock_Vertical import models, services


def render_sturrock_dashboard():
    """
    Sturrock & Robson | Federal Operating Console
    Demo‑safe, meeting‑ready.
    """

    # Boot MAIS kernel if available
    if KERNEL_AVAILABLE:
        vk.boot_system()

    # Initialize asset registry
    models.init_industrial_db()

    # -------------------------------
    # SIDEBAR: MAIS ADVISOR
    # -------------------------------
    with st.sidebar:
        st.markdown("### 🧠 MAIS Advisor")
        st.caption("Operational Intelligence Layer")

        context = st.selectbox(
            "Focus Area",
            [
                "Group Overview",
                "Fuel Integrity (LAS)",
                "Rail Infrastructure (Pandrol)",
                "Offshore Wind (Secorra)",
                "Manufacturing Risk (Shand)",
            ]
        )

        if context == "Fuel Integrity (LAS)":
            st.success("✔ Variance within tolerance")
            st.markdown(
                "- No anomalous refuelling patterns detected\n"
                "- SARS audit trail complete\n"
                "- Recommend weekly reconciliation cadence"
            )

        if context == "Rail Infrastructure (Pandrol)":
            st.error("⚠ Elevated sabotage risk")
            st.markdown(
                "- Clip tampering detected in Sector 4\n"
                "- Likely cause: opportunistic theft\n"
                "- Action: dispatch inspection crew within 24h"
            )

        if context == "Offshore Wind (Secorra)":
            st.info("🌀 Turbine cluster shows mild vibration anomalies")
            st.markdown(
                "- WTG‑04 requires blade inspection\n"
                "- Recommend drone survey within 48h"
            )

        if context == "Manufacturing Risk (Shand)":
            st.warning("⚙ CNC load trending high")
            st.markdown(
                "- 92% utilisation sustained for 3 days\n"
                "- Recommend preventive maintenance scheduling"
            )

    # -------------------------------
    # HEADER
    # -------------------------------
    st.markdown("## 🦅 Sturrock & Robson Group | Federal Console")
    st.caption("Governance: Federal Model | HQ: London / Johannesburg")

    c1, c2, c3 = st.columns(3)
    c1.metric("Portfolio Balance", "60/40", "Defensive / Growth")
    c2.metric("Engagement Score", "90%", "+16% (Cultural Turnaround)")
    c3.metric("Global Revenue", "£ 245M", "GBP / USD / ZAR Hedged")

    # -------------------------------
    # GEOGRAPHIC HEDGE
    # -------------------------------
    with st.expander("🌍 Geographic Revenue Hedge (Currency Resilience)", expanded=False):
        geo_data = pd.DataFrame({
            'Region': ['UK/Europe (GBP)', 'Americas (USD)', 'Africa/Aus (ZAR/AUD)'],
            'Revenue': [45, 30, 25]
        })
        fig = px.pie(
            geo_data,
            values='Revenue',
            names='Region',
            hole=0.4,
            color_discrete_sequence=['#2C3E50', '#27AE60', '#C0392B']
        )
        fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))

        c_chart, c_txt = st.columns([1, 2])
        c_chart.plotly_chart(fig, use_container_width=True)
        c_txt.markdown("### Currency Arbitrage Strategy")
        c_txt.success("✅ **GBP Base:** Stable capital allocation.")
        c_txt.info("ℹ️ **ZAR/AUD Ops:** High-yield commodity exposure.")

    st.divider()

    # -------------------------------
    # DIVISION TABS
    # -------------------------------
    tab_mining, tab_marine, tab_tech, tab_infra, tab_green, tab_admin = st.tabs([
        "⛏️ Martin & Robson",
        "⚓ Shand (Marine)",
        "⛽ LAS (Tech)",
        "🚆 Infra (Pandrol)",
        "♻️ Secorra (Green)",
        "🛠️ Asset Registry"
    ])

    # --- MARTIN & ROBSON ---
    with tab_mining:
        st.subheader("Martin & Robson | Magnetite Solutions")
        st.caption("Value Prop: Logistics Reliability & Technical Rheology")

        c_map, c_kpi = st.columns([2, 1])
        with c_map:
            st.markdown("**🚢 Global Logistics Corridor (Witbank ➝ Indonesia)**")
            st.progress(85, text="Shipment MR‑402: En Route to Indonesia (ETA: 4 Days)")
            st.progress(30, text="Shipment MR‑405: Loading at Richards Bay Coal Terminal")

        with c_kpi:
            st.markdown("**🧪 Process Efficiency**")
            st.metric("SG Control (Rheology)", "99.8%", "Target Met")

    # --- SHAND ENGINEERING ---
    with tab_marine:
        st.subheader("Shand Engineering | Critical Connections")
        s1, s2, s3 = st.columns(3)
        s1.metric("Compliance (OCIMF)", "PASS", "Audit Ready")
        s2.metric("Mfg Load (Grimsby)", "92%", "CNC/Welding")
        s3.metric("Diversification", "Healthcare", "New Vertical")

        st.divider()
        st.markdown("#### 🏥 Project Pivot: GHA Chemotherapy")
        st.success("✅ HVAC Integration: Complete")

    # --- LAS ---
    with tab_tech:
        st.subheader("Liquid Automation | Chain of Custody")
        col_flow, col_sars = st.columns(2)

        col_flow.markdown("**⛽ Reconciliation Engine**")
        col_flow.metric("Variance", "-0.37%", "Within Tolerance")

        col_sars.markdown("**🇿🇦 SARS Compliance Log**")
        col_sars.dataframe(
            pd.DataFrame({'Claim_ID': ['RB‑2025‑01'], 'Status': ['Ready']}),
            hide_index=True
        )

    # --- INFRA ---
    with tab_infra:
        st.subheader("Infrastructure | Anti‑Sabotage Systems")
        i1, i2 = st.columns(2)

        i1.markdown("**🚆 Pandrol (Rail)**")
        i1.error("🚨 ALERT: Clip Tampering (Sector 4)")

        i2.markdown("**🔥 SigmaHLR (Wellhead)**")
        i2.metric("Hydraulic Pressure", "320 Bar", "Stable")

    # --- SECORRA ---
    with tab_green:
        st.subheader("Secorra & REDS | The Growth Engine")
        st.caption("Value Prop: Offshore Wind O&M & Automation Transition")

        st.dataframe(
            pd.DataFrame({
                'Turbine_ID': ['WTG‑04', 'WTG‑09'],
                'Status': ['Maintenance Required', 'Operational']
            }),
            use_container_width=True,
            hide_index=True
        )

    # --- ASSET REGISTRY ---
    with tab_admin:
        st.subheader("The Iron Vault | Backend Data View")
        st.info("Visualizes data from `modules.industrial.Sturrock_Vertical.models`")

        c_sim, c_data = st.columns([1, 2])

        with c_sim:
            st.markdown("**Simulation Controls**")

            if st.button("➕ Register Test Asset"):
                rfq_id = f"RFQ-{np.random.randint(100,999)}"
                new_id = models.register_asset(
                    {
                        'Product': 'High‑Pressure Valve',
                        'Client': 'Sasol',
                        'RFQ_ID': rfq_id
                    },
                    location="Secunda"
                )
                st.toast(f"Registered: {new_id}")

            if st.button("📄 Attach Compliance Doc"):
                if not st.session_state.asset_registry.empty:
                    tgt_asset = st.session_state.asset_registry.iloc[0]['Asset_ID']
                    services.attach_compliance_doc(tgt_asset, "ISO‑9001")
                    st.toast(f"Doc attached to {tgt_asset}")
                else:
                    st.error("Registry Empty")

        with c_data:
            st.caption("Live `asset_registry` Table")
            if (
                'asset_registry' in st.session_state
                and not st.session_state.asset_registry.empty
            ):
                st.dataframe(st.session_state.asset_registry, use_container_width=True)
            else:
                st.write("No assets registered yet.")
