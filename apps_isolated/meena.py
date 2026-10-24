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

# CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .stButton>button { width: 100%; background-color: #1D8348; color: white; border-radius: 8px; font-weight: bold; }
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

# ─── TELEGRAM OTP FUNCTION WITH DIAGNOSTICS ───
def send_telegram_otp(chat_id, otp):
    st.write("### 🔍 OTP Diagnostic Check")
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TOKEN_HERE":
        st.error("❌ **FAILED:** Token missing in Streamlit Secrets.")
        return False
    else:
        st.success("✅ Token loaded.")

    if not chat_id:
        st.error("❌ **FAILED:** Chat ID is empty.")
        return False
    else:
        st.success(f"✅ Sending to Chat ID: `{chat_id}`")

    st.info("Attempting to send OTP via Telegram API...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": f"🦚 Meena Agencies\nYour OTP is: *{otp}*", "parse_mode": "Markdown"}
    
    try:
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            error_desc = res.json().get('description', 'Unknown error')
            st.error(f"❌ **Telegram API Error:** {error_desc}")
            if "chat not found" in error_desc:
                st.warning("💡 **Fix:** Open `@MeenaAgenciesBot` in Telegram and click 'START' first!")
            return False
        st.success("✅ OTP sent successfully to Telegram!")
        return True
    except Exception as e:
        st.error(f"❌ **Network Error:** {e}")
        return False

# ─── PAGES ───
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

def page_home(u):
    st.title(f"Welcome, {u.get('shop', 'Partner')} 👋")
    
    st.markdown("### ⚡ Quick Actions")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛒 Place Order", use_container_width=True, type="primary"):
            st.session_state.page = "order"
            st.rerun()
    with c2:
        if st.button("🛍️ View Cart", use_container_width=True):
            st.session_state.page = "cart"
            st.rerun()

def page_order():
    cart_count = len(st.session_state.get("cart", []))
    if cart_count > 0:
        c1, c2 = st.columns([3, 1])
        c1.title("🛒 Place Order")
        with c2:
            if st.button(f"🛍️ View Cart ({cart_count})", type="primary", use_container_width=True):
                st.session_state.page = "cart"
                st.rerun()
    else:
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
            st.rerun()

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
    
    # Initialize state safely
    if "show_otp_input" not in st.session_state:
        st.session_state.show_otp_input = False
    if "order_otp" not in st.session_state:
        st.session_state.order_otp = None

    if not st.session_state.show_otp_input:
        if st.button("💳 Checkout Securely", type="primary", use_container_width=True):
            otp = str(random.randint(100000, 999999))
            st.session_state.order_otp = otp
            
            chat_id = st.session_state.user.get("telegram_chat_id", "8205802064")
            
            if send_telegram_otp(chat_id, otp):
                st.session_state.show_otp_input = True
                st.rerun()

    if st.session_state.show_otp_input:
        st.info("Please enter the 6-digit OTP sent to your Telegram.")
        
        
        input_otp = st.text_input("Enter OTP", max_chars=6)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify & Place Order", type="primary", use_container_width=True):
                # Strip whitespaces just in case
                clean_input = input_otp.strip() if input_otp else ""
                expected_otp = str(st.session_state.order_otp).strip() if st.session_state.order_otp else ""
                
                if clean_input == expected_otp and len(clean_input) == 6:
                    st.success("🎉 Order Placed Successfully!")
                    st.session_state.cart = []
                    st.session_state.show_otp_input = False
                    st.session_state.order_otp = None
                    st.balloons()
                    import time
                    time.sleep(2)
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error(f"❌ Invalid OTP. You typed: '{clean_input}'")
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_otp_input = False
                st.session_state.order_otp = None
                st.rerun()



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
