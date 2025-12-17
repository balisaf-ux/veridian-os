import streamlit as st
import vas_kernel as vk

# NEW MODULAR IMPORTS
import vas_admin as v_admin
import vas_industry as v_ind
import vas_logistics as v_log

vk.set_design_system()

if not vk.check_login():
    st.stop()

with st.sidebar:
    st.title("VAS | OS")
    st.caption("Veridian Master Operating System")
    
    if st.session_state.user_role == "ADMIN":
        st.markdown("Identity: **STRATEGIST**")
        st.header("Admin Core")
        menu = st.radio("Module", ["Central Command", "DealStream", "Hunter"])
        st.divider()
        st.header("Industry Clouds")
        # Updated Title for S&R
        industry_sim = st.selectbox("Vertical", ["Select...", "Industrial (Sturrock & Robson)", "Agri (Bonnyvale)", "Logistics (TTE)", "TTE Portal"])
        
    else:
        st.markdown("Identity: **CLIENT**")
        st.header("Operational Units")
        menu = st.radio("View", ["Group Cockpit", "Industrial", "Agri", "Logistics"])
    
    st.divider()
    if st.button("Log Out"): vk.logout()

# ROUTING LOGIC
if st.session_state.user_role == "ADMIN":
    if industry_sim == "Select...":
        if menu == "Central Command": v_admin.render_admin_home()
        elif menu == "DealStream": v_admin.render_crm_module()
        elif menu == "Hunter": v_admin.render_hunter_module()
    
    # UPDATED ROUTING TO NEW S&R MODULE
    elif industry_sim == "Industrial (Sturrock & Robson)": 
        v_ind.render_sturrock_robson_module()
        
    elif industry_sim == "Agri (Bonnyvale)": 
        v_ind.render_bonnyvale_module()
        
    elif industry_sim == "Logistics (TTE)": 
        v_log.render_logistics_cloud()
        
    elif industry_sim == "TTE Portal": 
        v_log.render_tte_portal()

elif st.session_state.user_role == "CLIENT":
    if menu == "Group Cockpit": v_admin.render_admin_home()
    elif menu == "Industrial": v_ind.render_sturrock_robson_module() # UPDATED
    elif menu == "Agri": v_ind.render_bonnyvale_module()
    elif menu == "Logistics": v_log.render_logistics_cloud()
