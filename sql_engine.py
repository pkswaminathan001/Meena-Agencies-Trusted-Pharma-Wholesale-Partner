from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import re

DB_FILE = str(BASE_DIR / "meena_enterprise.db")

def init_db():
    """Converts JSON data to a SQLite database for real SQL querying."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Retailers table
    c.execute("""CREATE TABLE IF NOT EXISTS retailers (
        id TEXT PRIMARY KEY,
        shop TEXT,
        owner TEXT,
        status TEXT,
        credit_limit REAL,
        outstanding REAL
    )""")
    
    # Load data from JSON and insert
    if os.path.exists("retailers.json"):
        with open("retailers.json", "r") as f:
            retailers = json.load(f)
        for r in retailers:
            c.execute("INSERT OR REPLACE INTO retailers VALUES (?, ?, ?, ?, ?, ?)",
                      (r.get("id"), r.get("shop"), r.get("owner"), r.get("status"), 
                       r.get("credit_limit", 0), r.get("outstanding", 0)))
    
    conn.commit()
    conn.close()

def generate_sql(query):
    """Simulates an LLM translating Natural Language to SQL."""
    q = query.lower()
    
    if "active retailer" in q or "active shop" in q:
        return "SELECT id, shop, owner, outstanding FROM retailers WHERE status = 'Active';"
    elif "blocked" in q:
        return "SELECT id, shop, owner, outstanding FROM retailers WHERE status = 'Blocked';"
    elif "outstanding" in q or "dues" in q or "balance" in q:
        return "SELECT shop, outstanding FROM retailers ORDER BY outstanding DESC;"
    elif "total" in q and "retailer" in q:
        return "SELECT COUNT(*) as total_retailers FROM retailers;"
    elif "delete" in q or "drop" in q:
        return q # Pass the malicious query through so the guardrail catches it
    else:
        return "SELECT * FROM retailers LIMIT 5;"

def is_safe_query(sql):
    """The Execution Guardrail (Page 11)."""
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    sql_upper = sql.upper()
    
    for kw in dangerous_keywords:
        if re.search(r'\b' + kw + r'\b', sql_upper):
            return False, kw
    return True, None

@st.cache_resource
def get_db_connection():
    return sqlite3.connect(DB_FILE)

def render_chat_to_sql():
    st.markdown("## 🗄️ Chat-to-SQL (Advanced)")
    st.caption("Ask questions in plain English. The AI generates SQL, enforces security, and returns the data.")

    # Ensure DB exists
    init_db()

    user_query = st.text_input("Ask a question about your retailers:", placeholder="e.g., Show me all active retailers")
    
    if st.button("🔍 Generate & Execute SQL", type="primary"):
        if not user_query:
            st.warning("Please enter a question.")
            return

        # Step 1: Generate SQL
        generated_sql = generate_sql(user_query)
        
        st.markdown("### 🤖 Generated SQL")
        st.code(generated_sql, language="sql")

        # Step 2: Security Guardrail
        st.markdown("### 🛡️ Security Guardrail")
        safe, bad_word = is_safe_query(generated_sql)
        
        if not safe:
            st.error(f"🚨 **BLOCKED:** The query contains the forbidden keyword `{bad_word}`. Read-Only enforcement is active.")
            return
        else:
            st.success("✅ Query passed security checks (Read-Only).")

        # Step 3: Execute
        st.markdown("### 📊 Results")
        try:
            conn = get_db_connection()
            df = pd.read_sql_query(generated_sql, conn)
            conn.close()
            
            if df.empty:
                st.info("Query executed successfully, but returned no results.")
            else:
                st.dataframe(df, use_container_width=True)
                st.caption(f"Returned {len(df)} rows from the database.")
                
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
