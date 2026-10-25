import streamlit as st
import threading
import time
import subprocess
import sys
from pathlib import Path

# Run the bot in a background thread on startup
if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    
    def run_bot():
        bot_path = Path(__file__).resolve().parent / "telegram_bot.py"
        subprocess.Popen([sys.executable, str(bot_path)])
    
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

st.set_page_config(page_title="Meena Bot Status", page_icon="🤖")
st.title("🤖 Meena Agencies Bot Status")
st.success("Telegram Bot is running 24/7 on Streamlit Cloud")
st.markdown(f"**Bot Started At:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("The bot is listening for messages on Telegram.")
st.markdown("Send `hi` to your bot to test it.")
