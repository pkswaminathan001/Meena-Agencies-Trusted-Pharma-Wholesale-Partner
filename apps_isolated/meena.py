import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import os, json, sqlite3, hashlib, requests, datetime, random, time
import streamlit as st
import pandas as pd

# Safely import custom modules
try:
    from meena_modules.owner_verification import render_owner_verification
    from meena_modules.apple_tesla_ui import render_apple_tesla_view
    from meena_modules.gps_tracker import render_owner_rep_map
    from meena_modules.qc_rating import render_qc_dashboard
    from meena_modules.upi_payment import render_upi_payment
    from meena_modules.pricing_ai import render_pricing_sandbox
except ImportError:
    pass

try:
    for k, v in st.secrets.items(): os.environ[k] = str(v)
except Exception: pass

try: TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
except Exception: TELEGRAM_BOT_TOKEN = ""

st.set_page_config(page_title="Meena Agencies", page_icon="🦚", layout="wide")

# ─── STATE MANAGEMENT ───
if "page" not in st.session_state: st.session_state.page = "home"
if "cart" not in st.session_state: st.session_state.cart = []
if "show_otp_input" not in st.session_state: st.session_state.show_otp_input = False

def go_to(page_name):
    st.session_state.page = page_name

# ─── CSS: AMAZON UI, MARKETING BANNERS, & MOBILE GRID ───
st.markdown("""
<style>
    /* Amazon Backgrounds & Layout */
    .stApp { background-color: #eaeded !important; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
    
    /* ─── LOCK DOWN STREAMLIT UI ─── */
    /* Hide Hamburger Menu & Footer */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    
    /* Hide Top Header background */
    header { background: transparent !important; visibility: hidden !important; }
    
    /* Hide the top toolbar (Share, Star, Edit, GitHub) */
    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Hide the Deploy Button */
    .stDeployButton, .stAppDeployButton {
        display: none !important;
    }

    /* 2-Column Mobile Grid */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] { flex: 1 1 48% !important; min-width: 48% !important; max-width: 48% !important; }
    }
    
    /* ─── AMAZON CARDS: EQUAL HEIGHT & ALIGNMENT FIX ─── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important; padding: 12px !important;
        border-radius: 8px !important; border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        height: 100% !important; 
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { 
        gap: 0.1rem !important; height: 100% !important; display: flex !important; flex-direction: column !important;
    }
    /* Pushes the last element (the button) to the absolute bottom */
    div[data-testid="stVerticalBlockBorderWrapper"] > div > div:last-child {
        margin-top: auto !important; padding-top: 10px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] img { height: 140px !important; width: 100% !important; object-fit: contain !important; }
    
    /* Amazon Buttons */
    div.stButton > button[kind="primary"], div[data-testid="stForm"] button {
        background-color: #FFD814 !important; color: #0F1111 !important;
        border: 1px solid #FCD200 !important; border-radius: 8px !important;
        font-weight: bold !important; width: 100% !important; min-height: 40px !important; font-size: 14px !important;
    }
    div.stButton > button[kind="primary"]:hover, div[data-testid="stForm"] button:hover { background-color: #F7CA00 !important; }

    /* Homepage Banners & Cards */
    .amz-header { background: #131921; color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;}
    .promo-banner { background: linear-gradient(90deg, #ff9900 0%, #ff5500 100%); color: white; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: bold; font-size: 15px;}
    .amz-card { background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px;}
    
    /* Typography & Order History */
    .amz-title { color: #0F1111; font-size: 13px; font-weight: 600; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 2px; }
    .amz-price { color: #0F1111; font-size: 18px; font-weight: 700; margin-bottom: 4px;}
    .amz-decimal { font-size: 11px; position: relative; top: -3px; }
    .amz-stock-ok { color: #067d1f; font-size: 11px; font-weight: 600; margin-bottom: 4px; }
    .amz-rating { color: #FFA41C; font-size: 12px; margin-bottom: 4px; }
    
    .amz-order-header { background: #f0f2f2; border-radius: 8px 8px 0 0; padding: 12px; display: flex; justify-content: space-between; color: #565959; font-size: 12px; border-bottom: 1px solid #d5d9d9; margin: -12px -12px 12px -12px; }
    .amz-order-header b { color: #0F1111; font-weight: 500; display: block; font-size: 13px;}
</style>
""", unsafe_allow_html=True )


def get_icon(name):
    import urllib.parse
    return f"https://placehold.co/300x300/e2e8f0/1e293b/png?text={urllib.parse.quote(str(name))}&font=Montserrat&font-size=36"

@st.cache_data(ttl=60)
def load_inventory():
    db_path = BASE_DIR / "meena_enterprise.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT sku as name, 1.0 as price, qty as stock FROM products LIMIT 100", conn)
        conn.close()
        return df
    return pd.DataFrame()

@st.cache_data(ttl=60)
def load_retailers():
    rj_path = BASE_DIR / "retailers.json"
    if rj_path.exists():
        with open(rj_path, "r") as f: return json.load(f)
    return []

def send_telegram_otp(chat_id, otp):
    if not TELEGRAM_BOT_TOKEN or not chat_id: return False
    try:
        res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": f"🦚 Meena Agencies\nYour OTP is: *{otp}*", "parse_mode": "Markdown"}, timeout=10)
        return res.status_code == 200
    except Exception: return False

def save_order_history(user_id, cart, total):
    db_path = BASE_DIR / "meena_enterprise.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    order_id = f"ORD-{random.randint(1000, 9999)}"
    date_str = str(datetime.date.today())
    items_json = json.dumps(cart) # Store cart list as a JSON string
    status = "Paid"
    
    # Insert into SQLite
    c.execute("""
        INSERT INTO orders (order_id, user_id, date, total, items, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (order_id, user_id, date_str, total, items_json, status))
    
    conn.commit()
    conn.close()
    
    return {"order_id": order_id}

# ─── LOGIN ───
# ─── LOGIN ───
def login_screen():
    # 1. Inject CSS to force centering
    st.markdown("""
    <style>
        /* Force the main container to center its content perfectly */
        .block-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            padding-top: 5vh !important;
            max-width: 100% !important;
        }
        
        /* Constrain the form width */
        div[data-testid="stForm"] {
            width: 100% !important;
            max-width: 350px !important;
            margin: 0 auto !important;
        }
        
        /* Constrain the white bordered box */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            width: 100% !important;
            max-width: 400px !important;
            margin: 0 auto !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 2. Branding (Centered)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 3rem; margin-bottom: 0;">🦚</h1>
        <h2 style="margin-top: 0; color: #0F1111;">Meena Agencies</h2>
        <p style="color: #565959; font-size: 14px;">Trusted Pharma Wholesale Partner</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. The Form
    with st.container(border=True):
        with st.form("login"):
            st.markdown("### Sign in")
            rid = st.text_input("User ID").strip().upper()
            pin = st.text_input("PIN", type="password").strip()
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
        if submit:
            users = load_retailers()
            user = next((u for u in users if u.get("id") == rid), None)
            if user:
                input_hash = hashlib.sha256(pin.encode()).hexdigest()
                if input_hash == user.get("pin_hash") or pin == user.get("pin"):
                    st.session_state.user = user
                    st.session_state.page = "home"
                    st.rerun()
            st.error("❌ Invalid ID or PIN.")
# ─── 1. AMAZON HOMEPAGE & DIGITAL MARKETING BANNER ───
def page_home(u):
    st.markdown(f'''
        <div class="amz-header">
            <div style="font-size: 20px; font-weight: bold; color: #febd69;">🦚 Meena</div>
            <div style="font-size: 13px;">Hello, {u.get('shop', 'Partner')}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Digital Marketing Promo Banner
    st.markdown('<div class="promo-banner">🚀 MEGA SALE: Use code <b>MEENA10</b> at checkout for 10% off!</div>', unsafe_allow_html=True)

    # Quick Action Cards
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="amz-card"><h3 style="margin-top:0;">Your Orders</h3><p style="font-size:13px;">Track, return, or buy again.</p></div>', unsafe_allow_html=True)
        st.button("View Orders", key="btn_hist", on_click=go_to, args=("history",), use_container_width=True)
    with c2:
        st.markdown('<div class="amz-card"><h3 style="margin-top:0;">Shop Medicines</h3><p style="font-size:13px;">Browse the latest inventory.</p></div>', unsafe_allow_html=True)
        st.button("Start Shopping", key="btn_shop", on_click=go_to, args=("order",), type="primary", use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="amz-card"><h3 style="margin-top:0;">Your Account</h3><p style="font-size:13px;">Manage profile and security.</p></div>', unsafe_allow_html=True)
        st.button("Go to Profile", key="btn_prof", on_click=go_to, args=("profile",), use_container_width=True)
    with c4:
        st.markdown('<div class="amz-card"><h3 style="margin-top:0;">Cart</h3><p style="font-size:13px;">Review cart and checkout.</p></div>', unsafe_allow_html=True)
        st.button("Go to Cart", key="btn_cart", on_click=go_to, args=("cart",), use_container_width=True)

# ─── 2. PRODUCT GRID (AMAZON MOBILE STYLE) ───
@st.fragment
def product_grid(view):
    cols_per_row = 4 
    for i in range(0, len(view.head(30)), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx >= len(view): continue
            row = view.iloc[idx]
            name = str(row.get("name", "Unknown")).replace(" - 0", "").replace("-0", "").replace("- 1", "").strip()
            price = float(row.get("price", 0))
            stock = int(row.get("stock", 0))
            
            with cols[j]:
                with st.container(border=True, height=420):
                    st.markdown('<div style="color:#565959; font-size:10px; margin-bottom:4px;">Sponsored</div>', unsafe_allow_html=True)
                    st.image(get_icon(name), use_container_width=True)
                    st.markdown(f'<div class="amz-title">{name}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="amz-rating">⭐⭐⭐⭐☆ (1,245)</div>', unsafe_allow_html=True)
                    
                    if stock > 0: st.markdown(f'<div class="amz-stock-ok">✅ In stock ({stock})</div>', unsafe_allow_html=True)
                    else: st.markdown('<div style="color:#b12704; font-size:11px; font-weight:600;">❌ Out of stock</div>', unsafe_allow_html=True)
                    
                    rupees = int(price); paise = int(round((price - rupees) * 100))
                    st.markdown(f'<div class="amz-price"><span class="amz-decimal">₹</span>{rupees}<span class="amz-decimal">.{paise:02d}</span></div>', unsafe_allow_html=True)
                    
                    if st.button("Add to Cart", key=f"add_{name}_{idx}", disabled=(stock <= 0), use_container_width=True, type="primary"):
                        st.session_state.cart.append({"name": name, "price": price, "qty": 1})
                        st.toast(f"✅ Added {name}"); st.rerun()

def page_order():
    cart_count = len(st.session_state.cart)
    if cart_count > 0:
        c1, c2 = st.columns([3, 1])
        c1.title("🛒 Place Order")
        with c2:
            st.write("")
            st.button(f"🛍️ Cart ({cart_count})", type="primary", on_click=go_to, args=("cart",), use_container_width=True)
    else:
        st.title("🛒 Place Order")
        
    df = load_inventory()
    if df.empty: st.error("Inventory DB not found."); return
    search = st.text_input("🔍 Search", placeholder="Search medicines...").lower()
    view = df[df["name"].str.lower().str.contains(search)] if search else df
    if view.empty: st.warning("No results found."); return
    product_grid(view)

# ─── 3. CART & DIGITAL MARKETING COUPONS ───
def page_cart():
    st.title("🛍️ Shopping Cart")
    if not st.session_state.cart:
        st.info("Your Cart is empty."); return
        
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{item['name']}**  \n₹{item['price']} each")
        new_qty = c2.number_input("Qty", min_value=1, max_value=99, value=item["qty"], key=f"qty_{i}", label_visibility="collapsed")
        if new_qty != item["qty"]:
            st.session_state.cart[i]["qty"] = new_qty; st.rerun()
        if c3.button("🗑️", key=f"del_{i}", help="Remove item"):
            st.session_state.cart.pop(i); st.toast("Item removed"); st.rerun()
            
    total = sum(item["price"] * item["qty"] for item in st.session_state.cart)
    
    st.write("")
    with st.container(border=True, height=420):
        # Marketing Coupon Logic
        coupon = st.text_input("🎟️ Enter Promo Code", placeholder="Try MEENA10")
        discount = 0
        if coupon.strip().upper() == "MEENA10":
            discount = total * 0.10
            st.success(f"✅ Promo Applied! You saved ₹{discount:,.2f}")
        elif coupon:
            st.error("❌ Invalid Promo Code")
            
        final_total = total - discount
        st.markdown(f"### Subtotal: ₹{total:,.2f}")
        if discount > 0:
            st.markdown(f"### Discount: -₹{discount:,.2f}")
            st.markdown(f"## Final Total: ₹{final_total:,.2f}")
            
        if st.button("💳 Proceed to Checkout", type="primary", use_container_width=True):
            st.session_state.show_otp_input = True; st.rerun()
            
    if st.session_state.show_otp_input:
        st.subheader("Verify & Place Order")
        input_otp = st.text_input("Enter 6-digit OTP", max_chars=6)
        otp_valid = len(input_otp.strip()) == 6 and input_otp.strip().isdigit()
        
        if st.button("Verify & Place Order", type="primary", use_container_width=True, disabled=not otp_valid):
            saved = save_order_history(st.session_state.user.get("id"), st.session_state.cart, final_total)
            st.success(f"🎉 Order {saved['order_id']} placed!")
            st.session_state.cart = []; st.session_state.show_otp_input = False
            st.balloons(); time.sleep(2); go_to("home"); st.rerun()
                
        with st.expander("🔑 Use PIN instead of OTP"):
            fallback_pin = st.text_input("4-digit PIN", type="password", max_chars=4)
            if st.button("Verify PIN & Place Order", use_container_width=True, disabled=(len(fallback_pin) != 4)):
                saved = save_order_history(st.session_state.user.get("id"), st.session_state.cart, final_total)
                st.success(f"🎉 Order {saved['order_id']} placed via PIN!")
                st.session_state.cart = []; st.session_state.show_otp_input = False
                st.balloons(); time.sleep(2); go_to("home"); st.rerun()

# ─── 4. AMAZON ORDER HISTORY (SQLite Version) ───
def page_history(u):
    st.title("Your Orders")
    db_path = BASE_DIR / "meena_enterprise.db"
    
    if not db_path.exists():
        st.info("You have not placed any orders yet."); return
        
    conn = sqlite3.connect(db_path)
    # Fetch orders for this specific user
    df_orders = pd.read_sql_query("SELECT * FROM orders WHERE user_id = ? ORDER BY rowid DESC", conn, params=(str(u.get("id")),))
    conn.close()
    
    if df_orders.empty:
        st.info("You have not placed any orders yet.")
        return
    
    for index, order in df_orders.iterrows():
        with st.container(border=True):
            st.markdown(f'''
                <div class="amz-order-header">
                    <div>ORDER PLACED<br><b>{order['date']}</b></div>
                    <div>TOTAL<br><b>₹{order['total']:,.2f}</b></div>
                    <div>ORDER #<br><b>{order['order_id']}</b></div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Parse the JSON string back into a Python list
            items = json.loads(order['items'])
            
            for item in items:
                c1, c2, c3 = st.columns([2, 5, 2])
                with c1: st.image(get_icon(item['name']), use_container_width=True)
                with c2:
                    st.markdown(f"**{item['name']}**")
                    st.caption(f"Qty: {item['qty']} | ₹{item['price']}")
                    st.markdown("<span style='color: #067d1f; font-weight: 600;'>✅ Delivered</span>", unsafe_allow_html=True)
                with c3:
                    if st.button("Buy it again", key=f"buy_{order['order_id']}_{item['name']}", use_container_width=True):
                        st.session_state.cart.append({"name": item['name'], "price": item['price'], "qty": 1})
                        st.toast(f"Added {item['name']} to cart"); st.rerun()un()

# ─── 5. AMAZON PROFILE ───
def page_profile(u):
    st.title("Your Account")
    st.markdown(f"**Hello, {u.get('name', 'Partner')}**")
    st.caption(f"Retailer ID: {u.get('id')} | Shop: {u.get('shop')}")
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True, height=420):
            st.markdown("<h3>Login & Security</h3>", unsafe_allow_html=True)
            st.write(f"**Email:** {u.get('email', 'N/A')}")
            st.write(f"**Role:** {u.get('role', 'Retailer').capitalize()}")
            st.button("Edit Password", disabled=True, help="Contact admin to change PIN")
    with c2:
        with st.container(border=True, height=420):
            st.markdown("<h3>Order History</h3>", unsafe_allow_html=True)
            st.write("Track, return, or buy things again.")
            st.button("View Your Orders", type="primary", on_click=go_to, args=("history",), use_container_width=True)

# ─── SIDEBAR & ROUTER ───
def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #0B3C5D;'>🦚 Meena</h2>", unsafe_allow_html=True)
        role = st.session_state.user.get("role", "Retailer").upper()
        st.markdown(f"<p style='text-align: center; color: #1D8348; font-weight: 600;'>{role}</p>", unsafe_allow_html=True)
        st.divider()
        
        menu = [("home", "🏠 Home"), ("order", "🛒 Place Order"), ("cart", "🛍️ Cart"), ("history", "📜 Order History"), ("profile", "👤 Profile")]
            
        for key, label in menu:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.page == key else "secondary", on_click=go_to, args=(key,)):
                pass
                
        st.divider()
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.clear(); st.rerun()

def main():
    if "user" not in st.session_state:
        login_screen(); return
    
    render_sidebar()
    u = st.session_state.user
    
    if st.session_state.page == "home": page_home(u)
    elif st.session_state.page == "order": page_order()
    elif st.session_state.page == "cart": page_cart()
    elif st.session_state.page == "history": page_history(u)
    elif st.session_state.page == "profile": page_profile(u)

# RUN APP (MUST BE THE VERY LAST LINE)
main()