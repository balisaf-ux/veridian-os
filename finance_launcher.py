import streamlit as st
import sys
import os

st.set_page_config(layout="wide")
st.title("🔧 Finance Direct Launcher (Diagnostic Mode)")

# 1. Force Python to see the root folder
sys.path.append(os.getcwd())

st.write("--- 1. IMPORTING MODULE ---")
# This will crash visibly if the file is broken
from modules.finance.app import render_finance_vertical
st.success("✅ Import Successful.")

st.write("--- 2. EXECUTING RENDER ---")
# This will crash visibly if the render logic is broken
render_finance_vertical()
st.success("✅ Render Successful.")
