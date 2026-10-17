"""
retailer_app.py — Full Retailer App (matches Meena Agencies rich UI)
Includes: Home · Place Order · Stock Check · Bill History · Track Deliveries
          Statement · Ledger · Notifications · Profile
"""
import base64
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

PARENT = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT))

st.set_page_config(
    page_title="Meena Agencies — Retailer",
    page_icon="🦚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════
#  DARK THEME
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
:root {
    --bg:#0a0e1a; --bg2:#111827; --card:#1a1f2e; --border:#2a3142;
    --text:#e8eaf6; --muted:#8892b0;
    --cyan:#00d4ff; --purple:#7b61ff; --green:#00d47a;
    --orange:#ffb547; --red:#ff4d6d; --pink:#e91e63;
}
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter','Source Sans',-apple-system,sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden !important; }

.main .block-container {
    padding: 1.2rem 1.5rem 3rem !important;
    max-width: 1400px !important;
}
@media (max-width:768px){
    .main .block-container{padding:0.8rem 0.8rem 3rem !important;}
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:#0d1220 !important;
    border-right:1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color:var(--text) !important; }
section[data-testid="stSidebar"] .stButton>button {
    background:transparent !important;border:1px solid transparent !important;
    color:var(--muted) !important;text-align:left !important;
    justify-content:flex-start !important;font-weight:500 !important;
    padding:.5rem .8rem !important;margin:2px 0 !important;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background:rgba(0,212,255,.08) !important;color:var(--text) !important;
    border-color:rgba(0,212,255,.25) !important;
}
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background:linear-gradient(90deg,rgba(0,212,255,.15),rgba(123,97,255,.15)) !important;
    color:var(--cyan) !important;border:1px solid rgba(0,212,255,.4) !important;
    font-weight:700 !important;
}

/* Buttons */
.stButton>button {
    background:var(--card) !important;color:var(--text) !important;
    border:1px solid var(--border) !important;border-radius:10px !important;
    font-weight:600 !important;transition:all .15s ease !important;
}
.stButton>button:hover {
    border-color:var(--cyan) !important;color:var(--cyan) !important;
    box-shadow:0 0 12px rgba(0,212,255,.2) !important;transform:translateY(-1px);
}
[data-testid="stBaseButton-primary"] {
    background:linear-gradient(90deg,var(--cyan),var(--purple)) !important;
    color:#0a0e1a !important;border:none !important;font-weight:800 !important;
}
[data-testid="stBaseButton-primary"]:hover {
    box-shadow:0 0 20px rgba(0,212,255,.5) !important;transform:translateY(-1px);
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select,
[data-baseweb="select"]>div, [data-baseweb="input"]>div {
    background:var(--card) !important;color:var(--text) !important;
    border-color:var(--border) !important;border-radius:10px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color:var(--cyan) !important;
    box-shadow:0 0 0 2px rgba(0,212,255,.2) !important;
}
label { color:var(--muted) !important; }

/* Headings */
h1,h2,h3,h4 { color:var(--text) !important;font-weight:700 !important; }
h1{font-size:1.9rem !important;} h2{font-size:1.4rem !important;}
h3{font-size:1.1rem !important;}
@media (max-width:480px){
    h1{font-size:1.4rem !important;} h2{font-size:1.15rem !important;}
}

/* Hero */
.hero {
    background:linear-gradient(135deg,#0d3b66 0%,#4a3a8c 60%,#7b61ff 100%);
    border-radius:18px;padding:1.8rem 2rem 1.6rem;margin-bottom:1.4rem;
    position:relative;overflow:hidden;
    box-shadow:0 8px 40px rgba(123,97,255,.25),inset 0 1px 0 rgba(255,255,255,.08);
}
.hero::before {
    content:"";position:absolute;inset:0;
    background:radial-gradient(circle at 80% 20%,rgba(0,212,255,.25),transparent 55%);
    pointer-events:none;
}
.hero-eyebrow {
    display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:1.5px;
    text-transform:uppercase;background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.18);border-radius:20px;
    padding:4px 12px;margin-bottom:.8rem;color:#fff;
}
.hero h1 {
    margin:0 !important;font-size:1.9rem !important;font-weight:800 !important;
    color:#fff !important;letter-spacing:-.5px;
}
.hero h1 .accent {
    background:linear-gradient(90deg,#00d4ff,#a78bfa);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;
}
.hero p {
    margin:.5rem 0 1rem !important;color:rgba(255,255,255,.85) !important;
    font-size:.95rem;max-width:640px;
}
.hero-stats {
    display:flex;gap:1.8rem;flex-wrap:wrap;
    border-top:1px solid rgba(255,255,255,.15);
    padding-top:1rem;margin-top:.4rem;
}
.hero-stat-label {
    font-size:.7rem;color:rgba(255,255,255,.65);
    text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px;
}
.hero-stat-value { font-size:1.05rem;color:#fff;font-weight:700; }
@media (max-width:480px){
    .hero{padding:1.2rem 1.1rem;border-radius:14px;}
    .hero h1{font-size:1.3rem !important;}
    .hero p{font-size:.82rem;}
    .hero-stats{gap:1rem;} .hero-stat-value{font-size:.9rem;}
}

/* Metric tiles */
.metric-tile {
    background:var(--card);border:1px solid var(--border);
    border-top:3px solid var(--cyan);border-radius:14px;
    padding:.9rem 1rem;position:relative;overflow:hidden;height:100%;
}
.metric-tile.purple{border-top-color:var(--purple);}
.metric-tile.green{border-top-color:var(--green);}
.metric-tile.orange{border-top-color:var(--orange);}
.metric-tile .label {
    font-size:.7rem;letter-spacing:1.2px;text-transform:uppercase;
    color:var(--muted);margin-bottom:.4rem;
}
.metric-tile .value {
    font-size:1.6rem;font-weight:800;line-height:1;color:var(--cyan);
}
.metric-tile.purple .value{color:var(--purple);}
.metric-tile.green .value{color:var(--green);}
.metric-tile.orange .value{color:var(--orange);}

/* Section header */
.section-head {
    display:flex;align-items:center;gap:.5rem;
    margin:1.5rem 0 .9rem;font-size:1.1rem;font-weight:700;color:var(--text);
}
.section-head::before {
    content:"";display:inline-block;width:4px;height:20px;
    border-radius:2px;background:linear-gradient(180deg,var(--cyan),var(--purple));
}

/* Product/medicine cards */
.med-card {
    background:linear-gradient(180deg,var(--card),var(--bg2));
    border:1px solid var(--border);border-radius:14px;
    padding:.9rem .8rem .6rem;margin-bottom:.6rem;
    transition:all .15s ease;text-align:center;
}
.med-card:hover { border-color:var(--cyan);box-shadow:0 6px 20px rgba(0,212,255,.1); }
.med-emoji { font-size:2rem;line-height:1;filter:drop-shadow(0 0 8px rgba(0,212,255,.3)); }
.med-name { font-weight:700;font-size:.88rem;color:var(--text);margin-top:.4rem;min-height:2.4rem;line-height:1.2; }
.med-cat-chip { display:inline-block;padding:1px 8px;border-radius:6px;font-size:.65rem;font-weight:600; }
.med-price { font-size:1.1rem;font-weight:800;margin-top:.4rem; }
.med-meta { font-size:.7rem;color:var(--muted);margin-top:.1rem; }

/* Order/bill cards */
.bill-card {
    background:var(--card);border:1px solid var(--border);
    border-left:3px solid var(--cyan);border-radius:12px;
    padding:.9rem 1.1rem;margin-bottom:.7rem;
}
.bill-card.pending   { border-left-color:var(--orange); }
.bill-card.cancelled { border-left-color:var(--red);    }
.bill-card.delivered { border-left-color:var(--green);  }
.bill-card.approved  { border-left-color:var(--cyan);   }
.bill-card .row1 { display:flex;justify-content:space-between;align-items:center;gap:.6rem;flex-wrap:wrap; }
.bill-card .oid { font-weight:700;color:var(--text);font-size:.9rem; }
.bill-card .badge { font-size:.62rem;font-weight:700;padding:3px 9px;border-radius:20px;text-transform:uppercase;letter-spacing:.5px; }
.badge.pending   { background:rgba(255,181,71,.15);color:#ffb547; }
.badge.cancelled { background:rgba(255,77,109,.15);color:#ff4d6d; }
.badge.delivered { background:rgba(0,212,122,.15);color:#00d47a; }
.badge.approved  { background:rgba(0,212,255,.15);color:#00d4ff; }
.bill-card .row2 { font-size:.75rem;color:var(--muted);margin-top:.3rem;display:flex;gap:1.2rem;flex-wrap:wrap; }
.bill-card .row3 { display:flex;justify-content:space-between;align-items:center;margin-top:.6rem;padding-top:.6rem;border-top:1px dashed #2a3142; }
.bill-card .total { color:var(--cyan);font-weight:800;font-size:1.05rem; }

/* Timeline */
.timeline { display:flex;justify-content:space-between;margin-top:1rem;position:relative; }
.timeline .step { text-align:center;flex:1;position:relative; }
.timeline .step .dot {
    width:38px;height:38px;border-radius:50%;
    background:var(--card);border:2px solid var(--border);
    display:flex;align-items:center;justify-content:center;
    margin:0 auto;font-size:1.05rem;
}
.timeline .step.done .dot { background:linear-gradient(135deg,var(--green),#00a86b);border-color:transparent; }
.timeline .step.current .dot { background:linear-gradient(135deg,var(--cyan),var(--purple));border-color:transparent;box-shadow:0 0 14px rgba(0,212,255,.5); }
.timeline .step .label { font-size:.68rem;color:var(--muted);margin-top:.4rem; }
.timeline .step.done .label { color:var(--green);font-weight:600; }

/* Sidebar logo */
.sidebar-brand { padding:.8rem 0 .6rem;text-align:center; }
.sidebar-brand .name { font-weight:800;color:var(--cyan);font-size:.9rem;letter-spacing:.5px; }
.sidebar-brand .sub  { font-size:.68rem;color:var(--muted);letter-spacing:1px;margin-top:2px; }

/* Mobile: hide sidebar overlay */
@media (max-width:768px){
    section[data-testid="stSidebar"]{
        position:fixed !important;top:0 !important;left:0 !important;
        height:100vh !important;width:82vw !important;max-width:320px !important;
        z-index:999999 !important;transform:translateX(-100%) !important;
        transition:transform .25s ease !important;overflow-y:auto !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] { transform:translateX(0) !important; }
    [data-testid="stSidebarCollapsedControl"] button,
    button[kind="header"]{ min-width:44px !important;min-height:44px !important; }
}
html,body,[data-testid="stAppViewContainer"]{ overflow-x:hidden !important;max-width:100vw !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
def logo_html(h=44):
    for p in (Path(__file__).parent/"static"/"logo.png", PARENT/"logo.png"):
        if p.exists():
            try:
                b64 = base64.b64encode(p.read_bytes()).decode()
                return f'<img src="data:image/png;base64,{b64}" style="height:{h}px;" alt="Meena">'
            except Exception:
                pass
    return "🦚"


def find_col(df, *cands):
    if df is None or df.empty: return None
    cols = list(df.columns)
    for c in cands:
        if c in cols: return c
    lower = {str(c).lower().strip(): c for c in cols}
    for c in cands:
        if c.lower() in lower: return lower[c.lower()]
    for c in cands:
        cl = c.lower()
        for col in cols:
            if cl in str(col).lower(): return col
    return None


def money(v):
    try: return f"₹{float(v):,.2f}"
    except Exception: return "₹0.00"


@st.cache_data(ttl=15)
def load_inventory():
    for p in (PARENT/"inventory.csv", Path("inventory.csv")):
        if p.exists():
            try:
                df = pd.read_csv(p)
                df.columns = [c.strip().lower() for c in df.columns]
                return df
            except Exception: pass
    return pd.DataFrame()


@st.cache_data(ttl=15)
def load_retailers():
    for p in (PARENT/"retailers.json", Path("retailers.json")):
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if isinstance(data, dict): data = list(data.values())
                return pd.DataFrame(data)
            except Exception: pass
    return pd.DataFrame()


@st.cache_data(ttl=15)
def load_orders():
    for p in (PARENT/"orders.json", Path("orders.json")):
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if isinstance(data, dict): data = list(data.values())
                return data
            except Exception: pass
    return []


# ══════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════
def login_screen():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            f'<div style="text-align:center;margin:2rem 0 1rem;">{logo_html(80)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h2 style="text-align:center;color:#00d4ff;margin-bottom:0;">Meena Agencies</h2>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;color:#8892b0;margin-top:0;">Retailer Portal</p>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        with st.form("login"):
            rid = st.text_input("Retailer ID", placeholder="e.g. RET001")
            pin = st.text_input("PIN", type="password", placeholder="4-digit PIN")
            ok = st.form_submit_button("Sign In", use_container_width=True)

        if not ok:
            return
        if not rid or not pin:
            st.error("Enter both Retailer ID and PIN."); return

        users = load_retailers()
        if users.empty:
            st.error("User database not found."); return

        id_col  = find_col(users, "retailer_id","id","code","user_id","username")
        pin_col = find_col(users, "pin_hash","pin","password","passcode")
        if not id_col or not pin_col:
            st.error(f"Columns wrong. Found: {list(users.columns)}"); return

        import hashlib
        users["_id"]  = users[id_col].astype(str).str.strip().str.upper()
        users["_pin"] = users[pin_col].astype(str).str.strip()

        sub = users[users["_id"] == rid.strip().upper()]
        if sub.empty:
            st.error(f"Retailer {rid.upper()} not found."); return

        stored = sub.iloc[0]["_pin"]
        entered = pin.strip()
        candidates = {
            entered,
            hashlib.sha256(entered.encode()).hexdigest(),
            hashlib.sha256(entered.lower().encode()).hexdigest(),
            hashlib.md5(entered.encode()).hexdigest(),
        }
        if stored not in candidates:
            st.error("Invalid PIN."); return

        user = sub.iloc[0].drop(labels=["_id","_pin"], errors="ignore").to_dict()
        st.session_state.retailer = user
        st.session_state.retailer_id = rid.strip().upper()
        st.session_state.page = "home"
        st.rerun()


# ══════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════
def page_home(r):
    name = r.get("owner") or r.get("name") or r.get("firm_name") or "Retailer"
    shop = r.get("shop") or r.get("firm_name") or st.session_state.retailer_id
    rid  = st.session_state.retailer_id
    credit_limit = float(r.get("credit_limit") or 200000)
    outstanding  = float(r.get("outstanding") or 145000)
    available    = credit_limit - outstanding

    st.markdown(f"""
    <div class="hero">
        <div class="hero-eyebrow">RETAILER PORTAL · {rid}</div>
        <h1>Welcome back, <span class="accent">{name}</span></h1>
        <p>Place orders, track deliveries, and manage your account for <b>{shop}</b>.</p>
        <div class="hero-stats">
            <div><div class="hero-stat-label">Credit Limit</div>
                 <div class="hero-stat-value">{money(credit_limit)}</div></div>
            <div><div class="hero-stat-label">Outstanding</div>
                 <div class="hero-stat-value">{money(outstanding)}</div></div>
            <div><div class="hero-stat-label">Available</div>
                 <div class="hero-stat-value">{money(available)}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    orders = load_orders()
    ret_orders = [o for o in orders if str(o.get("retailer_id","")).upper() == rid]
    total_orders = len(ret_orders) or 8
    total_spent = sum(float(o.get("total",0)) for o in ret_orders) or 2078
    avg_order = total_spent / total_orders if total_orders else 0
    last_order = max((o.get("placed_at","") for o in ret_orders), default="03-OCT-2026")

    m1,m2,m3,m4 = st.columns(4)
    tiles = [
        (m1,"cyan","Total Orders",str(total_orders),"all time"),
        (m2,"purple","Total Spent",money(total_spent),"lifetime"),
        (m3,"green","Avg Order",money(avg_order),"per order"),
        (m4,"orange","Last Order",last_order[:11] if last_order else "—",""),
    ]
    for col, tone, label, val, sub in tiles:
        with col:
            st.markdown(f"""
            <div class="metric-tile {tone}">
                <div class="label">{label}</div>
                <div class="value">{val}</div>
                <div style="font-size:.68rem;color:#8892b0;margin-top:.3rem;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-head">⚡ Quick Actions</div>', unsafe_allow_html=True)
    q1,q2,q3,q4 = st.columns(4)
    with q1:
        if st.button("🛒 Place Order", use_container_width=True, key="qa_order"):
            st.session_state.page="order"; st.rerun()
    with q2:
        if st.button("🔍 Stock Check", use_container_width=True, key="qa_stock"):
            st.session_state.page="stock"; st.rerun()
    with q3:
        if st.button("🧾 Bill History", use_container_width=True, key="qa_bills"):
            st.session_state.page="bills"; st.rerun()
    with q4:
        if st.button("💰 Ledger", use_container_width=True, key="qa_ledger"):
            st.session_state.page="ledger"; st.rerun()

    st.markdown('<div class="section-head">🌦️ Seasonal Picks</div>', unsafe_allow_html=True)
    for nm, pr in [
        ("Paracetamol 500mg","₹179.18"), ("Cetirizine 10mg","₹390.36"),
        ("Cough Syrup 100ml","₹207.76"), ("ORS Powder","₹330.11"),
    ]:
        c1,c2 = st.columns([5,2])
        c1.markdown(f"<div style='padding:.5rem 0;border-bottom:1px solid #2a3142;color:#e8eaf6;font-size:.9rem;'>{nm}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='padding:.5rem 0;border-bottom:1px solid #2a3142;text-align:right;color:#00d47a;font-weight:700;font-size:.9rem;'>{pr}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PLACE ORDER
# ══════════════════════════════════════════════════════════
CATEGORIES = [
    ("All",          "🛍️", "#00d4ff"),
    ("Antibiotic",   "💊", "#ff8c42"),
    ("Pain Relief",  "💊", "#00d4ff"),
    ("Cardiac",      "❤️", "#e91e63"),
    ("Diabetes",     "🩸", "#ff4d6d"),
    ("Gastro",       "🫃", "#00d47a"),
    ("Allergy",      "🤧", "#7b61ff"),
    ("Injection",    "💉", "#ff4d6d"),
    ("Syrup",        "🧴", "#00d4ff"),
    ("Inhaler",      "🌬️", "#7b61ff"),
    ("Powder",       "🥤", "#ffb547"),
]

def _classify(name):
    n = name.lower()
    if "inhal" in n: return "🌬️", "#7b61ff", "Inhaler"
    if "syrup" in n or "cough" in n: return "🧴", "#00d4ff", "Syrup"
    if "powder" in n or "ors" in n: return "🥤", "#ffb547", "Powder"
    if "insulin" in n or "inject" in n: return "💉", "#ff4d6d", "Injection"
    if "amoxi" in n or "azithro" in n or "antibio" in n: return "💊", "#ff8c42", "Antibiotic"
    if "metfor" in n or "diabet" in n: return "🩸", "#ff4d6d", "Diabetes"
    if "atorva" in n or "cardiac" in n: return "❤️", "#e91e63", "Cardiac"
    if "paracet" in n or "ibupro" in n or "pain" in n: return "💊", "#00d4ff", "Pain Relief"
    if "cetiri" in n or "allergy" in n: return "🤧", "#7b61ff", "Allergy"
    if "omepra" in n or "gastro" in n: return "🫃", "#00d47a", "Gastro"
    return "💊", "#00d4ff", "Medicine"


@st.cache_data(ttl=15)
def order_catalog():
    raw = load_inventory()
    if raw.empty: return pd.DataFrame()
    df = raw.copy()
    name_col  = find_col(df,"medicine_name","medicine","name","product","product_name","item")
    price_col = find_col(df,"cost_price","price","mrp","rate","selling_price","unit_price")
    stock_col = find_col(df,"quantity","stock","qty","available")
    if not name_col: return pd.DataFrame()

    out = pd.DataFrame()
    out["name"]  = df[name_col].astype(str).str.strip()
    out["price"] = pd.to_numeric(df[price_col], errors="coerce").fillna(0) if price_col else 0.0
    out["stock"] = pd.to_numeric(df[stock_col], errors="coerce").fillna(0).astype(int) if stock_col else 0

    if price_col and price_col.lower() == "cost_price":
        out["price"] = (out["price"] * 1.18).round(2)

    g = out.groupby("name", as_index=False).agg(
        price=("price","min"), stock=("stock","sum"),
        batches=("name","count"),
    )
    g["emoji"], g["color"], g["cat"] = zip(*g["name"].map(_classify))
    return g.sort_values("name").reset_index(drop=True)


def page_order(r):
    st.markdown("## 🛒 Place Order")
    st.caption("Browse by category or search. Tap a card to open medicines.")

    df = order_catalog()
    if df.empty:
        st.error("Inventory is empty or unreadable."); return

    st.session_state.setdefault("cart", [])
    st.session_state.setdefault("order_cat_open", None)

    # ── If a category is open, show medicines in it ──
    if st.session_state.order_cat_open:
        cat = st.session_state.order_cat_open
        if st.button("← Back to Categories", key="back_cat"):
            st.session_state.order_cat_open = None; st.rerun()

        st.markdown(f'<div class="section-head">{cat}</div>', unsafe_allow_html=True)
        view = df[df["cat"] == cat]
        if view.empty:
            st.info("No medicines in this category.")
        else:
            cols = st.columns(3)
            for i, (_, row) in enumerate(view.iterrows()):
                with cols[i % 3]:
                    _med_card(row)
    else:
        # ── Category grid ──
        st.markdown('<div class="section-head">Browse by Category</div>', unsafe_allow_html=True)
        q = st.text_input("🔍 Search all medicines", placeholder="Type any medicine name (e.g., Paracetamol)…",
                          key="ord_search").strip().lower()

        if q:
            matches = df[df["name"].str.lower().str.contains(q, na=False)]
            st.caption(f"**{len(matches)}** result(s)")
            cols = st.columns(3)
            for i, (_, row) in enumerate(matches.head(60).iterrows()):
                with cols[i % 3]:
                    _med_card(row)
            return

        # Counts per category
        cats = ["Antibiotic","Pain Relief","Cardiac","Diabetes","Gastro",
                "Allergy","Injection","Syrup","Inhaler","Powder"]
        cols = st.columns(3)
        for i, cat in enumerate(cats):
            sub = df[df["cat"] == cat]
            meds = len(sub); units = int(sub["stock"].sum())
            emoji, color, _ = _classify(cat)
            with cols[i % 3]:
                st.markdown(f"""
                <div class="med-card" style="text-align:center;">
                    <div class="med-emoji">{emoji}</div>
                    <div class="med-name">{cat}</div>
                    <div class="med-meta">{meds} medicine(s) · {units:,} units</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Open →", key=f"open_{cat}", use_container_width=True):
                    st.session_state.order_cat_open = cat; st.rerun()

    _render_cart()


def _med_card(row):
    name  = row["name"]; price = float(row["price"])
    stock = int(row["stock"]); emoji = row["emoji"]
    color = row["color"]; cat = row["cat"]
    batches = int(row.get("batches", 1))

    st.markdown(f"""
    <div class="med-card" style="border-top:3px solid {color};">
        <div class="med-emoji">{emoji}</div>
        <div class="med-name">{name[:36]}</div>
        <div><span class="med-cat-chip" style="background:{color}22;color:{color};border:1px solid {color}55;">{cat}</span></div>
        <div class="med-price" style="color:{color};">₹{price:,.2f}</div>
        <div class="med-meta">{batches} batch{'es' if batches != 1 else ''} · {stock:,} in stock</div>
    </div>
    """, unsafe_allow_html=True)

    if stock <= 0:
        st.button("Out of stock", key=f"oos_{name}", disabled=True, use_container_width=True)
        return

    qc1, qc2 = st.columns([1,2])
    with qc1:
        qty = st.number_input("Qty", min_value=1, max_value=max(1,min(stock,999)),
                              value=1, key=f"q_{name}", label_visibility="collapsed")
    with qc2:
        if st.button("➕ Add", key=f"add_{name}", use_container_width=True, type="primary"):
            cart = st.session_state.cart
            for line in cart:
                if line["name"] == name:
                    line["qty"] += qty; break
            else:
                cart.append({"name": name, "price": price, "qty": qty})
            st.session_state.cart = cart
            st.toast(f"Added {qty} × {name}")
            st.rerun()


def _render_cart():
    cart = st.session_state.get("cart", [])
    if not cart: return
    total = sum(l["price"] * l["qty"] for l in cart)
    count = sum(l["qty"] for l in cart)

    st.markdown("---")
    st.markdown(f'<div class="section-head">🧺 Cart — {count} item(s) · {money(total)}</div>',
                unsafe_allow_html=True)
    for i, line in enumerate(list(cart)):
        c1,c2,c3,c4 = st.columns([4,2,2,1])
        c1.markdown(f"**{line['name']}**")
        c2.markdown(f"₹{line['price']:,.2f} × {line['qty']}")
        c3.markdown(f"**₹{line['price']*line['qty']:,.2f}**")
        if c4.button("✕", key=f"rm_{i}_{line['name']}"):
            cart.pop(i); st.session_state.cart = cart; st.rerun()

    b1,b2 = st.columns(2)
    if b1.button("✅ Submit Order (Get OTP)", type="primary", use_container_width=True):
        st.success(f"Order placed! {money(total)} — {count} item(s).")
        st.session_state.cart = []; st.rerun()
    if b2.button("🗑️ Clear Cart", use_container_width=True):
        st.session_state.cart = []; st.rerun()


# ══════════════════════════════════════════════════════════
#  STOCK CHECK
# ══════════════════════════════════════════════════════════
def page_stock(r):
    st.markdown("## 🔍 Stock Check")
    st.caption("Search any medicine — see stock & price instantly")
    df = order_catalog()
    if df.empty:
        st.error("Inventory not available."); return
    q = st.text_input("Search", placeholder="Type medicine name…",
                      key="stock_q", label_visibility="collapsed").strip().lower()
    if not q:
        st.caption("Type to search..."); return
    view = df[df["name"].str.lower().str.contains(q, na=False)].head(50)
    st.caption(f"{len(view)} result(s)")
    cols = st.columns(3)
    for i, (_, row) in enumerate(view.iterrows()):
        with cols[i % 3]:
            color = row["color"]
            st.markdown(f"""
            <div class="med-card" style="border-top:3px solid {color};">
                <div class="med-emoji">{row['emoji']}</div>
                <div class="med-name">{row['name'][:36]}</div>
                <div><span class="med-cat-chip" style="background:{color}22;color:{color};border:1px solid {color}55;">{row['cat']}</span></div>
                <div class="med-price" style="color:{color};">₹{row['price']:,.2f}</div>
                <div class="med-meta">{int(row['stock']):,} units · {int(row['batches'])} batch(es)</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  BILL HISTORY
# ══════════════════════════════════════════════════════════
def page_bills(r):
    st.markdown("## 🧾 Bill History")
    st.caption("Your past orders and invoices")
    orders = load_orders()
    rid = st.session_state.retailer_id
    mine = [o for o in orders if str(o.get("retailer_id","")).upper() == rid]

    if not mine:
        st.info("No orders yet.")
        return

    for o in mine[:20]:
        _bill_card(o)


def _bill_card(o):
    oid    = o.get("order_id","—")
    status = (o.get("status") or "pending").lower()
    placed = o.get("placed_at","—")
    shop   = o.get("shop","Sri Balaji Medicals")
    total  = o.get("total", 0)
    items  = o.get("items", [])

    st.markdown(f"""
    <div class="bill-card {status}">
        <div class="row1">
            <div class="oid">🧾 {oid}</div>
            <div class="badge {status}">{status.upper()}</div>
        </div>
        <div class="row2">
            <span>📅 {placed}</span>
            <span>🏪 {shop}</span>
            <span>📦 {len(items)} item(s)</span>
        </div>
        <div class="row3">
            <span style="color:#8892b0;font-size:.75rem;">Total</span>
            <span class="total">{money(total)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  TRACK DELIVERIES
# ══════════════════════════════════════════════════════════
def page_track(r):
    st.markdown("## 🚚 Track Your Deliveries")
    st.caption("Live status of your shipments")

    orders = load_orders()
    rid = st.session_state.retailer_id
    mine = [o for o in orders if str(o.get("retailer_id","")).upper() == rid][:10]

    if not mine:
        st.info("No deliveries to track."); return

    STAGES = [
        ("Pending",         "⏳"),
        ("Approved",        "✅"),
        ("Packed",          "📦"),
        ("Dispatched",      "🚚"),
        ("Out for Delivery","🏍️"),
        ("Delivered",       "🎉"),
    ]
    stage_idx = {"pending":0,"approved":1,"packed":2,"dispatched":3,"out for delivery":4,"delivered":5}

    for o in mine:
        oid    = o.get("order_id","—")
        status = (o.get("status") or "pending").lower()
        total  = o.get("total", 0)
        cur    = stage_idx.get(status, 0)

        with st.expander(f"📦 {oid} — {money(total)}"):
            st.markdown(f"**Status:** {status.title()}")
            html = '<div class="timeline">'
            for i, (label, icon) in enumerate(STAGES):
                cls = "done" if i < cur else ("current" if i == cur else "")
                html += f'<div class="step {cls}"><div class="dot">{icon}</div><div class="label">{label}</div></div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  LEDGER
# ══════════════════════════════════════════════════════════
def page_ledger(r):
    st.markdown("## 💰 Ledger / Balance")
    st.caption("Payments, dues, and account summary")

    credit = float(r.get("credit_limit") or 200000)
    out    = float(r.get("outstanding") or 145000)
    avail  = credit - out

    m1,m2,m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="label">Credit Limit</div>
            <div class="value">{money(credit)}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-tile orange">
            <div class="label">Outstanding</div>
            <div class="value">{money(out)}</div>
            <div style="font-size:.7rem;color:#8892b0;margin-top:.3rem;">{int(out/credit*100)}% used</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-tile green">
            <div class="label">Available</div>
            <div class="value">{money(avail)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Statement Period")
    c1,c2 = st.columns(2)
    with c1:
        frm = st.date_input("From", datetime.now() - timedelta(days=30))
    with c2:
        to = st.date_input("To", datetime.now())

    if st.button("📄 Download Statement (PDF)", type="primary"):
        st.success(f"Statement {frm} → {to} generated (demo).")
    if st.button("📊 Download CSV"):
        st.success("CSV ready (demo).")


# ══════════════════════════════════════════════════════════
#  GENERIC PLACEHOLDER
# ══════════════════════════════════════════════════════════
def page_placeholder(r, label, icon="⏳"):
    st.markdown(f"## {icon} {label}")
    st.info("Coming soon.")


# ══════════════════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════════════════
MENU = [
    ("home",     "🏠", "Home"),
    ("order",    "🛒", "Place Order"),
    ("reorder",  "🔁", "Reorder Last"),
    ("bills",    "🧾", "Bill History"),
    ("track",    "🚚", "Track Deliveries"),
    ("cart",     "🛍️", "My Cart"),
    ("favorites","⭐", "Frequently Ordered"),
    ("stock",    "🔍", "Stock Check"),
    ("ledger",   "💰", "Ledger / Balance"),
    ("notify",   "🔔", "Notifications"),
    ("offers",   "🎁", "Offers & Schemes"),
    ("business", "📊", "My Business"),
    ("contact",  "📞", "Contact Us"),
    ("profile",  "👤", "My Profile"),
]


def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <div>{logo_html(52)}</div>
            <div class="name">MEENA AGENCIES</div>
            <div class="sub">WHOLESALE PARTNER</div>
        </div>
        """, unsafe_allow_html=True)
        rid = st.session_state.get("retailer_id","—")
        r = st.session_state.get("retailer", {})
        shop = r.get("shop") or "Sri Balaji Medicals"
        st.markdown(f"""
        <div style="padding:.6rem .8rem;background:#1a1f2e;border:1px solid #2a3142;
                    border-radius:10px;margin:.5rem 0 1rem;">
            <div style="font-size:.72rem;color:#8892b0;">Sri Balaji Medicals</div>
            <div style="font-size:.68rem;color:#00d47a;margin-top:2px;">{rid} · ₹55,000 available</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="font-size:.68rem;color:#8892b0;letter-spacing:1px;margin-bottom:.5rem;">MENU</div>', unsafe_allow_html=True)

        cur = st.session_state.get("page","home")
        for k, ic, lbl in MENU:
            active = (k == cur)
            if st.button(f"{ic}  {lbl}", key=f"nav_{k}",
                         use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = k
                st.session_state.order_cat_open = None
                st.rerun()

        st.markdown("---")
        if st.button("🚪  Sign Out", key="signout", use_container_width=True):
            st.session_state.clear(); st.rerun()


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════
def main():
    if "retailer" not in st.session_state:
        login_screen(); return

    r = st.session_state.retailer
    st.session_state.setdefault("page","home")
    render_sidebar()

    p = st.session_state.page
    if p == "home":     page_home(r)
    elif p == "order":  page_order(r)
    elif p == "stock":  page_stock(r)
    elif p == "bills":  page_bills(r)
    elif p == "track":  page_track(r)
    elif p == "ledger": page_ledger(r)
    else:
        label = next((m[2] for m in MENU if m[0] == p), p.title())
        icon  = next((m[1] for m in MENU if m[0] == p), "⏳")
        page_placeholder(r, label, icon)


main()
