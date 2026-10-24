import streamlit as st
import pandas as pd
import json
import sqlite3
import hashlib
import requests

import base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

import random
import time
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
    footer {visibility: hidden;}
    /* Keep the sidebar toggle visible for mobile */
    [data-testid="collapsedControl"] { display: flex !important; }
    header { background-color: transparent !important; }
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
                start_time = time.time()
                
                users = load_retailers()
                user = next((u for u in users if u["id"] == rid), None)
                
                if user:
                    input_hash = hashlib.sha256(pin.encode()).hexdigest()
                    if input_hash == user.get("pin_hash") or pin == user.get("pin"):
                        end_time = time.time()
                        load_time = round((end_time - start_time) * 1000, 2) # in milliseconds
                        
                        st.session_state.user = user
                        st.session_state.page = "home"
                        st.session_state.login_speed = load_time
                        st.rerun()
                
                st.error("❌ Invalid ID or PIN")

# ─── PAGES ───
def page_home(u):
    st.title(f"Welcome, {u.get('shop', 'Partner')} 👋")
    
    # Display login speed if available
    if "login_speed" in st.session_state:
        st.toast(f"⚡ Logged in securely in {st.session_state.login_speed} ms")
        del st.session_state.login_speed

    
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
            
    st.divider()
    st.info("💡 **Tip:** You can also open the sidebar menu (click the `>` icon on the top left) to access all pages.")


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
    
    # Initialize state if not present
    if "show_otp_input" not in st.session_state:
        st.session_state.show_otp_input = False
    if "order_otp" not in st.session_state:
        st.session_state.order_otp = None

    if not st.session_state.show_otp_input:
        if st.button("💳 Checkout Securely", type="primary", use_container_width=True):
            # Simulate sending OTP
            import random
            otp = str(random.randint(100000, 999999))
            st.session_state.order_otp = otp
            st.session_state.show_otp_input = True
            st.success(f"✅ OTP sent to Telegram! (Demo Code: {otp})")
            st.rerun()

    if st.session_state.show_otp_input:
        st.info("Please enter the 6-digit OTP sent to your Telegram.")
        input_otp = st.text_input("Enter OTP", max_chars=6)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify & Place Order", type="primary", use_container_width=True):
                if input_otp == st.session_state.order_otp:
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
                    st.error("❌ Invalid OTP")
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
        # Display the BIG CIRCLE logo
        logo_b64 = get_base64_image("logo.png")
        if logo_b64:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-top: 10px; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{logo_b64}" 
                         style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border: 4px solid #1D8348;">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
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
