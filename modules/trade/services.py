import streamlit as st
import pandas as pd
import json
from modules.finance.services import create_journal_entry
from modules.core.db_manager import load_technical_skus, load_prospects_to_dataframe

def get_logistics_handshake(sku_id, qty_tons):
    """
    MAX CAPABILITY LOGIC: Dynamically selects vehicle type based on 
    Physics-Link (Hazchem) and cargo weight.
    """
    df_skus = load_technical_skus()
    is_hazchem = False
    
    if not df_skus.empty and sku_id in df_skus['sku_id'].values:
        # Pull Hazchem status from technical registry
        is_hazchem = df_skus[df_skus['sku_id'] == sku_id].iloc[0]['hazchem_mandatory']

    # Vehicle Selection Logic based on Physics
    if is_hazchem:
        v_type = "34-Ton Hazchem Side Tipper" if qty_tons > 15 else "8-Ton Hazchem Integrated"
        base_rate = 32.50 # Premium Hazchem Rate
    else:
        v_type = "34-Ton Tri-Axle Flatbed" if qty_tons > 15 else "8-Ton Flatbed"
        base_rate = 24.50 # Standard Commercial Rate

    # Transport Estimate (Standard JHB to DBN route)
    distance = 550 
    est_cost = distance * base_rate
    
    return {
        "vehicle": v_type,
        "est_rate": est_cost,
        "is_hazchem": is_hazchem,
        "compliance_string": "✅ HAZCHEM VEHICLE REQUIRED" if is_hazchem else "🟢 STANDARD VEHICLE"
    }

def validate_deal_compliance(rfq_id, sku_id, vendor_name):
    """Enforces Physics-Link safety and checks Vendor Permit status."""
    df_skus = load_technical_skus()
    if df_skus.empty or sku_id not in df_skus['sku_id'].values:
        return True, "Standard Item: No Technical Restrictions."

    sku_data = df_skus[df_skus['sku_id'] == sku_id].iloc[0]
    
    # Physics-Link check
    if sku_data['hazchem_mandatory']:
        df_prospects = load_prospects_to_dataframe()
        if not df_prospects.empty and vendor_name in df_prospects['Company'].values:
            vendor_data = df_prospects[df_prospects['Company'] == vendor_name].iloc[0]
            # Verify permit in persistent registry
            if not vendor_data.get('hazchem_permit', 0):
                return False, f"⚠️ HAZCHEM BLOCK: {vendor_name} lacks valid Hazchem Permit for {sku_id}."
    
    return True, "Governance Gate Cleared."

def post_trade_to_finance(rfq_id, description, amount):
    """Post to General Ledger once deal is WON."""
    if amount <= 0: return False, "Invalid Amount"
    lines = [
        {'code': 1200, 'name': 'Accounts Receivable', 'debit': amount, 'credit': 0},
        {'code': 4000, 'name': 'Trade Revenue', 'debit': 0, 'credit': amount}
    ]
    return create_journal_entry(
        date=pd.Timestamp.now().date(),
        description=description,
        reference=rfq_id,
        lines=lines,
        source_module="MAGISTERIAL_TRADE"
    )
