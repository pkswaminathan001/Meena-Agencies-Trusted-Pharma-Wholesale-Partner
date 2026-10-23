import streamlit as st
import pandas as pd
import json
import os
import sqlite3
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="Meena Agencies ERP", page_icon="🦚", layout="wide", initial_sidebar_state="expanded")

# ─── ENTERPRISE UI/UX DESIGN SYSTEM (Page 60) ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global Typography & Colors */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #1C2833; /* Charcoal Black */
    }
    .stApp {
        background-color: #F4F6F7; /* Soft Gray Canvas */
    }

    /* Headers */
    h1, h2, h3 {
        color: #0B3C5D !important; /* Deep Medical Blue */
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Buttons (Pharma Green) */
    .stButton > button {
        background-color: #1D8348 !important; /* Pharma Green */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #145c32 !important;
        box-shadow: 0 4px 8px rgba(29, 131, 72, 0.3);
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #D5D8DC !important;
    }

    /* Card Layout for Products */
    .product-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #0B3C5D;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .product-name {
        font-size: 18px;
        font-weight: 600;
        color: #0B3C5D;
        margin-bottom: 5px;
    }
    .product-price {
        font-size: 16px;
        color: #1D8348;
        font-weight: 700;
    }
    .product-stock {
        font-size: 12px;
        color: #D35400; /* Amber Alert */
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Login Card */
    .login-container {
        background: #FFFFFF;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        max-width: 450px;
        margin: 50px auto;
        border-top: 6px solid #0B3C5D;
    }
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

# ─── AUTHENTICATION ───
def login_screen():
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown("""
        <div class="login-container">
            <h2 style="text-align:center; margin-bottom: 30px;">🦚 Meena Agencies</h2>
            <p style="text-align:center; color: #666; margin-bottom: 30px;">Trusted Pharma Wholesale Partner</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.info("💡 **Test Credentials:**\nRetailer: `RET001` / `3210`\nOwner: `OWNER001` / `1234`")
            rid = st.text_input("User ID", placeholder="e.g. RET001").strip().upper()
            pin = st.text_input("PIN", type="password").strip()
            submitted = st.form_submit_button("Secure Login", use_container_width=True)

        if submitted:
            if not rid or not pin:
                st.error("Please enter ID and PIN.")
                return
            
            users = load_retailers()
            user_record = next((u for u in users if u["id"] == rid), None)
            
            if not user_record:
                st.error("❌ User ID not found in database.")
                return
                
            input_hash = hashlib.sha256(pin.encode()).hexdigest()
            stored_hash = user_record.get("pin_hash", "")
            stored_plain = user_record.get("pin", "")
            
            if input_hash == stored_hash or pin == stored_hash or pin == stored_plain:
                st.session_state.retailer = user_record
                st.session_state.retailer_id = rid
                st.session_state.role = user_record.get("role", "retailer")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("❌ Invalid PIN.")

# ─── PAGES ───
def page_home(r):
    st.markdown(f"<h1>Welcome back, {r.get('shop', 'Partner')} 👋</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Here is your business overview for today.</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders Placed", "1,245", "+12%")
    c2.metric("Outstanding Credit", "₹ 1,45,000", "-5%", delta_color="inverse")
    c3.metric("Items in Catalog", "10,000", "Active")

    st.markdown("---")
    st.info("💡 **Quick Tip:** Navigate to 'Place Order' to browse the latest medicine stock and place your orders instantly.")

def page_order():
    st.markdown("<h1>🛒 Place Order</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Browse our catalog and add items to your cart.</p>", unsafe_allow_html=True)
    
    df = load_inventory()
    if df.empty:
        st.error("Inventory database could not be loaded.")
        return

    if "cart" not in st.session_state:
        st.session_state.cart = []

    q = st.text_input("🔍 Search medicines by name", placeholder="Type here...").strip().lower()
    view = df[df["name"].astype(str).str.lower().str.contains(q, na=False)] if q else df

    st.markdown("<br>", unsafe_allow_html=True)
    
    for _, row in view.head(20).iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            # Enterprise Card UI
            st.markdown(f"""
            <div class="product-card">
                <div class="product-name">{row['name']}</div>
                <div class="product-price">₹ {row['price']:.2f}</div>
                <div class="product-stock">In Stock: {row['stock']} units</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("") # Spacing
            st.write("")
            if st.button("➕ Add to Cart", key=f"add_{row['name']}", use_container_width=True):
                st.session_state.cart.append({"name": row['name'], "price": row['price'], "qty": 1})
                st.toast(f"✅ Added {row['name']} to cart!")

def page_cart():
    st.markdown("<h1>🛍️ My Cart</h1>", unsafe_allow_html=True)
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Your cart is empty. Go to 'Place Order' to add items.")
        return
    
    total = 0
    for i, item in enumerate(cart):
        total += item["price"] * item["qty"]
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{item['name']}</div>
            <div class="product-price">₹ {item['price'] * item['qty']:.2f}</div>
            <div class="product-stock">Qty: {item['qty']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"<h2 style='color: #0B3C5D;'>Grand Total: ₹ {total:.2f}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("✅ Checkout", type="primary", use_container_width=True):
            st.success("🎉 Order Placed Successfully! Warehouse notified.")
            st.session_state.cart = []
            st.balloons()

def page_ledger():
    st.markdown("<h1>💰 Ledger & Balance</h1>", unsafe_allow_html=True)
    st.info("Your financial ledger is synced with the Meena Agencies ERP.")

# ─── SIDEBAR & ROUTER ───
MENU = [
    ("home", "🏠", "Dashboard"),
    ("order", "🛒", "Place Order"),
    ("cart", "🛍️", "My Cart"),
    ("ledger", "💰", "Ledger"),
    ("profile", "👤", "My Profile"),
]

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <h2 style='color: #0B3C5D;'>🦚 Meena</h2>
            <p style='color: #1D8348; font-weight: 600;'>{st.session_state.get('role', '').upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        
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
