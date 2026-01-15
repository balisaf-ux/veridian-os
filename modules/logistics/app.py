import streamlit as st
import pandas as pd

# =========================================================
# 1. UNIFIED DB LAYER
# =========================================================
try:
    from modules.logistics.db_utils import init_db, load_data, run_query
except ImportError:
    # Fallback to prevent crash if DB utils aren't set up yet
    def init_db(): 
        pass
    def load_data(q): 
        return pd.DataFrame()
    def run_query(q): 
        pass

# =========================================================
# 2. CORE LOGISTICS CONSTANTS & SERVICES
# =========================================================
try:
    from modules.logistics.constants import DIESEL_PRICE, CORRIDORS
    from modules.logistics.services import calculate_route_economics
    from modules.logistics.rules import enrich_fleet_data
except ImportError:
    # Defaults for "Safe Mode"
    DIESEL_PRICE = 24.50
    CORRIDORS = {"Durban-JHB": 600}
    def calculate_route_economics(r, e): 
        return {"total_ops_cost": 0, "fuel_cost": 0, "toll_cost": 0}
    def enrich_fleet_data(df): 
        return df

# =========================================================
# 3. VIEW IMPORTS (Gracefully degrade if missing)
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
except ImportError as e:
    print(f"⚠️ View Import Warning: {e}")


# =========================================================
# 4. LOGISTICS VERTICAL (MAIN ENTRY POINT)
# =========================================================
def render_logistics_vertical():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------
    st.markdown("<h1 style='color:#D4AF37;'>🚛 Logistics Cloud</h1>", unsafe_allow_html=True)
    st.caption("v16.3 Modular Architecture (All Systems Active)")

    # -----------------------------------------------------
    # INITIALISE DATABASE
    # -----------------------------------------------------
    init_db()

    # -----------------------------------------------------
    # OPTIONAL ADMIN TOOLS (SOVEREIGN / INTERNAL ONLY)
    # -----------------------------------------------------
    # We safely check session state to hide this from external guests if needed
    user = st.session_state.get("user_session", {})
    role = user.get("role", "Unknown")

    if role != "External_Auditor":
        with st.expander("⚙️ Admin Database Tools"):
            if st.button("Initialize RFQ Table"):
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
                st.success("RFQ table verified.")

    # -----------------------------------------------------
    # LOAD DATA CONTEXT (SAFE FALLBACKS)
    # -----------------------------------------------------
    try:
        df_fleet_raw = load_data("SELECT * FROM log_vehicles")
        df_fleet = (
            enrich_fleet_data(df_fleet_raw.copy())
            if df_fleet_raw is not None and not df_fleet_raw.empty
            else pd.DataFrame()
        )
    except Exception:
        df_fleet = pd.DataFrame()

    try:
        df_orders = load_data("SELECT * FROM ind_rfqs WHERE status='Pending'")
        df_orders = df_orders if df_orders is not None else pd.DataFrame()
    except Exception:
        df_orders = pd.DataFrame()

    # -----------------------------------------------------
    # TOP-LEVEL METRICS
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
            if CORRIDORS:
                route = st.selectbox("Select Corridor", list(CORRIDORS.keys()))
            else:
                route = st.selectbox("Select Corridor", ["Generic Route"])

            if not df_fleet.empty and "reg_number" in df_fleet.columns:
                trucks = df_fleet["reg_number"].tolist()
            else:
                trucks = ["Generic Asset"]

            truck_str = st.selectbox("Assign Asset", trucks)

            eff = 38.0  # Default efficiency
            st.info(f"Efficiency: **{eff} L/100km**")

        with c2:
            eco = calculate_route_economics(route, eff)
            st.metric("Break-Even Cost", f"R {eco['total_ops_cost']:,.2f}")
            st.caption(f"Fuel: R {eco['fuel_cost']:,.0f} | Tolls: R {eco['toll_cost']:,.0f}")

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

