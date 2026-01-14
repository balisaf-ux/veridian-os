import streamlit as st
import pandas as pd
import datetime
import plotly.express as px  # UPGRADE: Better Visuals
import plotly.graph_objects as go
from modules.core.db_manager import (
    save_strategic_target, 
    log_interaction, 
    load_prospects_to_dataframe, 
    load_interaction_history,
    update_target_focus,
    set_annual_target,
    get_annual_target
)

# --- CONFIGURATION & GEO-INTELLIGENCE ---
STAGE_WEIGHTS = {"New": 0.10, "Contacted": 0.25, "Meeting": 0.50, "Negotiation": 0.75, "WON": 1.00}
INTERACTION_TYPES = ["WhatsApp", "LinkedIn DM", "Video Call", "Call", "Email", "Site Visit", "Strategy Session"]

# SA REGIONAL COORDINATES (Central Points)
REGION_COORDS = {
    "Gauteng": {"lat": -26.2041, "lon": 28.0473},
    "KZN": {"lat": -29.8587, "lon": 31.0218},
    "Western Cape": {"lat": -33.9249, "lon": 18.4241},
    "Mpumalanga": {"lat": -25.4753, "lon": 30.9694},
    "Limpopo": {"lat": -23.4013, "lon": 29.4179},
    "North West": {"lat": -26.6639, "lon": 25.8828},
    "Free State": {"lat": -28.4541, "lon": 26.7968},
    "Eastern Cape": {"lat": -32.2968, "lon": 26.4194},
    "Northern Cape": {"lat": -29.0467, "lon": 21.8569},
    "Cross-Border": {"lat": -17.8216, "lon": 31.0492}
}

def render_prospecting_vertical():
    # --- HEADER AESTHETICS ---
    st.markdown("## ⚔️ War Room | Strategic Command")
    st.markdown("##### *Magisterial Intelligence: Market Segmentation & Execution*")
    st.divider()

    # --- 1. DATA HARVEST ---
    df_raw = load_prospects_to_dataframe()
    
    # NORMALIZE DATA
    if not df_raw.empty:
        df = df_raw.rename(columns={
            'company_name': 'Company', 'parent_company': 'Parent',
            'estimated_value': 'Value', 'industry': 'Industry',
            'region': 'Region', 'status': 'Status'
        })
        # Geo-Coding
        df['lat'] = df['Region'].map(lambda x: REGION_COORDS.get(x, REGION_COORDS["Gauteng"])['lat'])
        df['lon'] = df['Region'].map(lambda x: REGION_COORDS.get(x, REGION_COORDS["Gauteng"])['lon'])
    else:
        df = pd.DataFrame(columns=['Company', 'Parent', 'Value', 'Industry', 'Region', 'Status', 'lat', 'lon', 'focus_period'])

    # TARGET CALCULATIONS
    current_year = datetime.datetime.now().year
    annual_target = get_annual_target(current_year)
    monthly_target = annual_target / 12
    weekly_target = annual_target / 52
    
    # METRICS LOGIC
    if not df.empty:
        df['Weighted_Value'] = df.apply(lambda x: x['Value'] * STAGE_WEIGHTS.get(x['Status'], 0.1), axis=1)
        total_won = df[df['Status'] == 'WON']['Value'].sum()
        total_weighted = df['Weighted_Value'].sum()
        run_rate = total_weighted * 12
        gap = annual_target - run_rate
    else:
        total_won, total_weighted, run_rate, gap = 0.0, 0.0, 0.0, annual_target

    # --- 2. THE VISUAL COCKPIT (THE "WOW" FACTOR) ---
    # High-impact metric row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏁 Annual Target", f"R {annual_target:,.0f}", f"Monthly: R {monthly_target:,.0f}")
    m2.metric("📉 Run Rate", f"R {run_rate:,.0f}", delta=f"Gap: R {gap:,.0f}", delta_color="inverse")
    m3.metric("💰 Banked (WON)", f"R {total_won:,.0f}", "Real Revenue")
    m4.metric("⚖️ Weighted Pipe", f"R {total_weighted:,.0f}", "Risk Adjusted")

    st.markdown("") # Spacing

    # DASHBOARD TABS
    tab_vis, tab_map, tab_matrix = st.tabs(["📊 Strategic Visuals", "🌍 Geographic Command", "🗃️ Target Matrix"])

    with tab_vis:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 🌪️ Opportunity Funnel")
            if not df.empty:
                # Plotly Funnel
                funnel_data = df.groupby('Status')['Value'].sum().reindex(list(STAGE_WEIGHTS.keys())).fillna(0).reset_index()
                fig_funnel = px.funnel(funnel_data, x='Value', y='Status', color='Status', 
                                     color_discrete_sequence=px.colors.sequential.Blues_r)
                fig_funnel.update_layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0), height=300)
                st.plotly_chart(fig_funnel, use_container_width=True)
            else:
                st.info("Pipeline Empty. Inject targets to generate telemetry.")

        with c2:
            st.markdown("#### 🎯 Target vs Reality")
            # Plotly Gauge / Bullet Chart styling
            fig_target = go.Figure()
            fig_target.add_trace(go.Indicator(
                mode = "number+gauge+delta",
                value = run_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Projected Performance"},
                delta = {'reference': annual_target, 'position': "top"},
                gauge = {
                    'axis': {'range': [None, max(annual_target * 1.2, run_rate * 1.2)]},
                    'bar': {'color': "#2E86C1"},
                    'steps': [
                        {'range': [0, annual_target * 0.5], 'color': "lightgray"},
                        {'range': [annual_target * 0.5, annual_target], 'color': "gray"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': annual_target}}))
            fig_target.update_layout(margin=dict(t=30, l=20, r=20, b=0), height=300)
            st.plotly_chart(fig_target, use_container_width=True)

    with tab_map:
        st.markdown("#### 📍 Operational Footprint")
        if not df.empty and 'lat' in df.columns:
            # Simple Streamlit Map - Clean and Effective
            st.map(df, latitude='lat', longitude='lon', size='Value', color='#FF4B4B', zoom=4)
        else:
            st.info("No geographic data available.")

    with tab_matrix:
        # FILTERS
        f1, f2, f3 = st.columns(3)
        avail_ind = df['Industry'].unique() if not df.empty else []
        avail_reg = df['Region'].unique() if not df.empty else []
        
        sel_ind = f1.multiselect("Industry", avail_ind, default=list(avail_ind))
        sel_reg = f2.multiselect("Region", avail_reg, default=list(avail_reg))
        show_whales = f3.checkbox("Whales Only (>R1m)", value=False)
        
        # FILTER LOGIC
        df_view = df.copy()
        if not df.empty:
            if sel_ind: df_view = df_view[df_view['Industry'].isin(sel_ind)]
            if sel_reg: df_view = df_view[df_view['Region'].isin(sel_reg)]
            if show_whales: df_view = df_view[df_view['Value'] >= 1000000]

        st.dataframe(
            df_view[['Company', 'Parent', 'Industry', 'Region', 'Value', 'Status', 'focus_period']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Value": st.column_config.NumberColumn("Est. Value", format="R %.2f"),
                "Parent": st.column_config.TextColumn("Holding Group", help="Who Owns Whom"),
                "focus_period": st.column_config.Column("Priority")
            }
        )

    # --- 3. TACTICAL DRAWER (INPUT & LOGGING) ---
    st.divider()
    
    # We use an Expander to keep the "War Room" visuals clean, but accessible.
    with st.expander("📡 **Intelligence Injection & Logging (Open to Edit)**", expanded=True):
        
        tab_inject, tab_log = st.tabs(["➕ New Target Dossier", "⚡ Engagement Log"])
        
        # A. INTELLIGENCE INJECTION
        with tab_inject:
            st.caption("Strategic Entry: Populate all known fields for maximum intelligence matrix capability.")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**1. Entity Profile**")
                i_company = st.text_input("Target Name", placeholder="e.g. Afrimat KZN")
                i_parent = st.text_input("Parent Group", placeholder="e.g. Afrimat Listed")
                i_contact = st.text_input("Key Power Player", placeholder="Name & Role")
            
            with c2:
                st.markdown("**2. Market Position**")
                i_ind = st.selectbox("Industry Sector", ["Mining", "Construction", "Retail", "Energy", "Logistics", "Agriculture"])
                i_reg = st.selectbox("Geographic Node", list(REGION_COORDS.keys()))
            
            with c3:
                st.markdown("**3. Strategic Value**")
                i_val = st.number_input("Est. Monthly Value (ZAR)", step=50000.0, help="Revenue Potential per Month")
                i_notes = st.text_area("Attack Angle", placeholder="Strategic approach...", height=100)
            
            if st.button("📍 Pin Target to Matrix", type="primary"):
                if i_company:
                    save_strategic_target(i_company, i_parent, i_contact, i_ind, i_reg, i_val, i_notes)
                    st.toast(f"Target {i_company} Locked.")
                    st.rerun()

        # B. ENGAGEMENT LOG
        with tab_log:
            c_log, c_hist = st.columns([1, 2])
            with c_log:
                st.markdown("**Log New Activity**")
                if not df.empty:
                    target_opts = df['Company'].unique()
                    act_target = st.selectbox("Select Target", target_opts)
                    act_type = st.selectbox("Interaction Type", INTERACTION_TYPES)
                    act_note = st.text_input("Outcome / Sentiment")
                    act_next = st.text_input("Next Action Step")
                    if st.button("💾 Save Log"):
                        log_interaction(act_target, act_type, act_note, act_next)
                        st.success("Interaction Recorded.")
                else:
                    st.info("Inject a target to enable logging.")

            with c_hist:
                st.markdown("**Recent History**")
                if not df.empty:
                    df_hist = load_interaction_history(act_target)
                    if not df_hist.empty:
                        st.dataframe(df_hist[['date', 'interaction_type', 'outcome']], use_container_width=True, hide_index=True)
                    else:
                        st.caption("No history found for this target.")

    # --- 4. CALIBRATION (SIDEBAR) ---
    with st.sidebar:
        st.divider()
        st.header("⚙️ Calibration")
        new_t = st.number_input("Annual Goal (ZAR)", value=float(annual_target), step=1000000.0)
        if st.button("Update Target"):
            set_annual_target(current_year, new_t)
            st.rerun()
