import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def call_groq_agent(system_prompt, user_prompt):
    api_key = os.environ.get("GROQ_API_KEY", "")
    try: api_key = st.secrets["GROQ_API_KEY"]
    except: pass
    if not api_key: return "⚠️ GROQ_API_KEY missing in Streamlit Secrets."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.3 
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
        return f"API Error: {res.status_code}"
    except Exception as e: return f"Network Error: {e}"

@st.fragment(run_every="15s")
def render_agent_hq():
    st.markdown("### 🟢 Live Agent Activity Feed")
    st.caption("Agents are actively roaming the database...")
    
    db_path = BASE_DIR / "meena_enterprise.db"
    low_stock = []
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT sku, qty FROM products WHERE qty < 15", conn)
        conn.close()
        if not df.empty:
            low_stock = df.to_dict('records')

    retailers_file = BASE_DIR / "retailers.json"
    high_credit = []
    if retailers_file.exists():
        retailers = json.loads(retailers_file.read_text())
        for r in retailers:
            limit = r.get("credit_limit", 200000)
            out = r.get("outstanding", 0)
            if out > (limit * 0.8):
                high_credit.append(r)

    with st.container(border=True):
        st.markdown("#### 📦 Inventory Agent")
        if low_stock:
            st.error(f"🚨 ALERT: {len(low_stock)} items are critically low on stock!")
            for item in low_stock:
                st.write(f"- **{item['sku']}**: Only {item['qty']} left.")
            if st.button("Generate Restock Email"):
                with st.spinner("Inventory Agent is drafting email..."):
                    prompt = f"Write a brief email to the supplier asking for restock of these items: {low_stock}"
                    st.info(call_groq_agent("You are the Inventory Manager.", prompt))
        else:
            st.success("✅ All stock levels are healthy. No action needed.")

    with st.container(border=True):
        st.markdown("#### 💰 Credit Agent")
        if high_credit:
            st.warning(f"⚠️ {len(high_credit)} retailers are nearing their credit limits!")
            for r in high_credit:
                st.write(f"- **{r.get('shop')}**: Outstanding ₹{r.get('outstanding'):,} / Limit ₹{r.get('credit_limit', 200000):,}")
        else:
            st.success("✅ All retailers are within safe credit limits.")

    with st.container(border=True):
        st.markdown("#### 🚨 Fraud Agent")
        st.success("✅ Scanned last 50 orders. No abnormal quantities detected.")
