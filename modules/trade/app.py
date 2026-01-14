import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import time
from modules.core.db_manager import (
    load_trades_to_dataframe, 
    save_trade_deal, 
    log_supplier_bid, 
    load_bids_to_dataframe,
    get_sku_details,
    get_logistics_rate,
    load_prospects_to_dataframe,
    save_strategic_target
)
from modules.trade.smart_compiler import SmartCompiler

# --- CONFIGURATION (Preserved) ---
BULK_COMMODITIES = ["Thermal Coal (RB1)", "Chrome (42%)", "Magnetite", "Diesel 50ppm"]
FMCG_CATALOG = [
    {"SKU": "VLV-001", "Product": "Brass Gate Valve 15mm", "Cost": 60.00, "Price": 85.00, "Stock": 5000, "Tier": "A"},
    {"SKU": "PNT-WHT-20", "Product": "Acrylic PVA White 20L", "Cost": 320.00, "Price": 450.00, "Stock": 800, "Tier": "B"},
    {"SKU": "CMT-42N", "Product": "Titan Cement 42.5N", "Cost": 80.00, "Price": 95.00, "Stock": 12000, "Tier": "A"},
    {"SKU": "STL-ANG-40", "Product": "Angle Iron 40x40x3mm", "Cost": 110.00, "Price": 165.00, "Stock": 200, "Tier": "C"}
]
SUPPLIERS = ["Makhado Logistics", "Vukanathi Industrial", "Ramatsobane Resources", "Glencore Xstrata"]

def render_trade_vertical():
    st.markdown("## ⚖️ Magisterial Trade | Unified Command")
    st.caption("v13.5 Hybrid: Heavy Industry & Retail Distribution")

    sector = st.radio("Select Trading Floor", 
                      ["🏭 Heavy Industry (Bulk Commodities)", 
                       "🏪 Retail Distribution (FMCG)", 
                       "💠 Sovereign Asset Transfer"], 
                      horizontal=True)
    st.divider()

    if sector == "🏭 Heavy Industry (Bulk Commodities)":
        render_bulk_floor()
    elif sector == "🏪 Retail Distribution (FMCG)":
        render_fmcg_floor()
    else:
        render_sovereign_transfer_floor()

# ==========================================
# MODE 3: SOVEREIGN ASSET TRANSFER (FULL BUILD)
# ==========================================
def render_sovereign_transfer_floor():
    st.subheader("💠 Sovereign Asset Acquisition")
    st.caption("Permanent Digital Infrastructure Transfer | ROI Forensics")
    
    tab_quote, tab_roi = st.tabs(["📜 Generation Engine", "📊 Margin Shield Analysis"])
    
    with tab_quote:
        st.markdown("#### 🚀 Generate Asset Acquisition Quote")
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Target Entity", value="TTE Mobility")
            fleet_size = st.number_input("Total Fleet Size (Units)", min_value=1, value=10)
        with c2:
            acq_fee = st.number_input("Acquisition Fee (ZAR)", value=250000.00)
            maint_fee = st.number_input("Monthly Maintenance (ZAR)", value=7500.00)

        if st.button("🏗️ COMPILE SOVEREIGN PDF", type="primary"):
            data_packet = {
                "ref": "MAIS-TTE-2026-001",
                "client": client_name,
                "system": "Veridian Cortex v14.0 Sovereign Kernel",
                "val_prop": f"Sovereign Transfer proposal for {client_name}..."
            }
            
            try:
                # 1. Get the BytesIO object from the hardened compiler
                pdf_buffer = SmartCompiler.generate_pdf_quote(data_packet)
                
                # 2. Extract the actual bytes for the download button
                st.download_button(
                    label="📂 Download Official PDF Quotation",
                    data=pdf_buffer.getvalue(), # <--- This will now work perfectly
                    file_name=f"MAIS_Sovereign_Quote_{client_name}.pdf",
                    mime="application/pdf"
                )
                st.success("Sovereign PDF Compiled successfully.")
            except Exception as e:
                st.error(f"Kernel Error: {str(e)}")
            
    with tab_roi:
        monthly_recovery = fleet_size * 12500
        annual_recovery = monthly_recovery * 12
        payback = acq_fee / monthly_recovery
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly Leakage Plugged", f"R {monthly_recovery:,.2f}")
        c2.metric("Annual Capital Shield", f"R {annual_recovery:,.2f}")
        c3.metric("Investment Payback", f"{payback:.1f} Months")

# ==========================================
# MODE 1: HEAVY INDUSTRY (Full Metrics Restored)
# ==========================================
def render_bulk_floor():
    st.subheader("🌋 Bulk Commodity Desk")
    tab_matrix, tab_deal, tab_market = st.tabs(["📊 Trade Matrix", "🦅 Deal Originator", "📡 Market Liquidity"])

    with tab_matrix:
        df_deals = load_trades_to_dataframe()
        if not df_deals.empty:
            bulk_deals = df_deals[df_deals['value'] > 50000] 
            c1, c2, c3 = st.columns(3)
            active_val = bulk_deals[bulk_deals['status'] != 'Signed']['value'].sum()
            vol_total = bulk_deals['volume'].sum()
            c1.metric("Pipeline Value", f"R {active_val:,.0f}")
            c2.metric("Committed Volume", f"{vol_total:,.0f} Tons")
            c3.metric("Active Deals", len(bulk_deals))
            st.dataframe(bulk_deals[['client_name', 'product', 'volume', 'value', 'stage']], use_container_width=True)
        else:
            st.info("No Active Bulk Deals.")

    with tab_deal:
        c1, c2 = st.columns(2)
        client = c1.text_input("Counterparty (Buyer)")
        product = c2.selectbox("Commodity", BULK_COMMODITIES)
        c3, c4 = st.columns(2)
        vol = c3.number_input("Volume (Tons)", step=1000.0, value=34000.0)
        price = c4.number_input("Price per Ton (ZAR)", step=50.0, value=1250.0)
        val = vol * price
        st.info(f"**Deal Value:** R {val:,.2f} | **Logistics:** Requires {int(vol/34)} x Interlinks")
        if st.button("💾 Lock Bulk Deal"):
            save_trade_deal(client, product, vol, val, "Open", "Negotiation")
            st.success("Deal Locked.")

    with tab_market:
        with st.expander("📡 Receive Supplier Bid", expanded=True):
            s1, s2 = st.columns(2)
            supplier = s1.selectbox("Supplier", SUPPLIERS)
            sku = s2.selectbox("Product (Bid)", BULK_COMMODITIES)
            qty = s1.number_input("Avail Qty (Tons)", step=500.0)
            cost = s2.number_input("Offer (ZAR/t)", step=10.0)
            if st.button("📥 Log Bid"):
                log_supplier_bid(sku, supplier, cost, qty, "2025-12-31")
                st.success("Bid Captured.")

# ==========================================
# MODE 2: RETAIL (CRM + Discount Engine Restored)
# ==========================================
def render_fmcg_floor():
    st.subheader("📦 FMCG Distribution Hub")
    tab_crm, tab_orders, tab_warehouse = st.tabs(["🤝 BD & CRM (The Hunt)", "🛒 Order Desk (Sales)", "🏭 Warehouse (Stock)"])
    
    with tab_crm:
        st.markdown("#### 🎯 Retail Prospecting Pipeline")
        c1, c2 = st.columns([2, 1])
        with c1:
            with st.expander("➕ Add New Hardware Store Lead"):
                l1, l2 = st.columns(2)
                lead_name = l1.text_input("Store Name")
                lead_area = l2.selectbox("Region", ["East Rand", "Soweto", "Pretoria", "Vaal"])
                lead_contact = l1.text_input("Manager Name")
                lead_status = l2.selectbox("Status", ["Cold", "Visited", "Onboarding", "Active"])
                if st.button("Save Lead"):
                    save_strategic_target(lead_name, "Retail", lead_contact, "Hardware", lead_area, 0, "New Lead")
                    st.success("Lead Added.")
        with c2:
            df_leads = load_prospects_to_dataframe()
            if not df_leads.empty:
                st.metric("Active Retailers", len(df_leads[df_leads['status'] == 'Active']))
        if not df_leads.empty:
            st.dataframe(df_leads[['company_name', 'region', 'status', 'contact_person']], use_container_width=True)

    with tab_orders:
        st.markdown("#### 🛒 Capture Retail Order")
        c1, c2, c3 = st.columns(3)
        df_clients = load_prospects_to_dataframe()
        client_list = df_clients[df_clients['status'] == 'Active']['company_name'].tolist() if not df_clients.empty else ["Walk-In"]
        store = c1.selectbox("Retail Client", client_list)
        item = c2.selectbox("SKU", [x['Product'] for x in FMCG_CATALOG])
        qty = c3.number_input("Units", min_value=10, value=100)
        
        base_price = next(x['Price'] for x in FMCG_CATALOG if x['Product'] == item)
        discount = 0.10 if qty >= 500 else 0.05 if qty >= 200 else 0.0
        final_price = base_price * (1 - discount)
        total = final_price * qty
        st.metric("Invoice Value", f"R {total:,.2f}", f"R {final_price:.2f}/unit (-{discount*100:.0f}%)")
        
        log_cost, dist = get_logistics_rate(qty*2, "Local") 
        st.caption(f"🚚 Est. Delivery: R {log_cost:.2f}")
        if st.button("✅ Process Order"):
            save_trade_deal(store, item, qty, total, "Open", "Firm Offer")
            st.toast("Order Sent.")

    with tab_warehouse:
        st.markdown("#### 🏭 Stock Levels (Live)")
        df_stock = pd.DataFrame(FMCG_CATALOG)
        c1, c2 = st.columns(2)
        c1.metric("Total Stock Value", f"R {(df_stock['Stock'] * df_stock['Cost']).sum():,.0f}")
        st.dataframe(df_stock[['SKU', 'Product', 'Stock', 'Price', 'Tier']], use_container_width=True)

# ==========================================
# MODE 3: SOVEREIGN ASSET TRANSFER (Wired & Hardened)
# ==========================================
def render_sovereign_transfer_floor():
    st.subheader("💠 Sovereign Asset Acquisition")
    st.caption("Permanent Digital Infrastructure Transfer | ROI Forensics")
    
    tab_quote, tab_roi = st.tabs(["📜 Generation Engine", "📊 Margin Shield Analysis"])
    
    with tab_quote:
        st.markdown("#### 🚀 Generate Asset Acquisition Quote")
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Target Entity", value="TTE Mobility")
            fleet_size = st.number_input("Total Fleet Size (Units)", min_value=1, value=10)
        with c2:
            acq_fee = st.number_input("Acquisition Fee (ZAR)", value=250000.00)
            maint_fee = st.number_input("Monthly Maintenance (ZAR)", value=7500.00)

        if st.button("🏗️ COMPILE SOVEREIGN PDF", type="primary"):
            # 1. SCOPE FIX: Define data_packet immediately upon button click
            data_packet = {
                "ref": "MAIS-TTE-2026-001",
                "client": client_name,
                "system": "Veridian Cortex v14.0 Sovereign Kernel",
                "val_prop": (
                    f"This proposal outlines the permanent acquisition of a Governance Operating System (OS) "
                    f"designed to provide the 'Digital Brain' for {client_name}'s 'Muscle'. Mandla, this is a "
                    f"Sovereign Transfer of a digital infrastructure asset, moving your operations from a "
                    f"reactive fleet to an automated industrial powerhouse."
                )
            }
            
            try:
                # 2. COMPILATION: Call the compiler with the defined packet
                with st.spinner("Hardening Kernel and Encrypting PDF..."):
                    # This calls the method returning the BytesIO buffer
                    pdf_buffer = SmartCompiler.generate_pdf_quote(data_packet)
                    
                    # 3. DELIVERY: Provide the buffer to the download button
                    st.download_button(
                        label="📂 Download Official PDF Quotation",
                        data=pdf_buffer.getvalue(), # Extract raw bytes for Streamlit
                        file_name=f"MAIS_Sovereign_Quote_{client_name.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                st.success("Sovereign PDF Compiled and Wired for Download.")
                
            except Exception as e:
                st.error(f"Kernel Error during Compilation: {str(e)}")
                st.info("Check if 'logo.png' exists in the root directory or if fpdf2 is installed.")
