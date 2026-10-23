import streamlit as st
import pandas as pd
import json
import sqlite3
import hashlib
import requests
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Securely read token from Streamlit Cloud Secrets
try:
    TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
except:
    TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"

st.set_page_config(page_title="Meena Agencies", page_icon="🦚", layout="wide")

# ─── DAD'S CSS FIXES (No Scrolling, Hide Menus) ───
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .stButton>button { width: 100%; background-color: #1D8348; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #145c32; color: white; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADERS ───
@st.cache_data(ttl=60)
def load_inventory():
    db_path = BASE_DIR / "meena_enterprise.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT sku as name, 150.0 as price, qty as stock FROM products LIMIT 100", conn)
        conn.close()
        return df
    return pd.DataFrame()

@st.cache_data(ttl=60)
def load_retailers():
    rj_path = BASE_DIR / "retailers.json"
    if rj_path.exists():
        with open(rj_path, "r") as f:
            return json.load(f)
    return []

# ─── TELEGRAM OTP FUNCTION ───
def send_telegram_otp(chat_id, otp):
    if TELEGRAM_BOT_TOKEN == "YOUR_TOKEN_HERE":
        st.error("❌ Token not found in Streamlit Secrets.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": f"🦚 Meena Agencies Security\nYour OTP is: *{otp}*", "parse_mode": "Markdown"}
    try:
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            # Show the exact error from Telegram on the screen
            st.error(f"Telegram Error: {res.text}")
            return False
        return True
    except Exception as e:
        st.error(f"Network Error: {e}")
        return False

# ─── LOGIN ───
def login_screen():
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.title("🦚 Meena Agencies")
        st.caption("Trusted Pharma Wholesale Partner")
        with st.form("login"):
            st.info("Owner: `OWNER001` / `1234` | Retailer: `RET001` / `3210`")
            rid = st.text_input("User ID").strip().upper()
            pin = st.text_input("PIN", type="password").strip()
            if st.form_submit_button("Login", use_container_width=True):
                users = load_retailers()
                user = next((u for u in users if u["id"] == rid), None)
                if user:
                    input_hash = hashlib.sha256(pin.encode()).hexdigest()
                    if input_hash == user.get("pin_hash") or pin == user.get("pin"):
                        st.session_state.user = user
                        st.session_state.page = "home"
                        st.rerun()
                st.error("❌ Invalid ID or PIN")

# ─── PAGES ───
def page_home(u):
    st.title(f"Welcome, {u.get('shop', 'Partner')} 👋")
    st.info("Navigate to 'Place Order' to browse the catalog.")

def page_order():
    st.title("🛒 Place Order")
    df = load_inventory()
    if df.empty:
        st.error("Inventory DB not found.")
        return

    if "cart" not in st.session_state:
        st.session_state.cart = []

    search = st.text_input("Search medicine", placeholder="e.g. Dolo").lower()
    view = df[df["name"].str.lower().str.contains(search)] if search else df

    for _, row in view.head(20).iterrows():
        c1, c2, c3 = st.columns([4, 2, 2])
        c1.write(f"**{row['name']}**")
        c2.write(f"₹{row['price']}")
        if c3.button("Add", key=f"add_{row['name']}"):
            st.session_state.cart.append({"name": row['name'], "price": row['price'], "qty": 1})
            st.toast(f"Added {row['name']}")

def page_cart():
    st.title("🛍️ My Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Cart is empty.")
        return
    
    total = sum(item["price"] * item["qty"] for item in cart)
    for item in cart:
        st.write(f"{item['name']} - ₹{item['price'] * item['qty']}")
        
    st.markdown(f"### Total: ₹{total}")
    
    if st.button("💳 Checkout Securely", type="primary"):
        otp = str(random.randint(100000, 999999))
        st.session_state.order_otp = otp
        
        # Use the Telegram chat ID from the user's profile (or a fallback for demo)
        chat_id = st.session_state.user.get("telegram_chat_id", "YOUR_CHAT_ID_HERE")
        sent = send_telegram_otp(chat_id, otp)
        
        if sent:
            st.success("✅ OTP sent to your Telegram app!")
        else:
            st.warning(f"⚠️ Demo Mode. Your OTP is: **{otp}**")
            
        st.session_state.show_otp_input = True

    if st.session_state.get("show_otp_input"):
        input_otp = st.text_input("Enter OTP", max_chars=6)
        if st.button("Verify & Place Order"):
            if input_otp == st.session_state.get("order_otp"):
                st.success("🎉 Order Placed Successfully!")
                st.session_state.cart = []
                st.session_state.show_otp_input = False
            else:
                st.error("❌ Invalid OTP")

def page_profile(u):
    st.title("👤 Profile")
    st.json(u)

# ─── SIDEBAR ───
def render_sidebar():
    with st.sidebar:
        st.title("🦚 Meena")
        st.caption(st.session_state.user.get("role", "Retailer").upper())
        st.divider()
        
        menu = [("home", "🏠 Dashboard"), ("order", "🛒 Place Order"), ("cart", "🛍️ My Cart"), ("profile", "👤 Profile")]
        
        for key, label in menu:
            if st.button(label, use_container_width=True):
                st.session_state.page = key
                st.rerun()
                
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def main():
    if "user" not in st.session_state:
        login_screen()
        return

    st.session_state.setdefault("page", "home")
    render_sidebar()

    page = st.session_state.page
    u = st.session_state.user
    
    if page == "home": page_home(u)
    elif page == "order": page_order()
    elif page == "cart": page_cart()
    elif page == "profile": page_profile(u)

main()
