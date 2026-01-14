import streamlit as st
import pandas as pd
import datetime

def init_industrial_db():
    """
    Initializes the 'Iron Vault' - The Asset & Compliance Database.
    """
    # 1. THE ASSET TREE (The Physical Reality)
    if 'asset_registry' not in st.session_state:
        st.session_state.asset_registry = pd.DataFrame(columns=[
            'Asset_ID',       # MAIS-AGL-PMP-001
            'Name',           # 6-inch Centrifugal Pump
            'Client',         # Anglo American
            'Trade_Deal_ID',  # Link to Commercial Source (Traceability)
            'Install_Location', # Plant A -> Conveyor B
            'QR_String',      # The Digital Identity
            'Created_At'
        ])

    # 2. THE COMPLIANCE VAULT (The Paperwork)
    if 'compliance_vault' not in st.session_state:
        st.session_state.compliance_vault = pd.DataFrame(columns=[
            'Doc_ID',
            'Asset_ID',       # Link to Asset
            'Doc_Type',       # ISO Cert, Material Test, Warranty
            'Expiry_Date',    # For compliance alerts
            'Status'          # Active/Expired
        ])

def register_asset(deal_dict, location="Unassigned"):
    """
    Creates the Digital Twin from a Trade Deal.
    """
    init_industrial_db()
    
    # Generate ID
    idx = len(st.session_state.asset_registry) + 1
    client_code = deal_dict['Client'][:3].upper()
    asset_id = f"MAIS-{client_code}-{idx:04d}"
    
    # Generate QR (Work Package C)
    qr_code = f"https://mais.veridian.os/track/{asset_id}"
    
    new_asset = {
        'Asset_ID': asset_id,
        'Name': deal_dict['Product'],
        'Client': deal_dict['Client'],
        'Trade_Deal_ID': deal_dict['RFQ_ID'],
        'Install_Location': location,
        'QR_String': qr_code,
        'Created_At': str(datetime.date.today())
    }
    
    st.session_state.asset_registry = pd.concat(
        [st.session_state.asset_registry, pd.DataFrame([new_asset])], 
        ignore_index=True
    )
    
    return asset_id
