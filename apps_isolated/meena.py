import streamlit as st
import pandas as pd
import json
import os
import sqlite3
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize Cloud Data
import sys
sys.path.insert(0, str(BASE_DIR))
import cloud_bootstrap
cloud_bootstrap.ensure_data_exists()

st.set_page_config(page_title="Meena Agencies", page_icon="🛒", layout="wide")

# ─── DATA LOADERS ───
@st.cache_data(ttl=60)
def load_inventory():
    db_path = BASE_DIR / "meena_enterprise.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT sku as name, 100.0 as price, qty as stock FROM products LIMIT 500", conn)
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

# ─── AUTHENTICATION LOGIC ───
def login_screen():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<h2 style="text-align:center;">Meena Agencies</h2>', unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("login_form"):
            rid = st.text_input("User ID", placeholder="e.g. RET001 or OWNER001").strip().upper()
            pin = st.text_input("PIN", type="password").strip()
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not rid or not pin:
                st.error("Please enter ID and PIN.")
                return
            
            users = load_retailers()
            user_record = next((u for u in users if u["id"] == rid), None)
            
            if not user_record:
                st.error("❌ User ID not found.")
                return
                
            # Dynamic Hash Verification
            input_hash = hashlib.sha256(pin.encode()).hexdigest()
            stored_hash = user_record.get("pin_hash", "")
            
            if input_hash == stored_hash or pin == stored_hash: # Fallback for plain text
                st.session_state.retailer = user_record
                st.session_state.retailer_id = rid
                st.session_state.role = user_record.get("role", "retailer")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("❌ Invalid PIN.")

# ─── PAGES ───
def page_home(r):
    st.markdown(f"### Welcome, {r.get('shop', 'User')} 👋")
    st.info("Use the menu on the left to navigate.")

def page_order():
    st.markdown("## 🛒 Place Order")
    df = load_inventory()
    
    if df.empty:
        st.error("Inventory database is empty.")
        return

    if "cart" not in st.session_state:
        st.session_state.cart = []

    q = st.text_input("Search medicine", placeholder="e.g. Dolo").strip().lower()
    view = df[df["name"].astype(str).str.lower().str.contains(q, na=False)] if q else df

    for _, row in view.head(20).iterrows():
        c1, c2, c3 = st.columns([5, 2, 2])
        c1.markdown(f"**{row['name']}**")
        c2.markdown(f"₹{row['price']:.2f}")
        with c3:
            if st.button("Add", key=f"add_{row['name']}"):
                st.session_state.cart.append({"name": row['name'], "price": row['price'], "qty": 1})
                st.toast(f"Added {row['name']}")

def page_cart():
    st.markdown("## 🛍️ My Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Your cart is empty.")
        return
    
    total = sum(item["price"] * item["qty"] for item in cart)
    for i, item in enumerate(cart):
        st.write(f"{item['name']} - ₹{item['price'] * item['qty']:.2f}")
        
    st.markdown(f"### Total: ₹{total:.2f}")
    if st.button("Checkout", type="primary"):
        st.success("Order Placed Successfully!")
        st.session_state.cart = []

def page_ledger():
    st.markdown("## 💰 Ledger / Balance")
    st.info("Your financial records are synced with the ERP.")

# ─── SIDEBAR & ROUTER ───
MENU = [
    ("home", "🏠", "Home"),
    ("order", "🛒", "Place Order"),
    ("cart", "🛍️", "My Cart"),
    ("ledger", "💰", "Ledger / Balance"),
    ("profile", "👤", "My Profile"),
]

def render_sidebar():
    with st.sidebar:
        st.markdown(f"**Meena Agencies** ({st.session_state.get('role', '').title()})")
        st.markdown("---")
        for key, icon, label in MENU:
            if st.button(f"{icon} {label}", use_container_width=True, type="primary" if st.session_state.get('page') == key else "secondary"):
                st.session_state.page = key
                st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def main():
    if "retailer" not in st.session_state:
        login_screen()
        return

    st.session_state.setdefault("page", "home")
    render_sidebar()

    page = st.session_state.page
    r = st.session_state.retailer
    
    if page == "home": page_home(r)
    elif page == "order": page_order()
    elif page == "cart": page_cart()
    elif page == "ledger": page_ledger()
    elif page == "profile": st.json(r)

main()
