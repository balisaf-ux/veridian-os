# modules/logistics/db_utils.py

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# =========================================================
# DATABASE CORE MODULE
# =========================================================

# Use your ORIGINAL DB so fleet + missions + registry remain intact
DB_URL = "sqlite:///fleet_data.db"

# Allow multi-threaded access (Streamlit requirement)
engine = create_engine(DB_URL, future=True, connect_args={"check_same_thread": False})


# =========================================================
# WRITE WRAPPER (COMMITS AUTOMATICALLY)
# =========================================================

def run_query(query_str: str, params: dict | None = None):
    """
    Unified write/query executor.
    Uses engine.begin() which automatically commits.
    Returns True/False for UI cleanliness.
    """
    try:
        with engine.begin() as conn:
            conn.execute(text(query_str), params or {})
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False


# =========================================================
# READ WRAPPER
# =========================================================

def load_data(query_str: str, params: dict | None = None) -> pd.DataFrame:
    """
    Unified read executor.
    Returns a DataFrame or empty DataFrame on failure.
    """
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query_str), conn, params=params or {})
    except Exception:
        return pd.DataFrame()


# =========================================================
# SCHEMA INITIALISATION (SOVEREIGN LOGISTICS STACK v17)
# =========================================================

def init_db() -> None:
    """
    Creates all core logistics tables in their modern schema.
    This version preserves:
    - Fleet Registry
    - Missions
    - Dispatch Journal
    - Simulation Engine RFQs
    """

    tables = [

        # -------------------------
        # FLEET (RESTORED ORIGINAL)
        # -------------------------
        """
        CREATE TABLE IF NOT EXISTS log_vehicles (
            reg_number TEXT PRIMARY KEY,
            type TEXT,
            make_model TEXT,
            fuel_rating REAL,
            status TEXT DEFAULT 'Idle',
            driver_name TEXT,
            location TEXT DEFAULT 'Depot'
        );
        """,

        # -------------------------
        # MISSIONS
        # -------------------------
        """
        CREATE TABLE IF NOT EXISTS log_missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_name TEXT,
            reg_number TEXT,
            driver_name TEXT,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            status TEXT DEFAULT 'Staged',
            location TEXT,
            notes TEXT
        );
        """,

        # -------------------------
        # DISPATCH JOURNAL
        # -------------------------
        """
        CREATE TABLE IF NOT EXISTS log_dispatch_journal (
            trip_id TEXT PRIMARY KEY,
            rfq_ref TEXT,
            truck_reg TEXT,
            driver TEXT,
            status TEXT,
            tare_weight REAL,
            gross_weight REAL,
            net_weight REAL,
            ticket_no TEXT,
            start_time DATETIME,
            end_time DATETIME
        );
        """,

        # -------------------------
        # RFQs (MATCHES SIMULATION ENGINE)
        # -------------------------
        """
        CREATE TABLE IF NOT EXISTS ind_rfqs (
            rfq_id TEXT PRIMARY KEY,
            client TEXT,
            origin TEXT,
            destination TEXT,
            tons REAL,
            commodity TEXT,
            status TEXT,
            created_at DATETIME
        );
        """,

        # -------------------------
        # RISK
        # -------------------------
        """
        CREATE TABLE IF NOT EXISTS log_risk_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            type TEXT,
            severity TEXT,
            description TEXT,
            cost_impact REAL,
            status TEXT
        );
        """,

        # -------------------------
        # COMPLIANCE
        # -------------------------
        """
        CREATE TABLE IF NOT EXISTS log_compliance_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT,
            ref_number TEXT,
            expiry_date DATE,
            status TEXT
        );
        """
    ]

    for stmt in tables:
        run_query(stmt)

    print("[DB INIT] Sovereign Logistics Schema Loaded (v17)")
