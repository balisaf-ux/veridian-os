import streamlit as st
import numpy as np
import time
from datetime import datetime

# --- 1. ROBUST IMPORTS ---
try:
    from .db_utils import run_query
except ImportError:
    try:
        from ..db_utils import run_query
    except ImportError:
        from modules.logistics.db_utils import run_query


def render_customer_wizard():
    st.markdown("### 🤖 Client Booking Portal")
    st.caption("External Facing Interface (Live RFQ Intake)")

    # -----------------------------
    # SESSION STATE INITIALIZATION
    # -----------------------------
    defaults = {
        "portal_step": 1,
        "portal_credit": "Pending",
        "portal_quote": 0.0,
        "portal_payload": {},
        "portal_client": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # -----------------------------
    # PROGRESS BAR
    # -----------------------------
    st.progress(
        st.session_state.portal_step / 4,
        text=f"Step {st.session_state.portal_step} of 4"
    )

    # =========================================================
    # STEP 1: CLIENT REGISTRATION
    # =========================================================
    if st.session_state.portal_step == 1:
        st.subheader("1. Client Registration")

        with st.form("portal_reg"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Entity Name", value="Vukanathi Logistics")
            reg = c2.text_input("Reg Number", value="2024/0056/07")
            sector = c1.selectbox("Sector", ["Mining", "FMCG", "Construction", "Agriculture", "Energy"])
            c_terms = c2.checkbox("Apply for 30-Day Terms?")

            if st.form_submit_button("Run Credit Check"):
                st.session_state.portal_credit = (
                    "APPROVED (30 Days)" if c_terms else "CASH (COD)"
                )
                st.session_state.portal_client = {
                    "name": name,
                    "reg": reg,
                    "sector": sector,
                    "terms": st.session_state.portal_credit,
                }

                st.toast(f"Credit Status: {st.session_state.portal_credit}")
                time.sleep(0.4)
                st.session_state.portal_step = 2
                st.rerun()

    # =========================================================
    # STEP 2: LOAD SPECIFICATIONS
    # =========================================================
    elif st.session_state.portal_step == 2:
        st.subheader("2. Load Specifications")
        st.info(f"Terms: {st.session_state.portal_credit}")

        with st.form("portal_load"):
            c1, c2 = st.columns(2)
            origin = c1.selectbox("Origin", ["JHB City Deep", "Durban Port", "Richards Bay"])
            dest = c2.selectbox("Destination", ["Cape Town", "Polokwane", "Gqeberha"])
            cargo = c1.text_input("Cargo Description", "Steel Coils")
            wgt = c2.number_input("Weight (Tons)", min_value=5, max_value=34, value=28)

            if st.form_submit_button("Get Quote"):
                # Pricing model
                base_rate = 14_500
                per_ton = 320
                distance_factor = 1.15 if origin != dest else 1.0

                quote = (base_rate + (wgt * per_ton)) * distance_factor

                st.session_state.portal_quote = round(quote, 2)
                st.session_state.portal_payload = {
                    "origin": origin,
                    "destination": dest,
                    "cargo": cargo,
                    "weight": wgt,
                }
                st.session_state.portal_step = 3
                st.rerun()

    # =========================================================
    # STEP 3: COMMERCIAL ACCEPTANCE
    # =========================================================
    elif st.session_state.portal_step == 3:

        # --- SAFETY GUARD ---
        if not st.session_state.portal_payload or not st.session_state.portal_client:
            st.warning("Session expired. Restarting booking.")
            st.session_state.portal_step = 1
            st.rerun()

        st.subheader("3. Commercial Terms")

        st.metric("Total Quote", f"R {st.session_state.portal_quote:,.2f}")
        st.caption(
            f"Route: {st.session_state.portal_payload.get('origin')} → "
            f"{st.session_state.portal_payload.get('destination')} | "
            f"{st.session_state.portal_payload.get('weight')} tons"
        )

        c1, c2 = st.columns(2)

        if c1.button("❌ Reject Quote"):
            st.session_state.portal_step = 2
            st.rerun()

        if c2.button("✅ Accept & Book"):
            client = st.session_state.portal_client
            load = st.session_state.portal_payload

            # CREATE RFQ
            run_query(
                """
                INSERT INTO ind_rfqs 
                    (client, origin, destination, tons, commodity, status, created_at)
                VALUES 
                    (:client, :origin, :dest, :tons, :comm, 'Pending', :ts)
                """,
                {
                    "client": client["name"],
                    "origin": load["origin"],
                    "dest": load["destination"],
                    "tons": load["weight"],
                    "comm": load["cargo"],
                    "ts": datetime.now().isoformat(),
                },
            )

            st.toast("RFQ created and queued for Dispatch.")
            st.session_state.portal_step = 4
            st.rerun()

    # =========================================================
    # STEP 4: SUCCESS
    # =========================================================
    elif st.session_state.portal_step == 4:
        st.balloons()
        st.success("Booking Confirmed! Dispatch Team Notified.")

        st.write("### 📦 Booking Summary")
        st.json({
            "Client": st.session_state.portal_client,
            "Load": st.session_state.portal_payload,
            "Quote": st.session_state.portal_quote,
            "Terms": st.session_state.portal_credit,
        })

        if st.button("New Booking"):
            st.session_state.portal_step = 1
            st.session_state.portal_credit = "Pending"
            st.session_state.portal_quote = 0.0
            st.session_state.portal_payload = {}
            st.session_state.portal_client = {}
            st.rerun()
