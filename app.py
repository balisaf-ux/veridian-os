import streamlit as st
import os
import sys
import time

# --- IMPORTS (DEPENDENCIES) ---
# This links the "Engine Room" (dashboard.py) to the main switchboard.
try:
    from modules.admin.dashboard import render_admin_core
    # Security Import (Ensure modules/security/auth.py exists)
    from modules.security.auth import login_user 
except ImportError:
    # Fallback prevents crash if security module is missing during setup
    def login_user(u, p): return {"username": "Admin", "role": "Sovereign", "modules": "UNIVERSAL"}

# --- 1. SYSTEM CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(
    page_title="MAIS | Sovereign Command",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed at launch for Login Screen focus
)

# --- 2. MAGISTERIAL VISUAL TEXTURE (CSS INJECTION) ---
st.markdown("""
    <style>
    /* GLOBAL DARK NAVY THEME */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* SIDEBAR & METRICS */
    section[data-testid="stSidebar"] { background-color: #161920; border-right: 1px solid #333; }
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #333; border-radius: 4px; padding: 10px; }
    div[data-testid="stMetricValue"] { color: #d4af37 !important; } /* Gold Data */
    
    /* HEADERS & ACCENTS */
    h1, h2, h3 { color: #d4af37 !important; font-family: 'Segoe UI', sans-serif; letter-spacing: 1px; }
    
    /* INPUTS & BUTTONS */
    .stTextInput > div > div > input { background-color: #0e1117; color: #fff; border: 1px solid #444; }
    .stTextInput > div > div > input:focus { border-color: #d4af37; }
    div.stButton > button { background-color: #d4af37; color: #000; border: none; font-weight: bold; }
    div.stButton > button:hover { background-color: #fff; color: #000; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SOVEREIGN BOOTLOADER ---
# Forces Python to see the root 'project_cortex' folder as the package home.
sys.path.append(os.getcwd())

# --- 4. KERNEL INITIALIZATION ---
try:
    from modules.core.db_manager import init_db
    init_db()
except ImportError as e:
    # Non-blocking error (allows app to run even if DB init fails momentarily)
    print(f"⚠️ KERNEL WARNING: {e}")

# --- 5. GATEKEEPER PROTOCOL (SECURITY LAYER) ---
def run_gatekeeper():
    """Intercepts traffic. Returns User Session if authenticated."""
    if "user_session" not in st.session_state:
        st.session_state["user_session"] = None

    if st.session_state["user_session"]:
        return st.session_state["user_session"]

    # --- LOGIN PORTAL UI ---
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write(""); st.write("")
        st.markdown("<h1 style='text-align: center; color: #d4af37;'>🦅 MAIS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>MAGISTERIAL AI SYSTEMS | v16.8</p>", unsafe_allow_html=True)
        
        tab_login, tab_req = st.tabs(["🔑 Command Login", "📝 Request Access"])
        
        with tab_login:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Initialize Uplink", use_container_width=True):
                    user = login_user(u, p)
                    if user:
                        st.session_state["user_session"] = user
                        st.toast("Identity Verified. Accessing Core...", icon="🦅")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("🚫 Access Denied")
        
        with tab_req:
            st.info("For Tier-1 Procurement Executives.")
            st.text_input("Corporate Email")
            if st.button("Request Verification", use_container_width=True):
                st.success("Request Transmitted to Sovereign Command.")

    st.stop() # HALT APP EXECUTION HERE

# ACTIVATE GATES
current_user = run_gatekeeper()

# --- 6. MAIN APPLICATION ROUTER (YOUR BASELINE) ---
def main():
    # --- SIDEBAR: EXECUTIVE COMMAND ---
    with st.sidebar:
        st.title("MAIS | OS")
        st.caption(f"User: {current_user['username']} | Role: {current_user['role']}")
        st.markdown("---")
        
        # Determine Menu Options based on Role
        # If user has "UNIVERSAL" access, they see everything.
        all_options = [
            "Admin Core", 
            "Magisterial Mercantile",
            "Magisterial Trade",
            "Retail Operations",
            "War Room (Prospecting)", 
            "Logistics Cloud",
            "Industrial Portal (Sourcing)",
            "Financial Control"
        ]
        
        # RBAC Filtering (Optional: You can enable strict filtering here later)
        if current_user.get("modules") == "UNIVERSAL":
            available_modules = all_options
        else:
            # Fallback for now to show all, or filter if you implemented the list in auth.py
            available_modules = all_options 

        menu = st.radio("Select Command Module", available_modules)
        
        st.markdown("---")
        if st.button("🔒 Log Out"):
            st.session_state["user_session"] = None
            st.rerun()

    # --- MAIN DECK: ROUTING LOGIC ---
    
    # A. FINANCIAL CONTROL
    if menu == "Financial Control":
        try:
            from modules.finance.app import render_finance_vertical
            render_finance_vertical()
        except Exception as e: st.error(f"⚠️ Finance Module Crash: {e}")
            
    # B. LOGISTICS
    elif menu == "Logistics Cloud":            
        try:
            from modules.logistics.app import render_logistics_vertical
            render_logistics_vertical()
        except Exception as e: st.error(f"⚠️ Logistics Module Crash: {e}")

    # C. MAGISTERIAL MERCANTILE
    elif menu == "Magisterial Mercantile":
        try:
            from modules.mercantile.app import render_mercantile_vertical
            render_mercantile_vertical()
        except ImportError: st.error("⚠️ Mercantile Module Not Found.")
        except Exception as e: st.error(f"⚠️ Mercantile Module Crash: {e}")

    # D. MAGISTERIAL TRADE
    elif menu == "Magisterial Trade":
        try:
            from modules.trade.app import render_trade_vertical
            render_trade_vertical()
        except Exception as e: st.error(f"⚠️ Trade Module Crash: {e}")

    # E. RETAIL OPERATIONS
    elif menu == "Retail Operations":
        try:
            from modules.retail.app import render_retail_vertical
            render_retail_vertical()
        except ImportError: st.error("⚠️ Retail Module Missing.")
        except Exception as e: st.error(f"⚠️ Retail Module Crash: {e}")

    # F. WAR ROOM
    elif menu == "War Room (Prospecting)":
        try:
            from modules.prospecting.app import render_prospecting_vertical
            render_prospecting_vertical()
        except Exception as e: st.error(f"⚠️ War Room Crash: {e}")

    # G. INDUSTRIAL PORTAL
    elif menu == "Industrial Portal (Sourcing)":
        try:
            from modules.industrial.app import render_industrial_vertical
            render_industrial_vertical()
        except ImportError: st.error("⚠️ Industrial Module Missing.")
        except Exception as e: st.error(f"⚠️ Industrial Portal Crash: {e}")

    # H. ADMIN CORE
    elif menu == "Admin Core":
        render_admin_core()

if __name__ == "__main__":
    main()
