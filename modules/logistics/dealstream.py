# modules/logistics/dealstream.py

import datetime
import streamlit as st
import pandas as pd

from modules.logistics.db_utils import run_query


def render_dealstream_marketplace():
    st.markdown("### ⚡ DealStream: Live Freight Marketplace")
    st.caption("The Handshake Protocol: Trade (Demand) ↔ Logistics (Supply)")

    # =========================================================
    # 1. MOCK DATA (Market-side, not yet bound to RFQs)
    # =========================================================
    active_loads = [
        {
            "id": "LD-101",
            "route": "JHB → DBN (N3)",
            "origin": "JHB City Deep",
            "destination": "Durban Port",
            "cargo": "Industrial Valves",
            "weight_kg": 450,
            "rate": 3_500,
            "status": "OPEN",
            "safety": "🟢 HIGH",
        },
        {
            "id": "LD-102",
            "route": "MPU → RBAY (R33)",
            "origin": "Ermelo (Mpumalanga)",
            "destination": "Richards Bay",
            "cargo": "Coal (Bulk)",
            "weight_kg": 34_000,
            "rate": 18_500,
            "status": "OPEN",
            "safety": "🔴 LOW (Potholes)",
        },
        {
            "id": "LD-103",
            "route": "CPT → JHB (N1)",
            "origin": "Cape Town",
            "destination": "JHB City Deep",
            "cargo": "Solar Inverters",
            "weight_kg": 1_200,
            "rate": 9_200,
            "status": "OPEN",
            "safety": "🟡 MED (Traffic)",
        },
    ]

    # =========================================================
    # 2. MARKET METRICS
    # =========================================================
    market_vol = sum(item["rate"] for item in active_loads)
    avg_rate = market_vol / len(active_loads) if active_loads else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Open Loads", len(active_loads), "+2 New")
    col2.metric("Market Volume", f"R {market_vol:,.0f}", f"Avg: R {avg_rate:,.0f}")
    col3.metric("Safety Index", "N3: Good", "R33: Critical")

    st.markdown("---")

    # =========================================================
    # 3. LOAD BOARD → RFQ HANDSHAKE
    # =========================================================
    for load in active_loads:
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

            # -------------------------
            # LEFT: ROUTE & CARGO
            # -------------------------
            with c1:
                st.subheader(f"📍 {load['route']}")
                st.caption(f"Ref: {load['id']} | Cargo: {load['cargo']}")

            # -------------------------
            # MIDDLE: WEIGHT & SAFETY
            # -------------------------
            with c2:
                st.markdown(f"**Weight:** {load['weight_kg']} kg")

                if "🔴" in load["safety"]:
                    st.error(f"🛣️ {load['safety']}")
                elif "🟢" in load["safety"]:
                    st.success(f"🛣️ {load['safety']}")
                else:
                    st.warning(f"🛣️ {load['safety']}")

            # -------------------------
            # RATE
            # -------------------------
            with c3:
                st.markdown(f"### R {load['rate']:,}")
                st.caption("Target Rate")

            # -------------------------
            # ACTION: BOOK → Creates RFQ
            # -------------------------
            with c4:
                if st.button("⚡ BOOK", key=load["id"], use_container_width=True):
                    # Convert market load → RFQ in ind_rfqs
                    rfq_id = f"RFQ-{int(datetime.datetime.now().timestamp())}"

                    run_query(
                        """
                        INSERT INTO ind_rfqs (rfq_id, client, product, volume, route, status)
                        VALUES (:id, :client, :prod, :vol, :route, 'Pending')
                        """,
                        {
                            "id": rfq_id,
                            "client": "Market Client",          # Placeholder — can be extended
                            "prod": load["cargo"],
                            "vol": load["weight_kg"] / 1000.0,  # tons
                            "route": load["route"],
                        },
                    )

                    st.success(f"✅ Load {load['id']} converted to RFQ {rfq_id}.")
                    st.toast(f"Handshake Complete: {load['id']} → {rfq_id}")
