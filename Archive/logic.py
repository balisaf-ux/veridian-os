import streamlit as st
import pandas as pd
from modules.core.db_manager import load_fleet_to_dataframe, load_technical_skus

def validate_physics_handshake(sku_id, load_weight):
    """
    Hard-coded Physics-Link Guardrail.
    Validates SKU Hazchem requirements against Fleet Compliance.
    """
    # 1. Pull SKU Specs
    df_skus = load_technical_skus()
    sku_data = df_skus[df_skus['sku_id'] == sku_id]
    
    if sku_data.empty:
        return False, "Invalid SKU: No Technical Specs Found", []
    
    requires_hazchem = sku_data.iloc[0]['hazchem_mandatory'] == 1
    
    # 2. Query Fleet Registry
    df_fleet = load_fleet_to_dataframe()
    
    # Apply Asset-Match Filter
    mask = (df_fleet['max_tons'] >= load_weight)
    if requires_hazchem:
        mask &= (df_fleet['hazchem_compliant'] == 1)
        
    valid_vehicles = df_fleet[mask]
    
    if valid_vehicles.empty:
        return False, "PHYSICS BLOCK: No compliant vehicle available for this load.", []
    
    return True, "Physics Validation Passed", valid_vehicles['truck_id'].tolist()
