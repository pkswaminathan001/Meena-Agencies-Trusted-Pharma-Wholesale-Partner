import os
import json
import requests
import streamlit as st

def call_groq_agent(system_prompt, user_prompt):
    api_key = os.environ.get("GROQ_API_KEY", "")
    try: api_key = st.secrets["GROQ_API_KEY"]
    except: pass
    if not api_key: return "⚠️ GROQ_API_KEY missing in Streamlit Secrets."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.2 
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
        return f"API Error: {res.status_code}"
    except Exception as e: return f"Network Error: {e}"

def run_order_gauntlet(order, retailer, outstanding, credit_limit):
    order_summary = f"Order ID: {order.get('order_id')}\nTotal: ₹{order.get('total')}\nItems: {len(order.get('items', []))}"
    credit_summary = f"Retailer: {retailer.get('shop')}\nCredit Limit: ₹{credit_limit}\nCurrent Outstanding: ₹{outstanding}"

    builder_verdict = call_groq_agent("Argue WHY this order should be approved.", f"{order_summary}\n{credit_summary}")
    critic_verdict = call_groq_agent("Find the single biggest reason to REJECT this order.", f"{order_summary}\n{credit_summary}")
    boss_verdict = call_groq_agent("Read the Advocate and Auditor. Make the final call: APPROVE or REJECT.", f"Advocate: {builder_verdict}\nAuditor: {critic_verdict}")

    return builder_verdict, critic_verdict, boss_verdict
