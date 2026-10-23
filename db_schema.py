from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import datetime
import json
import os

DB_FILE = str(BASE_DIR / "meena_erp.db")

def init_erp_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. t_purchase_ledger (Page 26)
    c.execute("""CREATE TABLE IF NOT EXISTS t_purchase_ledger (
        purchase_id TEXT PRIMARY KEY,
        batch_number TEXT UNIQUE,
        hsn_code TEXT,
        base_unit_price_inr REAL,
        quantity_purchased INTEGER,
        expiry_date TEXT,
        created_at TEXT
    )""")
    
    # 2. t_receivables (Page 26)
    c.execute("""CREATE TABLE IF NOT EXISTS t_receivables (
        invoice_id TEXT PRIMARY KEY,
        client_id TEXT,
        batch_number TEXT,
        invoice_amount_currency REAL,
        currency_code TEXT,
        exchange_rate_applied REAL,
        invoice_status TEXT,
        promised_payment_date TEXT,
        actual_payment_date TEXT,
        created_at TEXT
    )""")
    
    # 3. t_audit_compliance_log (Page 27) - IMMUTABLE
    c.execute("""CREATE TABLE IF NOT EXISTS t_audit_compliance_log (
        audit_id TEXT PRIMARY KEY,
        invoice_id TEXT,
        drug_export_license_status INTEGER,
        bank_ebrc_reference TEXT,
        compliance_integrity_value INTEGER,
        row_hash TEXT,
        logged_at TEXT
    )""")
    
    conn.commit()
    conn.close()

def calculate_row_hash(invoice_id, license_status, ebrc_ref, comp_val, timestamp):
    """Generates a cryptographic fingerprint for the row."""
    payload = f"{invoice_id}|{license_status}|{ebrc_ref}|{comp_val}|{timestamp}"
    return hashlib.sha256(payload.encode()).hexdigest()

def verify_ledger():
    """Scans the ledger to ensure no one has tampered with the data."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT audit_id, invoice_id, drug_export_license_status, bank_ebrc_reference, compliance_integrity_value, logged_at, row_hash FROM t_audit_compliance_log")
    rows = c.fetchall()
    conn.close()
    
    tampered = []
    for row in rows:
        audit_id, inv_id, lic, ebrc, comp, ts, stored_hash = row
        # Recalculate expected hash
        expected_hash = calculate_row_hash(inv_id, lic, ebrc, comp, ts)
        if expected_hash != stored_hash:
            tampered.append(audit_id)
            
    return len(rows), tampered

def render_db_schema():
    st.markdown("## 🗄️ ERP Schema & Immutable Audit")
    st.caption("Unified Database Architecture with Cryptographic Audit Trails (Pages 26-27).")

    init_erp_db()

    tab1, tab2 = st.tabs(["📜 Immutable Audit Ledger", "📊 Table Explorer"])

    # ─── TAB 1: Audit Ledger ───
    with tab1:
        st.markdown("### Generate New Audit Log")
        st.write("Every compliance check appends an unalterable cryptographic hash to the ledger.")
        
        with st.form("audit_form"):
            inv_id = st.text_input("Invoice ID", value="INV-2026-001")
            lic_status = st.checkbox("Drug License Valid", value=True)
            ebrc_ref = st.text_input("Bank EBRC Reference", value="EBRC-889922")
            
            if st.form_submit_button("🔒 Commit to Immutable Ledger", type="primary"):
                timestamp = str(datetime.datetime.now())
                comp_val = int(lic_status)
                audit_id = f"AUD-{pd.Timestamp.now().strftime('%Y%M%d%H%M%S')}"
                r_hash = calculate_row_hash(inv_id, int(lic_status), ebrc_ref, comp_val, timestamp)
                
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO t_audit_compliance_log VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (audit_id, inv_id, int(lic_status), ebrc_ref, comp_val, r_hash, timestamp))
                conn.commit()
                conn.close()
                
                st.success(f"✅ Log committed! Cryptographic Hash: `{r_hash[:16]}...`")

        st.markdown("---")
        st.markdown("### 🛡️ Ledger Integrity Verification")
        st.write("Checks if any records have been tampered with by recalculating the hashes.")
        
        if st.button("▶️ Run Integrity Audit"):
            total, tampered = verify_ledger()
            if total == 0:
                st.info("Ledger is empty. Add a record first.")
            elif len(tampered) == 0:
                st.success(f"✅ **AUDIT PASSED:** All {total} records are cryptographically secure. No tampering detected.")
            else:
                st.error(f"🚨 **CRITICAL ALERT:** {len(tampered)} records have been tampered with! Audit IDs: {tampered}")

        # Display ledger
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM t_audit_compliance_log", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ─── TAB 2: Table Explorer ───
    with tab2:
        st.markdown("### Database Tables")
        table_choice = st.selectbox("Select Table", ["t_purchase_ledger", "t_receivables", "t_audit_compliance_log"])
        
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(f"SELECT * FROM {table_choice}", conn)
        conn.close()
        
        if df.empty:
            st.info(f"Table '{table_choice}' is currently empty.")
        else:
            st.dataframe(df, use_container_width=True)
