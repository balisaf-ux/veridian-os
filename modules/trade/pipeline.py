import streamlit as st
import pandas as pd

def render_pipeline_kanban():
    st.subheader("Magisterial Pipeline (Kanban)")
    
    if st.session_state.trade_rfqs.empty:
        st.info("Pipeline Empty. Initialize deals in 'The Hunter' tab.")
        return

    df = st.session_state.trade_rfqs
    
    # Weighted Value Calculation
    # For now, we assume 100% prob for simplicity, or 10% for Draft, 50% for Neg.
    def get_weight(status):
        if status == 'WON': return 1.0
        if status == 'NEGOTIATION': return 0.7
        if status == 'SOURCING': return 0.3
        return 0.1

    df['Value'] = df['Sell_Unit'] * df['Qty']
    df['Weighted_Value'] = df.apply(lambda x: x['Value'] * get_weight(x['Status']), axis=1)
    
    total_pipeline = df[df['Status'] != 'WON']['Value'].sum()
    weighted_pipeline = df[df['Status'] != 'WON']['Weighted_Value'].sum()
    
    st.metric("Total Active Pipeline (Weighted)", f"R {weighted_pipeline:,.0f}", f"Nominal: R {total_pipeline:,.0f}")
    st.divider()

    # KANBAN COLUMNS
    c1, c2, c3, c4 = st.columns(4)
    
    cols = {
        "DRAFT": c1,
        "SOURCING": c2,
        "NEGOTIATION": c3,
        "WON": c4
    }
    
    headers = {
        "DRAFT": "📝 Draft",
        "SOURCING": "🔍 Sourcing (VIS)",
        "NEGOTIATION": "🤝 Negotiation",
        "WON": "💰 Closed Won"
    }

    # Render Headers
    for status, col in cols.items():
        col.markdown(f"**{headers.get(status, status)}**")

    # Render Cards
    for idx, row in df.iterrows():
        status = row['Status']
        # Map statuses to columns (Handle variations if needed)
        target_col = cols.get(status, c1) 
        
        with target_col:
            st.info(f"**{row['Client']}**\n\n{row['Product']}\n\nR {row['Value']:,.0f}")
