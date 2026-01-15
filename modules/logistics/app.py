# modules/logistics/app.py

import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# OPTIONAL: One-time schema repair (commented out)
# ---------------------------------------------------------
from modules.logistics.db_utils import reset_fleet_table

# Uncomment this ONCE if your fleet table schema is broken:
# reset_fleet_table()

# Boot beacon (diagnostic)
st.write("🚦 Logistics Vertical Booted")


# =========================================================
# 1. UNIFIED LOGISTICS DB LAYER (SOVEREIGN)
# =========================================================
from modules.logistics.db_utils import (
    init_db,
    load_data,
    run_query,
)

try:
    from modules.logistics.db_utils import SCHEMA_VERSION
except ImportError:
    SCHEMA_VERSION = 17


# =========================================================
# 2. CORE LOGISTICS CONSTANTS & SERVICES
# =========================================================
try:
    from modules.logistics.constants import DIESEL_PRICE, CORRIDORS
    from modules.logistics.services import calculate_route_economics
    from modules.logistics.rules import enrich_fleet_data
except Exception:
    DIESEL_PRICE = 24.50
    CORRIDORS = {}

    def calculate_route_economics(r, e):
        return {"total_ops_cost": 0, "fuel_cost": 0, "toll_cost": 0}

    def enrich_fleet_data(df):
        return df


# =========================================================
# 3. VIEW IMPORTS (Graceful)
# =========================================================
try:
    from modules.logistics.views.gps_console import render_gps_console
    from modules.logistics.views.dispatch import render_dispatch_console
    from modules.logistics.dealstream import render_dealstream_marketplace
    from modules.logistics.views.risk_compliance import render_risk_view
    from modules.logistics.views.customer_portal import render_customer_wizard
    from modules.logistics.views.finance_dashboard import render_finance_view
    from modules.logistics.views.driver_ops import render_driver_portal
    from modules.logistics.views.fleet import render_fleet_registry
except Exception:
    pass


# =========================================================
# 4. LOGISTICS VERTICAL (MAIN ENTRY POINT)
# =========================================================
def render_logistics_vertical():

    # -----------------------------------------------------
    # HEADER — UPDATED PALETTE (BLUE)
    # -----------------------------------------------------
    st.markdown("<h1 style='color:#0033A0;'>🚛 Logistics Cloud</h1>", unsafe_allow_html=True)
    st.caption(f"MAIS Vertical • Sovereign Logistics Stack v{SCHEMA_VERSION}")

    # -----------------------------------------------------
    # INITIALISE DATABASE (SOVEREIGN)
    # -----------------------------------------------------
    init_db()

    # -----------------------------------------------------
    # USER CONTEXT
    # -----------------------------------------------------
    user = st.session_state.get("user_session", {})
    role = user.get("role", "Unknown")

    # -----------------------------------------------------
    # OPTIONAL ADMIN TOOLS (SOVEREIGN ONLY)
    # -----------------------------------------------------
    if role not in ["External_Auditor"]:
        with st.expander("⚙️ Sovereign Database Tools"):
            st.info("These tools operate on the sovereign logistics DB (fleet_data.db).")

            if st.button("Show DB Health"):
                try:
                    from modules.logistics.db_utils import db_health
                    st.json(db_health())
                except Exception as e:
                    st.error(f"DB Health Error: {e}")

            if st.button("Verify RFQ Table"):
                try:
                    run_query("""
                        CREATE TABLE IF NOT EXISTS ind_rfqs (
                            rfq_id TEXT PRIMARY KEY,
                            client TEXT,
                            origin TEXT,
                            destination TEXT,
                            tons REAL,
                            commodity TEXT,
                            status TEXT,
                            created_at DATETIME
                        );
                    """)
                    st.success("RFQ table verified and aligned with sovereign schema.")
                except Exception as e:
                    st.error(f"RFQ Verification Error: {e}")

    # -----------------------------------------------------
    # LOAD DATA CONTEXT
    # -----------------------------------------------------
    try:
        df_fleet_raw = load_data("SELECT * FROM log_vehicles")
        df_fleet = (
            enrich_fleet_data(df_fleet_raw.copy())
            if df_fleet_raw is not None and not df_fleet_raw.empty
            else pd.DataFrame()
        )
    except Exception as e:
        st.error(f"Fleet Load Error: {e}")
        df_fleet = pd.DataFrame()

    try:
        df_orders = load_data("SELECT * FROM ind_rfqs WHERE status='Pending'")
        df_orders = df_orders if df_orders is not None else pd.DataFrame()
    except Exception as e:
        st.error(f"Order Load Error: {e}")
        df_orders = pd.DataFrame()

    # -----------------------------------------------------
    # TOP-LEVEL METRICS — PALETTE SAFE
    # -----------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Assets", f"{len(df_fleet)}", "Operational")
    c2.metric("Backlog", f"{len(df_orders)}", "Pending")
    c3.metric("Diesel Index", f"R {DIESEL_PRICE}", "50ppm")
    c4.metric("Risk Shield", "ACTIVE", "Physics-Link")

    st.markdown("---")

    # -----------------------------------------------------
    # MASTER TABS
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # MARKET
    # -----------------------------------------------------
    with tabs[0]:
        try:
            render_dealstream_marketplace()
        except Exception as e:
            st.error(f"Marketplace Error: {e}")

    # -----------------------------------------------------
    # ROUTE PLANNER
    # -----------------------------------------------------
    with tabs[1]:
        st.subheader("Algorithmic Quoting Engine")

        c1, c2 = st.columns([1, 2])

        with c1:
            route = st.selectbox("Select Corridor", list(CORRIDORS.keys()) or ["Generic Route"])

            trucks = (
                df_fleet["reg_number"].tolist()
                if not df_fleet.empty and "reg_number" in df_fleet.columns
                else ["Generic Asset"]
            )

            truck_str = st.selectbox("Assign Asset", trucks)

            eff = 38.0
            st.info(f"Efficiency: **{eff} L/100km**")

        with c2:
            try:
                eco = calculate_route_economics(route, eff)
                st.metric("Break-Even Cost", f"R {eco['total_ops_cost']:,.2f}")
                st.caption(f"Fuel: R {eco['fuel_cost']:,.0f} | Tolls: R {eco['toll_cost']:,.0f}")
            except Exception as e:
                st.error(f"Economics Error: {e}")

    # -----------------------------------------------------
    # DISPATCH
    # -----------------------------------------------------
    with tabs[2]:
        try:
            render_dispatch_console(df_orders, df_fleet)
        except Exception as e:
            st.error(f"Dispatch Module Error: {e}")

    # -----------------------------------------------------
    # FLEET REGISTRY
    # -----------------------------------------------------
    with tabs[3]:
        try:
            render_fleet_registry(df_fleet)
        except Exception as e:
            st.error(f"Fleet Registry Error: {e}")

    # -----------------------------------------------------
    # DRIVER OPS
    # -----------------------------------------------------
    with tabs[4]:
        try:
            render_driver_portal(df_fleet)
        except Exception as e:
            st.error(f"Driver Portal Error: {e}")

    # -----------------------------------------------------
    # FINANCE
    # -----------------------------------------------------
    with tabs[5]:
        try:
            render_finance_view()
        except Exception as e:
            st.error(f"Finance Dashboard Error: {e}")

    # -----------------------------------------------------
    # RISK & FUEL
    # -----------------------------------------------------
    with tabs[6]:
        try:
            render_risk_view()
        except Exception as e:
            st.error(f"Risk & Fuel Error: {e}")

    # -----------------------------------------------------
    # CUSTOMER PORTAL
    # -----------------------------------------------------
    with tabs[7]:
        try:
            render_customer_wizard()
        except Exception as e:
            st.error(f"Customer Portal Error: {e}")

    # -----------------------------------------------------
    # GPS ENGINE
    # -----------------------------------------------------
    with tabs[8]:
        try:
            render_gps_console()
        except Exception as e:
            st.error(f"GPS Engine Error: {e}")


# =========================================================
# 5. DIRECT EXECUTION (DEV MODE)
# =========================================================
if __name__ == "__main__":
    render_logistics_vertical()

