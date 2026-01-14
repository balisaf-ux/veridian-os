import streamlit as st
import pandas as pd

# --- UNIFIED DB LAYER ---
from modules.logistics.db_utils import init_db, load_data, run_query

# --- MODULAR IMPORTS ---
from modules.logistics.constants import DIESEL_PRICE, CORRIDORS
from modules.logistics.services import calculate_route_economics
from modules.logistics.models import inject_sovereign_data
from modules.logistics.rules import enrich_fleet_data
from modules.logistics.gps_engine import run_gps_simulation
from modules.logistics.views.gps_console import render_gps_console


# --- VIEW IMPORTS ---
from modules.logistics.views.dispatch import render_dispatch_console
from modules.logistics.dealstream import render_dealstream_marketplace
from modules.logistics.views.risk_compliance import render_risk_view
from modules.logistics.views.customer_portal import render_customer_wizard
from modules.logistics.views.finance_dashboard import render_finance_view
from modules.logistics.views.driver_ops import render_driver_portal
from modules.logistics.views.fleet import render_fleet_registry


def render_logistics_vertical():

    st.markdown("## 🚛 Logistics Cloud | Sovereign Command")
    st.caption("v16.3 Modular Architecture (All Systems Active)")

    # Initialise DB once
    init_db()

    # TEMPORARY: Create RFQ table if missing
    if st.button("Create RFQ Table"):
        run_query(
            """
            CREATE TABLE IF NOT EXISTS ind_rfqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT,
                origin TEXT,
                destination TEXT,
                tons REAL,
                commodity TEXT,
                status TEXT,
                created_at TEXT
            );
            """
        )
        st.success("RFQ table created.")

    # Load Data Context
    df_fleet_raw = load_data("SELECT * FROM log_vehicles")
    df_fleet = enrich_fleet_data(df_fleet_raw.copy())

    df_orders = load_data("SELECT * FROM ind_rfqs WHERE status='Pending'")

    # Dashboard Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Fleet", f"{len(df_fleet)}", "Assets")
    c2.metric("Pending Orders", f"{len(df_orders)}", "Backlog")
    c3.metric("Diesel Index", f"R {DIESEL_PRICE}", "50ppm")
    c4.metric("Risk Shield", "ACTIVE", "Physics-Link")

    st.divider()

    # MASTER TABS
    tabs = st.tabs([
        "📢 Market",
        "🗺️ Route Planner",
        "⚡ Dispatch",
        "🚛 Fleet Registry",
        "📱 Driver",
        "🏦 Finance",
        "🛡️ Risk & Fuel",
        "🤖 Portal",
        "📡 GPS Engine"
    ])

    # MARKET
    with tabs[0]:
        render_dealstream_marketplace()

    # ROUTE PLANNER
    with tabs[1]:
        st.subheader("Algorithmic Quoting Engine")

        c1, c2 = st.columns([1, 2])

        with c1:
            route = st.selectbox("Select Corridor", list(CORRIDORS.keys()))
            trucks = df_fleet["reg_number"].tolist() if not df_fleet.empty else ["Generic"]
            truck_str = st.selectbox("Assign Asset", trucks)

            # Default efficiency – DB no longer stores fuel_rating
            eff = 38.0
            st.info(f"Efficiency: **{eff} L/100km**")

        with c2:
            eco = calculate_route_economics(route, eff)
            st.metric("Break-Even Cost", f"R {eco['total_ops_cost']:,.2f}")
            st.caption(f"Fuel: R {eco['fuel_cost']:,.0f} | Tolls: R {eco['toll_cost']:,.0f}")

    # DISPATCH
    with tabs[2]:
        try:
            render_dispatch_console(df_orders, df_fleet)
        except Exception as e:
            st.error(f"Dispatch Module Syncing: {e}")

    # FLEET
    with tabs[3]:
        render_fleet_registry(df_fleet)

    # DRIVER
    with tabs[4]:
        render_driver_portal(df_fleet)

    # FINANCE
    with tabs[5]:
        render_finance_view()

    # RISK & FUEL
    with tabs[6]:
        render_risk_view()

    # PORTAL
    with tabs[7]:
        render_customer_wizard()
        
    # GPS
    with tabs[8]:
        render_gps_console()

if __name__ == "__main__":
    render_logistics_vertical()

