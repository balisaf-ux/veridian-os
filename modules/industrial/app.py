import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- CROSS-MODULE IMPORTS (The Bridge) ---
from modules.finance.settlement import SettlementEngine
from modules.finance.models import Client

# --- DATABASE CONNECTION HELPER ---
def get_engine():
    db_path = r"C:\Users\Balisa\OneDrive\Documents\Business\Veridian Markets\IT\Python Code\project_cortex\cortex_live.db"
    if not os.path.exists(db_path):
        st.error(f"❌ DATABASE MISSING: {db_path}")
        return None
    return create_engine(f'sqlite:///{db_path}')

# --- ACTION: SAVE RFQ ---
def save_new_rfq(client, item, qty, rate, status="DRAFT"):
    engine = get_engine()
    if engine:
        try:
            total = float(qty) * float(rate)
            # Generate a simple ID based on timestamp hash or random
            import uuid
            rfq_id = f"RFQ-{str(uuid.uuid4())[:8].upper()}"
            
            with engine.connect() as conn:
                stmt = text("""
                    INSERT INTO ind_rfqs (rfq_id, client_name, project_scope, status, total_value, created_at)
                    VALUES (:id, :client, :scope, :status, :val, CURRENT_TIMESTAMP)
                """)
                conn.execute(stmt, {
                    "id": rfq_id, 
                    "client": client, 
                    "scope": f"{item} (Qty: {qty} @ {rate})", 
                    "status": status, 
                    "val": total
                })
                conn.commit()
            return True
        except Exception as e:
            st.error(f"Save Failed: {e}")
            return False
    return False

# --- ACTION: PUSH TO FINANCE ---
def promote_to_finance(rfq_id, client_name, amount, desc):
    """
    The Handshake. 
    Calls the Settlement Engine to turn an Industrial RFQ into a Financial Invoice.
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Ensure Client Exists (Auto-Onboarding for Speed)
    # We strip spaces and make it uppercase for the ID
    client_id = client_name.replace(" ", "_").upper()
    
    existing = session.query(Client).filter_by(id=client_id).first()
    if not existing:
        new_client = Client(id=client_id, name=client_name, credit_limit=500000.0)
        session.add(new_client)
        session.commit()
    
    # 2. Trigger Settlement Engine
    cortex = SettlementEngine(session)
    
    # We treat this as a "Sourcing Event"
    payload = {
        "client_id": client_id,
        "qty": 1, # We treat the RFQ as a single unit or "Lot"
        "rate": amount,
        "ref": rfq_id,
        "desc": desc
    }
    
    result = cortex.capitalize_event("SOURCING_DEAL", payload)
    
    # 3. Update RFQ Status if successful
    if result['status'] == 'SETTLED':
        with engine.connect() as conn:
            conn.execute(text("UPDATE ind_rfqs SET status = 'INVOICED' WHERE rfq_id = :id"), {"id": rfq_id})
            conn.commit()
            
    return result

# --- MAIN RENDER ---
def render_industrial_vertical():
    st.markdown("## 🏭 Industrial Portal | Sourcing Nexus")
    st.caption("v14.2 Integrated Deal Engine • Linked to Finance Module")

    engine = get_engine()
    
    # --- 1. LOAD DATA ---
    df_rfqs = pd.DataFrame()
    df_origins = pd.DataFrame()
    
    if engine:
        try:
            with engine.connect() as conn:
                df_origins = pd.read_sql("SELECT * FROM ind_origins", conn)
                df_rfqs = pd.read_sql("SELECT * FROM ind_rfqs ORDER BY created_at DESC", conn)
        except:
            pass

    # METRICS
    pending_val = df_rfqs[df_rfqs['status'] == 'DRAFT']['total_value'].sum() if not df_rfqs.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Deals", f"{len(df_rfqs)}", "RFQs")
    c2.metric("Verified Origins", f"{len(df_origins)}", "Locations")
    c3.metric("Pipeline Value", f"R {pending_val/1000:.1f}k", "Drafts")
    c4.metric("System Link", "ACTIVE", "Finance Module")

    st.markdown("---")

    tab_search, tab_rfq, tab_registry, tab_stockpiles = st.tabs([
        "🔍 Global Search", 
        "📝 Deal Manager (RFQs)", 
        "🏭 Origin Registry", 
        "🏔️ Virtual Stockpiles"
    ])

    # --- TAB 1: SEARCH ---
    with tab_search:
        st.subheader("Global Sourcing Search")
        c_search, c_btn = st.columns([4, 1])
        search_term = c_search.text_input("Find Industrial Equipment...", placeholder="e.g. Cement, Coal")
        c_btn.write("") 
        c_btn.write("") 
        if c_btn.button("Search Network", type="primary"):
            if not df_origins.empty:
                mask = (
                    df_origins['name'].str.contains(search_term, case=False) | 
                    df_origins['product'].str.contains(search_term, case=False) |
                    df_origins['location'].str.contains(search_term, case=False)
                )
                results = df_origins[mask]
                if not results.empty:
                    st.success(f"Found {len(results)} matches")
                    st.dataframe(results[['name', 'type', 'location', 'product', 'contract_status']], use_container_width=True)
                else:
                    st.warning("No matches found.")

    # --- TAB 2: DEAL MANAGER (The Integration Point) ---
    with tab_rfq:
        c1, c2 = st.columns([2, 1])
        c1.subheader("Deal Flow & Quotations")
        
        # A. CREATE NEW DEAL
        with c2.expander("➕ Create New Deal", expanded=False):
            with st.form("new_rfq_form"):
                client = st.text_input("Client Name", "Orion Energy")
                item = st.text_input("Product Scope", "HFO Batch A1")
                qty = st.number_input("Quantity", min_value=1.0, value=1000.0)
                rate = st.number_input("Rate (ZAR)", min_value=1.0, value=12.50)
                
                if st.form_submit_button("Draft Deal"):
                    save_new_rfq(client, item, qty, rate)
                    st.rerun()

        # B. MANAGE DEALS
        if not df_rfqs.empty:
            for idx, row in df_rfqs.iterrows():
                # Card Layout for Deals
                with st.container():
                    c_a, c_b, c_c, c_d = st.columns([2, 2, 1, 1])
                    c_a.write(f"**{row['client_name']}**")
                    c_a.caption(f"{row['rfq_id']} • {row['created_at']}")
                    c_b.write(f"{row['project_scope']}")
                    c_c.write(f"**R {row['total_value']:,.2f}**")
                    
                    status = row['status']
                    if status == 'DRAFT':
                        if c_d.button("🚀 Finance", key=f"btn_{row['rfq_id']}"):
                            with st.spinner("Contacting Treasury..."):
                                res = promote_to_finance(row['rfq_id'], row['client_name'], row['total_value'], row['project_scope'])
                                if res['status'] == 'SETTLED':
                                    st.success(f"Invoiced: {res['invoice_number']}")
                                    st.balloons() # VISUAL CONFIRMATION
                                    st.rerun()
                                else:
                                    st.error(f"Rejected: {res.get('reason')}")
                    else:
                        c_d.success(f"✅ {status}")
                    
                    st.divider()
        else:
            st.info("No Deals in Pipeline.")

    # --- TAB 3: REGISTRY ---
    with tab_registry:
        st.subheader("Register Primary Origins")
        if not df_origins.empty:
            st.dataframe(df_origins[['name', 'type', 'location', 'product', 'capacity']], use_container_width=True)
        
        with st.expander("➕ Onboard New Origin"):
            with st.form("add_origin_form"):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("Entity Name")
                new_type = c1.selectbox("Type", ["Mine", "Factory", "Warehouse"])
                new_loc = c2.text_input("Location")
                new_prod = c2.text_input("Primary Product")
                new_cap = st.number_input("Monthly Capacity", min_value=0, step=1000)
                
                if st.form_submit_button("Register Origin"):
                    if new_name:
                        save_new_origin(new_name, new_type, new_loc, new_prod, new_cap)
                        st.rerun()

    # --- TAB 4: STOCKPILES ---
    with tab_stockpiles:
        st.subheader("Virtual Inventory Management")
        st.info("Aggregated Stockpile View Offline.")
