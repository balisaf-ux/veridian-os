import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit.web.cli as stcli

def main():
    # Points to the app file we just built
    sr_app = os.path.join(
        ROOT, "modules", "industrial", "Sturrock_Vertical", "app.py"
    )
    
    # 1. Point to the app
    # 2. --global.developmentMode=false (Hides the "Deploy" button clutter)
    # 3. --server.runOnSave=true (Auto-updates if you tweak code live)
    sys.argv = [
        "streamlit", 
        "run", 
        sr_app, 
        "--global.developmentMode=false", 
        "--server.runOnSave=true"
    ]
    
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()