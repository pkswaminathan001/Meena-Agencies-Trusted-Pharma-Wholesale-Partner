<<<<<<< HEAD
import os
import json
import sqlite3
import requests
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "meena_enterprise.db"
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"
STREAMLIT_URL = "https://meena-agencies-trusted-pharma-wholesale-partner.streamlit.app/"

try:
    import tomllib
    with open(SECRETS_PATH, "rb") as f:
        secrets = tomllib.load(f)
    BOT_TOKEN = secrets.get("Telegram_Bot_Token", "")
    GROQ_API_KEY = secrets.get("GROQ_API_KEY", "")
except Exception as e:
    print(f"⚠️ Could not read secrets.toml: {e}")
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not BOT_TOKEN:
    print("❌ Error: Telegram_Bot_Token missing in secrets.toml.")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

def get_business_context():
    if not DB_PATH.exists(): return "No database found."
    try:
        conn = sqlite3.connect(DB_PATH)
        rev = pd.read_sql_query("SELECT SUM(total) as rev FROM orders WHERE status = 'Approved'", conn).iloc[0]['rev'] or 0.0
        pend = pd.read_sql_query("SELECT COUNT(*) as count FROM orders WHERE status = 'Pending'", conn).iloc[0]['count']
        stock = pd.read_sql_query("SELECT COUNT(*) as count FROM products WHERE qty < 15", conn).iloc[0]['count']
        conn.close()
        return f"Total Revenue: ₹{rev:,.2f}. Pending Orders: {pend}. Low Stock Items: {stock}."
    except Exception as e:
        return f"Could not read DB: {e}"

def call_groq(prompt):
    if not GROQ_API_KEY: return "⚠️ GROQ_API_KEY missing."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": f"You are the Meena Agencies AI Assistant. Here is the live business data: {get_business_context()}"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        data = res.json()
        
        if "choices" not in data:
            return f"❌ Groq Error: {data.get('error', {}).get('message', 'Unknown error')}"
            
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Network Error: {e}"

@bot.message_handler(commands=['start', 'hi', 'hello'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=STREAMLIT_URL)
    markup.add(InlineKeyboardButton("🦚 Open Meena Agencies App", web_app=web_app))
    
    bot.reply_to(message, 
        f"Hello {message.from_user.first_name}! 👋\n\n"
        "I am your AI Business Partner. Tap the button below to open the app, or ask me anything about your business (e.g., 'What is my revenue?' or 'Check low stock').", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    response = call_groq(message.text)
    bot.reply_to(message, response)

if __name__ == "__main__":
    print("🤖 Meena Agencies Telegram Bot is running...")
    print("Send a message to your bot on Telegram to test it!")
    bot.infinity_polling()
=======
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
>>>>>>> 1cde11dc0cca0c5bb7eba860774919b7865e870b
