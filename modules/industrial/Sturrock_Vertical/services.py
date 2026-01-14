import streamlit as st
import pandas as pd
import datetime

def generate_qr_identity(asset_id):
    """
    Returns the unique string for the QR Code.
    Future: This will link to the mobile app view.
    """
    return f"MAIS:ID:{asset_id}:VERIFIED"

def attach_compliance_doc(asset_id, doc_type, expiry_days=365):
    """
    Simulates uploading a compliance cert to The Vault.
    """
    if 'compliance_vault' not in st.session_state:
        return False

    expiry = datetime.date.today() + datetime.timedelta(days=expiry_days)
    
    new_doc = {
        'Doc_ID': f"DOC-{len(st.session_state.compliance_vault)+1}",
        'Asset_ID': asset_id,
        'Doc_Type': doc_type,
        'Expiry_Date': str(expiry),
        'Status': 'Active'
    }
    
    st.session_state.compliance_vault = pd.concat(
        [st.session_state.compliance_vault, pd.DataFrame([new_doc])], 
        ignore_index=True
    )
    return True

def get_asset_docs(trade_deal_id):
    """
    Retrieves all compliance docs linked to a specific Trade Deal
    via the Asset Registry.
    """
    # 1. Find Asset ID from Trade ID
    assets = st.session_state.asset_registry
    if assets.empty: return []
    
    linked_asset = assets[assets['Trade_Deal_ID'] == trade_deal_id]
    if linked_asset.empty: return []
    
    asset_id = linked_asset.iloc[0]['Asset_ID']
    
    # 2. Find Docs
    vault = st.session_state.compliance_vault
    docs = vault[vault['Asset_ID'] == asset_id]
    
    return docs.to_dict('records')
