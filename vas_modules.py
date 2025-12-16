import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
# Import Logic from Kernel
import vas_kernel as vk

# ==========================================
# 1. ADMIN CORE MODULES
# ==========================================

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

# ==========================================
# 2. INDUSTRY CLOUDS (AGRI & LOGISTICS)
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

def render_logistics_cloud():
    vk.init_logistics_data()
    vk.init_bonnyvale_data()
    
    st.markdown("## 🚛 Veridian Logistics Cloud")
    st.caption("Tenant: **Travel & Transport Entity (TTE)** | Status: **Sovereign**")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fleet Utilization", "82%", "+12%")
    k2.metric("Active Loads", "4", "On Route")
    k3.metric("Revenue (MTD)", "R 425,000", "DealStream: R120k")
    k4.metric("Fuel Efficiency", "38L/100km", "Alert: Truck 07")
    
    st.divider()

    tab_rev, tab_ops, tab_risk, tab_admin = st.tabs(["💰 DealStream (Loads)", "🌍 Fleet Command", "⛽ Fuel Sovereignty", "🪪 Compliance Passport"])

    # TAB 1: REVENUE
    with tab_rev:
        st.markdown("#### ⚡ Active Load Marketplace")
        df_market = st.session_state.logistics_marketplace
        for index, row in df_market.iterrows():
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])
                c1.markdown(f"**{row['Origin']}** ➝ **{row['Destination']}**")
                c2.caption(f"{row['Cargo']} • {row['Weight']}")
                c3.markdown(f"**R {row['Rate (ZAR)']:,.0f}**")
                c4.markdown(f"*{row['Status']}*")
                if c5.button("ACCEPT", key=f"btn_{row['Load_ID']}"):
                    st.toast(f"Load {row['Load_ID']} Secured! Rate confirmation sent.")
                st.divider()

    # TAB 2: OPS ENGINE (V5.3 - FLEET REGISTRY & AVAILABILITY ENGINE)
    with tab_ops:
        st.subheader("🌍 Fleet Command & Registry")
        
        # Sub-Tabs for Map vs. Input
        ops_view, ops_input = st.tabs(["📍 Live Tracking", "➕ Fleet Registry (Input)"])
        
        # SUB-TAB A: MAP & AVAILABILITY ENGINE
        with ops_view:
            df_fleet = st.session_state.agri_fleet
            st.map(st.session_state.agri_harvest, zoom=12)
            
            # --- THE SMART AVAILABILITY LOGIC ---
            st.markdown("#### ⏱️ Asset Availability Forecast")
            
            def calculate_availability(row):
                if row['Status'] == 'Idle': return "✅ IMMEDIATELY"
                elif row['Status'] == 'Active': return "🕒 +4 Hours (Unloading)"
                elif row['Status'] == 'Delayed': return "⚠️ +12 Hours (Maintenance)"
                elif row['Status'] == 'On Time': return "🕒 Tomorrow 08:00"
                else: return "Unknown"

            # Create a display copy
            df_display = df_fleet.copy()
            df_display['Earliest Availability'] = df_display.apply(calculate_availability, axis=1)
            
            # Show the strategic view
            st.dataframe(
                df_display[['Truck_ID', 'Type', 'Location', 'Status', 'Earliest Availability']].style.applymap(
                    lambda x: 'background-color: #d4edda' if 'IMMEDIATELY' in x else '', subset=['Earliest Availability']
                ),
                use_container_width=True, hide_index=True
            )

        # SUB-TAB B: THE INPUT FORM
        with ops_input:
            st.markdown("#### 🚛 Onboard New Asset")
            st.caption("Register Vehicle or Trailer into the TTE Digital Twin.")
            
            with st.form("fleet_input"):
                c1, c2 = st.columns(2)
                v_type = c1.selectbox("Asset Type", ["Mechanical Horse", "Interlink Trailer (30T)", "Tautliner (12T)", "Flat Deck", "LDV / Shuttle"])
                v_reg = c2.text_input("Registration Number (e.g., CA 123-456)")
                v_vin = c1.text_input("VIN / Chassis Number")
                v_driver = c2.text_input("Assigned Driver")
                v_loc = st.selectbox("Current Location", ["Depot (Kempton Park)", "Durban Port", "Cape Town", "En Route"])
                
                submitted = st.form_submit_button("💾 Register Asset")
                
                if submitted:
                    new_truck = pd.DataFrame({
                        'Truck_ID': [f"{v_reg} ({v_type.split()[0]})"],
                        'Type': [v_type],
                        'Driver': [v_driver],
                        'Location': [v_loc],
                        'Load_Tons': [0],
                        'Status': ['Idle'], 
                        'Owner': ['Vukanathi (TTE)']
                    })
                    st.session_state.agri_fleet = pd.concat([st.session_state.agri_fleet, new_truck], ignore_index=True)
                    st.success(f"Asset {v_reg} Registered! Availability: IMMEDIATE.")
                    time.sleep(1)
                    st.rerun()

    # TAB 3: RISK ENGINE
    with tab_risk:
        st.subheader("⛽ Fuel Forensics | TTE-07")
        c_fuel, c_alert = st.columns([3, 1])
        with c_fuel:
            fuel_hours = [f"{i}:00" for i in range(24)]
            fuel_levels = [900 - (i*10) if i != 8 else 900-(i*10)-50 for i in range(24)] 
            fuel_data = pd.DataFrame({'Time': fuel_hours, 'Fuel Level (L)': fuel_levels})
            st.line_chart(fuel_data.set_index('Time'), color="#C0392B")
        with c_alert:
            st.error("🚨 **THEFT EVENT**")
            st.markdown("08:00 AM • **-50L Drop**")
            st.button("👮 Log Incident")

    # TAB 4: ADMIN ENGINE
    with tab_admin:
        st.markdown("#### Veridian Verified Identity")
        comp = st.session_state.logistics_compliance
        c1, c2 = st.columns(2)
        with c1:
            st.success(f"✅ Company Reg: {comp['Company Reg']['status']}")
            st.success(f"✅ Tax Clearance: {comp['Tax Clearance']['status']}")
        with c2:
            st.success(f"✅ B-BBEE Status: {comp['B-BBEE Level']['status']}")
            if "Pending" in comp['Public Liability']['status']:
                st.warning(f"⚠️ Public Liability: {comp['Public Liability']['status']}")
                st.button("Renew via Broker")
            else:
                st.success(f"✅ Public Liability: {comp['Public Liability']['status']}")

# ==========================================
# 3. INDUSTRIAL MODULES (S&R)
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
# 4. TTE CUSTOMER PORTAL (WITH DEMO)
# ==========================================

def render_tte_portal():
    st.markdown("## 🚛 TTE Customer Portal")
    st.caption("Secure Client Booking & Credit Gateway")
    
    if 'tte_step' not in st.session_state: st.session_state.tte_step = 1
    if 'tte_credit_status' not in st.session_state: st.session_state.tte_credit_status = "Pending"
    if 'tte_quote' not in st.session_state: st.session_state.tte_quote = 0
    if 'tte_details' not in st.session_state: st.session_state.tte_details = {}
    if 'demo_fill' not in st.session_state: st.session_state.demo_fill = False

    step_progress = (st.session_state.tte_step / 4) 
    st.progress(step_progress, text=f"Step {st.session_state.tte_step} of 4")

    # STEP 1
    if st.session_state.tte_step == 1:
        if st.button("⚡ DEMO: Auto-Fill Form", type="primary"):
            st.session_state.demo_fill = True
            st.rerun()

        st.subheader("1. Client Registration & Credit Check")
        
        def_name = "Vukanathi Logistics" if st.session_state.demo_fill else ""
        def_reg = "2024/0056/07" if st.session_state.demo_fill else ""
        def_vat = "4900123456" if st.session_state.demo_fill else ""
        
        with st.form("client_reg"):
            c1, c2 = st.columns(2)
            c_name = c1.text_input("Company Name", value=def_name)
            c_reg = c2.text_input("Registration Number", value=def_reg)
            c_type = c1.selectbox("Client Sector", ["Government", "Corporate (Listed)", "Private/SME"])
            c_vat = c2.text_input("VAT Number", value=def_vat)
            st.markdown("---")
            st.markdown("**Credit Application**")
            c_terms = st.checkbox("Apply for 30-Day Payment Terms?", value=True if st.session_state.demo_fill else False)
            uploaded_docs = st.file_uploader("Upload CIPC & Bank Letter (Required for Credit)")
            submit_reg = st.form_submit_button("Submit Application")
            
            if submit_reg:
                if c_type in ["Government", "Corporate (Listed)"]:
                    st.session_state.tte_credit_status = "APPROVED (30 Days)"
                    st.success("✅ Credit Approved! Terms: 30 Days Net.")
                elif c_terms:
                    st.session_state.tte_credit_status = "REJECTED (Risk Profile)"
                    st.warning("⚠️ Credit Criteria Not Met. Defaulting to CASH / COD terms.")
                else:
                    st.session_state.tte_credit_status = "CASH (Standard)"
                    st.info("ℹ️ Account set to Cash on Delivery.")
                time.sleep(1.0)
                st.session_state.tte_step = 2
                st.rerun()

    # STEP 2
    elif st.session_state.tte_step == 2:
        st.subheader("2. Load Logistics & Quoting")
        st.caption(f"Account Terms: **{st.session_state.tte_credit_status}**")
        def_cargo = "Steel Coils (Grade A)" if st.session_state.demo_fill else ""
        
        with st.form("load_details"):
            l1, l2 = st.columns(2)
            origin = l1.selectbox("Origin", ["Johannesburg", "Durban", "Cape Town", "Polokwane"])
            dest = l2.selectbox("Destination", ["Durban", "Cape Town", "East London", "Nelspruit"])
            cargo = l1.text_input("Product Description", value=def_cargo)
            weight = l2.number_input("Load Weight (Tons)", 1, 34, 30)
            
            est_price = 15000 + ((weight - 10) * 500) if weight > 10 else 15000
            get_quote = st.form_submit_button("Generate Quote")
            
            if get_quote:
                st.session_state.tte_quote = est_price
                st.session_state.tte_details = {'Org': origin, 'Dst': dest, 'Wgt': weight, 'Crg': cargo}
                st.session_state.tte_step = 3
                st.rerun()

    # STEP 3
    elif st.session_state.tte_step == 3:
        st.subheader("3. Quote Acceptance")
        st.markdown(f"""
        <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9;">
            <h3>QUOTE: TTE-{np.random.randint(1000,9999)}</h3>
            <p><strong>Route:</strong> {st.session_state.tte_details['Org']} ➝ {st.session_state.tte_details['Dst']}</p>
            <p><strong>Cargo:</strong> {st.session_state.tte_details['Crg']} ({st.session_state.tte_details['Wgt']} Tons)</p>
            <hr>
            <h2 style="color: #0056b3;">TOTAL: R {st.session_state.tte_quote:,.2f}</h2>
            <p style="font-size: 0.8rem;">Terms: {st.session_state.tte_credit_status}</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("❌ Reject Quote"):
            st.session_state.tte_step = 2
            st.rerun()
        if c2.button("✅ ACCEPT & TRADE"):
            st.session_state.tte_step = 4
            st.rerun()

    # STEP 4
    elif st.session_state.tte_step == 4:
        st.subheader("4. Trading Active")
        st.balloons()
        st.success("TTE Ops Team Notified! Truck Dispatch Initiated.")
        st.markdown("### 📄 PRO-FORMA INVOICE GENERATED")
        st.info(f"Invoice #INV-2025-{np.random.randint(100,999)} has been emailed to finance@client.co.za")
        if st.button("Start New Booking"):
            st.session_state.tte_step = 1
            st.session_state.demo_fill = False 
            st.rerun()
