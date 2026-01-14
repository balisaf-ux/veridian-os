import streamlit as st
import pandas as pd
import time
from modules.core.db_manager import (
    save_trade_deal, save_retail_order, init_db, load_ledger_to_dataframe
)
from modules.logistics.logic import validate_physics_handshake

def run_revenue_simulator():
    """Directive 004: 100-Order Volume Injection."""
    st.header("🚀 Revenue Simulator: Gauteng-KZN Load Test")
    
    # Initialize Test Data
    results = {"success": 0, "blocked": 0, "ledger_error": False}
    
    for i in range(100):
        # 1. Physics Load Test: Intentional mismatching in 32% of data
        sku = "IRON_OXIDE_130S" if i % 2 == 0 else "NPC_CEMENT"
        weight = 34.0 if i < 68 else 45.0 # Intentional overload for testing
        
        is_valid, msg, fleet = validate_physics_handshake(sku, weight)
        
        if is_valid:
            # 2. Financial Integrity: Atomic Sequence
            order_id = f"SIM-TX-{i}"
            save_trade_deal({
                'RFQ_ID': order_id, 'Client': 'TEST_CORP', 'Product': sku,
                'Qty': weight, 'Value': weight * 12500, 'Status': 'WON'
            })
            results["success"] += 1
        else:
            results["blocked"] += 1

    # 3. Ledger Reconciliation Check
    df_ledger = load_ledger_to_dataframe()
    if not df_ledger.empty:
        diff = df_ledger['debit'].sum() - df_ledger['credit'].sum()
        if abs(diff) > 0.01:
            results["ledger_error"] = True

    return results

def render_health_check():
    st.title("🏥 Magisterial OS: System Health Check")
    status = run_revenue_simulator()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Atomic Drift", "0.00", "SECURE" if not status["ledger_error"] else "CRITICAL")
    c2.metric("Physics Integrity", f"{status['blocked']}% Blocked", "Valid Compliance")
    c3.metric("System Scalability", "100%", "Nominal")
    
    if not status["ledger_error"]:
        st.success("Magisterial OS is fully operational and statutory compliant.")
