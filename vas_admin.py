import streamlit as st
import pandas as pd
import vas_kernel as vk
import time

def render_admin_home():
    st.markdown("## 🌍 Central Command (God View)")
    c1, c2, c3 = st.columns(3)
    val = st.session_state.deals_db['Value (ZAR)'].sum() if 'deals_db' in st.session_state else 0
    c1.metric("Total System Value", f"R {val:,.0f}", "Live Data")
    c2.metric("Active Nodes", "3", "JHB • EL • MP")
    c3.metric("Global Alert Level", "LOW", "Stable")
    st.divider()
    
    st.subheader("Sovereign Footprint & Health")
    map_col, status_col = st.columns([2, 1], gap="medium")
    with map_col:
        st.map(pd.DataFrame({'lat': [-26.1076, -25.8728, -32.9833], 'lon': [28.0567, 29.2554, 27.8667]}), zoom=5, use_container_width=True)
    with status_col:
        st.markdown("""
        <div style="padding: 15px; border-left: 4px solid #27AE60; background-color: #F0FDF4; border-radius: 8px; margin-bottom: 10px;">
            <div style="font-weight: bold; color: #2C3E50;">Veridian Group (HQ)</div><div style="font-size: 0.8rem; color: #16A34A;">🟢 ONLINE • Systems Nominal</div>
        </div>
        <div style="padding: 15px; border-left: 4px solid #27AE60; background-color: #F0FDF4; border-radius: 8px; margin-bottom: 10px;">
            <div style="font-weight: bold; color: #2C3E50;">Bonnyvale (Agri)</div><div style="font-size: 0.8rem; color: #16A34A;">🟢 ONLINE • Harvest Active</div>
        </div>
        <div style="padding: 15px; border-left: 4px solid #C0392B; background-color: #FEF2F2; border-radius: 8px; margin-bottom: 10px;">
            <div style="font-weight: bold; color: #2C3E50;">Sturrock & Robson</div><div style="font-size: 0.8rem; color: #C0392B;">🔴 ALERT • Filter Pressure Critical</div>
        </div>
        """, unsafe_allow_html=True)

def render_crm_module():
    st.markdown("## 🤝 DealStream (Group CRM)")
    st.caption("Internal Pipeline Management & Execution")
    df = st.session_state.deals_db
    
    weighted_val = (df['Value (ZAR)'] * df['Probability']).sum()
    total_val = df['Value (ZAR)'].sum()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pipeline", f"R {total_val:,.0f}", f"{len(df)} Deals")
    m2.metric("Weighted Forecast", f"R {weighted_val:,.0f}", "Risk Adjusted")
    m3.metric("Win Rate", "32%")
    st.divider()

    st.subheader("Active Opportunities")
    with st.container():
        st.dataframe(df[['Deal Name', 'Entity', 'Stage', 'Value (ZAR)', 'Probability', 'ES_Risk_Score']].style.background_gradient(subset=['Probability'], cmap="Blues"), use_container_width=True, hide_index=True, height=300)
    
    st.write("")
    st.subheader("Deal Inspector")
    with st.container():
        c_select, c_space = st.columns([1, 2])
        with c_select:
            selected_deal = st.selectbox("Select Deal", df['Deal Name'].unique())
        current_row = df[df['Deal Name'] == selected_deal].iloc[0]
        st.divider()
        
        tab_edit, tab_engage, tab_proposal = st.tabs(["📝 Edit Deal", "🗣️ Log Engagement", "📄 Proposal Studio"])
        
        with tab_edit:
            with st.form("edit_deal_form"):
                stages = ["Lead", "Meeting", "Proposal", "Negotiation", "Closed", "Active"]
                current_stage = current_row['Stage']
                idx = stages.index(current_stage) if current_stage in stages else 0
                new_stage = st.selectbox("Stage", stages, index=idx)
                new_prob = st.slider("Probability", 0.0, 1.0, float(current_row['Probability']))
                if st.form_submit_button("Update Record"):
                    db_idx = df.index[df['Deal Name'] == selected_deal].tolist()[0]
                    st.session_state.deals_db.at[db_idx, 'Stage'] = new_stage
                    st.session_state.deals_db.at[db_idx, 'Probability'] = new_prob
                    st.success("Updated")
                    st.rerun()
        
        with tab_engage:
            with st.form("log_int"):
                i_date = st.date_input("Date"); i_type = st.selectbox("Type", ["Call", "Meeting", "Email"]); i_notes = st.text_area("Notes", height=100)
                if st.form_submit_button("Log Interaction"):
                    new_log = pd.DataFrame({'Deal Name': [selected_deal], 'Date': [i_date], 'Type': [i_type], 'Notes': [i_notes]})
                    st.session_state.activity_log = pd.concat([st.session_state.activity_log, new_log], ignore_index=True)
                    st.success("Logged")
                    st.rerun()
            hist = st.session_state.activity_log[st.session_state.activity_log['Deal Name'] == selected_deal].sort_values(by="Date", ascending=False)
            if not hist.empty:
                for i, r in hist.iterrows(): st.markdown(f"<div style='background:#f9f9f9;padding:10px;margin-bottom:5px;border-left:3px solid #0056b3'><small>{r['Date']} • {r['Type']}</small><br>{r['Notes']}</div>", unsafe_allow_html=True)

        with tab_proposal:
            if st.button("✨ Generate Strategy"):
                st.session_state['last_proposal'] = vk.generate_veridian_proposal(current_row)
            if 'last_proposal' in st.session_state:
                st.text_area("Output", st.session_state['last_proposal'], height=250)

def render_hunter_module():
    st.markdown("## 🦅 Hunter (Prospecting Engine)")
    st.caption("Market Segmentation & Target Identification")
    df_hunt = st.session_state.hunter_db
    
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1: sector_filter = st.multiselect("Sector", df_hunt['Sector'].unique(), default=df_hunt['Sector'].unique())
        with c2: region_filter = st.multiselect("Region", df_hunt['Region'].unique(), default=df_hunt['Region'].unique())
        with c3: min_rev = st.number_input("Min Turnover", 0, 100000000, 0)
    
    filtered_df = df_hunt[(df_hunt['Sector'].isin(sector_filter)) & (df_hunt['Region'].isin(region_filter)) & (df_hunt['Turnover (ZAR)'] >= min_rev)]
    st.divider()
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    c1, c2 = st.columns([2,1])
    with c1: target_to_convert = st.selectbox("Select Target", filtered_df['Company'].unique()) if not filtered_df.empty else None
    with c2:
        st.write(""); st.write("")
        if target_to_convert and st.button("Promote to DealStream"):
            target_row = df_hunt[df_hunt['Company'] == target_to_convert].iloc[0]
            new_deal = pd.DataFrame({'Deal Name': [target_row['Company']], 'Entity': ["VAS"], 'Sector': [target_row['Sector']], 'Stage': ["Lead"], 'Value (ZAR)': [target_row['Turnover (ZAR)'] * 0.05], 'Probability': [0.1], 'ES_Risk_Score': [5.0], 'ES_AEL_Total': [0], 'ES_Forecast_Shed_Hours': [0], 'ES_Top_Risk': ["Pending"]})
            st.session_state.deals_db = pd.concat([st.session_state.deals_db, new_deal], ignore_index=True)
            st.success("Promoted!"); time.sleep(0.5); st.rerun()

    st.divider()
    with st.expander("➕ Add New Prospect to Registry"):
        with st.form("reg"):
            n = st.text_input("Company"); s = st.selectbox("Sector", ["Mining","Logistics","Retail"]); t = st.number_input("Turnover")
            if st.form_submit_button("Add to Hunter Database"):
                new_p = pd.DataFrame({'Company': [n], 'Sector': [s], 'Turnover (ZAR)': [t], 'Region': ["Gauteng"], 'Status': ['Cold']})
                st.session_state.hunter_db = pd.concat([st.session_state.hunter_db, new_p], ignore_index=True)
                st.rerun()
