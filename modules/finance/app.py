import streamlit as st
import pandas as pd
import json
import os
from sqlalchemy import create_engine, text
from modules.core.db_manager import get_billing_docs, init_db

# --- IMPORTS FROM YOUR MODULES ---
from modules.finance.finance_view import render_finance_tab 
from modules.finance.models import init_finance_db
from modules.finance.services import create_journal_entry
from modules.finance.coa import SA_LOGISTICS_COA

def _load_state_from_kernel():
    """
    THE TRANSLATOR (PRODUCTION MODE)
    Connects to the Magisterial Ledger, maps Account Names to COA Codes,
    and formats data for the Executive Dashboard.
    """
    # 1. HARD-CODED PATH (The Source of Truth)
    db_file_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    
    # 2. VALIDATION
    if not os.path.exists(db_file_path):
        st.error(f"❌ CRITICAL: Database file MISSING at {db_file_path}")
        return

    # 3. CONNECT
    engine = create_engine(f'sqlite:///{db_file_path}')
    
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM finance_general_ledger ORDER BY timestamp DESC")
            df_raw = pd.read_sql(query, conn)
        
        # 4. HANDLE EMPTY STATE
        if df_raw.empty:
            st.session_state.general_ledger = pd.DataFrame(columns=[
                'Entry_ID', 'Date', 'Description', 'Reference', 'Code', 'Debit', 'Credit', 'Amount', 'Km', 'Type'
            ])
            return

        # 5. FLATTEN JSON & MAP ACCOUNTS TO CODES
        flattened_rows = []
        for _, row in df_raw.iterrows():
            lines_data = row['lines_data']
            if isinstance(lines_data, str):
                try:
                    lines_data = json.loads(lines_data)
                except json.JSONDecodeError:
                    continue 
            
            for line in lines_data:
                debit_val = float(line.get('debit', 0.0))
                credit_val = float(line.get('credit', 0.0))
                
                # --- THE ROSETTA STONE (MAPPING PATCH) ---
                # Maps generic text names to strict integer COA codes
                account_raw = line.get('account', 'Unknown')
                account_code = account_raw 
                
                if account_raw == "Sales Revenue":
                    account_code = 4500  # Trade Revenue (Sourcing)
                elif account_raw == "Accounts Receivable":
                    account_code = 1200  # Debtors
                elif account_raw == "VAT Control Account":
                    account_code = 2200  # VAT Liability
                elif account_raw == "Trade Revenue (Sourcing)":
                    account_code = 4500
                elif account_raw == "Logistics Revenue (Transport)":
                    account_code = 4000
                
                flattened_rows.append({
                    'Entry_ID': row['id'],
                    'Date': pd.to_datetime(row['timestamp']),
                    'Description': row['description'],
                    'Reference': row['id'], 
                    'Code': account_code, 
                    'Debit': debit_val,
                    'Credit': credit_val,
                    'Amount': credit_val - debit_val,   
                    'Km': 0.0,                          
                    'Type': row['status']
                })

        st.session_state.general_ledger = pd.DataFrame(flattened_rows)

    except Exception as e:
        st.error(f"⚠️ Cortex Link Error: {e}")
        st.session_state.general_ledger = pd.DataFrame()

def render_finance_vertical():
    st.markdown("## 💰 Financial Control | Sovereign Treasury")
    st.caption("v14.0 Modular Engine • Double-Entry Logic • Real-Time Analytics")

    # --- 1. INITIALIZATION SEQUENCE ---
    init_db() 
    init_finance_db()
    _load_state_from_kernel() 

    # --- 2. THE COMMAND DECK ---
    tab_dashboard, tab_journal, tab_invoices, tab_coa = st.tabs([
        "📊 Executive Dashboard", 
        "📒 Manual Journal", 
        "🧾 Document Repo",
        "🗂️ Chart of Accounts"
    ])

    # --- TAB 1: EXECUTIVE DASHBOARD ---
    with tab_dashboard:
        render_finance_tab()

    # --- TAB 2: MANUAL JOURNAL ---
    with tab_journal:
        st.subheader("✍️ Manual General Ledger Entry")
        st.caption("Direct Injection into the Sovereign Kernel")
        
        with st.form("manual_journal_entry"):
            c1, c2, c3 = st.columns(3)
            ref = c1.text_input("Reference", placeholder="e.g., ADJ-001")
            desc = c2.text_input("Description", placeholder="Capital Injection / Correction")
            date = c3.date_input("Date")
            
            st.markdown("---")
            c4, c5, c6 = st.columns(3)
            coa_options = [f"{c['code']} - {c['name']}" for c in SA_LOGISTICS_COA]
            db_acc = c4.selectbox("Debit Account", coa_options, key="db_acc_sel")
            db_amt = c5.number_input("Debit Amount", min_value=0.0, step=100.0, key="db_amt_val")
            cr_acc = c4.selectbox("Credit Account", coa_options, index=3, key="cr_acc_sel")
            cr_amt = c5.number_input("Credit Amount", min_value=0.0, step=100.0, key="cr_amt_val")
            
            if st.form_submit_button("🚀 Post to Ledger"):
                if db_amt > 0 and db_amt == cr_amt:
                    db_code = db_acc.split(" - ")[0]
                    cr_code = cr_acc.split(" - ")[0]
                    lines = [
                        {'code': db_code, 'debit': db_amt, 'credit': 0},
                        {'code': cr_code, 'debit': 0, 'credit': cr_amt}
                    ]
                    success, msg = create_journal_entry(date, desc, ref, lines, source_module="MANUAL")
                    if success:
                        st.success(f"Journal Posted: {msg}")
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.divider()
        st.markdown("#### 📜 Live Ledger Stream")
        if 'general_ledger' in st.session_state and not st.session_state.general_ledger.empty:
            st.dataframe(st.session_state.general_ledger.head(50), use_container_width=True)
        else:
            st.info("Ledger Empty.")

    with tab_invoices:
        st.subheader("📄 Document Repository")
        df_docs = get_billing_docs()
        if not df_docs.empty:
            st.dataframe(df_docs, use_container_width=True)
        else:
            st.info("No Invoices or Quotes generated yet.")

    with tab_coa:
        st.subheader("📚 Master Chart of Accounts")
        st.dataframe(pd.DataFrame(SA_LOGISTICS_COA), use_container_width=True)
