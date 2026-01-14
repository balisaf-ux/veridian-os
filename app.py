import streamlit as st
import os
import sys

# --- IMPORTS ---
# This links the "Engine Room" (dashboard.py) to the main switchboard.
from modules.admin.dashboard import render_admin_core

# --- SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="VAS | Sovereign OS",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. SOVEREIGN BOOTLOADER ---
# Forces Python to see the root 'project_cortex' folder as the package home.
sys.path.append(os.getcwd())

# --- 2. KERNEL INITIALIZATION ---
try:
    from modules.core.db_manager import init_db
    # Initialize the Sovereign Kernel (SQL Tables) immediately on boot
    init_db()
except ImportError as e:
    st.error(f"❌ KERNEL FAILURE: {e}")
    st.stop()

# --- 3. MAIN APPLICATION ROUTER ---
def main():
    # --- SIDEBAR: EXECUTIVE COMMAND ---
    with st.sidebar:
        st.title("VAS | OS")
        st.caption("v15.6 Sovereign Command") 
        st.markdown("---")
        
        # The Navigation Menu
        # STRATEGY: Mercantile (Principal) sits above Trade (Broker) & Operations (Logistics)
        menu = st.radio(
            "Select Command Module",
            [
                "Admin Core", 
                "Magisterial Mercantile",
                "Magisterial Trade",
                "Retail Operations",
                "War Room (Prospecting)", 
                "Logistics Cloud",            # <--- LABEL SET HERE
                "Industrial Portal (Sourcing)",
                "Financial Control"
            ]
        )
        
        st.markdown("---")
        st.caption("System Status: **NOMINAL**")
        if st.button("♻️ Reboot System"):
            st.rerun()

    # --- MAIN DECK: ROUTING LOGIC ---
    
    # A. FINANCIAL CONTROL (The Scoreboard)
    if menu == "Financial Control":
        try:
            from modules.finance.app import render_finance_vertical
            render_finance_vertical()
        except Exception as e:
            st.error(f"⚠️ Finance Module Crash: {e}")
            
    # B. LOGISTICS (The Expense Engine)
    elif menu == "Logistics Cloud":           # <--- FIXED: NOW MATCHES THE MENU LABEL
        try:
            from modules.logistics.app import render_logistics_vertical
            render_logistics_vertical()
        except Exception as e:
            st.error(f"⚠️ Logistics Module Crash: {e}")

    # C. MAGISTERIAL MERCANTILE (The Principal / Assets)
    elif menu == "Magisterial Mercantile":
        try:
            from modules.mercantile.app import render_mercantile_vertical
            render_mercantile_vertical()
        except ImportError:
             st.error("⚠️ Mercantile Module Not Found. Ensure 'modules/mercantile/app.py' exists.")
        except Exception as e:
            st.error(f"⚠️ Mercantile Module Crash: {e}")

    # D. MAGISTERIAL TRADE (The Broker / Pipeline)
    elif menu == "Magisterial Trade":
        try:
            from modules.trade.app import render_trade_vertical
            render_trade_vertical()
        except Exception as e:
            st.error(f"⚠️ Trade Module Crash: {e}")

    # E. RETAIL OPERATIONS (FMCG Command)
    elif menu == "Retail Operations":
        try:
            from modules.retail.app import render_retail_vertical
            render_retail_vertical()
        except ImportError:
            st.error("⚠️ Retail Module Missing: Ensure 'modules/retail/app.py' is created.")
        except Exception as e:
            st.error(f"⚠️ Retail Module Crash: {e}")

    # F. WAR ROOM (The Hunter)
    elif menu == "War Room (Prospecting)":
        try:
            from modules.prospecting.app import render_prospecting_vertical
            render_prospecting_vertical()
        except Exception as e:
            st.error(f"⚠️ War Room Crash: {e}")

    # G. INDUSTRIAL PORTAL (The Sourcing Nexus)
    elif menu == "Industrial Portal (Sourcing)":
        try:
            from modules.industrial.app import render_industrial_vertical
            render_industrial_vertical()
        except ImportError:
            st.error("⚠️ Industrial Module Missing: Ensure 'modules/industrial/app.py' is created.")
        except Exception as e:
            st.error(f"⚠️ Industrial Portal Crash: {e}")

    # H. ADMIN CORE (The Engine Room)
    elif menu == "Admin Core":
        render_admin_core()

if __name__ == "__main__":
    main()
