import sys
import os
import streamlit as st

# --- PATH FIXER ---
# 1. Get the directory where THIS file (app.py) lives
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up 3 levels to reach the project root ('project_cortex')
#    Level 1: ../ (industrial)
#    Level 2: ../../ (modules)
#    Level 3: ../../../ (project_cortex) -> This is what we want!
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))

# 3. Add to Python Path so 'import modules' works
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ------------------

from modules.industrial.Sturrock_Vertical.ui import render_sturrock_dashboard

st.set_page_config(
    page_title="Sturrock & Robson | Federal Console",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_sturrock_dashboard()