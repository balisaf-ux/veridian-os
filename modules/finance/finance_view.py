import streamlit as st

import plotly.express as px

import plotly.graph_objects as go

from modules.finance.analytics import get_financial_split



def render_finance_tab():

    st.subheader("📊 Executive Financial Command")

    

    if 'general_ledger' not in st.session_state or st.session_state.general_ledger.empty:

        st.warning("Ledger Empty. No financial data to display.")

        return



    # 1. RUN ANALYTICS

    fin_data = get_financial_split(st.session_state.general_ledger)

    

    rev_log = fin_data['logistics_revenue']

    rev_trade = fin_data['trade_revenue']

    cost_ops = fin_data['logistics_costs'] # Negative value

    cost_fixed = fin_data['shared_overheads'] # Negative value

    

    # Net Profit Calculation

    gross_profit_logistics = rev_log + cost_ops

    total_net_profit = gross_profit_logistics + rev_trade + cost_fixed



    # 2. THE WATERFALL (Work Package A - Task 2)

    st.markdown("### 🌊 Net Profit Waterfall")

    fig = go.Figure(go.Waterfall(

        name = "20", orientation = "v",

        measure = ["relative", "relative", "total", "relative", "relative", "total"],

        x = ["Logistics Rev", "Direct Costs", "Fleet Gross", "Trade Margin", "Overheads", "NET PROFIT"],

        textposition = "outside",

        text = [f"{rev_log/1000:.1f}k", f"{cost_ops/1000:.1f}k", f"{gross_profit_logistics/1000:.1f}k", 

                f"{rev_trade/1000:.1f}k", f"{cost_fixed/1000:.1f}k", f"{total_net_profit/1000:.1f}k"],

        y = [rev_log, cost_ops, 0, rev_trade, cost_fixed, 0],

        connector = {"line":{"color":"rgb(63, 63, 63)"}},

    ))

    fig.update_layout(height=350, title="Contribution Analysis (ZAR)")

    st.plotly_chart(fig, use_container_width=True)



    st.divider()



    # 3. SPLIT METRICS (Work Package A - Task 1)

    c1, c2 = st.columns(2)

    

    with c1:

        st.markdown("#### 🚛 Stream A: Logistics Efficiency")

        km = fin_data['total_km'] if fin_data['total_km'] > 0 else 1

        

        k1, k2, k3 = st.columns(3)

        k1.metric("Fleet Revenue", f"R {rev_log:,.0f}")

        k2.metric("Rate / Km", f"R {rev_log/km:.2f}")

        k3.metric("CPK (Direct)", f"R {abs(cost_ops)/km:.2f}")

        

        st.caption("✅ Excludes Trade Revenue to protect CPK accuracy.")



    with c2:

        st.markdown("#### 🏗️ Stream B: Trade Margin")

        t1, t2 = st.columns(2)

        t1.metric("Trade Revenue", f"R {rev_trade:,.0f}")

        t2.metric("Contribution %", f"{(rev_trade / (rev_log + rev_trade) * 100):.1f}%")

        

        st.caption("ℹ️ Pure Margin (Zero Operational Weight).")

