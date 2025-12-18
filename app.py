import streamlit as st
import vas_kernel as vk

# IMPORTS
from vas_admin import render_admin_core
from vas_prospecting import render_prospecting_dashboard  # <--- NEW IMPORT FROM ROOT
from modules.industrial.sturrock import render_sturrock_dashboard
from modules.agriculture.bonnyvale import render_bonnyvale_dashboard
from modules.logistics.tte import render_tte_dashboard

st.set_page_config(page_title="Veridian | Group OS", layout="wide", page_icon="🦅")
vk.set_design_system()

if not vk.check_login(): st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("VAS | OS")
st.sidebar.caption("Sovereign Operating System v7.6")

# THE NEW TOP-LEVEL HIERARCHY
view_mode = st.sidebar.radio(
    "Clearance Level", 
    [
        "Admin Core",            # 1. The Backend
        "Veridian Prospecting",  # 2. The New Block (Moved Here)
        "Industry Clouds"        # 3. The Client Frontends
    ]
)

# --- ROUTING LOGIC ---

if view_mode == "Admin Core":
    render_admin_core()

elif view_mode == "Veridian Prospecting":
    render_prospecting_dashboard()  # <--- DIRECT ACCESS

elif view_mode == "Industry Clouds":
    st.sidebar.divider()
    
    # Standard Vertical Logic
    vertical = st.sidebar.selectbox("Select Vertical", ["Industrial", "Agriculture", "Logistics"])
    
    if vertical == "Industrial":
        render_sturrock_dashboard()
    elif vertical == "Agriculture":
        render_bonnyvale_dashboard()
    elif vertical == "Logistics":
        render_tte_dashboard()

st.sidebar.divider()
if st.sidebar.button("Log Out"): vk.logout()
