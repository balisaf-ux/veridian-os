import streamlit as st
import os
import sys

# =========================================================
# 1. CORE DEPENDENCIES & IMPORTS
# =========================================================
try:
    from modules.admin.dashboard import render_admin_core
    from modules.security.auth import login_user
except ImportError:
    # Fail CLOSED by default — only explicit test backdoors allowed
    def login_user(u, p):
        # Optional: test-only guest backdoor for Logistics
        if u == "MAIS_GUEST_24H" and p == "LOGISTICS_PORTAL_2026":
            return {
                "username": "Guest_Procurement",
                "role": "External_Auditor",
                "modules": ["Logistics Cloud"]
            }
        # Optional: dev-only sovereign backdoor, guarded by env
        if (
            os.environ.get("MAIS_DEV_BACKDOOR") == "ENABLED"
            and u == "Balisa"
            and p == "MAIS_SOVEREIGN"
        ):
            return {
                "username": "Admin",
                "role": "Sovereign",
                "modules": ["UNIVERSAL"]
            }
        return None

sys.path.append(os.getcwd())

# =========================================================
# 2. ENVIRONMENT DETECTION
# =========================================================
is_cloud = (
    "streamlit.app" in st.query_params.get("url", [""])[0]
    or os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud"
)

# =========================================================
# 3. UI CONFIGURATION & AESTHETICS (WHITE / BLUE / RED / BLACK)
# =========================================================
st.set_page_config(
    page_title="MAIS | Magisterial AI Systems",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    :root { 
        --white: #FFFFFF;
        --black: #0F172A;
        --blue: #0F3D91;
        --blue-dark: #0D2F73;
        --blue-light: #E8EEF8;
        --red: #C1121F;
        --gray-light: #F8FAFC;
        --gray-border: #E2E8F0;
        --gray-text: #64748B;
    }

    .stApp { 
        background-color: var(--white) !important; 
        color: var(--black) !important;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        color: var(--black) !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    [data-testid="stForm"] {
        background: var(--gray-light) !important;
        border: 1px solid var(--gray-border) !important;
        border-radius: 10px !important;
        padding: 2rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .mono-label { 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 11px; 
        color: var(--gray-text); 
        font-weight: 700; 
        text-transform: uppercase;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background-color: var(--blue) !important;
        color: var(--white) !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.2rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px;
        transition: background-color 0.2s ease-in-out;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: var(--blue-dark) !important;
    }

    .stTabs [data-baseweb="tab-list"] { 
        border-bottom: 2px solid var(--gray-border) !important; 
    }

    .stTabs [aria-selected="true"] { 
        color: var(--blue) !important; 
        border-bottom: 3px solid var(--blue) !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="false"] {
        color: var(--gray-text) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--gray-light) !important;
        border-right: 1px solid var(--gray-border) !important;
    }

    section[data-testid="stSidebar"] h2 {
        color: var(--blue) !important;
        font-weight: 800 !important;
    }

    .stAlert {
        border-left: 4px solid var(--red) !important;
        border-radius: 4px !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--blue) !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricDelta"] {
        color: var(--red) !important;
    }

    hr, .stDivider {
        border-top: 1px solid var(--gray-border) !important;
    }

    input, textarea, select {
        border-radius: 6px !important;
        border: 1px solid var(--gray-border) !important;
    }

    input:focus, textarea:focus, select:focus {
        border: 1px solid var(--blue) !important;
        box-shadow: 0 0 0 1px var(--blue-light) !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 4. SECURITY GATEKEEPER
# =========================================================
def run_gatekeeper():
    if "user_session" not in st.session_state:
        st.session_state["user_session"] = None

    if st.session_state["user_session"]:
        return st.session_state["user_session"]

    # LOGIN UI
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;
        padding:1rem 0;margin-bottom:2rem;border-bottom:2px solid #0F3D91;">
            <div style="display:flex;align-items:center;gap:15px;">
                <span style="font-size:1.8rem;font-weight:900;color:#0F3D91;">MAIS</span>
                <div style="width:1px;height:20px;background:#CBD5E1;"></div>
                <span style="font-size:10px;color:#64748B;text-transform:uppercase;
                letter-spacing:2px;font-weight:600;">Corporate Portal</span>
            </div>
            <div style="display:flex;gap:20px;font-size:11px;font-weight:700;
            text-transform:uppercase;color:#0F172A;">
                <span>Trade</span><span>Logistics</span><span>Industrial</span><span>Retail</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;font-size:5rem;color:#0F3D91;'>MAIS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;letter-spacing:0.3em;color:#64748B; margin-top:-15px;font-weight:600;'>THE CORPORATE CORTEX</p>", unsafe_allow_html=True)

        tab_login, tab_req = st.tabs(["🔒 SECURE LOGIN", "📝 PORTAL ACCESS"])

        with tab_login:
            with st.form("login_form"):
                st.markdown("<div class='mono-label'>Neural Link ID</div>", unsafe_allow_html=True)
                u = st.text_input("", label_visibility="collapsed", placeholder="Username")
                st.markdown("<div class='mono-label'>Cipher Sequence</div>", unsafe_allow_html=True)
                p = st.text_input("", type="password", label_visibility="collapsed", placeholder="Password")
                
                if st.form_submit_button("INITIALIZE SEQUENCE", use_container_width=True):
                    user = login_user(u, p)
                    if user:
                        st.session_state["user_session"] = user
                        st.rerun()
                    else:
                        st.error("🚫 Access Denied")

        with tab_req:
            st.info("Verified Access required for Tier-1 Procurement Executives.")
            st.text_input("FULL NAME & TITLE")
            st.text_input("CORPORATE EMAIL")
            if st.button("REQUEST VERIFICATION", use_container_width=True):
                st.success("Request Transmitted to Sovereign Command.")

    st.stop()

# =========================================================
# 5. MAIN APPLICATION ENGINE
# =========================================================
def main():
    current_user = run_gatekeeper()
    role = current_user.get("role")

    # -------------------------------
    # PATH A — GUEST / CLOUD ACCESS
    # -------------------------------
    if is_cloud or role == "External_Auditor":
        st.markdown(
            "<style>section[data-testid='stSidebar']{display:none!important;}</style>",
            unsafe_allow_html=True
        )
        try:
            from modules.logistics.app import render_logistics_vertical
            render_logistics_vertical()
        except Exception as e:
            st.error(f"⚠️ Logistics Portal Error: {e}")
        return # FIREWALL: STOP EXECUTION HERE

    # -------------------------------
    # PATH B — SOVEREIGN ACCESS
    # -------------------------------
    with st.sidebar:
        st.markdown(f"<h2 style='color:#0F3D91;'>MAIS | OS</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:11px;color:#64748B;'>USER: {current_user['username']}</div>",
            unsafe_allow_html=True
        )
        st.markdown("---")

        sovereign_modules = [
            "Admin Core", "Magisterial Mercantile", "Magisterial Trade",
            "Retail Operations", "War Room (Prospecting)",
            "Logistics Cloud", "Industrial Portal (Sourcing)", "Financial Control"
        ]

        menu = st.radio("Select Command Module", sovereign_modules)

        st.markdown("---")
        if st.button("🔒 TERMINATE SESSION"):
            st.session_state["user_session"] = None
            st.rerun()

    # -------------------------------
    # ROUTING ENGINE (Sovereign Only)
    # -------------------------------
    try:
        if menu == "Financial Control":
            from modules.finance.app import render_finance_vertical
            render_finance_vertical()

        elif menu == "Logistics Cloud":
            from modules.logistics.app import render_logistics_vertical
            render_logistics_vertical()

        elif menu == "Magisterial Mercantile":
            from modules.mercantile.app import render_mercantile_vertical
            render_mercantile_vertical()

        elif menu == "Magisterial Trade":
            from modules.trade.app import render_trade_vertical
            render_trade_vertical()

        elif menu == "Retail Operations":
            from modules.retail.app import render_retail_vertical
            render_retail_vertical()

        elif menu == "War Room (Prospecting)":
            from modules.prospecting.app import render_prospecting_vertical
            render_prospecting_vertical()

        elif menu == "Industrial Portal (Sourcing)":
            from modules.industrial.app import render_industrial_vertical
            render_industrial_vertical()

        elif menu == "Admin Core":
            render_admin_core()

    except Exception as e:
        st.error(f"⚠️ Module Crash: {e}")


if __name__ == "__main__":
    main()
