# diagnostic.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect
import os

def run_system_probe():
    st.set_page_config(page_title="System Probe", layout="wide")
    st.markdown("## 🩺 Sovereign System Probe")
    st.caption("Deep Diagnostic: Database Schema vs. Application Logic")
    
    # 1. CONNECT TO LIVE KERNEL
    # We use dynamic pathing to find the DB in the same folder
    db_path = os.path.join(os.getcwd(), "cortex_live.db")
    
    st.info(f"Targeting Database: `{db_path}`")
    
    if not os.path.exists(db_path):
        st.error("❌ CRITICAL: Database file not found!")
        st.stop()
        
    engine = create_engine(f'sqlite:///{db_path}')
    
    c1, c2 = st.columns(2)
    
    # 2. PROBE THE FLEET TABLE
    with c1:
        st.subheader("🚛 Fleet Database Schema")
        inspector = inspect(engine)
        
        if inspector.has_table("log_vehicles"):
            columns = [c['name'] for c in inspector.get_columns("log_vehicles")]
            
            # THE CHECKLIST
            required = ['reg_number', 'status', 'max_tons', 'hazchem_compliant']
            report = []
            missing_critical = False
            
            for req in required:
                if req in columns:
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL (MISSING)"
                    missing_critical = True
                report.append({"Column": req, "Status": status})
            
            st.dataframe(pd.DataFrame(report), hide_index=True, use_container_width=True)
            
            if missing_critical:
                st.error("🚨 DIAGNOSIS: The database is missing Physics columns.")
                st.markdown("""
                **Why is the view inert?**
                The `fleet.py` view is trying to read `max_tons` and `hazchem_compliant`, but they do not exist in the database table. 
                
                **The Fix:**
                1. Ensure `models.py` has the new columns.
                2. Go to **Dispatch Tab** -> **Inject Simulation Data** to force a schema rebuild.
                """)
            else:
                st.success("✅ Schema is Healthy. The columns exist.")
                
        else:
            st.error("❌ Table 'log_vehicles' NOT FOUND.")

    # 3. PROBE THE DATA
    with c2:
        st.subheader("📊 Live Data Sample")
        try:
            if inspector.has_table("log_vehicles"):
                df = pd.read_sql("SELECT * FROM log_vehicles LIMIT 3", engine)
                if not df.empty:
                    st.dataframe(df)
                    st.info(f"Total Rows: {len(pd.read_sql('SELECT * FROM log_vehicles', engine))}")
                else:
                    st.warning("Table exists but is EMPTY.")
            else:
                st.warning("Cannot read data: Table missing.")
        except Exception as e:
            st.error(f"Read Error: {e}")

if __name__ == "__main__":
    run_system_probe()
