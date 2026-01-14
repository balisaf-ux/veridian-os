import streamlit as st
import pandas as pd
import datetime
from modules.finance.models import init_finance_db

# NEW: Persistence Import (Sprint 4.0)
try:
    from modules.core.db_manager import save_journal_entry
except ImportError:
    # Fallback if core not initialized yet
    def save_journal_entry(*args, **kwargs): pass

# ==========================================
# 1. THE WRITER (TRANSACTION ENGINE)
# ==========================================
def create_journal_entry(date, description, reference, lines, source_module="MANUAL"):
    """
    Creates a Double-Entry Journal AND Persists to Disk.
    lines = [{'code': 1000, 'debit': 100, 'credit': 0}, ...]
    """
    init_finance_db()
    
    # 1. Validate Balance
    total_debit = sum([l['debit'] for l in lines])
    total_credit = sum([l['credit'] for l in lines])
    
    if abs(total_debit - total_credit) > 0.01:
        return False, f"⛔ Entry Unbalanced! Debits: {total_debit} | Credits: {total_credit}"

    # 2. Create Header ID
    # Unique ID based on timestamp to avoid collisions
    entry_id = f"JRN-{int(datetime.datetime.now().timestamp())}"
    
    # 3. Augment Lines with Names (from COA)
    # We look up the Account Name to store it permanently
    if 'chart_of_accounts' in st.session_state:
        coa = st.session_state.chart_of_accounts
    else:
        coa = pd.DataFrame(columns=['Code', 'Name', 'Type'])

    enriched_lines = []
    
    for l in lines:
        # Find account name
        acct_name = "Unknown"
        acct_type = "Unknown"
        
        if not coa.empty:
            # Safe lookup
            acct_row = coa[coa['Code'] == l['code']]
            if not acct_row.empty:
                acct_name = acct_row.iloc[0]['Name']
                acct_type = acct_row.iloc[0]['Type']
        
        # Add to enriched list
        l['name'] = acct_name
        l['type'] = acct_type
        enriched_lines.append(l)

    # 4. PERSIST TO DISK (The 'Etching in Stone')
    try:
        save_journal_entry(entry_id, date, reference, description, enriched_lines, source_module)
    except Exception as e:
        return False, f"Database Error: {e}"

    # 5. UPDATE SESSION STATE (Instant Feedback)
    # We flatten the lines for the DataFrame view used by the UI
    new_rows = []
    for el in enriched_lines:
        new_rows.append({
            'Entry_ID': entry_id,
            'Date': str(date),
            'Description': description,
            'Reference': reference,
            'Code': el['code'],
            'Account': el['name'],
            'Debit': el['debit'],
            'Credit': el['credit'],
            'Type': el['type'],
            'Source_Module': source_module
        })
    
    # Check if GL exists, if not create it
    if 'general_ledger' not in st.session_state:
        st.session_state.general_ledger = pd.DataFrame(columns=[
             'Entry_ID', 'Date', 'Description', 'Reference', 'Code', 'Account', 'Debit', 'Credit', 'Type', 'Source_Module'
        ])

    st.session_state.general_ledger = pd.concat(
        [st.session_state.general_ledger, pd.DataFrame(new_rows)], 
        ignore_index=True
    )
    
    return True, entry_id

# ==========================================
# 2. THE READERS (REPORTING ENGINE)
# ==========================================

def get_trial_balance():
    """
    Aggregates the General Ledger into a Trial Balance.
    Returns: DataFrame [Code, Name, Type, Debit, Credit, Net_Balance]
    """
    if 'general_ledger' not in st.session_state or st.session_state.general_ledger.empty:
        return pd.DataFrame()

    df = st.session_state.general_ledger.copy()
    
    # Group by Account
    tb = df.groupby(['Code', 'Account', 'Type'])[['Debit', 'Credit']].sum().reset_index()
    
    # Calculate Net
    # Asset/Expense: Debit - Credit
    # Liability/Income: Credit - Debit (But usually TB is just Net = Dr - Cr)
    tb['Net_Balance'] = tb['Debit'] - tb['Credit']
    
    return tb

def get_income_statement():
    """
    Generates the P&L from the Trial Balance.
    Returns: (DataFrame, net_profit_value)
    """
    tb = get_trial_balance()
    
    if tb.empty:
        return None, 0.0
        
    # Filter for P&L Accounts
    pl_df = tb[tb['Type'].isin(['INCOME', 'EXPENSE', 'REVENUE'])].copy()
    
    if pl_df.empty:
        return None, 0.0
        
    # Calculate Profit
    # Income is Credit (Negative in Dr-Cr logic usually, or positive in Cr-Dr)
    # Let's standardize: 
    # Income (Credit) should be positive contribution
    # Expense (Debit) should be negative contribution
    
    income = pl_df[pl_df['Type'].isin(['INCOME', 'REVENUE'])]['Credit'].sum() - pl_df[pl_df['Type'].isin(['INCOME', 'REVENUE'])]['Debit'].sum()
    expense = pl_df[pl_df['Type'] == 'EXPENSE']['Debit'].sum() - pl_df[pl_df['Type'] == 'EXPENSE']['Credit'].sum()
    
    net_profit = income - expense
    
    return pl_df, net_profit
