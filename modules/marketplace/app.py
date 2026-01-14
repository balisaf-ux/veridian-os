import streamlit as st
import pandas as pd
from modules.core.db_manager import load_trades_to_dataframe, load_technical_skus

def render_marketplace_vertical():
    """
    Restores the B2B Industrial Marketplace.
    Linked to Magisterial Trade and Technical SKUs.
    """
    st.markdown("### 🤝 B2B Industrial Marketplace")
    st.caption("Spot-Trading, Tender Bidding & Ecosystem Exchange")

    df_trades = load_trades_to_dataframe()
    df_skus = load_technical_skus()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Open RFQs", len(df_trades[df_trades['Status'] == 'DRAFT']) if not df_trades.empty else 0)
    m2.metric("Available SKUs", len(df_skus) if not df_skus.empty else 0)
    m3.metric("Market Liquidity", "High")

    tab_browse, tab_bidding = st.tabs(["🔎 Browse Exchange", "🔨 Active Bidding"])

    with tab_browse:
        st.markdown("#### 📦 Industrial SKU Catalog")
        if not df_skus.empty:
            st.dataframe(df_skus[['sku_id', 'grade', 'description', 'hazchem_mandatory']], use_container_width=True, hide_index=True)

    with tab_bidding:
        st.markdown("#### ⚡ Live Spot-Trade RFQs")
        if not df_trades.empty:
            open_deals = df_trades[df_trades['Status'].isin(['DRAFT', 'NEGOTIATION'])]
            for _, deal in open_deals.iterrows():
                with st.expander(f"RFQ: {deal['RFQ_ID']} | {deal['Product']} | Qty: {deal['Qty']}"):
                    st.write(f"**Target Client:** {deal['Client']}")
                    st.button("Submit Bid", key=f"bid_{deal['RFQ_ID']}")
