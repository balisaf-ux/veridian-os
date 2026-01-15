import streamlit as st
import plotly.express as px
import datetime
import pandas as pd

# ==========================================================
# 1. INTEGRATION IMPORTS (FINANCE ENGINE BRIDGE)
# ==========================================================
try:
    from modules.finance.services import create_journal_entry
except ImportError:
    def create_journal_entry(*args, **kwargs):
        return False, "Finance Core Offline"


def render_finance_portal():
    st.markdown("## 🏦 Finance Portal | Treasury")
    st.caption("Restricted Access: Internal Controllers Only")

    tab_overview, tab_input, tab_assets = st.tabs([
        "📊 CPK Dashboard",
        "✍️ Journal Desk",
        "🚛 Asset Register"
    ])

    # ==========================================================
    # TAB 1 — CPK DASHBOARD
    # ==========================================================
    with tab_overview:
        st.subheader("Operational Income Statement (MTD)")

        # Defensive: ensure ledger exists
        if (
            "general_ledger" not in st.session_state
            and "journal_entries" not in st.session_state
        ):
            st.warning("Ledger Empty")
            return

        # Prefer new Finance Engine schema if available
        if (
            "journal_entries" in st.session_state
            and not st.session_state.journal_entries.empty
        ):
            df_gl = st.session_state.journal_entries
            # Placeholder: full mapping will occur once Reporting Engine is online
            pass

        # Legacy ledger fallback (ensures no functionality loss)
        if "general_ledger" in st.session_state:
            df_gl = st.session_state.general_ledger

            if "Code" in df_gl.columns and "Amount" in df_gl.columns:
                revenue = df_gl[df_gl["Code"].astype(str).str.startswith("4")]["Amount"].sum()
                direct_costs = df_gl[df_gl["Code"].astype(str).str.startswith("5")]["Amount"].sum()
                overheads = df_gl[df_gl["Code"].astype(str).str.startswith("6")]["Amount"].sum()

                gross_profit = revenue + direct_costs
                net_profit = gross_profit + overheads

                total_km = df_gl["Km"].sum() if "Km" in df_gl.columns else 1
                total_km = total_km if total_km > 0 else 1

                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Revenue", f"R {revenue:,.0f}")
                m2.metric("Direct Costs", f"R {abs(direct_costs):,.0f}")
                m3.metric(
                    "Gross Profit",
                    f"R {gross_profit:,.0f}",
                    f"{(gross_profit / revenue) * 100:.1f}% Margin" if revenue else "0%",
                )
                m4.metric(
                    "Net Profit",
                    f"R {net_profit:,.0f}",
                    f"{(net_profit / revenue) * 100:.1f}% Net" if revenue else "0%",
                )

                st.divider()

                # CPK Analysis
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("#### 📉 Cost Per Kilometer")
                    st.info(f"**Running Distance:** {total_km:,.0f} km")

                    k1, k2, k3 = st.columns(3)
                    k1.metric("Rate / Km", f"R {revenue / total_km:.2f}")
                    k2.metric("Run Cost / Km", f"R {abs(direct_costs / total_km):.2f}")
                    k3.metric("Profit / Km", f"R {(gross_profit / total_km):.2f}")

                with c2:
                    df_costs = df_gl[df_gl["Code"].astype(str).str.startswith("5")].copy()
                    df_costs["Amount"] = df_costs["Amount"].abs()

                    if not df_costs.empty:
                        fig = px.pie(
                            df_costs,
                            values="Amount",
                            names="Desc",
                            title="Direct Cost Drivers",
                        )
                        fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("Waiting for financial data...")

    # ==========================================================
    # TAB 2 — JOURNAL DESK (DOUBLE ENTRY)
    # ==========================================================
    with tab_input:
        st.subheader("🧾 Transaction Capture")

        with st.form("transaction_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            t_date = c1.date_input("Transaction Date", datetime.date.today())
            t_ref = c2.text_input("Reference", placeholder="e.g. INV‑001")

            t_desc = st.text_input("Description", placeholder="e.g. Diesel — Truck 10")
            st.divider()

            c3, c4 = st.columns(2)

            # Debit (Expense)
            expense_option = c3.selectbox(
                "Expense Category (Debit)",
                [
                    "5000 - Fuel (Diesel)",
                    "5010 - Oil & Lubricants",
                    "5100 - Tyres & Retreads",
                    "5300 - Driver Wages",
                    "6000 - Repairs & Maint",
                    "6500 - Fines & Penalties",
                ],
            )
            debit_code = int(expense_option.split(" - ")[0])

            # Credit (Payment)
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
                    # Construct double entry
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

                        # Legacy ledger update (no functionality loss)
                        new_legacy_row = pd.DataFrame(
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
                                [st.session_state.general_ledger, new_legacy_row],
                                ignore_index=True,
                            )

                        st.rerun()
                    else:
                        st.error(f"⛔ Error: {msg}")

    # ==========================================================
    # TAB 3 — ASSET REGISTER
    # ==========================================================
    with tab_assets:
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
            else:
                st.warning("⚠️ Asset Register schema incomplete. Reset system to initialize.")

