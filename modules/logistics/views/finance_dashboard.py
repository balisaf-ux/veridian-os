# modules/logistics/views/finance_dashboard.py

import streamlit as st
import pandas as pd
import datetime

from modules.logistics.db_utils import load_data
from modules.logistics.constants import CORRIDORS, DIESEL_PRICE

# --- FINANCE CORE INTEGRATION ---
try:
    from modules.finance.services import create_journal_entry
except ImportError:
    # Fallback if Finance Core is offline
    def create_journal_entry(*args, **kwargs):
        return False, "Finance Core Offline"


# =========================================================
# FINANCE INTELLIGENCE ENGINES (LOCAL HELPERS)
# =========================================================

def _compute_cpk():
    """
    Computes CPK (Cost Per Kilometer) using:
    - Dispatch journal (actual trips)
    - Corridor metadata (distance, tolls)
    - Diesel price (global constant)
    """
    df = load_data("SELECT * FROM log_dispatch_journal")

    if df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in df.iterrows():
        route = row.get("rfq_ref", "")
        if route not in CORRIDORS:
            continue

        meta = CORRIDORS[route]
        dist = meta["dist"]
        tolls = meta["tolls"]

        # Fuel consumption estimate (L/100km)
        eff = 38.0
        liters = (dist / 100) * eff
        fuel_cost = liters * DIESEL_PRICE

        total_cost = fuel_cost + tolls
        cpk = total_cost / dist if dist > 0 else 0

        rows.append({
            "trip_id": row.get("trip_id"),
            "route": route,
            "distance_km": dist,
            "fuel_cost": fuel_cost,
            "toll_cost": tolls,
            "total_cost": total_cost,
            "cpk": cpk,
        })

    return pd.DataFrame(rows)


def _compute_fuel_variance(gl_df: pd.DataFrame):
    """
    Compares expected vs actual fuel spend.
    gl_df = general ledger entries (in-memory)
    """
    if gl_df.empty or "Code" not in gl_df.columns:
        return pd.DataFrame()

    fuel_entries = gl_df[gl_df["Code"] == 5000]  # Fuel
    if fuel_entries.empty:
        return pd.DataFrame()

    df_dispatch = load_data("SELECT * FROM log_dispatch_journal")
    if df_dispatch.empty:
        return pd.DataFrame()

    rows = []

    # Current simple model: compare total expected vs total actual
    for _, trip in df_dispatch.iterrows():
        route = trip.get("rfq_ref", "")
        if route not in CORRIDORS:
            continue

        meta = CORRIDORS[route]
        dist = meta["dist"]

        # Expected fuel burn
        eff = 38.0
        expected_liters = (dist / 100) * eff
        expected_cost = expected_liters * DIESEL_PRICE

        # Actual fuel spend (aggregate)
        actual_cost = fuel_entries["Amount"].abs().sum()

        variance = actual_cost - expected_cost

        rows.append({
            "route": route,
            "distance_km": dist,
            "expected_fuel_cost": expected_cost,
            "actual_fuel_cost": actual_cost,
            "variance": variance,
        })

    return pd.DataFrame(rows)


def _compute_corridor_profit(gl_df: pd.DataFrame):
    """
    Computes profitability per corridor using:
    - Revenue (GL code 4000+)
    - Costs (from CPK engine)
    """
    if gl_df.empty or "Code" not in gl_df.columns:
        return pd.DataFrame()

    df_cpk = _compute_cpk()
    if df_cpk.empty:
        return pd.DataFrame()

    revenue_df = gl_df[gl_df["Code"].astype(str).str.startswith("4")]

    rows = []

    for route in df_cpk["route"].unique():
        cost = df_cpk[df_cpk["route"] == route]["total_cost"].sum()
        revenue = revenue_df["Amount"].sum()

        profit = revenue - cost
        margin = (profit / revenue) * 100 if revenue > 0 else 0

        rows.append({
            "route": route,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "margin_pct": margin,
        })

    return pd.DataFrame(rows)


def _compute_depreciation(asset_df: pd.DataFrame):
    """
    Computes annual and monthly depreciation for fleet assets.
    Requires (if available):
    - Purchase_Value
    - Useful_Life_Years
    Falls back to simple defaults where missing.
    """
    if asset_df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in asset_df.iterrows():
        cost = row.get("Purchase_Value", 0) or 0
        life = row.get("Useful_Life_Years", 5) or 5

        annual_dep = cost / life if life > 0 else 0
        monthly_dep = annual_dep / 12

        rows.append({
            "Asset": row.get("Asset_ID", row.get("Reg", "Unknown")),
            "Purchase_Value": cost,
            "Useful_Life_Years": life,
            "Annual_Depreciation": annual_dep,
            "Monthly_Depreciation": monthly_dep,
        })

    return pd.DataFrame(rows)


# =========================================================
# MAIN FINANCE VIEW
# =========================================================

def render_finance_view():
    st.subheader("💰 Logistics Finance Controller")

    t_dash, t_journal, t_assets = st.tabs([
        "📊 CPK Dashboard",
        "✍️ Expense Journal",
        "🚛 Asset Register",
    ])

    # =========================================================
    # TAB 1 — CPK DASHBOARD
    # =========================================================
    with t_dash:
        st.info("Metrics based on Month-To-Date performance")

        revenue = 0
        direct_costs = 0
        gl_df = pd.DataFrame()

        if "general_ledger" in st.session_state:
            gl_df = st.session_state.general_ledger
            if not gl_df.empty and "Code" in gl_df.columns:
                revenue = gl_df[gl_df["Code"].astype(str).str.startswith("4")]["Amount"].sum()
                direct_costs = gl_df[gl_df["Code"].astype(str).str.startswith("5")]["Amount"].sum()

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Revenue (MTD)", f"R {revenue:,.0f}")
        k2.metric("Direct Costs", f"R {abs(direct_costs):,.0f}")
        k3.metric("Profit/Km", "R 8.30", "+12%")
        k4.metric("Fuel % of Cost", "42%", "High")

        st.caption("Direct Operating Costs (Simulated Mix)")
        chart_data = pd.DataFrame({
            "Category": ["Fuel", "Driver", "Tyres", "Tolls", "Maintenance"],
            "Cost": [45000, 15000, 8000, 12000, 5000],
        })
        st.bar_chart(chart_data.set_index("Category"))

        st.markdown("### Corridor CPK (Live from Dispatch)")
        df_cpk = _compute_cpk()
        if df_cpk.empty:
            st.info("No dispatch data yet. Run some trips to see CPK.")
        else:
            st.dataframe(df_cpk, use_container_width=True)

        st.markdown("### Corridor Profitability (GL + Dispatch)")
        df_profit = _compute_corridor_profit(gl_df) if not gl_df.empty else pd.DataFrame()
        if df_profit.empty:
            st.info("Insufficient data to compute corridor profitability.")
        else:
            st.dataframe(df_profit, use_container_width=True)

        st.markdown("### Fuel Variance (Expected vs Actual)")
        df_var = _compute_fuel_variance(gl_df) if not gl_df.empty else pd.DataFrame()
        if df_var.empty:
            st.info("No fuel entries found in the ledger.")
        else:
            st.dataframe(df_var, use_container_width=True)

    # =========================================================
    # TAB 2 — EXPENSE JOURNAL
    # =========================================================
    with t_journal:
        st.markdown("##### 🧾 Capture Operational Expense")

        with st.form("log_expense", clear_on_submit=True):
            c1, c2 = st.columns(2)
            t_date = c1.date_input("Transaction Date", datetime.date.today())
            t_ref = c2.text_input("Reference", placeholder="e.g. INV-001")
            t_desc = st.text_input("Description", placeholder="e.g. Diesel - TRK-001")

            st.divider()

            c3, c4 = st.columns(2)

            expense_option = c3.selectbox(
                "Expense Category (Debit)",
                [
                    "5000 - Fuel (Diesel)",
                    "5010 - Oil & Lubricants",
                    "5100 - Tyres & Retreads",
                    "5300 - Driver Wages",
                    "6000 - Repairs & Maintenance",
                    "6500 - Fines & Penalties",
                ],
            )
            debit_code = int(expense_option.split(" - ")[0])

            payment_option = c4.selectbox(
                "Payment Channel (Credit)",
                [
                    "1000 - Bank (FNB Main)",
                    "1050 - Fleet Card",
                    "1100 - Petty Cash",
                ],
            )
            credit_code = int(payment_option.split(" - ")[0])

            t_amount = c3.number_input("Amount (ZAR)", min_value=0.0, step=100.00)
            c4.file_uploader("Upload Slip (Optional)")

            if st.form_submit_button("🔒 Post to General Ledger", type="primary"):
                if t_amount <= 0:
                    st.warning("Amount must be greater than 0")
                else:
                    lines = [
                        {"code": debit_code, "debit": t_amount, "credit": 0},
                        {"code": credit_code, "debit": 0, "credit": t_amount},
                    ]

                    success, msg = create_journal_entry(
                        date=t_date,
                        description=t_desc,
                        reference=t_ref,
                        lines=lines,
                        source_module="LOGISTICS",
                    )

                    if success:
                        st.success(f"✅ Posted: {t_desc}")

                        new_row = pd.DataFrame(
                            [
                                {
                                    "Date": t_date,
                                    "Code": debit_code,
                                    "Desc": t_desc,
                                    "Amount": -t_amount,
                                    "Km": 0,
                                }
                            ]
                        )
                        if "general_ledger" in st.session_state:
                            st.session_state.general_ledger = pd.concat(
                                [st.session_state.general_ledger, new_row],
                                ignore_index=True,
                            )
                        st.rerun()
                    else:
                        st.error(f"⛔ Error: {msg}")

    # =========================================================
    # TAB 3 — ASSET REGISTER
    # =========================================================
    with t_assets:
        st.subheader("🚛 Fixed Asset Register")

        if "asset_register" not in st.session_state:
            st.info("Asset register not initialized.")
            return

        df_assets = st.session_state.asset_register

        if df_assets.empty:
            st.info("No assets registered in the system yet.")
        else:
            st.dataframe(df_assets, use_container_width=True)

            if "Current_Value" in df_assets.columns:
                total = df_assets["Current_Value"].sum()
                st.metric("Total Fleet Value", f"R {total:,.0f}")

            st.markdown("### Depreciation Schedule")
            df_dep = _compute_depreciation(df_assets)
            if df_dep.empty:
                st.info("Insufficient data to compute depreciation.")
            else:
                st.dataframe(df_dep, use_container_width=True)
