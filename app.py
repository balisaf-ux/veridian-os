import streamlit as st
import pandas as pd
import time
import vas_kernel as vk

# --- PAGE CONFIG ---
st.set_page_config(page_title="Veridian | Group OS", layout="wide", page_icon="🦅")

# --- MODULAR IMPORTS (HIERARCHICAL) ---
# We now import from the specific domain folders
from vas_admin import render_admin_core
from modules.industrial.sturrock import render_sturrock_dashboard
from modules.agriculture.bonnyvale import render_bonnyvale_dashboard
from modules.logistics.tte import render_tte_dashboard

# --- LOGIN CHECK ---
vk.set_design_system()
if not vk.check_login():
    st.stop()

# --- SIDEBAR: THE NAVIGATION TREE ---
st.sidebar.title("VAS | OS")
st.sidebar.caption("Sovereign Operating System v7.1")

# LEVEL 1: VIEW SELECTION
view_mode = st.sidebar.radio("Clearance Level", ["Admin Core", "Industry Clouds"])

if view_mode == "Admin Core":
    render_admin_core()

elif view_mode == "Industry Clouds":
    st.sidebar.divider()
    
    # LEVEL 2: INDUSTRY SELECTION (The Vertical)
    selected_industry = st.sidebar.selectbox(
        "Select Vertical",
        ["Industrial", "Agriculture", "Logistics", "Energy (Prospecting)"]
    )
    
    # LEVEL 3: COMPANY SELECTION (The Entity)
    # This map allows us to scale. New clients are added here.
    company_map = {
        "Industrial": ["Sturrock & Robson", "Frontier Civil (Lead)"],
        "Agriculture": ["Bonnyvale Estates", "Echo Farms (Lead)"],
        "Logistics": ["Travel & Transport (TTE)", "Titan Logistics"],
        "Energy (Prospecting)": ["No Active Assets"]
    }
    
    selected_company = st.sidebar.selectbox(
        "Select Entity",
        company_map[selected_industry]
    )
    
    # --- ROUTING ENGINE ---
    # 1. INDUSTRIAL CLOUD
    if selected_industry == "Industrial":
        if selected_company == "Sturrock & Robson":
            render_sturrock_dashboard()
        else:
            st.info(f"🚧 {selected_company} module is currently under development.")

    # 2. AGRI CLOUD
    elif selected_industry == "Agriculture":
        if selected_company == "Bonnyvale Estates":
            render_bonnyvale_dashboard()
        else:
            st.info(f"🚧 {selected_company} module is currently under development.")

    # 3. LOGISTICS CLOUD
    elif selected_industry == "Logistics":
        if selected_company == "Travel & Transport (TTE)":
            render_tte_dashboard()
        else:
            st.info(f"🚧 {selected_company} module is currently under development.")
            
    # 4. CATCH-ALL
    else:
        st.warning("⚠️ No active modules loaded for this sector.")

st.sidebar.divider()
if st.sidebar.button("Log Out"): vk.logout()
