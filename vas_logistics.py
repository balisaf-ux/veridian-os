import streamlit as st
import pandas as pd
import numpy as np
import time
import vas_kernel as vk

def render_logistics_cloud():
    # 1. Initialize Data Streams
    vk.init_logistics_data()
    vk.init_bonnyvale_data() # Pulls the base fleet data
    
    st.markdown("## 🚛 Veridian Logistics Cloud")
    st.caption("Tenant: **Travel & Transport Entity (TTE)** | Status: **Sovereign**")

    # 2. High-Level KPI Strip
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fleet Utilization", "82%", "+12%")
    k2.metric("Active Loads", "4", "On Route")
    k3.metric("Revenue (MTD)", "R 425,000", "DealStream: R120k")
    k4.metric("Fuel Efficiency", "38L/100km", "Alert: Truck 07")
    
    st.divider()

    # 3. The Command Center Tabs
    tab_rev, tab_ops, tab_risk, tab_admin = st.tabs(["💰 DealStream (Loads)", "🌍 Fleet Command", "⛽ Fuel Sovereignty", "🪪 Compliance Passport"])

    # --- TAB 1: REVENUE (DealStream) ---
    with tab_rev:
        st.markdown("#### ⚡ Active Load Marketplace")
        st.caption("Real-time load matching from Veridian Industrial Partners.")
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

    # --- TAB 2: OPS ENGINE (THE ILLUSIVE REGISTRY & AVAILABILITY ENGINE) ---
    with tab_ops:
        st.subheader("🌍 Fleet Command & Registry")
        
        # SPLIT VIEW: LIVE MAP vs. REGISTRY INPUT
        ops_view, ops_input = st.tabs(["📍 Live Tracking & Availability", "➕ Fleet Registry (Input)"])
        
        # A. LIVE TRACKING & AVAILABILITY ENGINE
        with ops_view:
            df_fleet = st.session_state.agri_fleet
            st.map(st.session_state.agri_harvest, zoom=12)
            
            st.markdown("#### ⏱️ Smart Availability Engine")
            st.caption("Predictive availability based on current asset status and location.")
            
            # --- THE ALGORITHM ---
            def calculate_availability(row):
                if row['Status'] == 'Idle': return "✅ IMMEDIATELY"
                elif row['Status'] == 'Active': return "🕒 +4 Hours (Unloading)"
                elif row['Status'] == 'Delayed': return "⚠️ +12 Hours (Maintenance)"
                elif row['Status'] == 'On Time': return "🕒 Tomorrow 08:00"
                else: return "Unknown"

            # Apply Logic
            df_display = df_fleet.copy()
            df_display['Forecast'] = df_display.apply(calculate_availability, axis=1)
            
            # Render Table with Green Highlight for Immediate Availability
            st.dataframe(
                df_display[['Truck_ID', 'Type', 'Location', 'Status', 'Forecast']].style.applymap(
                    lambda x: 'background-color: #d4edda' if 'IMMEDIATELY' in x else '', subset=['Forecast']
                ), use_container_width=True, hide_index=True
            )

        # B. THE REGISTRY INPUT FORM
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
                    # Append to Kernel Data
                    new_truck = pd.DataFrame({
                        'Truck_ID': [f"{v_reg} ({v_type.split()[0]})"],
                        'Type': [v_type],
                        'Driver': [v_driver],
                        'Location': [v_loc],
                        'Load_Tons': [0],
                        'Status': ['Idle'], # Default to Idle so it shows as AVAILABLE
                        'Owner': ['Vukanathi (TTE)']
                    })
                    st.session_state.agri_fleet = pd.concat([st.session_state.agri_fleet, new_truck], ignore_index=True)
                    st.success(f"Asset {v_reg} Registered! Availability: IMMEDIATE.")
                    time.sleep(1)
                    st.rerun()

    # --- TAB 3: RISK ENGINE ---
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

    # --- TAB 4: ADMIN ENGINE ---
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

# --- TTE CUSTOMER PORTAL (CLIENT FACING) ---
def render_tte_portal():
    st.markdown("## 🚛 TTE Customer Portal")
    st.caption("Secure Client Booking & Credit Gateway")
    
    # Session State Init
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
