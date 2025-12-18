import streamlit as st
import pandas as pd
import vas_kernel as vk

def render_bonnyvale_dashboard():
    vk.init_bonnyvale_data()
    st.markdown("## 🍍 Veridian Agri Cloud | Bonnyvale Estates")
    st.caption("Region: East London (Sunshine Coast) • Crop: **Pineapple (Cayenne/Queen)**")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Season Yield Target", "18,500 Tons", "Forecast")
    k2.metric("Harvest Progress", "12.4%", "+2% vs Schedule")
    k3.metric("Avg Brix (Sugar)", "14.6°", "Premium")
    k4.metric("Active Fleet", "3/4 Trucks", "Logistics Active")

    st.divider()
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        st.map(st.session_state.agri_harvest, latitude='lat', longitude='lon', zoom=13, use_container_width=True)
    with c2:
        st.markdown("**Block Readiness Index**")
        for index, row in st.session_state.agri_harvest.iterrows():
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
        st.info("ℹ️ **Co-op Alert:** Summerpride facility high traffic.")
        st.success("✅ **Optimization:** Back-haul opportunity identified.")
