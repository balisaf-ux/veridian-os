import streamlit as st
import pandas as pd
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# ==========================================
# PART 1: LEGACY FRONTEND (Streamlit State)
# Preserves existing dashboard functionality
# ==========================================

def init_finance_db():
    """
    Initializes the Double-Entry General Ledger.
    1. Chart of Accounts (COA)
    2. Journal Headers
    3. Ledger Lines
    """
    
    # --- 1. THE CHART OF ACCOUNTS (The Skeleton) ---
    if 'chart_of_accounts' not in st.session_state:
        st.session_state.chart_of_accounts = pd.DataFrame(columns=[
            'Code', 'Name', 'Type', 'Parent'
        ])
        
        # SEED DATA: Standard South African SME Structure
        seed_coa = [
            # ASSETS (1000 series)
            {'Code': 1000, 'Name': 'Bank - FNB Main', 'Type': 'ASSET', 'Parent': None},
            {'Code': 1100, 'Name': 'Petty Cash', 'Type': 'ASSET', 'Parent': None},
            {'Code': 1200, 'Name': 'Accounts Receivable (Debtors)', 'Type': 'ASSET', 'Parent': None},
            {'Code': 1500, 'Name': 'Inventory - Stock', 'Type': 'ASSET', 'Parent': None},
            {'Code': 1600, 'Name': 'Fixed Assets - Vehicles', 'Type': 'ASSET', 'Parent': None},

            # LIABILITIES (2000 series)
            {'Code': 2000, 'Name': 'Accounts Payable (Creditors)', 'Type': 'LIABILITY', 'Parent': None},
            {'Code': 2200, 'Name': 'VAT Control Account', 'Type': 'LIABILITY', 'Parent': None},
            {'Code': 2500, 'Name': 'Bank Loan - Vehicle Finance', 'Type': 'LIABILITY', 'Parent': None},

            # EQUITY (3000 series)
            {'Code': 3000, 'Name': 'Share Capital', 'Type': 'EQUITY', 'Parent': None},
            {'Code': 3100, 'Name': 'Retained Earnings', 'Type': 'EQUITY', 'Parent': None},

            # INCOME (4000 series)
            {'Code': 4000, 'Name': 'Logistics Revenue (Transport)', 'Type': 'INCOME', 'Parent': None},
            {'Code': 4500, 'Name': 'Trade Revenue (Sourcing)', 'Type': 'INCOME', 'Parent': None},

            # EXPENSES (5000+ series)
            {'Code': 5000, 'Name': 'Cost of Sales - Goods', 'Type': 'EXPENSE', 'Parent': None},
            {'Code': 5100, 'Name': 'Cost of Sales - Freight', 'Type': 'EXPENSE', 'Parent': None},
            {'Code': 5200, 'Name': 'Fuel & Oil', 'Type': 'EXPENSE', 'Parent': None},
            {'Code': 5300, 'Name': 'Vehicle Maintenance', 'Type': 'EXPENSE', 'Parent': None},
            {'Code': 6000, 'Name': 'Salaries & Wages', 'Type': 'EXPENSE', 'Parent': None},
            {'Code': 6100, 'Name': 'Rent & Utilities', 'Type': 'EXPENSE', 'Parent': None},
            {'Code': 6200, 'Name': 'Consulting Fees', 'Type': 'EXPENSE', 'Parent': None},
        ]
        st.session_state.chart_of_accounts = pd.concat(
            [st.session_state.chart_of_accounts, pd.DataFrame(seed_coa)], 
            ignore_index=True
        )

    # --- 2. JOURNAL ENTRIES (The Brain - Headers) ---
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = pd.DataFrame(columns=[
            'Entry_ID', 'Date', 'Description', 'Reference', 'Source_Module'
        ])

    # --- 3. LEDGER LINES (The Brain - Details) ---
    if 'ledger_lines' not in st.session_state:
        st.session_state.ledger_lines = pd.DataFrame(columns=[
            'Entry_ID', 'Account_Code', 'Debit', 'Credit'
        ])


# ==========================================
# PART 2: MAGISTERIAL BACKEND (SQLAlchemy)
# Powers the new Settlement & Journal Engines
# ==========================================

Base = declarative_base()

class Client(Base):
    """
    The Counterparty.
    Who we are trading with.
    """
    __tablename__ = 'finance_clients'
    
    id = Column(String(50), primary_key=True)  # e.g., 'ORION_ENERGY'
    name = Column(String(100), nullable=False)
    credit_limit = Column(Numeric(12, 2), default=0)
    current_debt = Column(Numeric(12, 2), default=0)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="client")

class Invoice(Base):
    """
    The Commercial Instrument.
    The legal demand for payment.
    """
    __tablename__ = 'finance_invoices'
    
    invoice_number = Column(String(50), primary_key=True) # e.g. INV-2026-001
    client_id = Column(String(50), ForeignKey('finance_clients.id'))
    date_issued = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='DRAFT') # DRAFT, SENT, PAID, VOID
    
    # Financials (Stored as specific values to prevent recalc drift)
    total_excl_vat = Column(Numeric(12, 2), nullable=False)
    vat_amount = Column(Numeric(12, 2), nullable=False)
    total_due = Column(Numeric(12, 2), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    lines = relationship("LineItem", back_populates="invoice")

class LineItem(Base):
    """
    The Granular Detail.
    What exactly are we billing for?
    """
    __tablename__ = 'finance_invoice_lines'
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), ForeignKey('finance_invoices.invoice_number'))
    description = Column(String(200))
    qty = Column(Numeric(10, 4)) # Allow 4 decimals for precise liquid volume
    rate = Column(Numeric(10, 2))
    total = Column(Numeric(12, 2))
    
    invoice = relationship("Invoice", back_populates="lines")

class JournalEntry(Base):
    """
    The General Ledger (Persistent).
    The single source of financial truth for the backend.
    """
    __tablename__ = 'finance_general_ledger'
    
    id = Column(String(50), primary_key=True) # JRN-UUID
    timestamp = Column(DateTime, default=datetime.now)
    description = Column(String(200))
    
    # Storing lines as JSON for speed in this phase.
    # Contains: [{account, debit, credit}, ...]
    lines_data = Column(JSON) 
    
    status = Column(String(20), default='POSTED')
