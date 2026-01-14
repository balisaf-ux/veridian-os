import sys
import os

print("--- FINANCE DIAGNOSTIC PROBE ---")
print(f"1. Working Directory: {os.getcwd()}")

# 1. TEST DEPENDENCIES
print("\n2. Testing External Libraries...")
try:
    import plotly.express as px
    print("   ✅ SUCCESS: Plotly is installed.")
except ImportError:
    print("   ❌ FATAL ERROR: Plotly is missing. Run 'pip install plotly'")

# 2. TEST KERNEL CONNECTION
print("\n3. Testing Kernel Functions...")
try:
    from modules.core.db_manager import save_journal_entry
    print("   ✅ SUCCESS: save_journal_entry found.")
except ImportError:
    print("   ❌ FATAL ERROR: save_journal_entry MISSING from db_manager.")

try:
    from modules.core.db_manager import init_chart_of_accounts
    print("   ✅ SUCCESS: init_chart_of_accounts found.")
except ImportError:
    print("   ❌ FATAL ERROR: init_chart_of_accounts MISSING from db_manager.")

# 3. TEST FINANCE MODULE LOAD
print("\n4. Attempting to Load Finance Vertical...")
try:
    from modules.finance import app as finance_app
    print("   ✅ SUCCESS: Finance Module loaded perfectly.")
except Exception as e:
    print(f"   ❌ CRASH DETECTED inside Finance Module: {e}")
    import traceback
    traceback.print_exc()

print("\n--- PROBE COMPLETE ---")
