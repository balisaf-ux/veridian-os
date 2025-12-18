import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import vas_kernel as vk

def render_prospecting_dashboard():
    # Trigger Kernel Data Check
    if 'hunter_db' not in st.session_state: vk.init_bonnyvale_data()
    
    st.markdown("## 🔭 Veridian Prospecting | Global Command")
    st.caption("Strategic Intelligence & Target Acquisition (Group Level)")

    # 1. VISUAL STRATEGY MAP (Risk vs Reward)
    st.markdown("### 🌍 Target Landscape")
    df_hunt = st.session_state.hunter_db
    
    # Safe Defaults for Schema
    for col, val in {'ES_Risk_Score': 5.0, 'Probability': 0.1, 'Turnover (ZAR)': 1000000}.items():
        if col not in df_hunt.columns: df_hunt[col] = val
    
    fig = px.scatter(
        df_hunt, x="ES_Risk_Score", y="Probability", size="Turnover (ZAR)", color="Sector",
        hover_name="Company", title="Strategy Map: Risk (X) vs. Win Probability (Y)",
        labels={"ES_Risk_Score": "Risk (1-10)", "Probability": "Win Prob"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # 2. THE WAR ROOM TABS
    tab_hunt, tab_engage, tab_pipe = st.tabs(["🦅 Hunter Registry", "🗣️ Engagement Log", "💰 DealStream"])

    # --- HUNTER (INPUTS & PROMOTION) ---
    with tab_hunt:
        with st.expander("🎯 ADD NEW PROSPECT (Input Intelligence)", expanded=False):
            with st.form("new_prospect"):
                c1, c2 = st.columns(2)
                p_name = c1.text_input("Company Name")
                p_sector = c2.selectbox("Sector", ["Mining", "Logistics", "Retail", "Energy", "Financial"])
                p_summary = st.text_area("Business Summary")
                c3, c4, c5 = st.columns(3)
                p_turn = c3.number_input("Turnover (ZAR)", value=1000000)
                p_reg = c4.selectbox("Region", ["Gauteng", "KZN", "Cape", "Intl"])
                p_stat = c5.selectbox("Status", ["Cold", "Warm", "Hot"])
                s1, s2 = st.columns(2)
                p_prob = s1.slider("Win Probability", 0.0, 1.0, 0.1)
                p_risk = s2.slider("Risk Score", 1.0, 10.0, 5.0)
                
                if st.form_submit_button("💾 Save Target"):
                    new_row = pd.DataFrame({
                        'Company': [p_name], 'Sector': [p_sector], 'Turnover (ZAR)': [p_turn],
                        'Region': [p_reg], 'Status': [p_stat], 'Business Summary': [p_summary],
                        'Probability': [p_prob], 'ES_Risk_Score': [p_risk]
                    })
                    st.session_state.hunter_db = pd.concat([st.session_state.hunter_db, new_row], ignore_index=True)
                    st.success("Target Acquired"); time.sleep(1); st.rerun()

        # Target Table
        st.dataframe(df_hunt, use_container_width=True, hide_index=True)

        # Promotion Logic
        st.divider()
        c1, c2 = st.columns([2,1])
        target = c1.selectbox("Select Target to Promote", df_hunt['Company'].unique())
        if c2.button("🚀 Promote to DealStream"):
             # Logic to move to DealStream...
             st.toast(f"Promoted {target} to Pipeline!")

    # --- ENGAGEMENT LOG ---
    with tab_engage:
        c1, c2 = st.columns([1,1])
        with c1:
            with st.form("log"):
                s_deal = st.selectbox("Target", st.session_state.deals_db['Deal Name'].unique())
                st.markdown("**Contact:**")
                c_name = st.text_input("Name"); c_pos = st.text_input("Position")
                c_email = st.text_input("Email"); c_phone = st.text_input("Phone")
                st.markdown("---")
                i_type = st.selectbox("Channel", ["LinkedIn", "Meeting", "Call", "Email"])
                i_note = st.text_area("Notes")
                if st.form_submit_button("Log It"):
                    # Save logic...
                    st.success("Logged"); st.rerun()
        with c2:
            st.markdown("#### History")
            if not st.session_state.activity_log.empty:
                st.dataframe(st.session_state.activity_log[['Date', 'Deal Name', 'Type', 'Notes']], hide_index=True)

    # --- DEALSTREAM ---
    with tab_pipe:
        st.dataframe(st.session_state.deals_db, use_container_width=True)
