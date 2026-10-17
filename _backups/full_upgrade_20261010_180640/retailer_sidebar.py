"""
retailer_sidebar.py — Clean left sidebar for retailer/customer.
Groups actions, shows profile, handles navigation.
"""
import streamlit as st
from inr import inr


# Menu items: (key, icon, label, description)
_MENU = [
    ("home",       "🏠", "Home",             "Dashboard at a glance"),
    ("order",      "🛒", "Place Order",      "Browse & buy medicines"),
    ("reorder",    "🔁", "Reorder Last",     "One-tap repeat of last order"),
    ("bills",      "🦚", "Bill History",     "Date-range bill selector"),
    ("track",      "🚚", "Track Deliveries", "See where your orders are"),
    ("cart",       "🛍️", "My Cart",          "Review before submitting"),
    ("favorites",  "⭐", "Frequently Ordered", "Your top medicines"),
    ("stock",      "🔍", "Stock Check",      "Search any medicine"),
    ("ledger",     "💰", "Ledger / Balance", "Payments & dues"),
    ("notify",     "🔔", "Notifications",    "Order updates"),
    ("offers",     "🎁", "Offers & Schemes", "Current deals"),
    ("business",   "📊", "My Business",      "Your purchase history"),
    ("contact",    "📞", "Contact Us",       "Reach Meena Agencies"),
    ("profile",    "👤", "My Profile",       "Contact, PIN, settings"),
]


def _inject_sidebar_css():
    if st.session_state.get("_retailer_sb_done"):
        return
    st.markdown("""
    <style>
    /* Sidebar container */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1130 0%, #0a0e27 100%) !important;
        border-right: 1px solid rgba(0,212,170,0.25) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem !important;
    }

    /* Brand block at top */
    .sb-brand {
        text-align: center;
        padding: 12px 0 18px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 14px;
    }
    .sb-brand-logo {
        display: inline-block;
        width: 56px; height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00d4aa, #7b61ff);
        padding: 3px;
        box-shadow: 0 6px 20px rgba(0,212,170,0.35);
    }
    .sb-brand-logo img {
        width: 100%; height: 100%;
        object-fit: contain; border-radius: 50%;
        background: #fff; display: block;
    }
    .sb-brand-name {
        margin-top: 8px;
        font-size: 0.78rem; font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #00d4aa, #7b61ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sb-brand-sub {
        font-size: 0.6rem; color: #6b7490;
        letter-spacing: 1.4px; text-transform: uppercase;
        margin-top: 2px;
    }

    /* Shop card */
    .sb-shop {
        background: linear-gradient(135deg, rgba(0,212,170,0.08), rgba(123,97,255,0.06));
        border: 1px solid rgba(0,212,170,0.2);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 0 4px 16px 4px;
    }
    .sb-shop-name {
        font-size: 0.85rem; font-weight: 800; color: #e8eaf6;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .sb-shop-id {
        font-size: 0.68rem; color: #8892b0; letter-spacing: 1px;
        margin-top: 2px;
    }
    .sb-shop-balance {
        font-size: 0.72rem; color: #00d4aa; font-weight: 700;
        margin-top: 6px;
    }

    /* Menu heading */
    .sb-heading {
        font-size: 0.62rem; color: #6b7490;
        letter-spacing: 2px; text-transform: uppercase;
        font-weight: 800;
        padding: 0 8px 6px 8px;
    }

    /* Sidebar buttons — full-width nav */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #cbd5f0 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.55rem 0.9rem !important;
        margin: 2px 0 !important;
        border-radius: 10px !important;
        transition: all .15s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0,212,170,0.10) !important;
        border-color: rgba(0,212,170,0.35) !important;
        color: #00d4aa !important;
        transform: translateX(3px) !important;
    }
    /* Active state */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(0,212,170,0.2), rgba(123,97,255,0.2)) !important;
        border-color: #00d4aa !important;
        color: #00d4aa !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 14px rgba(0,212,170,0.25) !important;
    }

    /* Sign-out at bottom */
    .sb-signout {
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 16px; padding-top: 12px;
    }

    /* Hide default nav */
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.session_state["_retailer_sb_done"] = True


def render(retailer):
    """
    Render the retailer sidebar. Returns the currently selected page key.
    retailer: dict with id, shop, owner, outstanding, credit_limit
    """
    _inject_sidebar_css()

    # Current page (default: home)
    if "retailer_page" not in st.session_state:
        st.session_state.retailer_page = "home"

    with st.sidebar:
        # ── Brand block with logo ──
        try:
            from pathlib import Path
            import base64
            logo_b64 = ""
            for name in ("logo_brand_small.png", "logo_rich_small.png", "logo.png"):
                pth = Path(name)
                if pth.exists():
                    logo_b64 = base64.b64encode(pth.read_bytes()).decode()
                    break
            if logo_b64:
                st.markdown(f'''
                <div class="sb-brand">
                    <div class="sb-brand-logo">
                        <img src="data:image/png;base64,{logo_b64}" alt="Logo" />
                    </div>
                    <div class="sb-brand-name">MEENA AGENCIES</div>
                    <div class="sb-brand-sub">Wholesale Partner</div>
                </div>
                ''', unsafe_allow_html=True)
        except Exception:
            pass

        # ── Shop info card ──
        shop = retailer.get("shop", "My Shop")
        rid = retailer.get("id", "—")
        out = float(retailer.get("outstanding", 0))
        lim = float(retailer.get("credit_limit", 0))
        avail = lim - out
        st.markdown(f'''
        <div class="sb-shop">
            <div class="sb-shop-name">{shop}</div>
            <div class="sb-shop-id">{rid}</div>
            <div class="sb-shop-balance">{inr(avail)} available</div>
        </div>
        ''', unsafe_allow_html=True)

        # ── Menu ──
        st.markdown('<div class="sb-heading">Menu</div>', unsafe_allow_html=True)

        for key, icon, label, desc in _MENU:
            active = st.session_state.retailer_page == key
            if st.button(
                f"{icon}  {label}",
                key=f"sb_btn_{key}",
                use_container_width=True,
                type="primary" if active else "secondary",
                help=desc,
            ):
                st.session_state.retailer_page = key
                st.rerun()

        # ── Sign out at bottom ──
        st.markdown('<div class="sb-signout"></div>', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="sb_signout", use_container_width=True):
            for k in list(st.session_state.keys()):
                try:
                    del st.session_state[k]
                except Exception:
                    pass
            st.rerun()

    return st.session_state.retailer_page
