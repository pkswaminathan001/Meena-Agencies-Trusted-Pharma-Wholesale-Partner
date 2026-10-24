import streamlit as st
from bulk_import import render_bulk_import
from rep_tracker import render_rep_checkin, render_owner_map
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

import datetime

def save_order_history(user_id, cart, total):
    orders_file = BASE_DIR / "orders.json"
    orders = []
    if orders_file.exists():
        try:
            with open(orders_file, "r") as f:
                orders = json.load(f)
        except:
            pass
            
    new_order = {
        "order_id": f"ORD-{random.randint(1000, 9999)}",
        "user_id": user_id,
        "date": str(datetime.date.today()),
        "items": cart,
        "total": total,
        "status": "Paid"
    }
    orders.append(new_order)
    with open(orders_file, "w") as f:
        json.dump(orders, f, indent=2)
    return new_order

def page_history(u):
    st.title("📜 Order History")
    orders_file = BASE_DIR / "orders.json"
    if not orders_file.exists():
        st.info("No orders placed yet.")
        return
        
    with open(orders_file, "r") as f:
        orders = json.load(f)
        
    user_orders = [o for o in orders if o.get("user_id") == u.get("id")]
    
    if not user_orders:
        st.info("You haven't placed any orders yet.")
        return
        
    for order in reversed(user_orders):
        with st.expander(f"Order {order['order_id']} - {order['date']} (₹{order['total']})"):
            st.write(f"**Status:** {order['status']}")
            for item in order['items']:
                st.write(f"- {item['name']} x {item['qty']} = ₹{item['price'] * item['qty']}")

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
                # Rate Limiting Logic
                if "failed_attempts" not in st.session_state:
                    st.session_state.failed_attempts = 0

                if st.session_state.failed_attempts >= 5:
                    st.error("🚨 SECURITY LOCK: Too many failed attempts. Please wait 15 minutes.")
                    return

                users = load_retailers()
                user = next((u for u in users if u["id"] == rid), None)
                if user:
                    input_hash = hashlib.sha256(pin.encode()).hexdigest()
                    if input_hash == user.get("pin_hash") or pin == user.get("pin"):
                        st.session_state.failed_attempts = 0 # Reset on success
                        
                        # 🛡️ AUTO-LINK TELEGRAM ID
                        # If the user doesn't have a Telegram ID saved, try to get it from the URL (if opened inside Telegram)
                        if not user.get("telegram_chat_id"):
                            # In a real Telegram Mini App, you would parse the initData here
                            # For now, we will assign a mock ID for testing
                            user["telegram_chat_id"] = "8205802064" # Replace with dynamic extraction logic
                            
                            # Update the JSON file with the new Telegram ID
                            rj_path = BASE_DIR / "retailers.json"
                            if rj_path.exists():
                                with open(rj_path, "r") as f:
                                    all_users = json.load(f)
                                for u in all_users:
                                    if u["id"] == user["id"]:
                                        u["telegram_chat_id"] = user["telegram_chat_id"]
                                with open(rj_path, "w") as f:
                                    json.dump(all_users, f, indent=2)
                        
                        st.session_state.user = user
                        st.session_state.page = "home"
                        st.rerun()
                
                # Increment failed attempts
                st.session_state.failed_attempts += 1
                st.error(f"❌ Invalid ID or PIN (Attempt {st.session_state.failed_attempts}/5)")

def page_home(u):
    st.title(f"Welcome back, {u.get('shop', 'Partner')} 👋")
    st.caption("Here is your business overview for today.")
    st.divider()

    # ─── 1. KEY METRICS (KPIs) ───
    c1, c2, c3 = st.columns(3)
    
    # Mock data (You can replace this with real DB queries later)
    outstanding = u.get("outstanding", 145000.0)
    c1.metric("Outstanding Credit", f"₹{outstanding:,.0f}", delta="-5% (Good)", delta_color="normal")
    
    c2.metric("Total Orders", "42", "+3 this week")
    
    c3.metric("Pending Deliveries", "2", delta="Active", delta_color="inverse")

    st.divider()

    # ─── 2. QUICK ACTIONS ───
    st.markdown("### ⚡ Quick Actions")
    a1, a2 = st.columns(2)
    with a1:
        if st.button("🛒 Place New Order", type="primary", use_container_width=True):
            st.session_state.page = "order"
            st.rerun()
    with a2:
        if st.button("📜 View Order History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

    st.divider()

    # ─── 3. RECENT ORDERS ───
    st.markdown("### 🧾 Recent Orders")
    
    # Load recent orders from JSON
    orders_file = BASE_DIR / "orders.json"
    recent_orders = []
    if orders_file.exists():
        try:
            with open(orders_file, "r") as f:
                all_orders = json.load(f)
                recent_orders = [o for o in all_orders if o.get("user_id") == u.get("id")][-3:] # Get last 3
        except:
            pass
            
    if not recent_orders:
        st.info("No recent orders found. Click 'Place New Order' to get started.")
    else:
        for order in reversed(recent_orders):
            with st.expander(f"Order {order['order_id']} - {order['date']} (₹{order['total']:,.2f})"):
                st.write(f"**Status:** {order['status']}")
                for item in order['items']:
                    st.write(f"- {item['name']} x {item['qty']}")
                if st.button(f"🔁 Reorder {order['order_id']}", key=f"reorder_{order['order_id']}"):
                    st.session_state.cart = order['items']
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
                # Strip whitespaces
                clean_input = input_otp.strip() if input_otp else ""
                expected_otp = str(st.session_state.order_otp).strip() if st.session_state.order_otp else ""
                
                # Secure Check: Strict 6 digits
                if clean_input == expected_otp and len(clean_input) == 6 and clean_input.isdigit():
                    # Save the order to history
                    saved_order = save_order_history(st.session_state.user.get("id"), cart, total)
                    st.success(f"🎉 Order {saved_order['order_id']} Placed Successfully!")
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
        
        menu = [("home", "🏠 Dashboard"), ("order", "🛒 Place Order"), ("cart", "🛍️ My Cart"), ("history", "📜 Order History"), ("profile", "👤 Profile")]
        
        role = str(st.session_state.user.get("role", "retailer")).lower().strip()
        
        for key, label in menu:
            # Hide Bulk Import and Map from retailers
            if key in ["bulk_import", "owner_map"] and role != "owner":
                continue
                
            # Show Rep Check-in to Reps and Owners only
            if key == "rep_checkin" and role not in ["rep", "sales_rep", "owner"]:
                continue
                
            # Always show Home, Order, Cart, History, Profile
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
    elif page == "history": page_history(u)
    elif page == "profile": page_profile(u)
    elif page == "bulk_import": render_bulk_import()
    elif page == "rep_checkin": render_rep_checkin(u)
    elif page == "owner_map": render_owner_map()

main()
