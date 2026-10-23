import streamlit as st
import pandas as pd
import json
import os
import sqlite3
import hashlib
from pathlib import Path
from PIL import Image
import io

BASE_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="Meena Agencies ERP", page_icon="🦚", layout="wide", initial_sidebar_state="expanded")

# ─── ENTERPRISE UI/UX DESIGN SYSTEM ───
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
        color: #0B3C5D;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .profile-hero h2, .profile-hero h3 {
        color: #FFFFFF !important; /* Force white inside the hero card */
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

    /* ─── ADVANCED PROFILE UI ─── */
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
    .badge-orange { background: #FFF3CD; color: #856404; }
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
            st.markdown(f"""
            <div class="product-card">
                <div class="product-name">{row['name']}</div>
                <div class="product-price">₹ {row['price']:.2f}</div>
                <div class="product-stock">In Stock: {row['stock']} units</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("")
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

def page_profile(r):
    st.markdown("<h1>👤 My Profile</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Manage your account details and security settings.</p>", unsafe_allow_html=True)

    # Initialize session state for profile picture if not present
    if "profile_pic" not in st.session_state:
        st.session_state.profile_pic = None

    # ─── HERO BANNER ───
    hero_html = f"""
    <div class="profile-hero">
        <div style="text-align: center;">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="profile-avatar" alt="Profile">
        </div>
        <div>
            <h2 class="profile-name">{r.get('shop', 'Meena Partner')}</h2>
            <div class="profile-role">{r.get('role', 'Retailer').title()}</div>
            <div class="profile-id">ID: {r.get('id', 'N/A')} | Owner: {r.get('owner', 'N/A')}</div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ─── PROFILE PICTURE UPLOAD ───
    with st.expander("📸 Change Profile Picture", expanded=False):
        uploaded_file = st.file_uploader("Upload a new profile image (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="New Profile Preview", width=150)
            if st.button("Save Profile Picture"):
                st.session_state.profile_pic = uploaded_file.getvalue()
                st.success("✅ Profile picture updated successfully!")
                st.rerun()

    # If a profile pic was uploaded, show it in the hero (This part would require a custom HTML component to replace the static URL, but we'll keep it simple for now)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── BUSINESS DETAILS & COMPLIANCE ───
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">🏢 Business Information</div>
            <div class="info-row"><span class="info-label">Shop Name</span><span class="info-value">Sri Balaji Medicals</span></div>
            <div class="info-row"><span class="info-label">Owner</span><span class="info-value">Chitra</span></div>
            <div class="info-row"><span class="info-label">Phone</span><span class="info-value">+91 98765 43210</span></div>
            <div class="info-row"><span class="info-label">Email</span><span class="info-value">contact@sribalaji.com</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">🛡️ Compliance & Security</div>
            <div class="info-row"><span class="info-label">Drug License</span><span class="info-value"><span class="badge badge-green">Verified</span></span></div>
            <div class="info-row"><span class="info-label">GST Status</span><span class="info-value"><span class="badge badge-green">Active</span></span></div>
            <div class="info-row"><span class="info-label">Account Status</span><span class="info-value"><span class="badge badge-blue">Active</span></span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── FINANCIAL SNAPSHOT ───
    st.markdown("### 💰 Financial Snapshot")
    f1, f2, f3 = st.columns(3)
    f1.metric("Total Orders Placed", "1,245")
    f2.metric("Outstanding Credit", "₹ 1,45,000")
    f3.metric("Credit Limit", "₹ 2,00,000")

    st.markdown("---")

    # ─── ACCOUNT ACTIONS ───
    st.markdown("### ⚙️ Account Settings")
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("🔑 Change PIN", use_container_width=True):
            st.info("PIN change request sent to Admin.")
    with a2:
        if st.button("📞 Contact Support", use_container_width=True):
            st.info("Support: +91 99999 99999")
    with a3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ─── SIDEBAR & ROUTER ───
MENU = [
    ("home", "🏠", "Dashboard"),
    ("order", "🛒", "Place Order"),
    ("cart", "🛍️", "My Cart"),
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
    elif page == "profile": page_profile(r)

main()
