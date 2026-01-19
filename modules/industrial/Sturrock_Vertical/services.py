import streamlit as st
import pandas as pd
import datetime

def attach_compliance_doc(asset_id, doc_type, expiry_days=365):
    """
    Simulates uploading a compliance cert to The Vault AND updates the asset status.
    This creates the 'Audit Trail' Nazeem is looking for.
    """
    # Safety Check: Ensure DB is initialized
    if 'asset_registry' not in st.session_state or 'compliance_vault' not in st.session_state:
        return False

    # 1. VISUAL UPDATE: Update the Main Registry so the UI changes immediately
    registry = st.session_state.asset_registry
    # Find the row index for this Asset ID
    idx = registry[registry['Asset_ID'] == asset_id].index

    if not idx.empty:
        # Update the 'Compliance' column to show verification
        st.session_state.asset_registry.at[idx[0], 'Compliance'] = f"{doc_type} (Verified)"
        # Also auto-upgrade the status to 'Active' or 'Operational'
        st.session_state.asset_registry.at[idx[0], 'Status'] = "Operational"
    else:
        return False # Asset not found, stop here

    # 2. BACKEND LOGGING: Add entry to the Compliance Vault (The permanent record)
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

def generate_qr_identity(asset_id):
    """
    Returns the unique string for the QR Code.
    Future: This will link to the mobile app view for field inspectors.
    """
    return f"MAIS:ID:{asset_id}:VERIFIED"