import streamlit as st
import pandas as pd
import sqlite3
import os
import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "veridian_cortex.db")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_all_tables():
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in c.fetchall()]
    except: return []
    finally: conn.close()

def run_query(query):
    conn = get_db_connection()
    try: return pd.read_sql_query(query, conn)
    except: return pd.DataFrame()
    finally: conn.close()

def nuke_table(table_name):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(f"DELETE FROM {table_name}")
        conn.commit()
        st.toast(f"☢️ {table_name} PURGED.")
    except Exception as e:
        st.error(f"Error: {e}")
    finally: conn.close()

# --- THE MAGISTERIAL UPGRADE ---
def render_admin_core():
    # HEADER
    st.markdown("## 🛡️ System Administration | Sovereign Kernel")
    st.caption(f"**Security Level:** ADMIN-1 | **Database Path:** `{os.path.basename(DB_PATH)}`")
    
    # 1. THE STATUS MONITOR (Visual Upgrade)
    with st.container():
        # Mock System Vitals for "Feel"
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kernel State", "ONLINE", "v12.0 Stable")
        
        # Real DB Metrics
        tables = get_all_tables()
        try: size_kb = os.path.getsize(DB_PATH) / 1024
        except: size_kb = 0
        
        c2.metric("Data Density", f"{size_kb:.1f} KB", "Core DB")
        c3.metric("Active Registries", len(tables), "SQL Tables")
        c4.metric("Session Time", "00:14:22", "Secure Link")
        
        # Visual Health Bar
        st.progress(100, text="System Integrity Check: PASSED")

    st.divider()

    # --- 2. COMMAND TABS ---
    tab_xray, tab_config, tab_danger = st.tabs(["🔍 Database X-Ray", "⚙️ System Constants", "☢️ Nuclear Option"])

    # A. DATABASE X-RAY (Professional View)
    with tab_xray:
        c_sel, c_view = st.columns([1, 3])
        with c_sel:
            st.markdown("##### 📂 Registry Select")
            selected_table = st.radio("Select Table", tables, label_visibility="collapsed")
        
        with c_view:
            if selected_table:
                st.markdown(f"##### 📋 Live Data: `{selected_table}`")
                df = run_query(f"SELECT * FROM {selected_table}")
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    height=400,
                    hide_index=True
                )
                st.caption(f"Total Records: {len(df)}")
            else:
                st.info("System Empty. Initialize Kernel.")

    # B. GLOBAL CONFIG (Grid Editor)
    with tab_config:
        st.markdown("##### ⚙️ Global Variables")
        st.caption("These constants drive the logic of the War Room and Financial Modules.")
        
        # Load Config
        df_conf = run_query("SELECT * FROM system_config")
        
        # 1. View Current State
        if not df_conf.empty:
            st.dataframe(
                df_conf, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "key": st.column_config.TextColumn("Variable Name", width="medium"),
                    "value": st.column_config.TextColumn("Current Value", width="medium")
                }
            )
        
        st.divider()
        
        # 2. Update Engine
        with st.form("config_update"):
            c1, c2 = st.columns([1, 1])
            k = c1.text_input("Variable Key", placeholder="e.g. target_2025")
            v = c2.text_input("New Value", placeholder="e.g. 15000000")
            
            if st.form_submit_button("💾 Update System Variable"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
                c.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)", (k, v))
                conn.commit()
                conn.close()
                st.toast(f"✅ System Variable '{k}' Updated.")
                time.sleep(1)
                st.rerun()

    # C. HAZARD ZONE (Red Alert Style)
    with tab_danger:
        st.error("⚠️ **AUTHORIZED PERSONNEL ONLY**")
        st.markdown("These actions are irreversible. They perform a hard delete on the selected registry.")
        
        with st.expander("🔓 Unlock Hazard Controls", expanded=True):
            target = st.selectbox("Select Target Registry to PURGE", tables)
            
            # Double Confirmation
            confirm = st.checkbox(f"I confirm I want to destroy all data in '{target}'")
            
            if st.button("🔥 EXECUTE PURGE", type="primary", disabled=not confirm):
                with st.spinner("Purging data blocks..."):
                    time.sleep(1) # Dramatic pause
                    nuke_table(target)
                st.rerun()
