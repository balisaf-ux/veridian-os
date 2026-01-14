import streamlit as st
import pandas as pd
import sqlite3
from modules.core.db_manager import DB_NAME

def render_retail_portal():
    """
    CUSTOMER PORTAL: The Digital Storefront.
    Allows external pull of inventory (Iron Oxide/Paint).
    """
    st.markdown("## 🛒 Customer Portal | Direct Order")
    st.caption("Veridian Industrial Sourcing")
    
    # 1. Fetch Product Catalog (Direct SQL for speed in Portal)
    conn = sqlite3.connect(DB_NAME)
    try:
        df_products = pd.read_sql_query("SELECT * FROM technical_skus", conn)
    except Exception:
        st.error("Catalog unavailable. Contact Sales.")
        conn.close()
        return
    conn.close()

    if df_products.empty:
        st.info("Catalog is empty. Add SKUs in Admin Core.")
        return

    # 2. Order Interface
    with st.form("retail_order_form"):
        st.subheader("Create New Order")
        c1, c2 = st.columns(2)
        client = c1.text_input("Company Name")
        product = c2.selectbox("Select Product", df_products['sku_id'].unique())
        qty = c1.number_input("Quantity (Units/Tons)", min_value=1.0)
        
        submitted = st.form_submit_button("🚀 Submit Order")
        
        if submitted and client:
            # Simple write-back logic
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            import datetime
            order_id = f"ORD-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Inject into retail_orders table
            c.execute("INSERT INTO retail_orders (order_id, retailer_name, sku_id, qty, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                      (order_id, client, product, qty, "Pending", datetime.datetime.now().isoformat()))
            conn.commit()
            conn.close()
            st.success(f"Order {order_id} Received. Dispatch notified.")
