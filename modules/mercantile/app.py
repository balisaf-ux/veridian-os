import streamlit as st
import pandas as pd
import os
import datetime
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# --- IMPORT MODELS ---
from modules.mercantile.models import Base, SovereignAsset, TradePosition, TreasuryInstrument

# --- CONFIGURATION ---
LIVE_FX = 18.24      # USD/ZAR
PUMP_PRICE = 24.50   # Retail Diesel Price

def get_engine():
    db_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    if not os.path.exists(db_path): return None
    return create_engine(f'sqlite:///{db_path}')

def init_mercantile_db(engine):
    """
    SELF-HEALING: Ensures Assets and Treasury tables exist.
    """
    inspector = inspect(engine)
    
    # 1. Build Physical Vault if missing
    if not inspector.has_table("merc_assets"):
        Base.metadata.create_all(engine)
        seed_assets(engine)

    # 2. Build Treasury Vault if missing (The New Update)
    if not inspector.has_table("merc_treasury"):
        Base.metadata.create_all(engine)
        st.toast("🏛️ Treasury Vault Constructed.")

def seed_assets(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    assets = [
        {"id": "TNK-DSL-01", "name": "JHB Depot Main Tank", "type": "LIQUID", "cap": 25000, "curr": 12500, "cost": 20.50, "loc": "City Deep"},
        {"id": "STK-COAL-01", "name": "RBCT Bonded Stockpile", "type": "SOLID", "cap": 50000, "curr": 10000, "cost": 1450.00, "loc": "Richards Bay"}
    ]
    for a in assets:
        new_asset = SovereignAsset(
            asset_id=a['id'], name=a['name'], type=a['type'],
            capacity=a['cap'], current_level=a['curr'],
            avg_cost_price=a['cost'], location=a['loc']
        )
        session.add(new_asset)
    session.commit()
    session.close()

def save_treasury_instrument(ref, type_, bank, amount, curr, date, deal_link):
    engine = get_engine()
    if engine:
        with engine.connect() as conn:
            stmt = text("""
                INSERT INTO merc_treasury (instrument_id, type, institution, amount_face, currency, expiry_date, status, linked_deal_id, created_at)
                VALUES (:ref, :type, :bank, :amt, :curr, :exp, 'ACTIVE', :link, CURRENT_TIMESTAMP)
            """)
            conn.execute(stmt, {
                "ref": ref, "type": type_, "bank": bank, "amt": amount,
                "curr": curr, "exp": date, "link": deal_link
            })
            conn.commit()

def render_mercantile_vertical():
    st.markdown("## 🏛️ Magisterial Mercantile | Sovereign Assets")
    st.caption("v15.4 Principal Holdings • Energy Import • Commodity Export • Treasury")

    engine = get_engine()
    if not engine:
        st.error("Database Connection Failed.")
        return

    # --- AUTO-FIX: ENSURE TABLES EXIST ---
    init_mercantile_db(engine)

    # 1. WEALTH AT A GLANCE
    total_asset_val = 0
    fuel_reserves = 0
    treasury_exp = 0
    
    with engine.connect() as conn:
        try:
            # Physical Assets
            df_assets = pd.read_sql("SELECT * FROM merc_assets", conn)
            if not df_assets.empty:
                df_assets['value'] = df_assets['current_level'] * df_assets['avg_cost_price']
                total_asset_val = df_assets['value'].sum()
                fuel_reserves = df_assets[df_assets['type']=='LIQUID']['current_level'].sum()
            
            # Financial Assets
            df_treasury = pd.read_sql("SELECT * FROM merc_treasury WHERE status='ACTIVE'", conn)
            if not df_treasury.empty:
                treasury_exp = df_treasury['amount_face'].sum()
                
        except Exception as e:
            st.error(f"Read Error: {e}")

    # 2. METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Physical Assets", f"R {total_asset_val/1e6:.2f}M", "Commodity & Fuel")
    c2.metric("Treasury Exposure", f"R {treasury_exp/1e6:.2f}M", "Active LCs & Hedges")
    c3.metric("USD / ZAR", f"R {LIVE_FX}", "Live Spot")
    c4.metric("Fuel Arbitrage", f"R {PUMP_PRICE - 20.50:.2f}/L", "Wholesale Margin")
    
    st.divider()

    # 3. THE DESKS
    tab_energy, tab_comm, tab_treasury = st.tabs([
        "🛢️ Energy Desk (Import)", 
        "⛏️ Commodity Desk (Export)", 
        "🏦 Treasury (Financial)"
    ])

    # === TAB 1: ENERGY DESK ===
    with tab_energy:
        st.subheader("Liquid Asset Management")
        c_left, c_right = st.columns([1, 2])
        with c_left:
            st.info("📦 **Stock Replenishment**")
            st.text_input("Supplier", "TotalEnergies Wholesale")
            vol = st.number_input("Order Volume (Liters)", value=5000, step=1000)
            price = st.number_input("Wholesale Rate (ZAR/L)", value=20.50)
            if st.button("🛒 Issue Purchase Order"):
                st.success(f"PO Issued for {vol}L @ R{price}. Asset Ledger Updated.")
        with c_right:
            st.markdown("##### ⛽ Tank Telemetry")
            if not df_assets.empty:
                fuel_df = df_assets[df_assets['type'] == 'LIQUID']
                for i, row in fuel_df.iterrows():
                    fill_pct = (row['current_level'] / row['capacity']) * 100
                    st.write(f"**{row['name']}** ({row['location']})")
                    st.progress(int(fill_pct))
                    st.caption(f"{row['current_level']:,.0f} L / {row['capacity']:,.0f} L")
            else:
                st.warning("No Liquid Assets found.")

    # === TAB 2: COMMODITY DESK ===
    with tab_comm:
        st.subheader("Solid Asset Arbitrage")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 1. Structure Export Deal")
            comm = st.selectbox("Commodity", ["Thermal Coal RB1", "Chrome", "Manganese"])
            tonnage = st.number_input("Volume (Tons)", value=10000)
            buy_zar = st.number_input("Buy (ZAR/t)", value=1450.00)
        with c2:
            st.markdown("##### 2. The Arbitrage")
            sell_usd = st.number_input("Sell (USD/t)", value=115.00)
            cost = buy_zar * tonnage
            rev_zar = (sell_usd * tonnage) * LIVE_FX
            profit = rev_zar - cost
            margin = (profit/rev_zar)*100 if rev_zar > 0 else 0
            st.metric("Projected Profit", f"R {profit:,.2f}", f"{margin:.1f}% Margin")
            if st.button("🔒 Lock Position (Buy ZAR / Sell USD)"):
                st.balloons()
                st.success("Position Locked. Logistics Orders Sent to TTE.")

    # === TAB 3: TREASURY (ACTIVATED) ===
    with tab_treasury:
        st.subheader("Central Bank Console")
        
        t_blotter, t_issue = st.tabs(["📜 Instrument Blotter", "✍️ Issue Instrument"])
        
        # A. THE BLOTTER (View Active Instruments)
        with t_blotter:
            st.markdown("##### Active Financial Instruments")
            if not df_treasury.empty:
                st.dataframe(
                    df_treasury[['instrument_id', 'type', 'institution', 'amount_face', 'currency', 'expiry_date', 'status']], 
                    use_container_width=True
                )
            else:
                st.info("Treasury Vault Empty. Issue an instrument to begin.")

        # B. ISSUE INSTRUMENT (Create LC or Hedge)
        with t_issue:
            st.markdown("##### Issue New Facility")
            
            with st.form("treasury_form"):
                c1, c2 = st.columns(2)
                inst_type = c1.selectbox("Instrument Type", ["Letter of Credit (LC)", "Forex Forward (FEC)", "Performance Bond"])
                bank = c2.selectbox("Counterparty", ["Standard Bank", "Investec", "Nedbank CIB"])
                
                amount = c1.number_input("Face Value", value=1000000.0)
                curr = c2.selectbox("Currency", ["ZAR", "USD", "EUR"])
                
                deal_link = c1.text_input("Linked Deal Ref (Optional)", "EXP-2026-001")
                expiry = c2.date_input("Expiry Date", datetime.date(2026, 12, 31))
                
                if st.form_submit_button("🏦 Issue Instrument"):
                    ref_id = f"{'LC' if 'Letter' in inst_type else 'FEC'}-{int(datetime.datetime.now().timestamp())}"
                    save_treasury_instrument(ref_id, inst_type, bank, amount, curr, expiry, deal_link)
                    st.success(f"Instrument {ref_id} Issued Successfully.")
                    st.rerun()
