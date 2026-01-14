import streamlit as st
import pandas as pd
import datetime

# --- 1. ROBUST IMPORTS ---
try:
    from .db_utils import load_data, run_query
except ImportError:
    try:
        from ..db_utils import load_data, run_query
    except ImportError:
        from modules.logistics.db_utils import load_data, run_query


# =========================================================
# 2. SELF-HEALING SCHEMA (RESILIENT)
# =========================================================
def ensure_risk_tables():
    """Creates risk and compliance tables if they don't exist."""
    run_query("""
        CREATE TABLE IF NOT EXISTS log_risk_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            type TEXT,
            severity TEXT,
            description TEXT,
            cost_impact REAL,
            status TEXT
        );
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS log_compliance_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT,
            ref_number TEXT,
            expiry_date DATE,
            status TEXT
        );
    """)


# =========================================================
# 3. MAIN VIEW
# =========================================================
def render_risk_view():
    st.subheader("🛡️ Risk & Compliance Operations")

    ensure_risk_tables()

    tab_incidents, tab_vault = st.tabs([
        "🚨 Risk Ledger (Live)",
        "🪪 Compliance Vault (DB)"
    ])

    # =========================================================
    # TAB 1: RISK LEDGER
    # =========================================================
    with tab_incidents:
        df_risk = load_data("SELECT * FROM log_risk_incidents ORDER BY date DESC")

        # Metrics
        total_loss = df_risk["cost_impact"].sum() if not df_risk.empty else 0.0
        open_cases = len(df_risk[df_risk["status"] == "Open"]) if not df_risk.empty else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Risk Cost", f"R {total_loss:,.2f}")
        m2.metric(
            "Open Incidents",
            open_cases,
            delta="Action Req" if open_cases > 0 else "Clear",
            delta_color="inverse",
        )
        m3.metric("Safety Score", "94/100")

        st.divider()

        c_view, c_log = st.columns([2, 1])

        # -------------------------
        # A. INCIDENT TABLE
        # -------------------------
        with c_view:
            if not df_risk.empty:
                df_risk_sorted = df_risk.sort_values("date", ascending=False)
                st.dataframe(
                    df_risk_sorted,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No incidents recorded in the Ledger.")

        # -------------------------
        # B. INCIDENT LOGGER
        # -------------------------
        with c_log:
            st.markdown("#### 📝 Log Incident")

            with st.form("risk_logger"):
                i_date = st.date_input("Date", value=datetime.date.today())
                i_type = st.selectbox("Type", ["Theft", "Accident", "Fine", "Breakdown", "Delay"])
                i_desc = st.text_input("Description")
                i_cost = st.number_input("Cost (ZAR)", min_value=0.0)

                # Auto-severity classification
                severity = (
                    "High" if i_cost >= 50000 else
                    "Medium" if i_cost >= 5000 else
                    "Low"
                )

                submitted = st.form_submit_button("🚨 Submit Log")
                if submitted:
                    run_query(
                        """
                        INSERT INTO log_risk_incidents
                            (date, type, severity, description, cost_impact, status)
                        VALUES
                            (:d, :t, :sev, :desc, :c, 'Open')
                        """,
                        {"d": i_date, "t": i_type, "sev": severity, "desc": i_desc, "c": i_cost},
                    )
                    st.success("Incident logged.")
                    st.rerun()

    # =========================================================
    # TAB 2: COMPLIANCE VAULT
    # =========================================================
    with tab_vault:
        df_docs = load_data("SELECT * FROM log_compliance_docs")

        # Auto-update expired documents
        today = datetime.date.today()
        if not df_docs.empty:
            for _, row in df_docs.iterrows():
                if row["expiry_date"] and row["expiry_date"] < today and row["status"] != "Expired":
                    run_query(
                        "UPDATE log_compliance_docs SET status='Expired' WHERE id=:id",
                        {"id": row["id"]},
                    )

        df_docs = load_data("SELECT * FROM log_compliance_docs")

        c_docs, c_up = st.columns([2, 1])

        # -------------------------
        # A. DOCUMENT TABLE
        # -------------------------
        with c_docs:
            if not df_docs.empty:
                df_docs_sorted = df_docs.sort_values("expiry_date")

                st.dataframe(
                    df_docs_sorted,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "expiry_date": st.column_config.DateColumn("Expires"),
                        "status": st.column_config.TextColumn("Status"),
                    },
                )

                # Expiry warnings
                expiring = df_docs_sorted[
                    (df_docs_sorted["expiry_date"] - today).dt.days.between(0, 30)
                ]
                if not expiring.empty:
                    st.warning(f"⚠️ {len(expiring)} documents expiring within 30 days.")
            else:
                st.info("Vault is empty.")

        # -------------------------
        # B. DOCUMENT UPLOAD
        # -------------------------
        with c_up:
            st.markdown("#### 🔄 Upload Document")

            with st.form("doc_up"):
                d_type = st.selectbox("Type", ["GIT", "Tax", "Liability", "Insurance", "Roadworthy"])
                d_ref = st.text_input("Ref Number")
                d_exp = st.date_input("Expiry Date", value=datetime.date.today())

                submitted = st.form_submit_button("💾 Save to Vault")
                if submitted:
                    run_query(
                        """
                        INSERT INTO log_compliance_docs
                            (doc_type, ref_number, expiry_date, status)
                        VALUES
                            (:t, :r, :e, 'Active')
                        """,
                        {"t": d_type, "r": d_ref, "e": d_exp},
                    )
                    st.success("Saved to Vault.")
                    st.rerun()
