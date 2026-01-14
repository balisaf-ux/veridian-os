import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import vas_kernel as vk

def render_prospecting_dashboard():
    # 1. TRIGGER DATA LOAD
    if 'hunter_db' not in st.session_state: vk.init_bonnyvale_data()
    
    st.markdown("## 🔭 Veridian Prospecting | Global Command")
    st.caption("Strategic Intelligence & Target Acquisition (Group Level)")

    # 2. VISUAL STRATEGY MAP (RESTORED)
    st.markdown("### 🌍 Target Landscape")
    df_hunt = st.session_state.hunter_db
    
    # Schema Safety Checks (Ensures no crashes if Kernel is old)
    if 'ES_Risk_Score' not in df_hunt.columns: df_hunt['ES_Risk_Score'] = 5.0
    if 'Probability' not in df_hunt.columns: df_hunt['Probability'] = 0.1
    if 'Turnover (ZAR)' not in df_hunt.columns: df_hunt['Turnover (ZAR)'] = 1000000
    
    fig = px.scatter(
        df_hunt, 
        x="ES_Risk_Score", 
        y="Probability", 
        size="Turnover (ZAR)", 
        color="Sector",
        hover_name="Company",
        title="Strategy Map: Risk (X) vs. Win Probability (Y) vs. Value (Size)",
        labels={"ES_Risk_Score": "Operational Risk (1-10)", "Probability": "Win Probability (0-1)"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="#f8f9fa")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 3. THE WAR ROOM TABS
    tab_hunt, tab_engage, tab_pipe = st.tabs(["🦅 Hunter Registry", "🗣️ Engagement Log", "💰 DealStream"])

    # --- TAB 1: HUNTER REGISTRY (FULL INPUTS RESTORED) ---
    with tab_hunt:
        # A. INPUT INTELLIGENCE FORM
        with st.expander("🎯 ADD NEW PROSPECT (Input Intelligence)", expanded=False):
            with st.form("new_prospect_form"):
                c1, c2 = st.columns(2)
                p_name = c1.text_input("Prospect / Company Name")
                p_sector = c2.selectbox("Industry / Sector", ["Mining", "Logistics", "Retail", "Energy", "Financial", "Public Sector"])
                
                # RESTORED: Business Summary
                p_summary = st.text_area("Business Summary & Context", placeholder="e.g., Large scale logistics operator facing efficiency challenges...")
                
                c3, c4, c5 = st.columns(3)
                p_turnover = c3.number_input("Est. Turnover (ZAR)", min_value=0, value=1000000)
                p_region = c4.selectbox("Region", ["Gauteng", "Western Cape", "KZN", "Eastern Cape", "International"])
                p_status = c5.selectbox("Initial Status", ["Cold", "Warm", "Hot"])
                
                st.markdown("**Strategic Assessment**")
                s1, s2 = st.columns(2)
                # RESTORED: Probability & Risk Sliders
                p_prob = s1.slider("Win Probability (%)", 0, 100, 10) / 100
                p_risk = s2.slider("ES Risk Score (1=Safe, 10=Critical)", 1.0, 10.0, 5.0)
                
                if st.form_submit_button("💾 Add Target to Registry"):
                    new_row = pd.DataFrame({
                        'Company': [p_name],
                        'Sector': [p_sector],
                        'Turnover (ZAR)': [p_turnover],
                        'Region': [p_region],
                        'Status': [p_status],
                        'Business Summary': [p_summary],
                        'Probability': [p_prob],
                        'ES_Risk_Score': [p_risk]
                    })
                    st.session_state.hunter_db = pd.concat([st.session_state.hunter_db, new_row], ignore_index=True)
                    st.success(f"Target '{p_name}' acquired.")
                    time.sleep(1)
                    st.rerun()

        # B. DATA TABLE & FILTERS
        st.subheader("Target Registry")
        
        c1, c2, c3 = st.columns(3)
        with c1: sector_filter = st.multiselect("Sector", df_hunt['Sector'].unique(), default=df_hunt['Sector'].unique())
        with c2: region_filter = st.multiselect("Region", df_hunt['Region'].unique(), default=df_hunt['Region'].unique())
        with c3: min_rev = st.number_input("Min Turnover Filter", 0, 100000000, 0)
    
        filtered_df = df_hunt[(df_hunt['Sector'].isin(sector_filter)) & (df_hunt['Region'].isin(region_filter)) & (df_hunt['Turnover (ZAR)'] >= min_rev)]
        
        st.dataframe(
            filtered_df[['Company', 'Sector', 'Region', 'Turnover (ZAR)', 'Probability', 'ES_Risk_Score', 'Status']], 
            use_container_width=True, 
            hide_index=True
        )
        
        # C. PROMOTION LOGIC
        st.divider()
        c1, c2 = st.columns([2,1])
        with c1: 
            target_to_convert = st.selectbox("Select Target to Promote", filtered_df['Company'].unique()) if not filtered_df.empty else None
        with c2:
            st.write(""); st.write("")
            if target_to_convert and st.button("🚀 Promote to DealStream"):
                target_row = df_hunt[df_hunt['Company'] == target_to_convert].iloc[0]
                new_deal = pd.DataFrame({
                    'Deal Name': [target_row['Company']], 
                    'Entity': ["VAS"], 
                    'Sector': [target_row['Sector']], 
                    'Stage': ["Lead"], 
                    'Value (ZAR)': [target_row['Turnover (ZAR)'] * 0.05], 
                    'Probability': [target_row['Probability']], 
                    'ES_Risk_Score': [target_row['ES_Risk_Score']]
                })
                st.session_state.deals_db = pd.concat([st.session_state.deals_db, new_deal], ignore_index=True)
                st.success(f"Promoted {target_to_convert} to DealStream!")
                time.sleep(1); st.rerun()

    # --- TAB 2: ENGAGEMENT LOG (FULL CONTACT DETAILS RESTORED) ---
    with tab_engage:
        st.subheader("Interaction Logging")
        c_input, c_history = st.columns([1, 1], gap="large")
        
        with c_input:
            st.markdown("#### 📝 Log New Interaction")
            with st.form("log_int"):
                s_deal = st.selectbox("Select Target / Deal", st.session_state.deals_db['Deal Name'].unique())
                
                # RESTORED: Granular Contact Details
                st.markdown("**Contact Details**")
                c_name = st.text_input("Name of Contact")
                c_pos = st.text_input("Position")
                c_email = st.text_input("Email Address")
                c_phone = st.text_input("Contact Number")
                
                st.markdown("---")
                
                # RESTORED: LinkedIn in Dropdown
                i_date = st.date_input("Date")
                i_type = st.selectbox("Engagement Type", ["LinkedIn", "Meeting (In-Person)", "Virtual Call", "Email", "Whatsapp", "Site Visit"])
                i_notes = st.text_area("Interaction Notes", height=100)
                
                if st.form_submit_button("💾 Save to Log"):
                    new_log = pd.DataFrame({
                        'Deal Name': [s_deal], 
                        'Company': [s_deal], 
                        'Contact Name': [c_name], 
                        'Position': [c_pos], 
                        'Email': [c_email], 
                        'Phone': [c_phone], 
                        'Date': [i_date], 
                        'Type': [i_type], 
                        'Notes': [i_notes]
                    })
                    
                    # Schema Safety for old logs
                    if 'Contact Name' not in st.session_state.activity_log.columns:
                        for col in ['Contact Name', 'Position', 'Email', 'Phone', 'Company']:
                            st.session_state.activity_log[col] = None
                            
                    st.session_state.activity_log = pd.concat([st.session_state.activity_log, new_log], ignore_index=True)
                    st.success("Engagement Recorded"); st.rerun()

        with c_history:
            st.markdown("#### 📜 Engagement History")
            if not st.session_state.activity_log.empty:
                hist = st.session_state.activity_log.sort_values(by="Date", ascending=False)
                for i, r in hist.iterrows():
                    # Display Contact Info if available
                    contact_info = f" | {r['Contact Name']} ({r['Position']})" if 'Contact Name' in r and pd.notna(r['Contact Name']) else ""
                    
                    st.markdown(
                        f"""
                        <div style='background:#f9f9f9; padding:15px; margin-bottom:10px; border-left:4px solid #0056b3; border-radius:5px;'>
                            <div style='font-weight:bold; font-size:1.1em; color:#2C3E50;'>
                                {r['Deal Name']} 
                                <span style='font-weight:normal; font-size:0.8em; color:#7f8c8d;'> • {r['Type']}</span>
                            </div>
                            <div style='font-size:0.85em; color:#34495e; margin-bottom:5px;'>
                                📅 {r['Date']} {contact_info}
                            </div>
                            <div style='font-style:italic; color:#555;'>"{r['Notes']}"</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                st.info("No engagement history found.")

    # --- TAB 3: DEALSTREAM (RESTORED) ---
    with tab_pipe:
        st.subheader("💰 DealStream (Active Pipeline)")
        st.dataframe(
            st.session_state.deals_db[['Deal Name', 'Entity', 'Stage', 'Value (ZAR)', 'Probability', 'ES_Risk_Score']].style.background_gradient(subset=['Probability'], cmap="Blues"), 
            use_container_width=True, 
            hide_index=True,
            height=400
        )
