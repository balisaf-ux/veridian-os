import streamlit as st
import pandas as pd
import vas_kernel as vk
import time

def render_admin_core():
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
        st.success("🟢 Veridian Group (HQ): ONLINE")
        st.success("🟢 Bonnyvale (Agri): ONLINE")
        st.error("🔴 Sturrock & Robson: ALERT (Filter Pressure)")

    st.markdown("---")
    st.subheader("DealStream & Hunter")
    st.info("ℹ️ CRM and Prospecting modules are active. Access via 'Admin Core' context menu if needed.")
