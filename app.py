# modules/logistics/db_utils.py

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# =========================================================
# MAIS VERTICAL METADATA
# =========================================================
VERTICAL = "Logistics Cloud"
SCHEMA_VERSION = 17

# =========================================================
# DATABASE CORE MODULE — SOVEREIGN LOGISTICS DB
# =========================================================
DB_URL = "sqlite:///fleet_data.db"

engine = create_engine(
    DB_URL,
    future=True,
    connect_args={"check_same_thread": False}
)

# =========================================================
# WRITE WRAPPER
# =========================================================
def run_query(query_str: str, params: dict | None = None) -> bool:
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
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query_str), conn, params=params or {})
    except Exception as e:
        st.error(f"Read Error: {e}")
        return pd.DataFrame()

# =========================================================
# DB HEALTH CHECK (MAIS-COMPATIBLE)
# =========================================================
def db_health():
    try:
        with engine.connect() as conn:
            tables = pd.read_sql(
                text("SELECT name FROM sqlite_master WHERE type='table'"),
                conn
            )
        return {"status": "OK", "tables": tables["name"].tolist()}
    except Exception as e:
        return {"status": "ERROR", "details": str(e)}

# =========================================================
# SCHEMA INITIALISATION (SOVEREIGN LOGISTICS STACK v17)
# =========================================================
def init_db() -> None:

    schema_statements = [

        # Fleet Registry
        """
        CREATE TABLE IF NOT EXISTS log_vehicles (
            reg_number TEXT PRIMARY KEY,
            type TEXT,
            make_model TEXT,
            fuel_rating REAL,
            status TEXT DEFAULT 'Idle',
            driver_name TEXT,
            location TEXT DEFAULT 'Depot',
            last_lat REAL,
            last_lon REAL
        );
        """,

        # Missions
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

        # Dispatch Journal
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

        # RFQs
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

        # Risk Incidents
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

        # Compliance Docs
        """
        CREATE TABLE IF NOT EXISTS log_compliance_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT,
            ref_number TEXT,
            expiry_date DATE,
            status TEXT
        );
        """,

        # GPS Pings
        """
        CREATE TABLE IF NOT EXISTS gps_pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_number TEXT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL,
            speed REAL,
            heading REAL,
            ignition INTEGER,
            signal_quality REAL,
            source TEXT
        );
        """
    ]

    for stmt in schema_statements:
        run_query(stmt)

    print(f"[DB INIT] {VERTICAL} Schema Loaded (v{SCHEMA_VERSION})")
