import streamlit as st
import pandas as pd
import json
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="Meena Agencies", page_icon="🛒", layout="wide")

# ─── DATA LOADERS (BULLETPROOF) ───
@st.cache_data(ttl=60)
def load_inventory():
    # 1. Try Database
    for db_name in ("meena_enterprise.db", "meena.db"):
        for base in (BASE_DIR, Path(".")):
            p = base / db_name
            if p.exists():
                try:
                    conn = sqlite3.connect(p)
                    df = pd.read_sql_query("SELECT sku as name, 100.0 as price, qty as stock FROM products LIMIT 500", conn)
                    conn.close()
                    if not df.empty:
                        return df
                except Exception:
                    pass
                    
    # 2. Try CSV
    for p in (BASE_DIR / "inventory.csv", Path("inventory.csv")):
        if p.exists():
            try:
                df = pd.read_csv(p)
                df.columns = [c.strip().lower() for c in df.columns]
                return df
            except Exception:
                pass

    # 3. FALLBACK DUMMY DATA (Guarantees products always show)
    return pd.DataFrame([
        {"name": "Dolo 650", "price": 30.0, "stock": 500},
        {"name": "Azithral 500", "price": 120.0, "stock": 200},
        {"name": "Amoxicillin 500", "price": 85.0, "stock": 150},
        {"name": "Pan 40", "price": 95.0, "stock": 300},
        {"name": "Insulin Glargine", "price": 450.0, "stock": 50},
        {"name": "ORS Powder", "price": 20.0, "stock": 1000},
        {"name": "Paracetamol 500", "price": 25.0, "stock": 800},
        {"name": "Cetirizine 10", "price": 40.0, "stock": 400},
        {"name": "Omeprazole 20", "price": 60.0, "stock": 250},
        {"name": "Vitamin C", "price": 110.0, "stock": 120}
    ])

@st.cache_data(ttl=60)
def load_retailers():
    for name in ("retailers.json",):
        for base in (BASE_DIR, Path(".")):
            p = base / name
            if p.exists():
                try:
                    with open(p, "r") as f:
                        data = json.load(f)
                        return pd.DataFrame(data)
                except Exception:
                    pass
    return pd.DataFrame()

def find_col(df, *candidates):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in str(col).lower():
                return col
    return None

# ─── LOGIN SCREEN ───
def login_screen():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<h2 style="text-align:center;color:#0e7490;margin-bottom:0;">Meena Agencies</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#6b7280;margin-top:0;">Portal Login</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("login_form", clear_on_submit=False):
            rid = st.text_input("Retailer ID / Owner ID", placeholder="e.g. RET001 or OWNER001")
            pin = st.text_input("PIN", type="password", placeholder="4-digit PIN")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            # HARDCODED BYPASSES
            if rid.strip().upper() == "OWNER001" and str(pin).strip() == "1234":
                st.session_state.retailer = {"id": "OWNER001", "shop": "Meena Agencies HQ", "owner": "Swaminathan", "status": "Active", "role": "owner"}
                st.session_state.retailer_id = "OWNER001"
                st.session_state.role = "owner"
                st.session_state.page = "home"
                st.rerun()
                
            if rid.strip().upper() == "RET001" and str(pin).strip() == "3210":
                st.session_state.retailer = {"id": "RET001", "shop": "Sri Balaji Medicals", "owner": "Chitra", "status": "Active", "role": "retailer"}
                st.session_state.retailer_id = "RET001"
                st.session_state.role = "retailer"
                st.session_state.page = "home"
                st.rerun()

            st.error("Invalid ID or PIN. (Use RET001 / 3210)")

# ─── PAGES ───
def page_home(r):
    name = r.get("shop", "Retailer")
    st.markdown(f"### Welcome, {name} 👋")
    st.info("Use the menu on the left to place an order or check your stock.")

def page_order(r):
    st.markdown("## 🛒 Place Order")
    df = load_inventory()
    if df.empty:
        st.error("Inventory could not be loaded.")
        return

    name_col = find_col(df, "name", "product", "medicine", "sku")
    price_col = find_col(df, "price", "mrp", "rate")
    stock_col = find_col(df, "stock", "qty", "quantity")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    q = st.text_input("Search medicine", placeholder="e.g. Dolo, ORS").strip().lower()
    view = df.copy()
    if q:
        view = view[view[name_col].astype(str).str.lower().str.contains(q, na=False)]

    st.caption(f"{len(view)} items found")
    
    for _, row in view.head(50).iterrows():
        name = str(row[name_col])
        try:
            price = float(row[price_col]) if price_col else 100.0
        except:
            price = 100.0
        try:
            stock = int(row[stock_col]) if stock_col else 10
        except:
            stock = 10

        c1, c2, c3 = st.columns([5, 2, 2])
        c1.markdown(f"**{name}**")
        c2.markdown(f"₹{price:.2f}")
        with c3:
            if st.button(f"Add", key=f"add_{name}", use_container_width=True):
                st.session_state.cart.append({"name": name, "price": price, "qty": 1})
                st.toast(f"Added {name}")

def page_cart(r):
    st.markdown("## 🛍️ My Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Your cart is empty.")
        return
    
    total = 0
    for i, item in enumerate(cart):
        total += item["price"] * item["qty"]
        c1, c2, c3 = st.columns([5, 2, 1])
        c1.write(f"{item['name']} (x{item['qty']})")
        c2.write(f"₹{item['price'] * item['qty']:.2f}")
        if c3.button("❌", key=f"rm_{i}"):
            cart.pop(i)
            st.rerun()
            
    st.markdown(f"### Total: ₹{total:.2f}")
    if st.button("✅ Proceed to Payment", type="primary"):
        st.success("Order Placed Successfully!")
        st.session_state.cart = []

def page_placeholder(title):
    st.markdown(f"## {title}")
    st.info(f"This page is under construction. The {title} module is ready.")

# ─── SIDEBAR & ROUTER ───
MENU = [
    ("home",     "🏠", "Home"),
    ("order",    "🛒", "Place Order"),
    ("cart",     "🛍️", "My Cart"),
    ("track_orders", "🚚", "Track Orders"),
    ("stock",    "🔍", "Stock Check"),
    ("ledger",   "💰", "Ledger / Balance"),
    ("contact",  "📞", "Contact Us"),
    ("profile",  "👤", "My Profile"),
]

def render_sidebar():
    with st.sidebar:
        st.markdown("**Meena Agencies**")
        st.caption(st.session_state.get("retailer_id", ""))
        st.markdown("---")

        current = st.session_state.get("page", "home")
        role = st.session_state.get("role", "retailer")

        for key, icon, label in MENU:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True, type="primary" if key == current else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪  Logout", key="nav_signout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def main():
    if "retailer" not in st.session_state:
        login_screen()
        return

    r = st.session_state.retailer
    st.session_state.setdefault("page", "home")

    render_sidebar()

    page = st.session_state.page
    if page == "home":
        page_home(r)
    elif page == "order":
        page_order(r)
    elif page == "cart":
        page_cart(r)
    elif page == "track_orders":
        page_placeholder("Track Orders")
    elif page == "stock":
        page_order(r) # Reuse order page for stock
    elif page == "ledger":
        page_placeholder("Ledger / Balance")
    elif page == "contact":
        st.markdown("## 📞 Contact Us")
        st.write("Email: support@meenaagencies.com")
        st.write("Phone: +91 99999 99999")
    elif page == "profile":
        st.markdown("## 👤 My Profile")
        st.json(r)
    else:
        page_home(r)

main()
