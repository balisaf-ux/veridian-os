import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION: THE LOST CATALOG ---
# Extracted from your original app.py
FMCG_CATALOG = [
    {"SKU": "VLV-001", "Product": "Brass Gate Valve 15mm", "Cost": 60.00, "Price": 85.00, "Stock": 5000, "Tier": "A"},
    {"SKU": "PNT-WHT-20", "Product": "Acrylic PVA White 20L", "Cost": 320.00, "Price": 450.00, "Stock": 800, "Tier": "B"},
    {"SKU": "CMT-42N", "Product": "Titan Cement 42.5N", "Cost": 80.00, "Price": 95.00, "Stock": 12000, "Tier": "A"},
    {"SKU": "ELE-DB-12", "Product": "Distribution Board 12-Way", "Cost": 450.00, "Price": 650.00, "Stock": 200, "Tier": "C"},
    {"SKU": "PLM-COP-15", "Product": "Copper Tube 15mm (5.5m)", "Cost": 210.00, "Price": 380.00, "Stock": 1500, "Tier": "A"}
]

def render_retail_vertical():
    st.markdown("## 🏪 Retail Operations | FMCG Command")
    st.caption("v15.2 General Trade • Point of Sale • Inventory Control")

    # 1. METRICS (High Frequency)
    df_cat = pd.DataFrame(FMCG_CATALOG)
    df_cat['Valuation'] = df_cat['Cost'] * df_cat['Stock']
    
    total_stock_val = df_cat['Valuation'].sum()
    total_items = df_cat['Stock'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stock Valuation", f"R {total_stock_val/1e6:.2f}M", "Cost Basis")
    c2.metric("Total Units", f"{total_items:,.0f}", "SKUs on Hand")
    c3.metric("Sales Velocity", "R 45,200", "Today")
    c4.metric("Margin Avg", "32%", "Target")
    
    st.divider()

    tab_pos, tab_inv = st.tabs(["🛒 Point of Sale (POS)", "📦 Inventory Grid"])

    # === TAB 1: POINT OF SALE ===
    with tab_pos:
        st.subheader("Counter Sales")
        
        c_left, c_right = st.columns([1, 2])
        
        with c_left:
            st.info("📝 **New Transaction**")
            selected_sku = st.selectbox("Select Product", df_cat['Product'].unique())
            
            # Auto-fill details based on selection
            item_data = df_cat[df_cat['Product'] == selected_sku].iloc[0]
            st.caption(f"SKU: {item_data['SKU']} | Stock: {item_data['Stock']}")
            
            qty = st.number_input("Quantity", min_value=1, max_value=int(item_data['Stock']), value=1)
            
            # Live Math
            line_total = qty * item_data['Price']
            st.markdown(f"### Total: R {line_total:,.2f}")
            
            if st.button("💳 Process Sale"):
                st.success(f"Sold {qty} x {item_data['SKU']} for R {line_total:,.2f}")
                st.toast("Inventory Updated. Revenue Posted.")

        with c_right:
            st.markdown("##### 🧾 Today's Feed")
            # Simulated Transaction Feed
            sales_data = pd.DataFrame([
                {"Time": "08:15", "SKU": "CMT-42N", "Qty": 50, "Value": 4750.00, "Clerk": "Sales-1"},
                {"Time": "09:30", "SKU": "VLV-001", "Qty": 12, "Value": 1020.00, "Clerk": "Sales-2"},
                {"Time": "11:45", "SKU": "PNT-WHT-20", "Qty": 5, "Value": 2250.00, "Clerk": "Sales-1"},
            ])
            st.dataframe(sales_data, use_container_width=True)

    # === TAB 2: INVENTORY GRID ===
    with tab_inv:
        st.subheader("Warehouse Stock")
        st.dataframe(
            df_cat.style.format({"Cost": "R {:.2f}", "Price": "R {:.2f}", "Valuation": "R {:.2f}"}),
            use_container_width=True
        )
