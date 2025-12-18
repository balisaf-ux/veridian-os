import streamlit as st
import vas_kernel as vk

# MODULAR IMPORTS
from vas_admin import render_admin_core
from modules.industrial.sturrock import render_sturrock_dashboard
from modules.agriculture.bonnyvale import render_bonnyvale_dashboard
from modules.logistics.tte import render_tte_dashboard
from modules.energy.prospecting import render_prospecting_dashboard # <--- ENSURE THIS IMPORT EXISTS

st.set_page_config(page_title="Veridian | Group OS", layout="wide", page_icon="🦅")
vk.set_design_system()

if not vk.check_login(): st.stop()

st.sidebar.title("VAS | OS")
view_mode = st.sidebar.radio("Clearance Level", ["Admin Core", "Industry Clouds"])

if view_mode == "Admin Core":
    render_admin_core()

elif view_mode == "Industry Clouds":
    st.sidebar.divider()
    
    # RENAMED SELECTION
    selected_industry = st.sidebar.selectbox(
        "Select Vertical",
        ["Industrial", "Agriculture", "Logistics", "Veridian Prospecting"]
    )
    
    company_map = {
        "Industrial": ["Sturrock & Robson"],
        "Agriculture": ["Bonnyvale Estates"],
        "Logistics": ["Travel & Transport (TTE)"],
        "Veridian Prospecting": ["Global Command"] # <--- NEW ENTITY
    }
    
    selected_company = st.sidebar.selectbox("Select Entity", company_map.get(selected_industry, []))
    
    # ROUTING
    if selected_industry == "Industrial": render_sturrock_dashboard()
    elif selected_industry == "Agriculture": render_bonnyvale_dashboard()
    elif selected_industry == "Logistics": render_tte_dashboard()
    elif selected_industry == "Veridian Prospecting": render_prospecting_dashboard() # <--- THE FIX
    else: st.warning("Module not loaded.")

st.sidebar.divider()
if st.sidebar.button("Log Out"): vk.logout()
