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