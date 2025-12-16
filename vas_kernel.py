import streamlit as st
import pandas as pd
import numpy as np 
import datetime

# --- 1. VISUAL CORE ---
def set_design_system():
    st.set_page_config(page_title="Veridian | Group OS", layout="wide", page_icon="🦅")
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        .stApp { background-color: #F8F9FA; color: #2C3E50; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #0056b3 !important; font-weight: 800; letter-spacing: -0.5px; }
        h4, h5, .stMetricLabel { color: #5D6D7E !important; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; }
        div[data-testid="stMetricValue"] { color: #2C3E50 !important; font-weight: 700; }
        .css-1r6slb0, div.stDataFrame, .stPlotlyChart, div[data-testid="stForm"], div[data-testid="stExpander"] {
            background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 1px solid #E5E8EB; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        section[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E5E8EB; }
        .stButton > button { background-color: #0056b3; color: white; border-radius: 6px; border: none; padding: 0.5rem 1rem; font-weight: 600; transition: all 0.2s; width: 100%; }
        .stButton > button:hover { background-color: #004494; box-shadow: 0 4px 8px rgba(0,86,179,0.2); }
        .alert-box { padding: 12px; border-radius: 8px; margin-bottom: 10px; font-size: 0.9rem; border-left: 4px solid; }
        .alert-red { background-color: #FDEDEC; color: #922B21; border-color: #D9534F; }
        .alert-green { background-color: #EAFAF1; color: #186A3B; border-color: #27AE60; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION (INIT ALL DATA) ---
def check_login():
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

    if st.session_state.user_role is None:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("## 🔒 VAS | OS Secure Login")
            st.markdown("Veridian Autonomous Systems v5.0 (Industry Clouds)")
            
            role = st.selectbox("Select Identity (Simulated)", 
                ["Select Identity...", "ADMIN_VAS (Balisa)", "CLIENT_SR (Sturrock Exec)"])
            
            if st.button("Authenticate"):
                # Initialize ALL data streams
                init_cortex_db()
                init_sr_data()
                init_bonnyvale_data() 
                init_logistics_data() # <--- NEW: LOGISTICS DATA
                
                if role == "ADMIN_VAS (Balisa)":
                    st.session_state.user_role = "ADMIN"
                    st.rerun()
                elif role == "CLIENT_SR (Sturrock Exec)":
                    st.session_state.user_role = "CLIENT"
                    st.rerun()
        return False
    return True

def logout():
    st.session_state.user_role = None
    st.rerun()

# --- 3. DATABASE INITIALIZATION (CORE) ---
def init_cortex_db():
    if 'deals_db' not in st.session_state:
        data = {
            'Deal Name': ['Sturrock & Robson Pilot', 'JCI Sandton Expansion', 'Bonnyvale Off-Take', 'EnergyShield Seed Round', 'Pineapple Export Logistics'],
            'Entity': ['VAS', 'FAFT', 'Bonnyvale', 'EnergyShield', 'Bonnyvale'],
            'Sector': ['Industrial', 'Finance', 'Agriculture', 'Finance', 'Agriculture'],
            'Stage': ['Proposal', 'Lead', 'Negotiation', 'Due Diligence', 'Active'],
            'Value (ZAR)': [35000, 1500000, 450000, 5000000, 120000],
            'Probability': [0.9, 0.4, 0.7, 0.5, 1.0],
            'ES_Risk_Score': [8.2, 6.5, 4.1, 3.5, 5.0],
            'ES_AEL_Total': [15400000, 4200000, 850000, 0, 42000],
            'ES_Forecast_Shed_Hours': [850, 400, 120, 0, 95],
            'ES_Top_Risk': ["Supply Volatility", "Regulatory Compliance", "Logistics Fragmentation", "N/A", "Cold Chain Break"]
        }
        st.session_state.deals_db = pd.DataFrame(data)

    if 'hunter_db' not in st.session_state:
        # SEEDING PROSPECTS - TTE ADDED HERE
        targets = {
            'Company': ['Travel & Transport Entity (TTE)', 'Orion Mining', 'Titan Logistics', 'Apex Retail', 'Delta Energy', 'Echo Farms', 'Nebula Tech', 'Frontier Civil'],
            'Sector': ['Logistics & Fleet', 'Mining', 'Logistics', 'Retail', 'Energy', 'Agriculture', 'Technology', 'Industrial'],
            'Turnover (ZAR)': [45000000, 85000000, 12000000, 55000000, 120000000, 8000000, 45000000, 22000000],
            'Region': ['Gauteng', 'North West', 'Gauteng', 'KZN', 'Mpumalanga', 'Eastern Cape', 'Western Cape', 'Gauteng'],
            'Status': ['Warm Lead', 'Cold', 'Target', 'Target', 'Cold', 'Warm', 'Cold', 'Target']
        }
        st.session_state.hunter_db = pd.DataFrame(targets)
        
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = pd.DataFrame(columns=['Deal Name', 'Date', 'Type', 'Notes'])

# --- 4. S&R SIMULATION DATA ---
def init_sr_data():
    if 'sr_liquid' not in st.session_state:
        hours = [f"{i}:00" for i in range(24)]
        flow_rates = [85 + np.random.uniform(-5, 5) for _ in range(24)] 
        pressure = [4.2 + np.random.uniform(-0.1, 0.2) for _ in range(24)] 
        st.session_state.sr_liquid = pd.DataFrame({'Time': hours, 'Flow Efficiency (%)': flow_rates, 'Pressure (Bar)': pressure})

    if 'sr_safety' not in st.session_state:
        st.session_state.sr_safety = pd.DataFrame({
            'Category': ['PPE Violation', 'Near Miss', 'Slip/Trip', 'Vehicle Interaction', 'Equipment Failure'],
            'Incidents': [12, 5, 3, 1, 8],
            'Risk_Weight': [2, 5, 3, 9, 7]
        })

    if 'sr_energy' not in st.session_state:
        dates = pd.date_range(start="2025-12-01", periods=15)
        grid_usage = [1200 + np.random.uniform(-100, 200) for _ in range(15)]
        solar_yield = [800 + np.random.uniform(-50, 50) for _ in range(15)]
        st.session_state.sr_energy = pd.DataFrame({'Date': dates, 'Grid Usage (kWh)': grid_usage, 'PPA Yield (kWh)': solar_yield})

# --- 5. BONNYVALE SIMULATION DATA (TTE INTEGRATED) ---
def init_bonnyvale_data():
    if 'agri_harvest' not in st.session_state:
        st.session_state.agri_harvest = pd.DataFrame({
            'Block_ID': ['BV-01 (Cayenne)', 'BV-02 (Queen)', 'BV-03 (Queen)', 'BV-04 (Cayenne)', 'BV-05 (Fallow)'],
            'Hectares': [45, 30, 32, 50, 25],
            'Yield_Est_Tons': [4500, 2100, 2240, 4800, 0],
            'Status': ['Ready to Harvest', 'Growing', 'Flowering', 'Harvesting', 'Maintenance'],
            'Brix_Level': [14.2, 11.5, 9.8, 15.1, 0],
            'lat': [-33.015, -33.020, -33.018, -33.012, -33.022],
            'lon': [27.910, 27.915, 27.905, 27.920, 27.925]
        })

    if 'agri_fleet' not in st.session_state:
        st.session_state.agri_fleet = pd.DataFrame({
            'Truck_ID': ['TRK-01', 'TRK-02', 'TRK-03', 'TTE-01 (Partner)'],
            'Type': ['Tautliner', 'Flat Deck', 'Tautliner', 'Flat Deck'],
            'Driver': ['Sipho M.', 'David K.', 'John L.', 'Mandla M.'],
            'Location': ['Field A (Loading)', 'En Route (R72)', 'Summerpride (Offloading)', 'Field B (Loading)'],
            'Load_Tons': [28.5, 12.0, 31.8, 30.0],
            'Status': ['Active', 'Delayed', 'On Time', 'Active']
        })

    if 'bv_packhouse' not in st.session_state:
        st.session_state.bv_packhouse = {
            'Tons Delivered': 880,
            'Tons Processed': 780,
            'Throughput Rate': 91.7
        }

# --- 6. LOGISTICS CLOUD DATA (NEW TTE/IMPERIAL DATA) ---
def init_logistics_data():
    """Generates data for the Logistics Vertical (TTE Tenant)"""
    
    # 1. DealStream: Loads available for Mandla to grab
    if 'logistics_marketplace' not in st.session_state:
        st.session_state.logistics_marketplace = pd.DataFrame({
            'Load_ID': ['L-804', 'L-805', 'L-809', 'L-812'],
            'Origin': ['Bonnyvale Estate (EL)', 'Toyota Plant (DBN)', 'Sappi (Nelspruit)', 'Distell (Stell)'],
            'Destination': ['Summerpride Cannery', 'Gauteng DC', 'Richards Bay', 'Cape Town Port'],
            'Cargo': ['Pineapple (Bulk)', 'Auto Parts', 'Timber', 'Wine (Pallets)'],
            'Weight': ['30 Tons', '12 Tons', '34 Tons', '28 Tons'],
            'Rate (ZAR)': [18500, 12000, 24000, 9500],
            'Status': ['Open', 'Open', 'Bidding', 'Open']
        })

    # 2. Compliance Passport: Mandla's Vendor Status
    if 'logistics_compliance' not in st.session_state:
        st.session_state.logistics_compliance = {
            'Company Reg': {'status': 'Verified', 'expiry': '2026-12-01'},
            'Tax Clearance': {'status': 'Verified', 'expiry': '2026-02-28'},
            'B-BBEE Level': {'status': 'Level 1', 'expiry': '2026-05-15'},
            'Goods in Transit': {'status': 'Active (R2.5m)', 'expiry': '2026-01-01'},
            'Public Liability': {'status': 'Pending Update', 'expiry': '2025-12-20'} # The Hook
        }

# --- 7. CORE LOGIC ---
def generate_veridian_proposal(deal_data):
    client_name = deal_data['Deal Name']
    today = datetime.date.today().strftime("%d %B %Y")
    es_ael = deal_data.get('ES_AEL_Total', 15400000)
    es_shed = deal_data.get('ES_Forecast_Shed_Hours', 850)
    es_risk_driver = deal_data.get('ES_Top_Risk', "Supply Volatility")
    es_score = deal_data.get('ES_Risk_Score', 8.2)

    return f"""
# 🦅 STRATEGIC PROPOSAL: {client_name.upper()}
**Date:** {today} | **Prepared By:** Veridian Strategy Office

---

## 1. EXECUTIVE SUMMARY
{client_name} is currently navigating a period of **unquantified financial exposure**. Veridian proposes the deployment of the **Veridian Execution System** to eliminate the high-risk bleed quantified below.

## 2. THE DIAGNOSIS (EnergyShield Logic)
* **Systemic Financial Bleed:** Annual Estimated Loss (**AEL**) of **R {es_ael:,.0f}**.
* **Critical Risk Profile:** Risk Score **{es_score}/10 (High)**, driven by **{es_risk_driver}**.
* **Operational Liability:** Vulnerable to **{es_shed} hours** of forecast load curtailment.

## 3. THE PRESCRIPTION
We propose an **Operational Nervous System** to eliminate the R {es_ael:,.0f} loss.
* **Phase 1: Diagnosis:** Legal Digital Twin stress-test.
* **Phase 2: Risk Transfer:** Structuring a PPA to transfer liability.
* **Phase 3: Execution:** Eliminating the AEL.

> *"Truth is the only strategy."*
    """
