import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

# --- CONFIGURATION: LOGISTICS CORRIDORS ---
CORRIDORS = {
    "N3: DBN Port -> JHB City Deep": {"dist": 570, "tolls": 2850, "risk": "Medium"},
    "N1: CPT -> JHB": {"dist": 1400, "tolls": 1900, "risk": "Low"},
    "N4: Maputo -> Witbank": {"dist": 380, "tolls": 1200, "risk": "High"},
    "N1: JHB -> Musina (Border)": {"dist": 520, "tolls": 1450, "risk": "Medium"},
    "R33: Mpumalanga -> Richards Bay": {"dist": 610, "tolls": 850, "risk": "High (Potholes)"}
}

DIESEL_PRICE = 24.50 

def get_engine():
    db_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    if not os.path.exists(db_path):
        return None
    return create_engine(f'sqlite:///{db_path}')

def calculate_route_economics(route_name, truck_efficiency):
    data = CORRIDORS[route_name]
    dist = data['dist']
    tolls = data['tolls']
    
    # Fuel Calculation: (Distance / 100) * Efficiency * Price
    liters_needed = (dist / 100) * truck_efficiency
    fuel_cost = liters_needed * DIESEL_PRICE
    
    total_cost = fuel_cost + tolls + 1500 # Overheads
    break_even_rate = total_cost * 1.15 # 15% Margin
    
    return {
        "distance": dist,
        "fuel_cost": fuel_cost,
        "toll_cost": tolls,
        "total_ops_cost": total_cost,
        "suggested_rate": break_even_rate,
        "risk": data['risk']
    }

def render_logistics_vertical():
    st.markdown("## 🚛 Logistics Command | TTE")
    st.caption("v14.2 Route Planning • Fleet Orchestration • Cost Analytics")

    engine = get_engine()
    
    # Live Fleet Query
    fleet_count = 0
    active_count = 0
    df_fleet = pd.DataFrame()
    
    if engine:
        try:
            with engine.connect() as conn:
                df_fleet = pd.read_sql("SELECT * FROM log_vehicles", conn)
                if not df_fleet.empty:
                    fleet_count = len(df_fleet)
                    active_count = len(df_fleet[df_fleet['status'] == 'Active'])
        except:
            pass

    # METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Fleet", f"{fleet_count}", "Vehicles")
    c2.metric("Active Units", f"{active_count}", "On Road")
    c3.metric("Diesel Price", f"R {DIESEL_PRICE}", "Inland 50ppm")
    c4.metric("Safety Score", "98%", "Nominal")

    st.markdown("---")

    tab_planner, tab_fleet, tab_live = st.tabs([
        "🗺️ Route Planner", 
        "🚛 Fleet Registry", 
        "📡 Control Tower"
    ])

    # --- TAB 1: ROUTE PLANNER ---
    with tab_planner:
        st.subheader("Route Feasibility & Costing")
        
        col_input, col_stats = st.columns([1, 2])
        
        with col_input:
            st.markdown("#### 1. Mission Parameters")
            selected_route = st.selectbox("Select Corridor", list(CORRIDORS.keys()))
            
            # Smart Selection: Pick from YOUR fleet or use Generic
            truck_options = ["Generic Interlink (38L/100km)"]
            if not df_fleet.empty:
                truck_options += [f"{r['reg_number']} ({r['type']})" for i, r in df_fleet.iterrows()]
            
            selected_truck_str = st.selectbox("Assign Vehicle", truck_options)
            
            # Calculate Logic
            efficiency = 38.0
            if "Generic" not in selected_truck_str and not df_fleet.empty:
                reg = selected_truck_str.split(" (")[0]
                truck_row = df_fleet[df_fleet['reg_number'] == reg]
                if not truck_row.empty:
                    efficiency = float(truck_row.iloc[0]['fuel_rating'])
            
            st.info(f"Efficiency: **{efficiency} L/100km**")
            
        with col_stats:
            st.markdown("#### 2. Mission Economics")
            eco = calculate_route_economics(selected_route, efficiency)
            
            ec1, ec2, ec3 = st.columns(3)
            ec1.metric("Distance", f"{eco['distance']} km", eco['risk'])
            ec2.metric("Fuel Cost", f"R {eco['fuel_cost']:,.0f}", f"{eco['fuel_cost']/eco['distance']:.2f} R/km")
            ec3.metric("Toll Fees", f"R {eco['toll_cost']:,.0f}", "Est.")
            
            st.divider()
            
            st.write(f"💰 **Break-Even Cost:** R {eco['total_ops_cost']:,.2f}")
            
            # Interactive Quoting
            target_rate = st.number_input("Quoted Rate (ZAR)", value=float(int(eco['suggested_rate'])))
            profit = target_rate - eco['total_ops_cost']
            
            if profit > 0:
                st.success(f"✅ Projected Profit: R {profit:,.2f}")
            else:
                st.error(f"⚠️ Loss Warning: -R {abs(profit):,.2f}")

            if st.button("🚀 Dispatch Fleet"):
                st.toast(f"Dispatch sent to {selected_truck_str}")

    # --- TAB 2: FLEET REGISTRY ---
    with tab_fleet:
        st.subheader("Asset Management")
        if not df_fleet.empty:
            st.dataframe(df_fleet[['reg_number', 'type', 'make', 'status', 'location', 'driver_name']], use_container_width=True)
        else:
            st.info("No Fleet Data. Run 'activate_fleet.py' to restore legacy data.")

    # --- TAB 3: LIVE OPS (Preserving your Map Nodes) ---
    with tab_live:
        st.subheader("Network Status")
        # Restoring the Node Data from your old models.py for visualization
        map_data = pd.DataFrame([
            {'lat': -26.2041, 'lon': 28.0473, 'name': 'JHB Hub'},
            {'lat': -29.8587, 'lon': 31.0218, 'name': 'DBN Port'},
            {'lat': -33.9249, 'lon': 18.4241, 'name': 'CPT Port'},
            {'lat': -33.0292, 'lon': 27.8546, 'name': 'EL Factory'}
        ])
        st.map(map_data)
        st.caption("Live Telemetry: Active")
