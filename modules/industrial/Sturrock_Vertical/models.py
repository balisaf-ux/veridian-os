import streamlit as st
import pandas as pd
import datetime

def init_industrial_db():
    """
    Initializes the 'Iron Vault' - The Asset & Compliance Database.
    PRE-SEEDED with Sturrock & Robson data for the Nazeem demo.
    """
    # 1. THE ASSET TREE (The Physical Reality)
    if 'asset_registry' not in st.session_state:
        # Define the schema
        columns = [
            'Asset_ID',       # e.g., MR-LOG-001
            'Division',       # Martin & Robson / Shand / LAS
            'Product',        # The item name
            'Client',         # End user (e.g., Glencore)
            'Location',       # Physical location
            'Status',         # Operational status
            'Compliance',     # ISO/OCIMF/SARS status
            'Created_At'
        ]
        
        # PRE-SEED DATA (Crucial for the demo to look active)
        seed_data = [
            {
                "Asset_ID": "MR-LOG-402",
                "Division": "Martin & Robson", 
                "Product": "Magnetite (Grade A - Bulk)", 
                "Client": "Glencore",
                "Location": "Richards Bay Terminal",
                "Status": "In Transit",
                "Compliance": "Export Cleared",
                "Created_At": str(datetime.date.today())
            },
            {
                "Asset_ID": "SH-MFG-009", 
                "Division": "Shand Engineering",
                "Product": "Marine Breakaway Coupling", 
                "Client": "Shell",
                "Location": "Grimsby Plant (UK)",
                "Status": "Manufacturing",
                "Compliance": "OCIMF Pending",
                "Created_At": str(datetime.date.today())
            },
            {
                "Asset_ID": "LAS-IOT-88", 
                "Division": "Liquid Automation",
                "Product": "Smart Nozzle Reader", 
                "Client": "Anglo Platinum",
                "Location": "Mogalakwena Mine",
                "Status": "Active",
                "Compliance": "SARS Logged",
                "Created_At": str(datetime.date.today())
            }
        ]
        
        st.session_state.asset_registry = pd.DataFrame(seed_data, columns=columns)

    # 2. THE COMPLIANCE VAULT (The Paperwork)
    if 'compliance_vault' not in st.session_state:
        st.session_state.compliance_vault = pd.DataFrame(columns=[
            'Doc_ID',
            'Asset_ID',       
            'Doc_Type',       # ISO Cert, Material Test, Warranty
            'Expiry_Date',    
            'Status'          
        ])

def register_asset(deal_dict, location="Unassigned"):
    """
    Creates the Digital Twin from a Trade Deal.
    """
    # Ensure DB exists
    init_industrial_db()
    
    # Generate ID logic
    idx = len(st.session_state.asset_registry) + 1
    # Try to determine division code from the input, default to GEN (General)
    div_code = "GEN"
    product_name = deal_dict.get('Product', 'Asset')
    
    if "Magnetite" in product_name: div_code = "MR"
    elif "Coupling" in product_name: div_code = "SH"
    elif "Reader" in product_name: div_code = "LAS"
    
    asset_id = f"{div_code}-AST-{idx:04d}"
    
    # Create the new record
    new_asset = {
        'Asset_ID': asset_id,
        'Division': deal_dict.get('Division', 'General Inventory'),
        'Product': product_name,
        'Client': deal_dict.get('Client', 'Internal'),
        'Location': location,
        'Status': 'Pending QC',
        'Compliance': 'Pending',
        'Created_At': str(datetime.date.today())
    }
    
    # Add to registry
    st.session_state.asset_registry = pd.concat(
        [st.session_state.asset_registry, pd.DataFrame([new_asset])], 
        ignore_index=True
    )
    
    return asset_id