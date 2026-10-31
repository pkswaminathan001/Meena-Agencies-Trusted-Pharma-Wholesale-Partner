# VERSION_MARKER = 999
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import os, json, sqlite3, hashlib, requests, datetime, random, time
import streamlit as st

import hashlib
import requests
try:
    from meena_modules.owner_verification import render_owner_verification
    from meena_modules.gps_tracker import render_owner_rep_map
    from meena_modules.qc_rating import render_qc_dashboard
    from meena_modules.upi_payment import render_upi_payment
    from meena_modules.pricing_ai import render_pricing_sandbox
except ImportError:
    pass

import pandas as pd

try:
    for k, v in st.secrets.items(): os.environ[k] = str(v)
except Exception: pass

try: TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
except Exception: TELEGRAM_BOT_TOKEN = ""

st.set_page_config(page_title="Meena Agencies", page_icon="🦚", layout="wide")

# ─── PWA: Manifest + Service Worker injection ───
import streamlit.components.v1 as _pwa_components
_pwa_components.html(
    """
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Meena">
    <meta name="theme-color" content="#131921">
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/app/static/sw.js').catch(e => console.warn('SW reg failed', e));
      }
    </script>
    """,
    height=0, width=0
)


if "page" not in st.session_state: st.session_state.page = "home"
if "cart" not in st.session_state: st.session_state.cart = []
if "show_otp_input" not in st.session_state: st.session_state.show_otp_input = False

def go_to(page_name):
    st.session_state.page = page_name

st.markdown("""
<style>
    /* D3: Hide back button and streamlit headers */
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    .stApp { background-color: #eaeded !important; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    header { background: transparent !important; visibility: hidden !important; }
    [data-testid="stToolbar"] { display: none !important; visibility: hidden !important; height: 0px !important; }
    .stDeployButton, .stAppDeployButton { display: none !important; }
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] { flex: 1 1 48% !important; min-width: 48% !important; max-width: 48% !important; }
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important; padding: 12px !important;
        border-radius: 8px !important; border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        height: 100% !important; display: flex !important; flex-direction: column !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { 
        gap: 0.1rem !important; height: 100% !important; display: flex !important; flex-direction: column !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div > div:last-child {
        margin-top: auto !important; padding-top: 10px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] img { height: 140px !important; width: 100% !important; object-fit: contain !important; }
    div.stButton > button[kind="primary"], div[data-testid="stForm"] button {
        background-color: #FFD814 !important; color: #0F1111 !important;
        border: 1px solid #FCD200 !important; border-radius: 8px !important;
        font-weight: bold !important; width: 100% !important; min-height: 40px !important; font-size: 14px !important;
    }
    div.stButton > button[kind="primary"]:hover, div[data-testid="stForm"] button:hover { background-color: #F7CA00 !important; }
    .amz-header { background: #131921; color: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;}
    .promo-banner { background: linear-gradient(90deg, #ff9900 0%, #ff5500 100%); color: white; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: bold; font-size: 15px;}
    .amz-card { background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px;}
    .amz-title { color: #0F1111; font-size: 13px; font-weight: 600; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 2px; }
    .amz-price { color: #0F1111; font-size: 18px; font-weight: 700; margin-bottom: 4px;}
    .amz-decimal { font-size: 11px; position: relative; top: -3px; }
    .amz-stock-ok { color: #067d1f; font-size: 11px; font-weight: 600; margin-bottom: 4px; }
    .amz-rating { color: #FFA41C; font-size: 12px; margin-bottom: 4px; }
    .amz-order-header { background: #f0f2f2; border-radius: 8px 8px 0 0; padding: 12px; display: flex; justify-content: space-between; color: #565959; font-size: 12px; border-bottom: 1px solid #d5d9d9; margin: -12px -12px 12px -12px; }
    .amz-order-header b { color: #0F1111; font-weight: 500; display: block; font-size: 13px;}
</style>
""", unsafe_allow_html=True)

def get_icon(name):
    import urllib.parse
    return f"https://placehold.co/300x300/e2e8f0/1e293b/png?text={urllib.parse.quote(str(name))}&font=Montserrat&font-size=36"

@st.cache_data(ttl=60)

def send_telegram_otp(chat_id, otp):
    try:
        TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
    except:
        return False
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": chat_id, "text": f"Your OTP is {otp}"})
        return res.status_code == 200
    except:
        return False

def load_inventory():
    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists(): return pd.DataFrame()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
        if not cursor.fetchone():
            conn.close()
            return pd.DataFrame()
        df = pd.read_sql_query("SELECT sku as name, 1.0 as price, qty as stock FROM products LIMIT 100", conn)
        conn.close()
        return df
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_retailers():
    rj_path = BASE_DIR / "retailers.json"
    if rj_path.exists():
        with open(rj_path, "r") as f: return json.load(f)
    return []

def save_order_history(user_id, cart, total):
    db_path = BASE_DIR / "meena_enterprise.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    order_id = f"ORD-{random.randint(1000, 9999)}"
    date_str = str(datetime.date.today())
    items_json = json.dumps(cart)
    status = "Paid"
    c.execute("INSERT INTO orders (order_id, user_id, date, total, items, status) VALUES (?, ?, ?, ?, ?, ?)", (order_id, user_id, date_str, total, items_json, status))
    conn.commit()
    conn.close()
    return {"order_id": order_id}

def login_screen():
    st.markdown("""<style>.block-container { display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; padding-top: 5vh !important; max-width: 100% !important; } div[data-testid="stForm"] { width: 100% !important; max-width: 350px !important; margin: 0 auto !important; } div[data-testid="stVerticalBlockBorderWrapper"] { width: 100% !important; max-width: 400px !important; margin: 0 auto !important; }</style>""", unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><h1 style="font-size: 3rem; margin-bottom: 0;">🦚</h1><h2 style="margin-top: 0; color: #0F1111;">Meena Agencies</h2><p style="color: #565959; font-size: 14px;">Trusted Pharma Wholesale Partner</p></div>""", unsafe_allow_html=True)
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
                salt = 'MEENA_PHARMA_SECURE_SALT_2026'
                input_hash = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000).hex()
                if input_hash == user.get("pin_hash"):
                    st.session_state.user = user
                    st.session_state.page = "home"
                    st.rerun()
            st.error("❌ Invalid ID or PIN.")

def render_add_stock_form():
    """One-shot Add Stock form for owner."""
    st.subheader("➕ Add Stock")
    with st.form("add_stock_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        sku = c1.text_input("SKU / Product Name")
        qty = c2.number_input("Quantity to Add", min_value=1, value=10)
        price = st.number_input("Unit Price (₹)", min_value=0.0, value=10.0)
        submitted = st.form_submit_button("✅ Add to Inventory", type="primary", use_container_width=True)
        if submitted and sku.strip():
            try:
                conn = sqlite3.connect(BASE_DIR / "meena_enterprise.db")
                cur = conn.cursor()
                # Try to update existing, else insert
                cur.execute("SELECT qty FROM products WHERE sku = ?", (sku.strip(),))
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "UPDATE products SET qty = qty + ?, price = ? WHERE sku = ?",
                        (int(qty), float(price), sku.strip())
                    )
                else:
                    cur.execute(
                        "INSERT INTO products (sku, price, qty) VALUES (?, ?, ?)",
                        (sku.strip(), float(price), int(qty))
                    )
                conn.commit()
                conn.close()
                st.success(f"✅ Added {qty} units of '{sku}' @ ₹{price:.2f} to inventory")
            except Exception as e:
                st.error(f"DB error: {e}")

def page_home(u):
    is_owner = u.get("role", "").lower() == "owner"
    
    if is_owner:
        # ─── OWNER: EXECUTIVE COMMAND CENTER ───
        st.markdown(f'<div class="amz-header"><div style="font-size: 20px; font-weight: bold; color: #febd69;">🦚 Meena HQ</div><div style="font-size: 13px;">Executive View</div></div>', unsafe_allow_html=True)
        
        db_path = BASE_DIR / "meena_enterprise.db"
        revenue, pending, low_stock = 0.0, 0, 0
        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                revenue = pd.read_sql_query("SELECT SUM(total) as rev FROM orders WHERE status = 'Paid'", conn).iloc[0]['rev'] or 0.0
                pending = pd.read_sql_query("SELECT COUNT(*) as c FROM orders WHERE status = 'Paid'", conn).iloc[0]['c']
                low_stock = pd.read_sql_query("SELECT COUNT(*) as c FROM products WHERE qty < 15", conn).iloc[0]['c']
                conn.close()
            except: pass
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Total Revenue", f"₹{revenue:,.2f}")
        m2.metric("📦 Pending Orders", f"{pending}")
        m3.metric("⚠️ Low Stock Items", f"{low_stock}")
        
        st.divider()
        st.markdown("### ⚡ Quick Actions")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="amz-card"><h3>👑 Owner Dashboard</h3><p style="font-size:13px;">Approve orders & AI Gauntlet.</p></div>', unsafe_allow_html=True)
            st.button("Open Dashboard", key="btn_owner_home", on_click=go_to, args=("owner",), type="primary", use_container_width=True)
        with c2:
            st.markdown('<div class="amz-card"><h3>🤖 AI Agent HQ</h3><p style="font-size:13px;">Chat with your AI staff.</p></div>', unsafe_allow_html=True)
            st.button("Open AI HQ", key="btn_ai_home", on_click=go_to, args=("agents",), type="primary", use_container_width=True)
        with c3:
            st.markdown('<div class="amz-card"><h3>🛒 Storefront</h3><p style="font-size:13px;">See what retailers see.</p></div>', unsafe_allow_html=True)
            st.button("Browse Store", key="btn_shop_home", on_click=go_to, args=("order",), use_container_width=True)

        st.divider()
        with st.expander("➕ Add Stock (One-Shot)", expanded=False):
            render_add_stock_form()
    else:
        # ─── RETAILER: AMAZON STOREFRONT ───
        st.markdown(f'<div class="amz-header"><div style="font-size: 20px; font-weight: bold; color: #febd69;">🦚 Meena</div><div style="font-size: 13px;">Hello, {u.get("shop", "Partner")}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="promo-banner">🚀 MEGA SALE: Use code <b>MEENA10</b> at checkout for 10% off!</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="amz-card"><h3>Your Orders</h3><p style="font-size:13px;">Track, return, or buy again.</p></div>', unsafe_allow_html=True)
            st.button("View Orders", key="btn_hist", on_click=go_to, args=("history",), use_container_width=True)
        with c2:
            st.markdown('<div class="amz-card"><h3>Shop Medicines</h3><p style="font-size:13px;">Browse the latest inventory.</p></div>', unsafe_allow_html=True)
            st.button("Start Shopping", key="btn_shop", on_click=go_to, args=("order",), type="primary", use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="amz-card"><h3>Your Account</h3><p style="font-size:13px;">Manage profile and security.</p></div>', unsafe_allow_html=True)
            st.button("Go to Profile", key="btn_prof", on_click=go_to, args=("profile",), use_container_width=True)
        with c4:
            st.markdown('<div class="amz-card"><h3>Cart</h3><p style="font-size:13px;">Review cart and checkout.</p></div>', unsafe_allow_html=True)
            st.button("Go to Cart", key="btn_cart", on_click=go_to, args=("cart",), use_container_width=True)
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
    else: st.title("🛒 Place Order")
    df = load_inventory()
    if df.empty:
        st.warning("Inventory database is not available yet. Please try again later.")
        return
    search = st.text_input("🔍 Search", placeholder="🔍 Search Amazons...").lower()
    view = df[df["name"].str.lower().str.contains(search)] if search else df
    if view.empty: st.warning("No results found."); return
    product_grid(view)

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
    with st.container(border=True):
        coupon = st.text_input("🎟️ Enter Promo Code", placeholder="Try MEENA10")
        discount = 0
        if coupon.strip().upper() == "MEENA10":
            discount = total * 0.10
            st.success(f"✅ Promo Applied! You saved ₹{discount:,.2f}")
        elif coupon: st.error("❌ Invalid Promo Code")
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

def page_history(u):
    st.title("Your Orders")
    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists(): st.info("You have not placed any orders yet."); return
    try:
        conn = sqlite3.connect(db_path)
        df_orders = pd.read_sql_query("SELECT * FROM orders WHERE user_id = ? ORDER BY rowid DESC", conn, params=(str(u.get("id")),))
        conn.close()
    except Exception:
        st.info("You have not placed any orders yet."); return
    if df_orders.empty: st.info("You have not placed any orders yet."); return
    for index, order in df_orders.iterrows():
        with st.container(border=True):
            st.markdown(f'''<div class="amz-order-header"><div>ORDER PLACED<br><b>{order['date']}</b></div><div>TOTAL<br><b>₹{order['total']:,.2f}</b></div><div>ORDER #<br><b>{order['order_id']}</b></div></div>''', unsafe_allow_html=True)
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
                        st.toast(f"Added {item['name']} to cart"); st.rerun()

def page_profile(u):
    st.title("Your Account")
    st.markdown(f"**Hello, {u.get('name', 'Partner')}**")
    st.caption(f"Retailer ID: {u.get('id')} | Shop: {u.get('shop')}")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<h3>Login & Security</h3>", unsafe_allow_html=True)
            st.write(f"**Email:** {u.get('email', 'N/A')}")
            st.write(f"**Role:** {u.get('role', 'Retailer').capitalize()}")
            st.button("Edit Password", disabled=True, help="Contact admin to change PIN")
    with c2:
        with st.container(border=True):
            st.markdown("<h3>Order History</h3>", unsafe_allow_html=True)
            st.write("Track, return, or buy things again.")
            st.button("View Your Orders", type="primary", on_click=go_to, args=("history",), use_container_width=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #0B3C5D;'>🦚 Meena</h2>", unsafe_allow_html=True)
        
        # D6: Show logged in user
        shop_name = st.session_state.user.get("shop", "Retailer")
        role = st.session_state.user.get("role", "Retailer").upper()
        st.markdown(f"<p style='text-align: center; color: #1D8348; font-weight: 600;'>{role}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 12px; color: gray;'>Logged in as: {shop_name}</p>", unsafe_allow_html=True)
        st.divider()
        
        menu = [
            ("home", "🏠 Dashboard"),
            ("order", "🛒 Place Order"),
            ("cart", "🛍️ My Cart"),
            ("history", "📜 Order History"),
            ("profile", "👤 Profile")
        ]
        
        if role == "OWNER":
            menu.append(("owner_map", "🗺️ Live Tracking & Owner Tools"))
        
        for key, label in menu:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.get('page') == key else "secondary"):
                st.session_state.page = key
                st.rerun()
                
        st.divider()
        # D4/D5: Single Logout button
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.clear()
            st.rerun()



def page_owner_dashboard(u):
    st.title("👑 Owner Dashboard: Approvals")
    if u.get("role", "").lower() != "owner":
        st.error("Access Denied."); return
    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists(): st.info("No orders found."); return
    conn = sqlite3.connect(db_path)
    df_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Paid' ORDER BY rowid DESC", conn)
    conn.close()
    if df_orders.empty: st.success("All caught up! No pending orders to approve."); return

    for index, order in df_orders.iterrows():
        with st.container(border=True):
            items = json.loads(order['items'])
            st.markdown(f"### Order {order['order_id']} | Total: ₹{order['total']:,.2f}")
            st.caption(f"User ID: {order['user_id']} | Date: {order['date']}")
            
            with st.expander("View Order Items"):
                for item in items: st.write(f"- {item['name']} (Qty: {item['qty']}) @ ₹{item['price']}")
            
            retailers = load_retailers()
            retailer = next((r for r in retailers if r.get("id") == order['user_id']), None)
            
            if retailer:
                if st.button(f"🤖 Run AI Gauntlet Review", key=f"gauntlet_{order['order_id']}"):
                    with st.spinner("Running Maker-Checker Loop..."):
                        try:
                            from apps_isolated.ai_gauntlet import run_order_gauntlet
                            builder_out, critic_out, boss_out = run_order_gauntlet(order.to_dict(), retailer, 185000, 200000)
                            st.info(builder_out)
                            st.warning(critic_out)
                            st.success(boss_out)
                        except Exception as e:
                            st.error(f"AI Error: {e}")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve Order", key=f"app_{order['order_id']}", type="primary"):
                    conn = sqlite3.connect(db_path)
                    conn.execute("UPDATE orders SET status = 'Approved' WHERE order_id = ?", (order['order_id'],))
                    conn.commit()
                    conn.close()
                    st.success("Order Approved!"); time.sleep(1); st.rerun()
                    
                if c2.button("❌ Reject Order", key=f"rej_{order['order_id']}"):
                    conn = sqlite3.connect(db_path)
                    conn.execute("UPDATE orders SET status = 'Rejected' WHERE order_id = ?", (order['order_id'],))
                    conn.commit()
                    conn.close()
                    st.error("Order Rejected!"); time.sleep(1); st.rerun()

# ─── AI AGENT HQ (Stub for now) ───
def render_agent_hq():
    st.title("🤖 AI Agent HQ")
    st.caption("Live agents. Each runs against your DB, critiques itself, and logs results.")

    # Run-all button
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("▶️ Run All Agents", type="primary", use_container_width=True):
            with st.spinner("Running 4 agents with boss loop..."):
                from apps_isolated.ai_agents import run_all_agents
                results = run_all_agents(st.session_state.user.get("id"))
            st.success(f"✅ {len(results)} agents completed")
            st.rerun()
    with c2:
        st.caption(f"Last run: {_last_agent_run()}")

    # 4 agent cards in 2x2 grid
    from apps_isolated.ai_agents import (
        run_inventory_agent, run_credit_agent, run_fraud_agent, run_forecast_agent, run_with_boss
    )
    agents = [
        ("📦 Inventory", "Low stock alerts + reorder quantities", run_inventory_agent),
        ("💰 Credit", "Retailer outstanding vs limit", run_credit_agent),
        ("🚨 Fraud", "Unusual order patterns", run_fraud_agent),
        ("📈 Forecast", "7-day revenue projection", run_forecast_agent),
    ]

    for i in range(0, 4, 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(agents):
                continue
            emoji_title, desc, fn = agents[idx]
            with col:
                with st.container(border=True):
                    st.markdown(f"### {emoji_title}")
                    st.caption(desc)
                    if st.button(f"Run {emoji_title.split()[-1]}", key=f"run_{idx}", use_container_width=True):
                        with st.spinner("Running with boss loop..."):
                            r = run_with_boss(fn)
                        status_emoji = "✅" if r["status"] == "passed" else "⚠️"
                        st.markdown(f"**{status_emoji} {r['status']}** ({r['rounds']} round{'s' if r['rounds'] > 1 else ''})")
                        for finding in r["final"]["findings"][:5]:
                            st.markdown(f"- {finding}")
                        st.caption(f"_{r['final']['summary']}_")

    # History log
    st.divider()
    st.subheader("📜 Recent Agent Runs")
    conn = sqlite3.connect(BASE_DIR / "meena_enterprise.db")
    try:
        df = pd.read_sql_query("SELECT * FROM agent_activity ORDER BY id DESC LIMIT 20", conn)
        conn.close()
        if df.empty:
            st.info("No agent runs yet. Click 'Run All Agents' to start.")
        else:
            df_display = df[["agent", "verdict", "rounds", "summary", "timestamp"]]
            st.dataframe(df_display, use_container_width=True)
    except Exception:
        conn.close()
        st.info("No agent runs yet.")


def _last_agent_run():
    conn = sqlite3.connect(BASE_DIR / "meena_enterprise.db")
    try:
        row = conn.execute("SELECT timestamp FROM agent_activity ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        return row[0] if row else "never"
    except Exception:
        conn.close()
        return "never"
# ─── REP DASHBOARD (Consent-Based Check-in/out) ───

# ═══════════════════════════════════════════════════════
#  GPS TRACKING — Real HTML5 Geolocation
# ═══════════════════════════════════════════════════════
GPS_FILE = BASE_DIR / "sales_rep_locations.json"

def save_rep_location(rep_id, lat, lon, address=""):
    """Save a rep's GPS coordinates to JSON + rep_activity table."""
    import json as _json
    from datetime import datetime as _dt
    
    # 1. Save to JSON
    data = {}
    if GPS_FILE.exists():
        try:
            data = _json.loads(GPS_FILE.read_text())
        except Exception:
            data = {}
    
    if rep_id not in data:
        data[rep_id] = []
    
    data[rep_id].append({
        "timestamp": _dt.now().isoformat(),
        "lat": float(lat),
        "lon": float(lon),
        "address": address
    })
    GPS_FILE.write_text(_json.dumps(data, indent=2))
    
    # 2. Also log into rep_activity table
    try:
        conn = sqlite3.connect(BASE_DIR / "meena_enterprise.db")
        conn.execute(
            "INSERT INTO rep_activity (rep_id, action, timestamp, latitude, longitude, retailer_id, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rep_id, "GPS_CAPTURE", _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
             float(lat), float(lon), "", address)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB save failed: {e}")
    
    return True


def inject_geolocation_js():
    """Inject HTML5 geolocation JS that posts lat/lon back via query params."""
    st.markdown("""
    <script>
    (function() {
        function pushGPS(lat, lon) {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('gps_lat', lat.toFixed(6));
            url.searchParams.set('gps_lon', lon.toFixed(6));
            url.searchParams.set('gps_ts', Date.now());
            window.parent.location.href = url.toString();
        }
        window.getMeenaGPS = function() {
            if (!navigator.geolocation) {
                alert('Geolocation not supported by this browser');
                return;
            }
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    pushGPS(pos.coords.latitude, pos.coords.longitude);
                },
                function(err) {
                    alert('Location error: ' + err.message);
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        };
    })();
    </script>
    """, unsafe_allow_html=True)


def capture_gps_from_query_params():
    """Read lat/lon from st.query_params after JS redirect; save + clear."""
    try:
        qp = st.query_params
    except Exception:
        return False
    
    lat = qp.get("gps_lat")
    lon = qp.get("gps_lon")
    if not lat or not lon:
        return False
    
    rep_id = st.session_state.get("user", {}).get("id", "UNKNOWN")
    try:
        save_rep_location(rep_id, float(lat), float(lon), address="browser-capture")
        st.success(f"📍 Location saved: {float(lat):.4f}, {float(lon):.4f}")
    except Exception as e:
        st.error(f"GPS save error: {e}")
    
    # Clear query params so it doesn't re-save on next rerun
    try:
        st.query_params.clear()
    except Exception:
        pass
    return True


def request_gps_and_log(rep_id, action, retailer_id="", notes=""):
    """Request GPS, save it, and log the activity with coordinates."""
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
    lat, lng = None, None
    if loc and loc.get("coords"):
        lat = loc["coords"]["latitude"]
        lng = loc["coords"]["longitude"]
        save_rep_location(rep_id, lat, lng, address=action)
    
    now_str = str(datetime.datetime.now())
    try:
        conn = sqlite3.connect(BASE_DIR / "meena_enterprise.db")
        conn.execute(
            "INSERT INTO rep_activity (rep_id, action, timestamp, latitude, longitude, retailer_id, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rep_id, action, now_str, lat, lng, retailer_id, notes)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Log error: {e}")
        return False
    
    if lat is not None:
        st.success(f"✅ {action} logged with GPS: {lat:.4f}, {lng:.4f}")
    else:
        st.warning(f"⚠️ {action} logged WITHOUT GPS (browser permission denied)")
    return True


def page_rep(u):
    st.title(f"🚚 Rep Dashboard — {u.get('owner', u.get('name', 'Rep'))}")
    st.caption(f"Rep ID: {u.get('id')} | Shop: {u.get('shop', 'N/A')}")
    st.divider()

    # Location capture (browser asks permission — visible to user)
    from streamlit_js_eval import get_geolocation
    loc = get_geolocation()
    lat, lng = (None, None)
    if loc and loc.get("coords"):
        lat = loc["coords"]["latitude"]
        lng = loc["coords"]["longitude"]
        st.success(f"📍 Current location: {lat:.4f}, {lng:.4f}")
    else:
        st.warning("📍 Please allow location access in your browser to check in.")

    db_path = BASE_DIR / "meena_enterprise.db"
    now = str(datetime.datetime.now())

    def log_activity(action, retailer_id="", notes=""):
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO rep_activity (rep_id, action, timestamp, latitude, longitude, retailer_id, notes) VALUES (?,?,?,?,?,?,?)",
            (u.get("id"), action, now, lat, lng, retailer_id, notes)
        )
        conn.commit()
        conn.close()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("☀️ Start Day", type="primary", use_container_width=True):
            request_gps_and_log(u.get("id"), "CHECK_IN")
            st.success(f"✅ Checked in at {now[:19]}")
            time.sleep(1); st.rerun()
    with c2:
        if st.button("🌙 End Day", use_container_width=True):
            request_gps_and_log(u.get("id"), "CHECK_OUT")
            st.success(f"✅ Checked out at {now[:19]}")
            time.sleep(1); st.rerun()
    with c3:
        st.write("")

    # GPS test button
    capture_gps_from_query_params()
    inject_geolocation_js()
    st.markdown("### 📍 Location Test")
    if st.button("📍 Get My Location", type="primary", use_container_width=True):
        st.markdown(
            "<script>window.getMeenaGPS && window.getMeenaGPS();</script>",
            unsafe_allow_html=True
        )
        st.info("📍 Requesting GPS... If nothing happens, check browser permissions.")
    
    with st.expander("📝 Log a Pharmacy Visit"):
        retailers = load_retailers()
        retailer_list = [f"{r['id']} — {r.get('shop','')}" for r in retailers if r.get('role') == 'retailer']
        chosen = st.selectbox("Select Retailer", retailer_list) if retailer_list else None
        notes = st.text_area("Visit Notes", placeholder="Example: Delivered order, discussed new stock...")
        if st.button("✅ Log Visit", type="primary", use_container_width=True, disabled=not chosen):
            retailer_id = chosen.split(" — ")[0]
            request_gps_and_log(u.get("id"), "VISIT", retailer_id=retailer_id, notes=notes)
            st.success("✅ Visit logged!")
            time.sleep(1); st.rerun()

    st.divider()
    st.subheader("📜 My Recent Activity")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM rep_activity WHERE rep_id = ? ORDER BY id DESC LIMIT 20", conn, params=(u.get("id"),))
    conn.close()
    if df.empty:
        st.info("No activity yet.")
    else:
        for _, row in df.iterrows():
            icon = "☀️" if row['action'] == "CHECK_IN" else "🌙" if row['action'] == "CHECK_OUT" else "📝"
            with st.container(border=True):
                st.markdown(f"**{icon} {row['action']}** — {row['timestamp'][:19]}")
                if pd.notna(row['latitude']):
                    st.caption(f"📍 {row['latitude']:.4f}, {row['longitude']:.4f}")
                if row['retailer_id']:
                    st.caption(f"🏪 Retailer: {row['retailer_id']}")
                if row['notes']:
                    st.caption(f"💬 {row['notes']}")


# ─── OWNER: STAFF MONITOR ───

# ═══════════════════════════════════════════════════════
#  ASSIGNMENT VERIFICATION — Haversine distance check
# ═══════════════════════════════════════════════════════
ASSIGNMENTS_FILE = BASE_DIR / "assignments.json"


def load_assignments():
    if not ASSIGNMENTS_FILE.exists():
        return {}
    try:
        return json.loads(ASSIGNMENTS_FILE.read_text())
    except Exception:
        return {}


def save_assignments(data):
    ASSIGNMENTS_FILE.write_text(json.dumps(data, indent=2))


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lon points."""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlam = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlam/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def latest_rep_location(rep_id):
    """Returns (lat, lon, timestamp) or None."""
    if not GPS_FILE.exists():
        return None
    try:
        data = json.loads(GPS_FILE.read_text())
        points = data.get(rep_id, [])
        if not points:
            return None
        last = points[-1]
        return (last["lat"], last["lon"], last.get("timestamp", ""))
    except Exception:
        return None


def verify_assignment(rep_id, retailer_id):
    """Returns dict with distance and visited status."""
    assignments = load_assignments()
    rep_assignments = assignments.get(rep_id, [])
    assignment = next((a for a in rep_assignments if a.get("retailer_id") == retailer_id), None)
    if not assignment:
        return {"assigned": False, "visited": None, "distance_m": None}

    loc = latest_rep_location(rep_id)
    if not loc:
        return {"assigned": True, "visited": None, "distance_m": None, "note": "no GPS"}

    lat, lon, ts = loc
    d = haversine_m(lat, lon, assignment["lat"], assignment["lon"])
    return {
        "assigned": True,
        "visited": d <= assignment.get("radius_m", 200),
        "distance_m": round(d, 1),
        "rep_lat": lat, "rep_lon": lon,
        "retailer_lat": assignment["lat"], "retailer_lon": assignment["lon"],
        "last_gps_ts": ts,
    }

def page_owner_staff_monitor(u):
    st.title("👥 Staff Monitor")
    st.caption("Live view of all sales reps' activity")

    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists():
        st.info("No data yet."); return

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM rep_activity ORDER BY id DESC LIMIT 200", conn)
    conn.close()

    if df.empty:
        st.info("No rep activity recorded yet.")
        return

    # Map of latest check-ins
    st.subheader("🗺️ Live Map (Latest Check-ins)")
    latest = df[df['latitude'].notna()].head(20)
    if not latest.empty:
        import folium
        from streamlit_folium import st_folium
        center_lat = latest['latitude'].mean()
        center_lng = latest['longitude'].mean()
        m = folium.Map(location=[center_lat, center_lng], zoom_start=10)
        for _, row in latest.iterrows():
            color = "green" if row['action'] == "CHECK_IN" else "red" if row['action'] == "CHECK_OUT" else "blue"
            folium.Marker(
                [row['latitude'], row['longitude']],
                popup=f"{row['rep_id']} — {row['action']} @ {row['timestamp'][:19]}",
                icon=folium.Icon(color=color)
            ).add_to(m)
        st_folium(m, width=700, height=400)
    else:
        st.warning("No location data available yet.")

    # Hours worked per rep (check-in to check-out)
    st.subheader("⏱️ Hours Worked (Latest Day)")
    from datetime import datetime as _dt
    summary = []
    for rep_id in df['rep_id'].unique():
        rep_df = df[df['rep_id'] == rep_id]
        check_ins = rep_df[rep_df['action'] == "CHECK_IN"]
        check_outs = rep_df[rep_df['action'] == "CHECK_OUT"]
        if not check_ins.empty and not check_outs.empty:
            try:
                in_time = _dt.strptime(check_ins.iloc[0]['timestamp'][:19], "%Y-%m-%d %H:%M:%S")
                out_time = _dt.strptime(check_outs.iloc[0]['timestamp'][:19], "%Y-%m-%d %H:%M:%S")
                hours = (out_time - in_time).total_seconds() / 3600
                summary.append({"Rep": rep_id, "Hours": round(hours, 2),
                                "Visits": len(rep_df[rep_df['action'] == "VISIT"])})
            except: pass
    if summary:
        st.dataframe(pd.DataFrame(summary), use_container_width=True)
    else:
        st.info("Not enough check-in/out data yet to compute hours.")

    st.divider()
    st.subheader("📜 Recent Activity Log")
    df_display = df[['rep_id', 'action', 'timestamp', 'retailer_id', 'notes']].head(30)
    st.dataframe(df_display, use_container_width=True)

    # ─── GPS: Tamil Nadu Map — Assignments ───
    st.divider()
    st.subheader("📍 Tamil Nadu Map — Assignments & Verification")
    
    assignments = load_assignments()
    if not assignments:
        st.info("📋 No assignments yet. Add one below to start tracking rep visits.")
    else:
        import folium
        from streamlit_folium import st_folium
        
        # Build verification rows
        rows = []
        for rep_id, reps_assignments in assignments.items():
            loc = latest_rep_location(rep_id)
            for a in reps_assignments:
                v = verify_assignment(rep_id, a.get("retailer_id"))
                rows.append({
                    "Rep": rep_id,
                    "Retailer": a.get("name", a.get("retailer_id")),
                    "Status": "✅ Visited" if v.get("visited") else ("⚠️ No GPS" if v.get("visited") is None else "❌ Not visited"),
                    "Distance (m)": v.get("distance_m", "—"),
                    "Last GPS": v.get("last_gps_ts", "—")[:16] if v.get("last_gps_ts") else "—",
                })
        
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        
        # Map centered on Tamil Nadu
        m = folium.Map(location=[11.1271, 78.6569], zoom_start=7, tiles="OpenStreetMap")
        
        # Add rep pins (blue)
        if GPS_FILE.exists():
            try:
                gps_data = json.loads(GPS_FILE.read_text())
                for rep_id, points in gps_data.items():
                    if not points:
                        continue
                    last = points[-1]
                    folium.Marker(
                        [last["lat"], last["lon"]],
                        popup=f"👤 {rep_id}<br>Last: {last.get('timestamp','')[:16]}",
                        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
                    ).add_to(m)
            except Exception:
                pass
        
        # Add retailer pins (green = visited, red = not visited)
        for rep_id, reps_assignments in assignments.items():
            for a in reps_assignments:
                v = verify_assignment(rep_id, a.get("retailer_id"))
                color = "green" if v.get("visited") else "red"
                folium.Marker(
                    [a["lat"], a["lon"]],
                    popup=f"🏪 {a.get('name','?')}<br>Rep: {rep_id}<br>{'✅ Visited' if v.get('visited') else '❌ Not visited'}",
                    icon=folium.Icon(color=color, icon="shopping-cart", prefix="fa"),
                ).add_to(m)
        
        st_folium(m, width=900, height=500, key="tn_assignments_map")
    
    # Add new assignment form
    with st.expander("➕ Assign Pharmacy to Rep"):
        with st.form("new_assignment", clear_on_submit=True):
            retailers = load_retailers()
            rep_options = [u for u in retailers if u.get("role") == "rep"]
            rep_choice = st.selectbox(
                "Rep",
                [f"{r['id']} — {r.get('name', r.get('shop',''))}" for r in rep_options]
            ) if rep_options else None
            name = st.text_input("Pharmacy Name", placeholder="e.g., Sri Balaji Medicals")
            c1, c2, c3 = st.columns(3)
            lat = c1.number_input("Latitude", value=13.0827, format="%.6f")
            lon = c2.number_input("Longitude", value=80.2707, format="%.6f")
            radius = c3.number_input("Radius (m)", min_value=50, max_value=2000, value=200)
            submitted = st.form_submit_button("💾 Save Assignment", type="primary", use_container_width=True)
            if submitted and rep_choice and name.strip():
                rep_id = rep_choice.split(" — ")[0]
                data = load_assignments()
                data.setdefault(rep_id, []).append({
                    "retailer_id": f"ASSIGN-{len(data.get(rep_id, [])) + 1:03d}",
                    "name": name.strip(),
                    "lat": float(lat),
                    "lon": float(lon),
                    "radius_m": int(radius),
                })
                save_assignments(data)
                st.success(f"✅ Assigned '{name}' to rep {rep_id}")
                st.rerun()


# ═══════════════════════════════════════════════════════
#  AI DOTS — Floating ChatGPT-style Chat Widget
# ═══════════════════════════════════════════════════════
def _ai_dots_css():
    st.markdown("""
    <style>
    .ai-dots-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 62px;
        height: 62px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
        box-shadow: 0 4px 20px rgba(0,212,255,0.5);
        color: white;
        font-size: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 99999;
        transition: transform 0.2s, box-shadow 0.2s;
        border: none;
    }
    .ai-dots-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 28px rgba(0,212,255,0.7);
    }
    .chat-window {
        position: fixed;
        bottom: 105px;
        right: 30px;
        width: 380px;
        max-width: calc(100vw - 60px);
        height: 520px;
        max-height: calc(100vh - 150px);
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
        z-index: 99998;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .chat-window-header {
        background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
        color: white;
        padding: 14px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
    }
    .chat-window-body {
        flex: 1;
        padding: 12px;
        overflow-y: auto;
        background: #fafafa;
    }
    @media (max-width: 480px) {
        .chat-window {
            width: calc(100vw - 20px);
            right: 10px;
            bottom: 90px;
        }
        .ai-dots-btn {
            right: 20px;
            bottom: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_ai_dots(user=None):
    """Render floating AI Dots chat button + drawer."""
    _ai_dots_css()
    
    if "ai_dots_open" not in st.session_state:
        st.session_state.ai_dots_open = False
    if "ai_dots_messages" not in st.session_state:
        st.session_state.ai_dots_messages = [
            {"role": "assistant", "content": "Vanakkam! 🙏 I'm Meena AI. Ask me about orders, stock, retailers, or anything."}
        ]
    
    # ─── Floating toggle button ───
    # We use a Streamlit button styled as the floating circle
    # Position it via CSS targeting the button container
    st.markdown(
        """
        <style>
        div[data-testid="stButton"]:has(button[kind="primary"][aria-label="ai_dots_toggle"]) {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 99999 !important;
            width: 62px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Button to toggle
    btn_label = "✕" if st.session_state.ai_dots_open else "💬"
    if st.button(btn_label, key="ai_dots_btn", type="primary", help="Ask Meena AI"):
        st.session_state.ai_dots_open = not st.session_state.ai_dots_open
        st.rerun()
    
    # ─── Chat drawer (only when open) ───
    if st.session_state.ai_dots_open:
        with st.container():
            st.markdown('<div class="chat-window">', unsafe_allow_html=True)
            st.markdown('<div class="chat-window-header"><span>🤖 Meena AI</span><span style="font-size:12px;opacity:0.8;">Groq</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-window-body">', unsafe_allow_html=True)
            
            # Render history
            for msg in st.session_state.ai_dots_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Input
            prompt = st.chat_input("Ask Meena AI...", key="ai_dots_input")
            if prompt:
                st.session_state.ai_dots_messages.append({"role": "user", "content": prompt})
                # Placeholder reply — Step 5 wires Groq
                st.session_state.ai_dots_messages.append({
                    "role": "assistant",
                    "content": "🤖 (Groq brain arrives in Step 5 — wiring next!)"
                })
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    if "user" not in st.session_state:
        login_screen(); return

    render_sidebar()
    u = st.session_state.user
    render_ai_dots(u)
    role = u.get("role", "").lower()

    if role == "owner":
        if st.session_state.page == "home": page_home(u)
        elif st.session_state.page == "owner": page_owner_dashboard(u)
        elif st.session_state.page == "agents": render_agent_hq()
        elif st.session_state.page == "staff": page_owner_staff_monitor(u)
        elif st.session_state.page == "order": page_order()
        elif st.session_state.page == "cart": page_cart()
        elif st.session_state.page == "history": page_history(u)
        elif st.session_state.page == "profile": page_profile(u)
        else: page_home(u)

    elif role == "retailer":
        if st.session_state.page == "home": page_home(u)
        elif st.session_state.page == "order": page_order()
        elif st.session_state.page == "cart": page_cart()
        elif st.session_state.page == "history": page_history(u)
        elif st.session_state.page == "profile": page_profile(u)
        else: page_home(u)

    elif role == "rep":
        if st.session_state.page == "rep": page_rep(u)
        else: page_rep(u)

    else:
        st.error("❌ Access Denied.")
        if st.button("Sign Out"):
            st.session_state.clear(); st.rerun()
   
# Run the app
main()
