import pandas as pd
import streamlit as st

def get_financial_split(df_gl):
    """
    Splits the General Ledger into two streams:
    Stream A: Logistics (Heavy Assets, CPK driven)
    Stream B: Trade (Paper Assets, Margin driven)
    """
    if df_gl.empty:
        return None, None

    # STREAM A: LOGISTICS (Standard Transport Codes: 4000, 4100)
    # Exclude Trade (4500)
    logistics_rev_mask = (df_gl['Code'].astype(str).str.startswith('4')) & (df_gl['Code'].astype(str) != '4500')
    df_logistics_rev = df_gl[logistics_rev_mask]
    
    # Direct Costs (5000 series) & Overheads (6000 series) are assumed Logistics for now
    # (Unless we tag specific trade costs later)
    df_ops_costs = df_gl[df_gl['Code'].astype(str).str.startswith('5')]
    df_overheads = df_gl[df_gl['Code'].astype(str).str.startswith('6')]

    # STREAM B: TRADE (Code 4500)
    trade_rev_mask = (df_gl['Code'].astype(str) == '4500')
    df_trade = df_gl[trade_rev_mask]

    return {
        "logistics_revenue": df_logistics_rev['Amount'].sum(),
        "logistics_costs": df_ops_costs['Amount'].sum(),
        "shared_overheads": df_overheads['Amount'].sum(),
        "trade_revenue": df_trade['Amount'].sum(),
        "total_km": df_gl['Km'].sum()
    }
