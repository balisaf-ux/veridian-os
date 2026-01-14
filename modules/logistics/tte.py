import streamlit as st
import vas_kernel as vk

# 1. CORRECT DATA IMPORT (THE FIX)
# We import the local initializer instead of calling the missing kernel function.
from modules.logistics.models import init_logistics_db 

# 2. COMPONENT IMPORTS
from modules.logistics.ops import render_ops_tab
from modules.logistics.finance import render_finance_portal
from modules.logistics.risk import render_risk_tabs
from modules.logistics.customer_portal import render_customer_portal
from modules.logistics.dealstream import render_dealstream_marketplace

def render_tte_dashboard():
    # ==========================================
    # 3. INITIALIZATION PROTOCOL (PATCHED)
    # ==========================================
    vk.boot_system()       # Initialize Global OS (Finance/Auth)
    init_logistics_db()    # Initialize Local Vertical (Fleet/Loads)
    
    # Note: removed vk.init_bonnyvale_data() as it is legacy Agri logic not required here.

    # 4. SESSION SAFETY
    if 'tte_step' not in st.session_state: st.session_state.tte_step = 1
    if 'tte_credit_status' not in st.session_state: st.session_state.tte_credit_status = "Pending"
    if 'demo_fill' not in st.session_state: st.session_state.demo_fill = False

    # 5. HEADER
    st.markdown("## 🚛 Veridian Logistics Cloud | TTE")
    st.caption("Operational & Financial Command (Architecture: V7.9 Live)")
    
    # KPI ROW (Live Financials)
    rev_mtd = 0
    if 'general_ledger' in st.session_state:
        gl = st.session_state.general_ledger
        # Defensive check for legacy schema compatibility
        if not gl.empty and 'Code' in gl.columns:
            # Sum Revenue (Codes starting with 4)
            rev_mtd = gl[gl['Code'].astype(str).str.startswith('4')]['Amount'].sum()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Utilization", "82%")
    k2.metric("Active Loads", "4")
    k3.metric("Revenue (MTD)", f"R {rev_mtd:,.0f}")
    k4.metric("Fuel Efficiency", "38L/100km")
    
    st.divider()

    # 6. THE MODULAR TABS
    t_rev, t_ops, t_fin, t_risk, t_portal = st.tabs([
        "💰 DealStream", 
        "🌍 Fleet Command", 
        "🏦 Finance Portal",
        "🛡️ Risk & Fuel",
        "🤖 Customer Portal"
    ])

    with t_rev:
        render_dealstream_marketplace()

    with t_ops:
        render_ops_tab()

    with t_fin:
        render_finance_portal()

    with t_risk:
        render_risk_tabs()

    with t_portal:
        render_customer_portal()
