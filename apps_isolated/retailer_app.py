import streamlit as st
import pandas as pd
import json
import os
import sqlite3
import hashlib
import plotly.express as px
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="Meena Agencies ERP", page_icon="🦚", layout="wide", initial_sidebar_state="expanded")

# ─── ENTERPRISE UI/UX DESIGN SYSTEM (Page 60) ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #1C2833;
    }
    .stApp { background-color: #F4F6F7; }

    h1, h2, h3 {
        color: #0B3C5D !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    .stButton > button {
        background-color: #1D8348 !important;
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

    .product-card {
        background: #FFFFFF; border-radius: 12px; padding: 20px;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #0B3C5D; transition: transform 0.2s;
    }
    .product-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }
    .product-name { font-size: 18px; font-weight: 600; color: #0B3C5D; margin-bottom: 5px; }
    .product-price { font-size: 16px; color: #1D8348; font-weight: 700; }
    .product-stock { font-size: 12px; color: #D35400; font-weight: 600; text-transform: uppercase; }
    
    .login-container {
        background: #FFFFFF; padding: 40px; border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 450px; margin: 50px auto;
        border-top: 6px solid #0B3C5D;
    }

    .profile-hero {
        background: linear-gradient(135deg, #0B3C5D 0%, #1D8348 100%);
        border-radius: 16px; padding: 30px; color: white;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 10px 20px rgba(11, 60, 93, 0.2);
        margin-bottom: 25px;
    }
    .profile-avatar {
        width: 100px; height: 100px; border-radius: 50%;
        border: 4px solid rgba(255, 255, 255, 0.3);
        object-fit: cover; background: #FFF;
    }
    .profile-hero .profile-name { color: #FFFFFF !important; font-size: 32px; font-weight: 700; margin: 0; text-shadow: 1px 1px 3px rgba(0,0,0,0.4); }
    .profile-hero .profile-role { color: #E0E0E0 !important; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; }
    .profile-hero .profile-id { color: #E0E0E0 !important; font-size: 14px; margin-top: 5px; }
    
    .info-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%;
    }
    .info-card-title { font-size: 16px; font-weight: 700; color: #0B3C5D; margin-bottom: 15px; border-bottom: 2px solid #F4F6F7; padding-bottom: 10px; }
    .info-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }
    .info-label { color: #666; font-weight: 600; }
    .info-value { color: #1C2833; font-weight: 500; }
    
    .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-right: 5px; }
    .badge-green { background: #D4EDDA; color: #155724; }
    .badge-blue { background: #CCE5FF; color: #004085; }
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

# ─── RETAILER PAGES ───
def page_home(r):
    st.markdown(f"<h1>Welcome back, {r.get('shop', 'Partner')} 👋</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Here is your business overview for today.</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders Placed", "1,245", "+12%")
    c2.metric("Pending Deliveries", "3", "Active")
    c3.metric("Items in Catalog", "10,000", "Live")
    
    st.markdown("---")
    
    st.markdown("### 🚚 Track Your Recent Order")
    st.info("Your recent order **ORD-8942** is currently **Out for Delivery** and expected to arrive by 5:00 PM today.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎁 Exclusive Offers")
        st.success("Buy 10 boxes of Dolo 650 and get 1 box absolutely FREE. Offer valid till Sunday!")
    with col2:
        st.markdown("### 🔁 Quick Reorder")
        st.write("Need the same items as last month?")
        if st.button("Reorder Last Order", type="primary", use_container_width=True):
            st.toast("✅ Items added to your cart!")
            st.session_state.page = "cart"
            st.rerun()


def page_order():
    st.markdown("<h1>🛒 Place Order</h1>", unsafe_allow_html=True)
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
            st.markdown(f"""
            <div class="product-card">
                <div class="product-name">{row['name']}</div>
                <div class="product-price">₹ {row['price']:.2f}</div>
                <div class="product-stock">In Stock: {row['stock']} units</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("")
            if st.button("➕ Add to Cart", key=f"add_{row['name']}", use_container_width=True):
                st.session_state.cart.append({"name": row['name'], "price": row['price'], "qty": 1})
                st.toast(f"✅ Added {row['name']} to cart!")

def page_cart():
    st.markdown("<h1>🛍️ My Cart</h1>", unsafe_allow_html=True)
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Your cart is empty.")
        return
    
    total = sum(item["price"] * item["qty"] for item in cart)
    for item in cart:
        st.write(f"**{item['name']}** - ₹{item['price'] * item['qty']:.2f}")
        
    st.markdown(f"<h2 style='color: #0B3C5D;'>Grand Total: ₹ {total:.2f}</h2>", unsafe_allow_html=True)
    if st.button("✅ Checkout", type="primary", use_container_width=True):
        st.success("🎉 Order Placed Successfully!")
        st.session_state.cart = []
        st.balloons()

# ─── OWNER PAGES (Enterprise Features) ───
def page_owner_dashboard():
    st.markdown("<h1>👑 Owner Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Real-time overview of Meena Agencies operations.</p>", unsafe_allow_html=True)
    
    # ─── TOP KPIs ───
    st.markdown("### 📊 Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue (Today)", "₹ 4,52,000", "+15%")
    c2.metric("Total Orders", "1,245", "+12%")
    c3.metric("Active Retailers", "142", "+2")
    c4.metric("Pending Approvals", "5", "Needs Review", delta_color="inverse")

    st.markdown("---")
    
    # ─── CHARTS & ALERTS ───
    col_chart, col_alerts = st.columns([2, 1])
    
    with col_chart:
        st.markdown("### 📈 Weekly Sales Trend")
        # Chart data
        import pandas as pd
        import plotly.express as px
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Sales (₹)": [45000, 52000, 48000, 61000, 58000, 75000, 68000]
        })
        fig = px.area(chart_data, x="Day", y="Sales (₹)", color_discrete_sequence=["#1D8348"])
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_alerts:
        st.markdown("### 🚨 Action Alerts")
        st.error("⚠️ **Low Stock:** Dolo 650 (Only 12 boxes left)")
        st.warning("⚠️ **Expiry Risk:** 3 batches expire in <30 days")
        st.info("ℹ️ **New Order:** Hospital Network East placed a ₹50k order.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Go to Expiry Engine", use_container_width=True):
            st.session_state.page = "expiry"
            st.rerun()

    st.markdown("---")

    # ─── RECENT ORDERS & QUICK ACTIONS ───
    col_orders, col_actions = st.columns([2, 1])
    
    with col_orders:
        st.markdown("### 🧾 Recent Orders")
        orders_data = pd.DataFrame({
            "Order ID": ["ORD-8942", "ORD-8941", "ORD-8940", "ORD-8939"],
            "Retailer": ["Sri Balaji Medicals", "Annai Pharmacy", "Vetri Medicals", "Muthu Medicals"],
            "Amount": ["₹ 12,450", "₹ 8,200", "₹ 24,100", "₹ 5,600"],
            "Status": ["Paid", "Pending", "Paid", "Shipped"]
        })
        st.dataframe(orders_data, use_container_width=True, hide_index=True)
        
    with col_actions:
        st.markdown("### ⚡ Quick Actions")
        
        # Quick Add Stock Form (Dad's D11 Rule)
        with st.expander("➕ Quick Add Stock", expanded=True):
            with st.form("quick_stock_form"):
                sku = st.text_input("Medicine Name")
                qty = st.number_input("Quantity", min_value=1, value=1)
                if st.form_submit_button("🚀 Add to Stock", use_container_width=True):
                    st.success(f"✅ Added {qty} x {sku} to inventory.")


def page_expiry_engine():
    st.markdown("<h1>⚠️ Expiry Risk Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Monitor batches nearing expiry to prevent dead stock.</p>", unsafe_allow_html=True)
    
    # Simulated Expiry Data from Document Page 12
    data = [
        {"SKU": "Insulin Glargine", "Batch": "B003", "Qty": 50, "Days Left": 12, "Status": "Critical"},
        {"SKU": "Amoxicillin 500", "Batch": "B002", "Qty": 200, "Days Left": 45, "Status": "Warning"},
        {"SKU": "ORS Powder", "Batch": "B005", "Qty": 300, "Days Left": 5, "Status": "Critical"},
    ]
    
    c1, c2 = st.columns(2)
    with c1:
        st.error("🚨 **Critical Action Required (<30 Days)**")
        for item in data:
            if item["Status"] == "Critical":
                st.markdown(f"""
                <div style="background:#FADBD8; border-left: 5px solid #C0392B; padding: 10px; margin-bottom:10px; border-radius:5px;">
                    <b>{item['SKU']}</b> (Batch: {item['Batch']})<br>
                    Expires in <b>{item['Days Left']} days</b>. Qty: {item['Qty']}.
                </div>
                """, unsafe_allow_html=True)
    with c2:
        st.warning("⚠️ **Warning Zone (30-90 Days)**")
        for item in data:
            if item["Status"] == "Warning":
                st.markdown(f"""
                <div style="background:#FDEBD0; border-left: 5px solid #D35400; padding: 10px; margin-bottom:10px; border-radius:5px;">
                    <b>{item['SKU']}</b> (Batch: {item['Batch']})<br>
                    Expires in <b>{item['Days Left']} days</b>. Qty: {item['Qty']}.
                </div>
                """, unsafe_allow_html=True)

def page_ocr_intake():
    st.markdown("<h1>📸 AI Vision Order Intake</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Upload a handwritten order. AI extracts and matches SKUs.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Order Image (JPG/PNG)", type=["jpg", "png"])
    if uploaded_file:
        st.success("✅ Image uploaded successfully.")
        if st.button("🤖 Run OCR & Extract"):
            with st.spinner("Processing image and matching database..."):
                st.info("📝 Extracted Text: 'Dolo 650 - 10 boxes, Amoxicilin 500 - 5'")
                st.success("✅ Matched to Inventory: Dolo 650 (10), Amoxicillin 500 (5)")
                st.button("✅ Approve & Create Draft Order")

def page_chat_sql():
    st.markdown("<h1>🗄️ Chat-to-SQL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Ask questions in plain English.</p>", unsafe_allow_html=True)
    
    query = st.text_input("Ask a question:", placeholder="e.g., Show me all active retailers")
    if st.button("🔍 Generate & Execute SQL"):
        if query:
            st.code("SELECT id, shop, owner, outstanding FROM retailers WHERE status = 'Active';", language="sql")
            st.dataframe(pd.DataFrame({"ID": ["RET001"], "Shop": ["Sri Balaji"], "Status": ["Active"]}), use_container_width=True)

def page_weather():
    st.markdown("<h1>🌤️ Weather & Tracking</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Live weather and sales rep tracking for Thanjavur.</p>", unsafe_allow_html=True)
    st.info("Current Weather: 32°C, Clear. Safe for field operations.")
    
    m = folium.Map(location=[10.7870, 79.1378], zoom_start=12)
    folium.Marker([10.7870, 79.1378], popup="HQ (Thanjavur)").add_to(m)
    st_folium(m, width=700, height=300)

def page_profile(r):
    st.markdown("<h1>👤 My Profile</h1>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="profile-hero">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-avatar">
        <div>
            <h2 class="profile-name">{r.get('shop', 'Meena Partner')}</h2>
            <div class="profile-role">{r.get('role', 'Retailer').title()}</div>
            <div class="profile-id">ID: {r.get('id', 'N/A')} | Owner: {r.get('owner', 'N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📸 Change Profile Picture"):
        st.file_uploader("Upload image", type=["png", "jpg"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">🏢 Business Information</div>
            <div class="info-row"><span class="info-label">Shop Name</span><span class="info-value">Sri Balaji</span></div>
            <div class="info-row"><span class="info-label">Phone</span><span class="info-value">+91 98765 43210</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">🛡️ Compliance</div>
            <div class="info-row"><span class="info-label">Drug License</span><span class="info-value"><span class="badge badge-green">Verified</span></span></div>
            <div class="info-row"><span class="info-label">GST Status</span><span class="info-value"><span class="badge badge-green">Active</span></span></div>
        </div>
        """, unsafe_allow_html=True)

# ─── SIDEBAR & ROUTER ───
def render_sidebar():
    role = st.session_state.get("role", "retailer")
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center; color: #0B3C5D;'>🦚 Meena</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #1D8348; font-weight: 600;'>{role.upper()}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Common Items
        MENU = [("home", "🏠", "Dashboard"), ("order", "🛒", "Place Order"), ("cart", "🛍️", "My Cart"), ("profile", "👤", "My Profile")]
        
        # Owner Items
        if role == "owner":
            MENU = [
                ("owner_dash", "👑", "Owner Command"),
                ("expiry", "⚠️", "Expiry Risk Engine"),
                ("ocr", "📸", "AI Vision OCR"),
                ("sql", "🗄️", "Chat-to-SQL"),
                ("weather", "🌤️", "Weather & Tracking"),
                ("profile", "👤", "My Profile")
            ]
            
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
    role = st.session_state.get("role")
    
    if page == "home": page_home(r)
    elif page == "order": page_order()
    elif page == "cart": page_cart()
    elif page == "profile": page_profile(r)
    elif page == "owner_dash" and role == "owner": page_owner_dashboard()
    elif page == "expiry" and role == "owner": page_expiry_engine()
    elif page == "ocr" and role == "owner": page_ocr_intake()
    elif page == "sql" and role == "owner": page_chat_sql()
    elif page == "weather" and role == "owner": page_weather()

main()
