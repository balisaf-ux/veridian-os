import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random

# ==========================================
# 0. SYSTEM AUTH & DESIGN
# ==========================================
def set_design_system():
    st.markdown("""<style>.stMetric {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2C3E50;}</style>""", unsafe_allow_html=True)

def check_login():
    if 'user_role' not in st.session_state: st.session_state.user_role = None
    if st.session_state.user_role is None:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image("https://placehold.co/400x150?text=Veridian+OS", use_container_width=True)
            with st.form("login"):
                pwd = st.text_input("Access Key", type="password")
                if st.form_submit_button("Initialize"):
                    if pwd == "admin": st.session_state.user_role = "ADMIN"; st.rerun()
                    elif pwd == "client": st.session_state.user_role = "CLIENT"; st.rerun()
        return False
    return True

def logout(): st.session_state.user_role = None; st.rerun()

# ==========================================
# 1. DATA INITIALIZATION
# ==========================================
def init_bonnyvale_data():
    if 'agri_harvest' not in st.session_state:
        st.session_state.agri_harvest = pd.DataFrame({
            'Block_ID': ['BV-01', 'BV-02', 'BV-03', 'BV-04', 'BV-05'],
            'Status': ['Harvest Ready', 'Maturing', 'Planting', 'Fallow', 'Harvest Ready'],
            'Readiness': [0.95, 0.60, 0.10, 0.0, 0.88], 
            'lat': [-33.015, -33.012, -33.018, -33.020, -33.010],
            'lon': [27.915, 27.912, 27.918, 27.920, 27.910]
        })
    if 'agri_fleet' not in st.session_state:
        st.session_state.agri_fleet = pd.DataFrame({
            'Truck_ID': ['TRK-01', 'TRK-02', 'TRK-03'], 'Type': ['Interlink', 'Interlink', 'Flatbed'],
            'Status': ['Active', 'Delayed', 'On Time'], 'Location': ['Zone A', 'Summerpride', 'N2'],
            'Load_Tons': [32, 34, 28], 'Driver': ['Mandla', 'Sipho', 'John'], 'Owner': ['TTE', 'TTE', 'Indep']
        })

def init_logistics_data():
    if 'logistics_marketplace' not in st.session_state:
        st.session_state.logistics_marketplace = pd.DataFrame({
            'Load_ID': ['L-101', 'L-102', 'L-103'], 'Origin': ['JHB', 'DBN', 'CPT'],
            'Destination': ['DBN', 'CPT', 'EL'], 'Cargo': ['Steel', 'FMCG', 'Fruit'],
            'Weight': ['32T', '18T', '28T'], 'Rate (ZAR)': [18500, 22000, 16500],
            'Status': ['Open', 'Open', 'Negotiating']
        })
    if 'logistics_compliance' not in st.session_state:
        st.session_state.logistics_compliance = {
            'Company Reg': {'status': 'Verified', 'exp': '2026'},
            'Tax Clearance': {'status': 'Verified', 'exp': '2025-12'},
            'B-BBEE Level': {'status': 'Level 1', 'exp': '2026'},
            'Public Liability': {'status': 'Pending Update', 'exp': '2024-11'}
        }

def init_sr_data():
    if 'sr_liquid' not in st.session_state:
        hours = [f"{i}:00" for i in range(24)]
        efficiency = [85 + np.random.randint(-5, 5) for _ in range(24)]
        st.session_state.sr_liquid = pd.DataFrame({'Time': hours, 'Flow Efficiency (%)': efficiency})
    if 'sr_safety' not in st.session_state:
        st.session_state.sr_safety = pd.DataFrame({'Category': ['Near Miss', 'First Aid', 'LTI'], 'Incidents': [12, 4, 0]})
    if 'sr_energy' not in st.session_state:
        dates = pd.date_range(start="2025-12-01", periods=15)
        st.session_state.sr_energy = pd.DataFrame({'Date': dates, 'Grid': [100-(i*2) for i in range(15)], 'PPA': [i*2 for i in range(15)]})

# ==========================================
# 2. PROSPECTING DATABASES (UPDATED SCHEMA V3)
# ==========================================
if 'deals_db' not in st.session_state:
    st.session_state.deals_db = pd.DataFrame({
        'Deal Name': ['Sturrock & Robson', 'Bonnyvale Estates'],
        'Entity': ['Industrial', 'Agri'], 'Stage': ['Active', 'Active'],
        'Value (ZAR)': [4500000, 1200000], 'Probability': [1.0, 1.0], 'ES_Risk_Score': [7.2, 4.1]
    })

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = pd.DataFrame(columns=[
        'Deal Name', 'Company', 'Contact Name', 'Position', 'Email', 'Phone', 'Date', 'Type', 'Notes'
    ])

# UPDATED: Added 'Summary', 'Probability', 'Risk' to Hunter DB
if 'hunter_db' not in st.session_state:
    st.session_state.hunter_db = pd.DataFrame({
        'Company': ['Anglo American', 'Transnet', 'Shoprite'],
        'Sector': ['Mining', 'Logistics', 'Retail'],
        'Turnover (ZAR)': [150000000, 45000000, 89000000],
        'Region': ['Gauteng', 'KZN', 'Western Cape'],
        'Status': ['Cold', 'Warm', 'Cold'],
        'Business Summary': ['Global mining giant.', 'State-owned rail & port.', 'Leading retailer.'],
        'Probability': [0.1, 0.3, 0.05],
        'ES_Risk_Score': [4.5, 8.2, 3.1]
    })
