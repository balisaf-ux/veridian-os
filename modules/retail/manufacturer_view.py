import streamlit as st
from modules.core.db_manager import load_technical_skus
from modules.logistics.logic import validate_physics_handshake

def render_manufacturer_console(concern_id="CEMENT_CORP"):
    """
    Dynamic Industrial Console for Concerns.
    Accepts concern_id to load factory metrics and SKUs.
    """
    st.title(f"🏭 Concern Console: {concern_id}")
    st.caption("Industrial Metrics & Physics-Link Dispatch Control")

    # Load SKUs associated with this concern
    df_skus = load_technical_skus()
    concern_skus = df_skus[df_skus['industry_target'].str.contains(concern_id, na=False)]

    st.subheader("📦 Industrial SKU Registry")
    st.dataframe(concern_skus, use_container_width=True, hide_index=True)

    # Dispatch Interface with Hard Block
    st.markdown("---")
    st.subheader("📟 Physics-Link Dispatch Gate")
    
    selected_sku = st.selectbox("Select SKU for Dispatch", concern_skus['sku_id'])
    tonnage = st.number_input("Load Weight (Tons)", min_value=1.0, value=34.0)
    
    # Execute Physics Handshake
    is_valid, msg, fleet_options = validate_physics_handshake(selected_sku, tonnage)
    
    if is_valid:
        st.success(msg)
        truck = st.selectbox("Assign Compliant Vehicle", fleet_options)
        if st.button("🚀 AUTHORIZE DISPATCH"):
            st.info("Trip Sheet Generated & Journal Staged (In-Transit).")
    else:
        st.error(msg)
        st.button("🚀 AUTHORIZE DISPATCH", disabled=True)
