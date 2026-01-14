import streamlit as st
import numpy as np
import time

def render_customer_portal():
    st.markdown("#### 🤖 Customer Portal | Booking Engine")
    st.caption("External Client Interface (Quotes & Onboarding)")
    
    # Progress Bar
    st.progress(st.session_state.tte_step / 4, text=f"Step {st.session_state.tte_step} of 4")
    
    # STEP 1: REGISTRATION
    if st.session_state.tte_step == 1:
        if st.button("⚡ DEMO: Auto-Fill Form", type="primary"):
            st.session_state.demo_fill = True
            st.rerun()

        st.subheader("1. Client Registration & Credit Check")
        
        val_name = "Vukanathi Logistics" if st.session_state.demo_fill else ""
        val_reg = "2024/0056/07" if st.session_state.demo_fill else ""
        val_vat = "4900123456" if st.session_state.demo_fill else ""
        
        with st.form("client_reg"):
            c1, c2 = st.columns(2)
            c_name = c1.text_input("Company Name", value=val_name)
            c_reg = c2.text_input("Registration Number", value=val_reg)
            c_type = c1.selectbox("Client Sector", ["Government", "Corporate (Listed)", "Private/SME"])
            c_vat = c2.text_input("VAT Number", value=val_vat)
            
            st.markdown("---")
            c_terms = st.checkbox("Apply for 30-Day Payment Terms?", value=True if st.session_state.demo_fill else False)
            
            if st.form_submit_button("Submit Application"):
                if c_type in ["Government", "Corporate (Listed)"]:
                    st.session_state.tte_credit_status = "APPROVED (30 Days)"
                    st.success("✅ Credit Approved! Terms: 30 Days Net.")
                elif c_terms:
                    st.session_state.tte_credit_status = "REJECTED (Risk Profile)"
                    st.warning("⚠️ Credit Criteria Not Met. Defaulting to CASH terms.")
                else:
                    st.session_state.tte_credit_status = "CASH (Standard)"
                    st.info("ℹ️ Account set to Cash on Delivery.")
                
                time.sleep(0.5); st.session_state.tte_step = 2; st.rerun()

    # STEP 2: LOAD DETAILS
    elif st.session_state.tte_step == 2:
        st.subheader("2. Load Logistics & Quoting")
        st.caption(f"Account Terms: **{st.session_state.tte_credit_status}**")
        val_cargo = "Steel Coils (Grade A)" if st.session_state.demo_fill else ""
        
        with st.form("load_details"):
            l1, l2 = st.columns(2)
            origin = l1.selectbox("Origin", ["Johannesburg", "Durban", "Cape Town", "Polokwane"])
            dest = l2.selectbox("Destination", ["Durban", "Cape Town", "East London", "Nelspruit"])
            cargo = l1.text_input("Product Description", value=val_cargo)
            weight = l2.number_input("Load Weight (Tons)", 1, 34, 30)
            
            est_price = 15000 + ((weight - 10) * 500) if weight > 10 else 15000
            
            if st.form_submit_button("Generate Quote ➝"):
                st.session_state.tte_quote = est_price
                st.session_state.tte_details = {'Org': origin, 'Dst': dest, 'Wgt': weight, 'Crg': cargo}
                st.session_state.tte_step = 3; st.rerun()

    # STEP 3: ACCEPTANCE
    elif st.session_state.tte_step == 3:
        st.subheader("3. Quote Acceptance")
        
        st.markdown(f"""
        <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 20px;">
            <h3 style="margin-top:0;">QUOTE: TTE-{np.random.randint(1000,9999)}</h3>
            <p><strong>Route:</strong> {st.session_state.tte_details['Org']} ➝ {st.session_state.tte_details['Dst']}</p>
            <p><strong>Cargo:</strong> {st.session_state.tte_details['Crg']} ({st.session_state.tte_details['Wgt']} Tons)</p>
            <hr>
            <h2 style="color: #0056b3;">TOTAL: R {st.session_state.tte_quote:,.2f}</h2>
            <p style="font-size: 0.8rem;">Terms: {st.session_state.tte_credit_status}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("❌ Reject Quote"): st.session_state.tte_step = 2; st.rerun()
        if c2.button("✅ ACCEPT & TRADE"): st.session_state.tte_step = 4; st.rerun()

    # STEP 4: INVOICE
    elif st.session_state.tte_step == 4:
        st.balloons()
        st.success("TTE Ops Team Notified! Truck Dispatch Initiated.")
        st.markdown("### 📄 PRO-FORMA INVOICE GENERATED")
        st.info(f"Invoice #INV-2025-{np.random.randint(100,999)} has been emailed.")
        if st.button("Start New Booking"):
            st.session_state.tte_step = 1; st.session_state.demo_fill = False; st.rerun()
