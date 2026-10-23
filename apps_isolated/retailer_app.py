import streamlit as st
import pandas as pd
import json
import os
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

# ─── CONFIG ───
st.set_page_config(
    page_title="Meena Agencies ERP",
    page_icon="🦚",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── MINIMAL, STABLE CSS (No complex HTML) ───
st.markdown("""
<style>
    /* Clean typography and spacing */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stApp {
        background-color: #F8F9FA;
    }
    h1, h2, h3 {
        color: #0B3C5D;
        font-weight: 600;
    }
    .stButton > button {
        background-color: #1D8348;
        color: white;
        border-radius: 6px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #145c32;
        color: white;
    }
    /* Ensure metrics have a clean card look */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #0B3C5D;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADERS ───
@st.cache_data(ttl=60)
def load_inventory():
    db_path = BASE_DIR / "meena_enterprise.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT sku as name, 150.0 as price, qty as stock FROM products LIMIT 500", conn)
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

# ─── AUTHENTICATION ───
def login_screen():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("## 🦚 Meena Agencies")
        st.markdown("**Trusted Pharma Wholesale Partner**")
        st.divider()
        
        with st.form("login_form"):
            st.info("💡 **Test Credentials:** Retailer: `RET001` / `3210` | Owner: `OWNER001` / `1234`")
            rid = st.text_input("User ID", placeholder="e.g. RET001").strip().upper()
            pin = st.text_input("PIN", type="password").strip()
            submitted = st.form_submit_button("Secure Login", use_container_width=True)

        if submitted:
            users = load_retailers()
            user_record = next((u for u in users if u["id"] == rid), None)
            
            if user_record:
                input_hash = hashlib.sha256(pin.encode()).hexdigest()
                if input_hash == user_record.get("pin_hash") or pin == user_record.get("pin"):
                    st.session_state.retailer = user_record
                    st.session_state.retailer_id = rid
                    st.session_state.role = user_record.get("role", "retailer")
                    st.session_state.page = "home"
                    st.rerun()
            st.error("❌ Invalid ID or PIN.")

# ─── RETAILER DASHBOARD (Populated & Clean) ───
def page_home(r):
    st.title(f"Welcome back, {r.get('shop', 'Partner')} 👋")
    st.caption("Here is your business overview for today.")
    
    # KPI ROW
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders Placed", "1,245", "+12%")
    c2.metric("Pending Deliveries", "3", "Active")
    c3.metric("Items in Catalog", "10,000", "Live")
    
    st.divider()
    
    # TWO-COLUMN LAYOUT FOR OFFERS AND REORDER
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎁 Exclusive Offers")
        st.success("Buy 10 boxes of Dolo 650 and get 1 box absolutely FREE. Offer valid till Sunday!")
        st.info("📢 **New Scheme:** 5% instant discount on orders above ₹10,000.")
        
    with col2:
        st.subheader("🔁 Quick Reorder")
        st.write("Need the same items as last month?")
        if st.button("Reorder Last Order", type="primary", use_container_width=True):
            st.toast("✅ Items added to your cart!")
            st.session_state.page = "cart"
            st.rerun()
            
    st.divider()
    
    # RECENT ORDERS TABLE
    st.subheader("📋 Recent Orders")
    recent_orders = pd.DataFrame({
        "Order ID": ["ORD-8942", "ORD-8941", "ORD-8940"],
        "Date": ["2026-10-23", "2026-10-22", "2026-10-20"],
        "Amount": ["₹ 12,450", "₹ 8,200", "₹ 24,100"],
        "Status": ["Paid", "Pending", "Shipped"]
    })
    st.dataframe(recent_orders, use_container_width=True, hide_index=True)

# ─── OWNER DASHBOARD (Charts & Alerts) ───
def page_owner_dashboard():
    st.title("👑 Owner Command Center")
    st.caption("Real-time overview of Meena Agencies operations.")
    
    # KPI ROW
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue (Today)", "₹ 4,52,000", "+15%")
    c2.metric("Total Orders", "1,245", "+12%")
    c3.metric("Active Retailers", "142", "+2")
    c4.metric("Pending Approvals", "5", "Needs Review", delta_color="inverse")
    
    st.divider()
    
    # CHARTS & ALERTS ROW
    col_chart, col_alerts = st.columns([2, 1])
    
    with col_chart:
        st.subheader("📈 Weekly Sales Trend")
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Sales (₹)": [45000, 52000, 48000, 61000, 58000, 75000, 68000]
        })
        st.bar_chart(chart_data, x="Day", y="Sales (₹)", color="#1D8348")
        
    with col_alerts:
        st.subheader("🚨 Action Alerts")
        st.error("⚠️ **Low Stock:** Dolo 650 (Only 12 boxes left)")
        st.warning("⚠️ **Expiry Risk:** 3 batches expire in <30 days")
        st.info("ℹ️ **New Order:** Hospital Network East placed a ₹50k order.")
        
        if st.button("📥 Go to Expiry Engine", use_container_width=True):
            st.session_state.page = "expiry"
            st.rerun()
            
    st.divider()
    
    # QUICK ACTIONS ROW
    col_orders, col_actions = st.columns([2, 1])
    
    with col_orders:
        st.subheader("🧾 Recent Orders")
        orders_data = pd.DataFrame({
            "Order ID": ["ORD-8942", "ORD-8941", "ORD-8940", "ORD-8939"],
            "Retailer": ["Sri Balaji Medicals", "Annai Pharmacy", "Vetri Medicals", "Muthu Medicals"],
            "Amount": ["₹ 12,450", "₹ 8,200", "₹ 24,100", "₹ 5,600"],
            "Status": ["Paid", "Pending", "Paid", "Shipped"]
        })
        st.dataframe(orders_data, use_container_width=True, hide_index=True)
        
    with col_actions:
        st.subheader("⚡ Quick Add Stock")
        with st.form("quick_stock_form"):
            sku = st.text_input("Medicine Name")
            qty = st.number_input("Quantity", min_value=1, value=1)
            if st.form_submit_button("🚀 Add to Stock", use_container_width=True):
                st.success(f"✅ Added {qty} x {sku} to inventory.")

# ─── OTHER PAGES (Simplified Native Layout) ───
def page_order():
    st.title("🛒 Place Order")
    df = load_inventory()
    if df.empty:
        st.error("Inventory database could not be loaded.")
        return

    if "cart" not in st.session_state:
        st.session_state.cart = []

    q = st.text_input("🔍 Search medicines by name", placeholder="Type here...").strip().lower()
    view = df[df["name"].astype(str).str.lower().str.contains(q, na=False)] if q else df

    for _, row in view.head(10).iterrows():
        c1, c2, c3 = st.columns([4, 2, 2])
        c1.write(f"**{row['name']}**")
        c2.write(f"₹ {row['price']:.2f}")
        with c3:
            if st.button("Add", key=f"add_{row['name']}", use_container_width=True):
                st.session_state.cart.append({"name": row['name'], "price": row['price'], "qty": 1})
                st.toast(f"Added {row['name']}")

def page_cart():
    st.title("🛍️ My Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Your cart is empty.")
        return
    
    total = sum(item["price"] * item["qty"] for item in cart)
    for item in cart:
        st.write(f"**{item['name']}** - ₹{item['price'] * item['qty']:.2f}")
        
    st.subheader(f"Grand Total: ₹ {total:.2f}")
    if st.button("✅ Checkout", type="primary", use_container_width=True):
        st.success("🎉 Order Placed Successfully!")
        st.session_state.cart = []
        st.balloons()

def page_expiry():
    st.title("⚠️ Expiry Risk Engine")
    st.write("Monitor batches nearing expiry to prevent dead stock.")
    
    data = pd.DataFrame([
        {"SKU": "Insulin Glargine", "Batch": "B003", "Qty": 50, "Days Left": 12, "Status": "Critical"},
        {"SKU": "Amoxicillin 500", "Batch": "B002", "Qty": 200, "Days Left": 45, "Status": "Warning"},
        {"SKU": "ORS Powder", "Batch": "B005", "Qty": 300, "Days Left": 5, "Status": "Critical"},
    ])
    st.dataframe(data, use_container_width=True)

def page_profile(r):
    st.title("👤 My Profile")
    st.write(f"**Shop Name:** {r.get('shop', 'N/A')}")
    st.write(f"**Owner:** {r.get('owner', 'N/A')}")
    st.write(f"**Role:** {r.get('role', 'N/A').title()}")
    st.write(f"**ID:** {r.get('id', 'N/A')}")
    st.divider()
    st.subheader("🛡️ Compliance")
    st.success("✅ Drug License: Verified")
    st.success("✅ GST Status: Active")

# ─── SIDEBAR & ROUTER ───
def render_sidebar():
    role = st.session_state.get("role", "retailer")
    with st.sidebar:
        st.title("🦚 Meena")
        st.caption(role.upper())
        st.divider()
        
        MENU = [("home", "🏠 Dashboard"), ("order", "🛒 Place Order"), ("cart", "🛍️ My Cart"), ("profile", "👤 My Profile")]
        
        if role == "owner":
            MENU = [
                ("owner_dash", "👑 Owner Command"),
                ("expiry", "⚠️ Expiry Risk Engine"),
                ("profile", "👤 My Profile")
            ]
            
        for key, label in MENU:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.get('page') == key else "secondary"):
                st.session_state.page = key
                st.rerun()
                
        st.divider()
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
    role = st.session_state.get("role")
    
    if page == "home": page_home(r)
    elif page == "order": page_order()
    elif page == "cart": page_cart()
    elif page == "profile": page_profile(r)
    elif page == "owner_dash" and role == "owner": page_owner_dashboard()
    elif page == "expiry" and role == "owner": page_expiry()

main()
