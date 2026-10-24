import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import os, json, sqlite3, hashlib, requests, datetime, random, time
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

try:
    for k, v in st.secrets.items():
        os.environ[k] = str(v)
except Exception:
    pass

try:
    from meena_modules.owner_verification import render_owner_verification
    from meena_modules.apple_tesla_ui import render_apple_tesla_view
    from meena_modules.gps_tracker import render_owner_rep_map
    from meena_modules.qc_rating import render_qc_dashboard
    from meena_modules.upi_payment import render_upi_payment
    from meena_modules.pricing_ai import render_pricing_sandbox
    from meena_modules.invoice_generator import generate_invoice_pdf
except ImportError:
    pass

try:
    TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
except Exception:
    TELEGRAM_BOT_TOKEN = ""

st.set_page_config(page_title="Meena Agencies", page_icon="🦚", layout="wide")

# ─── CSS: BRING BACK HAMBURGER MENU & KEEP AMAZON GRID ───
st.markdown("""
<style>
    /* 1. Hide default Streamlit menu & footer, but keep the header transparent */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
    
    /* 2. Force the mobile hamburger menu (sidebar toggle) to be visible & styled */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        color: #0B3C5D !important;
        background-color: white !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        padding: 8px !important;
        margin: 15px !important;
        z-index: 99999 !important;
    }
    
    .block-container {padding-top: 1rem; padding-bottom: 0; max-width: 1200px;}

    /* 3. FORCE 2-COLUMN GRID ON MOBILE */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.3rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            flex: 1 1 48% !important;
            min-width: 48% !important;
            max-width: 48% !important;
        }
    }

    /* 4. KILL WHITESPACE INSIDE CARDS */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 6px !important;
        border-radius: 8px;
        border: 1px solid #e5e5e5;
        margin-bottom: 4px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        gap: 0.05rem !important;
    }
    
    /* 5. FIX IMAGE SIZE */
    div[data-testid="stVerticalBlockBorderWrapper"] img {
        height: 130px !important;
        width: 100% !important;
        object-fit: contain !important;
        margin-bottom: 2px !important;
        border-radius: 4px;
    }
    
    /* 6. AMAZON YELLOW BUTTON */
    div.stButton > button[kind="primary"] {
        background-color: #FFD814 !important;
        color: #0F1111 !important;
        border: 1px solid #FCD200 !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        padding: 2px 8px !important;
        width: 100% !important;
        min-height: 28px !important;
        height: 28px !important;
        font-size: 12px !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #F7CA00 !important;
    }

    /* 7. TIGHT TYPOGRAPHY */
    .amz-sponsored { color: #565959; font-size: 10px; font-weight: 400; margin-bottom: 2px; }
    .amz-title { 
        color: #0F1111; 
        font-size: 13px; 
        font-weight: 600; 
        line-height: 1.2; 
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 2px;
    }
    .amz-price { color: #0F1111; font-size: 18px; font-weight: 700; margin-bottom: 4px;}
    .amz-decimal { font-size: 11px; position: relative; top: -3px; }
    .amz-stock-ok { color: #067d1f; font-size: 10px; font-weight: 600; margin-bottom: 4px; }
    .amz-stock-out { color: #b12704; font-size: 10px; font-weight: 600; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── BETTER MEDICINE IMAGE GENERATOR ───
def get_icon(name):
    import urllib.parse
    clean_name = str(name).replace(" ", "+")
    # Light grey background, dark text. Looks like a product package.
    return f"https://placehold.co/300x300/e2e8f0/1e293b/png?text={clean_name}&font=Montserrat&font-size=36"

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
        with open(rj_path, "r") as f:
            return json.load(f)
    return []

def send_telegram_otp(chat_id, otp):
    if not TELEGRAM_BOT_TOKEN or not chat_id: return False
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": f"🦚 Meena Agencies\nYour OTP is: *{otp}*", "parse_mode": "Markdown"},
            timeout=10,
        )
        return res.status_code == 200
    except Exception: return False

def save_order_history(user_id, cart, total):
    orders_file = BASE_DIR / "orders.json"
    orders = []
    if orders_file.exists():
        try: orders = json.loads(orders_file.read_text())
        except Exception: pass
    new_order = {"order_id": f"ORD-{random.randint(1000, 9999)}", "user_id": user_id,
                 "date": str(datetime.date.today()), "items": cart, "total": total, "status": "Paid"}
    orders.append(new_order)
    orders_file.write_text(json.dumps(orders, indent=2))
    return new_order

def login_screen():
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.title("🦚 Meena Agencies")
        st.caption("Trusted Pharma Wholesale Partner")
        st.info("Please enter your ID and PIN.")
        with st.form("login"):
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

def page_home(u):
    st.title(f"Welcome back, {u.get('shop', 'Partner')} 👋")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders", "42", "+3 this week")
    c2.metric("Pending Deliveries", "2", delta="Active", delta_color="inverse")
    c3.metric("Support Tickets", "0", "All clear")
    st.divider()
    st.markdown("### ⚡ Quick Actions")
    a1, a2 = st.columns(2)
    with a1:
        if st.button("🛒 Place New Order", type="primary", use_container_width=True):
            st.session_state.page = "order"; st.rerun()
    with a2:
        if st.button("📜 View Order History", use_container_width=True):
            st.session_state.page = "history"; st.rerun()
    st.divider()
    try: render_apple_tesla_view(u, [], lambda x, y: f"₹{x:,.2f}")
    except Exception: pass

@st.fragment
def product_grid(view):
    cols_per_row = 3 
    for i in range(0, len(view.head(30)), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx >= len(view): continue
            row = view.iloc[idx]
            
            raw_name = str(row.get("name", "Unknown"))
            name = raw_name.replace(" - 0", "").replace("-0", "").replace("- 1", "").strip()
            
            price = float(row.get("price", 0))
            stock = int(row.get("stock", 0))
            
            with cols[j]:
                with st.container(border=True):
                    st.markdown('<div class="amz-sponsored">Sponsored</div>', unsafe_allow_html=True)
                    
                    try: st.image(get_icon(name), use_container_width=True)
                    except Exception: pass
                    
                    st.markdown(f'<div class="amz-title">{name}</div>', unsafe_allow_html=True)
                    
                    if stock > 0:
                        st.markdown(f'<div class="amz-stock-ok">✅ In stock ({stock})</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="amz-stock-out">❌ Out of stock</div>', unsafe_allow_html=True)
                    
                    rupees = int(price)
                    paise = int(round((price - rupees) * 100))
                    st.markdown(f'<div class="amz-price"><span class="amz-decimal">₹</span>{rupees}<span class="amz-decimal">.{paise:02d}</span></div>', unsafe_allow_html=True)
                    
                    if st.button("Add to Cart", key=f"add_{name}", disabled=(stock <= 0), use_container_width=True, type="primary"):
                        st.session_state.cart.append({"name": name, "price": price, "qty": 1})
                        st.toast(f"✅ Added {name}"); st.rerun()

def page_order():
    if "cart" not in st.session_state: st.session_state.cart = []
    cart_count = len(st.session_state.cart)
    
    if cart_count > 0:
        c1, c2 = st.columns([3, 1])
        c1.title("🛒 Place Order")
        with c2:
            st.write("")
            if st.button(f"🛍️ Cart ({cart_count})", type="primary", use_container_width=True):
                st.session_state.page = "cart"; st.rerun()
    else:
        st.title("🛒 Place Order")
        
    df = load_inventory()
    if df.empty:
        st.error("Inventory DB not found."); return
        
    search = st.text_input("🔍 Search", placeholder="Search medicines...").lower()
    view = df[df["name"].str.lower().str.contains(search)] if search else df
    
    if view.empty:
        st.warning("No results found."); return
        
    product_grid(view)

def page_cart():
    st.title("🛍️ My Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Cart is empty."); return
        
    for i, item in enumerate(cart):
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{item['name']}**  \n₹{item['price']} each")
        new_qty = c2.number_input("Qty", min_value=1, max_value=99, value=item["qty"], key=f"qty_{i}", label_visibility="collapsed")
        if new_qty != item["qty"]:
            st.session_state.cart[i]["qty"] = new_qty; st.rerun()
        if c3.button("🗑️", key=f"del_{i}", help="Remove item"):
            st.session_state.cart.pop(i); st.toast("Item removed"); st.rerun()
            
    total = sum(item["price"] * item["qty"] for item in st.session_state.cart)
    
    with st.container(border=True):
        st.markdown(f"### Total: ₹{total:,.2f}")
        
    if "show_otp_input" not in st.session_state: st.session_state.show_otp_input = False
    if "order_otp" not in st.session_state: st.session_state.order_otp = None
    
    if not st.session_state.show_otp_input:
        if st.button("💳 Proceed to Checkout", type="primary", use_container_width=True):
            otp = str(random.randint(100000, 999999))
            st.session_state.order_otp = otp
            chat_id = st.session_state.user.get("telegram_chat_id", "")
            sent = send_telegram_otp(chat_id, otp) if chat_id else False
            st.session_state.show_otp_input = True
            if sent: st.toast("OTP sent to your Telegram")
            st.rerun()
            
    if st.session_state.show_otp_input:
        st.subheader("Verify & Place Order")
        input_otp = st.text_input("Enter 6-digit OTP", max_chars=6)
        otp_valid = len(input_otp.strip()) == 6 and input_otp.strip().isdigit()
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Verify & Place Order", type="primary", use_container_width=True, disabled=not otp_valid):
                if input_otp.strip() == str(st.session_state.order_otp).strip():
                    saved = save_order_history(st.session_state.user.get("id"), st.session_state.cart, total)
                    st.success(f"🎉 Order {saved['order_id']} placed!")
                    st.session_state.cart = []
                    st.session_state.show_otp_input = False
                    st.session_state.order_otp = None
                    st.balloons(); time.sleep(2); st.session_state.page = "home"; st.rerun()
                else:
                    st.error("❌ Incorrect OTP.")
        with c2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_otp_input = False
                st.session_state.order_otp = None
                st.rerun()
                
        with st.expander("🔑 Use PIN instead of OTP"):
            fallback_pin = st.text_input("4-digit PIN", type="password", max_chars=4)
            if st.button("Verify PIN & Place Order", use_container_width=True, disabled=(len(fallback_pin) != 4)):
                input_hash = hashlib.sha256(fallback_pin.encode()).hexdigest()
                user = st.session_state.user
                if fallback_pin == user.get("pin") or input_hash == user.get("pin_hash"):
                    saved = save_order_history(user.get("id"), st.session_state.cart, total)
                    st.success(f"🎉 Order {saved['order_id']} placed via PIN!")
                    st.session_state.cart = []
                    st.session_state.show_otp_input = False
                    st.session_state.order_otp = None
                    st.balloons(); time.sleep(2); st.session_state.page = "home"; st.rerun()
                else:
                    st.error("❌ PIN does not match.")

    st.divider()
    try: render_upi_payment({"order_id": "NEW-ORDER", "total": total}, st.session_state.get("user", {}))
    except Exception: pass

def page_history(u):
    st.title("📜 My Orders")
    orders_file = BASE_DIR / "orders.json"
    if not orders_file.exists():
        st.info("No orders yet."); return
    try: orders = json.loads(orders_file.read_text())
    except Exception: return
    
    user_orders = [o for o in orders if str(o.get("user_id")) == str(u.get("id"))]
    for order in reversed(user_orders):
        with st.container(border=True):
            st.markdown(f"### Order {order['order_id']}")
            st.caption(f"Date: {order['date']} | Total: ₹{order['total']}")
            st.write(f"**Status:** {order['status']}")

def page_profile(u):
    st.title("👤 Profile")
    safe = {k: v for k, v in u.items() if k not in ("pin", "pin_hash")}
    st.json(safe)

def page_rep_checkin(u):
    st.title("📍 Sales Rep Check-In")
    if st.button("📍 Get My Current Location", type="primary", use_container_width=True):
        with st.spinner("Getting GPS..."):
            loc = get_geolocation()
            if loc and "coords" in loc:
                st.success(f"✅ Location shared! (Lat: {loc['coords']['latitude']:.4f})")
            else:
                st.error("❌ Could not get location.")

def page_owner_map():
    st.title("🗺️ Live Sales Rep Tracking")
    @st.fragment(run_every=10)
    def draw_live_map():
        m = folium.Map(location=[10.7870, 79.1378], zoom_start=7)
        st_folium(m, use_container_width=True, height=400)
    draw_live_map()
    try: render_owner_verification()
    except Exception: pass

def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #0B3C5D;'>🦚 Meena</h2>", unsafe_allow_html=True)
        role = st.session_state.user.get("role", "Retailer").upper()
        st.markdown(f"<p style='text-align: center; color: #1D8348; font-weight: 600;'>{role}</p>", unsafe_allow_html=True)
        st.divider()
        
        menu = [("home", "🏠 Dashboard"), ("order", "🛒 Place Order"), ("cart", "🛍️ My Cart"), ("history", "📜 Order History"), ("profile", "👤 Profile")]
        if role == "OWNER":
            menu.extend([("rep_checkin", "📍 Rep Check-In"), ("owner_map", "🗺️ Live Tracking")])
        elif role in ["SALES_REP", "STAFF", "WORKER"]:
            menu.append(("rep_checkin", "📍 Rep Check-In"))
            
        for key, label in menu:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.get("page") == key else "secondary"):
                st.session_state.page = key; st.rerun()
                
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear(); st.rerun()

def main():
    if "user" not in st.session_state:
        login_screen(); return
    st.session_state.setdefault("page", "home")
    render_sidebar()
    page = st.session_state.page
    u = st.session_state.user
    if page == "home": page_home(u)
    elif page == "owner_map": page_owner_map()
    elif page == "order": page_order()
    elif page == "cart": page_cart()
    elif page == "history": page_history(u)
    elif page == "profile": page_profile(u)
    elif page == "rep_checkin": page_rep_checkin(u)

main()
