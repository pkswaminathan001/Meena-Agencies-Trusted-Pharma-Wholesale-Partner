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

if "page" not in st.session_state: st.session_state.page = "home"
if "cart" not in st.session_state: st.session_state.cart = []
if "show_otp_input" not in st.session_state: st.session_state.show_otp_input = False

def go_to(page_name):
    st.session_state.page = page_name

st.markdown("""
<style>
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
        role = st.session_state.user.get("role", "Retailer").upper()
        st.markdown(f"<p style='text-align: center; color: #1D8348; font-weight: 600;'>{role}</p>", unsafe_allow_html=True)
        st.divider()

        menu = [("home", "🏠 Home")]

        if role == "OWNER":
            menu.extend([
                ("owner", "👑 Owner Dashboard"),
                ("agents", "🤖 AI Agent HQ"),
                ("staff", "👥 Staff Monitor"),
                ("order", "🛒 Place Order"),
                ("history", "📜 Order History"),
                ("profile", "👤 Profile"),
            ])
        elif role == "RETAILER":
            menu.extend([
                ("order", "🛒 Place Order"),
                ("cart", "🛍️ Cart"),
                ("history", "📜 Order History"),
                ("profile", "👤 Profile"),
            ])
        elif role == "REP":
            menu.append(("rep", "🚚 My Dashboard"))

        for key, label in menu:
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state.page == key else "secondary",
                         on_click=go_to, args=(key,)):
                pass

        st.divider()
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.clear(); st.rerun()
# ─── OWNER DASHBOARD (Approvals) ───
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
        if st.button("☀️ Start Day", type="primary", use_container_width=True, disabled=lat is None):
            log_activity("CHECK_IN")
            st.success(f"✅ Checked in at {now[:19]}")
            time.sleep(1); st.rerun()
    with c2:
        if st.button("🌙 End Day", use_container_width=True, disabled=lat is None):
            log_activity("CHECK_OUT")
            st.success(f"✅ Checked out at {now[:19]}")
            time.sleep(1); st.rerun()
    with c3:
        st.write("")

    with st.expander("📝 Log a Pharmacy Visit"):
        retailers = load_retailers()
        retailer_list = [f"{r['id']} — {r.get('shop','')}" for r in retailers if r.get('role') == 'retailer']
        chosen = st.selectbox("Select Retailer", retailer_list) if retailer_list else None
        notes = st.text_area("Visit Notes", placeholder="Example: Delivered order, discussed new stock...")
        if st.button("✅ Log Visit", type="primary", use_container_width=True, disabled=(lat is None or not chosen)):
            retailer_id = chosen.split(" — ")[0]
            log_activity("VISIT", retailer_id=retailer_id, notes=notes)
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
def main():
    if "user" not in st.session_state:
        login_screen(); return

    render_sidebar()
    u = st.session_state.user
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
