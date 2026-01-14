import streamlit as st
import pandas as pd
# NEW: Import Database Manager
from modules.core.db_manager import init_db, load_ledger_to_dataframe, load_trades_to_dataframe

def boot_system():
    """
    The VAS Operating System Bootloader.
    Now with PERSISTENCE (Sprint 4.0).
    """
    
    # 0. HARDWARE CHECK (Initialize DB)
    init_db()

    # 1. SYSTEM STATUS
    if 'system_status' not in st.session_state:
        st.session_state.system_status = "ONLINE"

    # 2. FINANCE KERNEL (Load from Disk)
    if 'general_ledger' not in st.session_state:
        # Try load from DB
        df_ledger = load_ledger_to_dataframe()
        
        if df_ledger.empty:
            # Fallback to empty schema if DB is new
            st.session_state.general_ledger = pd.DataFrame(columns=[
                'Entry_ID', 'Date', 'Description', 'Reference', 'Code', 'Account', 'Debit', 'Credit', 'Type'
            ])
        else:
            st.session_state.general_ledger = df_ledger
            
    # Legacy Support (journal_entries) - Link to GL
    if 'journal_entries' not in st.session_state:
         st.session_state.journal_entries = st.session_state.general_ledger

    # 3. TRADE KERNEL (Load from Disk)
    if 'trade_rfqs' not in st.session_state:
        df_trades = load_trades_to_dataframe()
        
        if df_trades.empty:
            st.session_state.trade_rfqs = pd.DataFrame(columns=[
                'RFQ_ID', 'Client', 'Status', 'Product', 
                'Qty', 'Sell_Unit', 'Cost_Unit'
            ])
        else:
            # We need to ensure we don't lose the columns not in DB (Cost_Unit, Sell_Unit)
            # For now, we load what we have. In a full ERP, we'd persist all columns.
            # To prevent 'KeyError' in the app, we inject defaults for missing cols.
            if 'Sell_Unit' not in df_trades.columns: df_trades['Sell_Unit'] = 0.0
            if 'Cost_Unit' not in df_trades.columns: df_trades['Cost_Unit'] = 0.0
            st.session_state.trade_rfqs = df_trades

    # 4. HUNTER KERNEL
    if 'hunter_db' not in st.session_state:
        # (Prospecting persistence can be added in Sprint 4.1, keeping seed for now)
        st.session_state.hunter_db = pd.DataFrame([
            {'Company': 'Anglo American', 'Status': 'Active', 'Sector': 'Mining', 'ES_Risk_Score': 2.0},
            {'Company': 'Sasol', 'Status': 'Lead', 'Sector': 'Energy', 'ES_Risk_Score': 4.5}
        ])
