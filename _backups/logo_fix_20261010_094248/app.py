import streamlit as st
import bot_otp
import theme  # GUI foundation
import ui_helpers  # UI polish helpers
import ux_flow  # UX flow helpers
import retailer_journey  # CX retailer journey
import hx_personas  # HX persona helpers
import toolbox_demo  # Demo page


# ═══════════════════════════════════════════════════════════
# CUSTOMER_EASY_ORDER_V1 — reduce visual noise, focus on ordering
# ═══════════════════════════════════════════════════════════
CUSTOMER_EASY_CSS = """
<style>
/* Cleaner metric cards — smaller, less noisy */
[data-testid="stMetric"] {
    padding: 10px 14px !important;
    min-height: 0 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    letter-spacing: 0.5px !important;
}

/* Bigger, easier category cards */
.med-card {
    transition: transform .2s ease, box-shadow .2s ease !important;
    cursor: pointer !important;
}
.med-card:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 12px 28px rgba(0,212,170,0.35) !important;
}

/* Cleaner "Select" button under cards */
button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all .2s ease !important;
}
button[kind="secondary"]:hover {
    background: linear-gradient(90deg, rgba(0,212,170,0.15), rgba(123,97,255,0.10)) !important;
    color: #00d4aa !important;
    transform: translateY(-1px) !important;
}

/* Cleaner expanders */
[data-testid="stExpander"] {
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    padding: 14px 18px !important;
}

/* Prominent cart bar */
.ma-cart-bar {
    position: sticky;
    bottom: 0;
    z-index: 999;
    background: linear-gradient(135deg, rgba(0,212,170,0.95), rgba(123,97,255,0.95));
    color: #fff;
    padding: 14px 22px;
    border-radius: 14px 14px 0 0;
    box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 700;
    margin-top: 20px;
}
.ma-cart-bar .ma-cart-count {
    font-size: 1rem;
}
.ma-cart-bar .ma-cart-total {
    font-size: 1.2rem;
}

/* Cleaner tab appearance */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 18px !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}
</style>
"""



# ═══════════════════════════════════════════════════════════
# TELEGRAM ORDER — OTP POPUP (Streamlit modal)
# ═══════════════════════════════════════════════════════════
def _tg_fmt_items(items):
    lines = []
    for it in items[:5]:
        lines.append(f"• {it['medicine']} × {it['qty']}")
    if len(items) > 5:
        lines.append(f"• ...and {len(items)-5} more")
    return "\n".join(lines)


def _telegram_order_otp_dialog(order, retailer):
    """Popup rendered as a large bordered box. Works on any Streamlit version."""
    # Visual header
    st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 2px solid #00d4ff; border-radius: 16px;
            padding: 1.5rem 1.75rem; margin: 0.5rem 0 1rem 0;
            box-shadow: 0 8px 32px rgba(0,212,255,0.25);">
    <h2 style="color: #00d4ff; margin: 0 0 0.25rem 0; font-size: 1.5rem;">
        🔐 Telegram Order — Enter OTP
    </h2>
    <p style="color: #e0e0e0; margin: 0; font-size: 1rem;">
        You have an order from Telegram
    </p>
</div>
    """, unsafe_allow_html=True)
    st.markdown("### You have an order from Telegram")
    st.markdown(
        f"**Order ID:** `{order['order_id']}`  \n"
        f"**Total:** ₹{order['total']:,.2f}  \n"
        f"**Items:**\n{_tg_fmt_items(order.get('items', []))}"
    )
    st.info("An OTP was sent to your Telegram. Enter the 6 digits below to confirm.")

    code = st.text_input("Enter 6-digit OTP", max_chars=6, key="tg_otp_input_v2")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Verify & Confirm", use_container_width=True, key="tg_verify_v2"):
            if not code or len(code) != 6:
                st.error("Enter a 6-digit code.")
            else:
                ok, msg = bot_otp.verify(order["order_id"], code)
                if ok:
                    orders = load_orders()
                    for o in orders:
                        if o.get("order_id") == order["order_id"]:
                            o["status"] = "Pending"
                            o["otp_verified_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
                            break
                    save_orders(orders)
                    bot_otp.clear_pending_order(retailer["id"])
                    st.success("✅ Order confirmed!")
                    st.balloons()
                    import time as _t
                    _t.sleep(1.2)
                    st.rerun()
                else:
                    st.error(msg)
    with c2:
        if st.button("⏳ Later", use_container_width=True, key="tg_later_v2"):
            st.rerun()


def _inject_customer_easy_css():
    try:
        import streamlit as st
        st.markdown(CUSTOMER_EASY_CSS, unsafe_allow_html=True)
    except Exception:
        pass




# ═══════════════════════════════════════════════════════════
# CUST_CART_BUBBLE_V1 — floating cart bubble for customers
# ═══════════════════════════════════════════════════════════
CUST_CART_BUBBLE_CSS = """
<style>
/* Style the button as a floating round bubble */
div[data-testid="stButton"]:has(> button[key="cust_cart_bubble"]) {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 9999999 !important;
    width: 72px !important;
    max-width: 72px !important;
    margin: 0 !important;
}
div[data-testid="stButton"]:has(> button[key="cust_cart_bubble"]) > button {
    width: 72px !important;
    height: 72px !important;
    min-height: 72px !important;
    max-width: 72px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #00d4aa 0%, #7b61ff 100%) !important;
    color: #ffffff !important;
    font-size: 1.55rem !important;
    font-weight: 800 !important;
    border: 2px solid rgba(255,255,255,0.35) !important;
    box-shadow:
        0 12px 32px rgba(0,212,170,0.6),
        0 4px 12px rgba(0,0,0,0.45),
        0 0 0 4px rgba(0,212,170,0.12) !important;
    animation: custBubblePulse 2.4s ease-in-out infinite !important;
    transition: transform .25s ease !important;
}
div[data-testid="stButton"]:has(> button[key="cust_cart_bubble"]) > button:hover {
    transform: scale(1.1) !important;
}
@keyframes custBubblePulse {
    0%, 100% { box-shadow: 0 12px 32px rgba(0,212,170,0.6), 0 4px 12px rgba(0,0,0,0.45); }
    50%      { box-shadow: 0 12px 46px rgba(0,212,170,0.95), 0 6px 18px rgba(0,0,0,0.55); }
}
@media (max-width: 640px) {
    div[data-testid="stButton"]:has(> button[key="cust_cart_bubble"]) {
        width: 62px !important;
        bottom: 16px !important;
        right: 16px !important;
    }
    div[data-testid="stButton"]:has(> button[key="cust_cart_bubble"]) > button {
        width: 62px !important;
        height: 62px !important;
        min-height: 62px !important;
        max-width: 62px !important;
        font-size: 1.3rem !important;
    }
}
</style>
"""


def render_customer_cart_bubble():
    """Floating cart bubble for customer view. Auto-hides when cart empty."""
    cart = st.session_state.get("cart", []) or []
    if not cart:
        return
    total_qty = sum(int(it.get("qty", 1) or 1) for it in cart)
    st.markdown(CUST_CART_BUBBLE_CSS, unsafe_allow_html=True)
    if st.button(f"🛒 {total_qty}", key="cust_cart_bubble",
                 help="View your cart"):
        st.session_state["show_cart_review"] = True
        st.rerun()


def render_cart_review_dialog():
    """Amazon-style cart review popup."""
    cart = st.session_state.get("cart", []) or []
    if not cart:
        return

    total_amt = 0.0
    total_qty = 0
    st.markdown("### 🧾 Review Your Cart")
    st.caption("Check your items before placing the order")

    for i, it in enumerate(cart):
        med = it.get("medicine") or it.get("name") or "Item"
        qty = int(it.get("qty", 1) or 1)
        batch = it.get("batch", "—")
        price = float(it.get("price", 0) or 0)
        line = qty * price
        total_qty += qty
        total_amt += line

        emoji = "💊"
        ln = str(med).lower()
        if any(k in ln for k in ["syrup", "susp", "liquid"]): emoji = "🧴"
        elif any(k in ln for k in ["inject", "insulin", "vial", "glargine"]): emoji = "💉"
        elif any(k in ln for k in ["powder", "sachet", "ors"]): emoji = "🥄"
        elif any(k in ln for k in ["inhaler", "respule"]): emoji = "💨"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:14px;
                    padding:12px 16px;margin-bottom:8px;
                    background:linear-gradient(135deg,rgba(30,45,80,0.55),rgba(15,25,50,0.7));
                    border:1px solid rgba(0,212,170,0.20);border-radius:12px;">
            <div style="font-size:2rem;width:44px;text-align:center;">{emoji}</div>
            <div style="flex:1;min-width:0;">
                <div style="font-weight:700;color:#eaf6ff;font-size:0.95rem;">{med}</div>
                <div style="font-size:0.72rem;color:#8892b0;">Batch: {batch} · ₹{price:,.2f} each</div>
            </div>
            <div style="font-weight:800;color:#00d4aa;font-size:1.15rem;">× {qty}</div>
            <div style="font-weight:800;color:#eaf6ff;font-size:1rem;min-width:80px;text-align:right;">₹{line:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(0,212,170,0.20),rgba(123,97,255,0.15));
                padding:16px 20px;border-radius:12px;margin-top:14px;
                display:flex;justify-content:space-between;align-items:center;
                border:1px solid rgba(0,212,170,0.4);">
        <span style="color:#8892b0;font-size:0.9rem;">📦 {len(cart)} items · {total_qty} units</span>
        <span style="font-weight:800;color:#00d4aa;font-size:1.4rem;">₹{total_amt:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)


import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas as _pd  # restored alias
from datetime import datetime, timedelta
import json
import functools
import os, hashlib, random, string, time
from threading import Thread
from auto_tracker import inject_tracker
# BROKEN-IMPORT-REMOVED: # (broken accounting import removed — was crashing app)
from breaks import log_lock, log_unlock, get_current_break, get_today_breaks, get_worker_summary
from intelligence import load_activity, log_activity, calculate_worker_metrics, detect_breaks, analyze_workload_balance, generate_daily_report, generate_weekly_insights, psychological_profile, strategic_recommendations, generate_monthly_report, generate_yearly_report, analyze_worker_problems, compare_to_industry, INDUSTRY_BENCHMARKS
from security import hash_secret, verify_secret, log_action, check_rate, is_weak_pin, check_session_timeout, SESSION_TIMEOUT, read_audit
from oi import calculate_health_score, detect_fraud, predict_demand, generate_purchase_orders, answer_whatif, decide_order_probabilistic
from reports_visual import render_kpi_strip, render_health_bars, render_action_cards, render_root_cause, render_insight, render_health_gauge, render_trend_line, render_retailer_scorecard
import order_intelligence
import delivery_ui
import staff_ui
import staff_dashboard
import owner_staff_report
import login_ui
import discounts
import discounts_ui
import navigation
import marketing
import marketing_ui
import rbac

# ─── Audit Pro integration ───
from audit_pro import log_event, read_events, verify_chain, user_summary, all_users_summary, owner_wipe
from analytics_engine import full_report as analytics_full_report
from operations import (record_payment, cancel_order, add_stock, search_orders, generate_invoice)
import forecast_pro
import catalog
import customer_order_ui
import invoice_pro
import animations
import responsive
import medicine_cards
import statement_png
import statement_pdf
import pandas as _pd_fc

def track(user, action, page="", details=""):
    """Fire-and-forget audit event. Never raises."""
    try:
        log_event(user, action, page=page, details=details)
    except Exception:
        pass

def current_user_key():
    """Best-effort identity from session_state."""
    try:
        if st.session_state.get("role") == "owner":
            return "OWNER"
        r = st.session_state.get("retailer")
        if r:
            return r.get("id", "UNKNOWN")
    except Exception:
        pass
    return "GUEST"

def track_page(page_name):
    """Record a page view only once per tab switch (dedup by session)."""
    _key = f"_last_page_{page_name}"
    import time as _t
    _now = _t.time()
    _last = st.session_state.get(_key, 0)
    if _now - _last > 30:  # only log if 30s+ since last view of this tab
        st.session_state[_key] = _now
        track(current_user_key(), "PAGE_VIEW", page=page_name)



# ═══════════════════════════════════════════════════════════
# BEAUTIFUL LOGIN PAGE — Meena Agencies branded
# ═══════════════════════════════════════════════════════════
def render_login_hero():
    """Animated login page hero with rotating Lord Murugan Vel logo."""
    import base64
    from pathlib import Path as _PL

    # Load logo as base64 (self-contained)
    logo_b64 = ""
    if _PL("logo.png").exists():
        try:
            logo_b64 = base64.b64encode(_PL("logo.png").read_bytes()).decode()
        except Exception:
            pass

    st.markdown(f"""
    <style>
    /* ─── Divine gradient background ─── */
    .login-bg {{
        padding-bottom: 5px;
        background: radial-gradient(ellipse at top, #1a1f3a 0%, #0a0e27 60%);
        background-attachment: fixed;
        min-height: 80vh;
        position: relative;
        overflow: hidden;
    }}
    .login-bg::before {{
        content: '';
        position: absolute;
        top: -20%; left: 50%;
        transform: translateX(-50%);
        width: 800px; height: 800px;
        background: radial-gradient(circle, rgba(255,181,71,0.15) 0%, transparent 60%);
        animation: divineGlow 6s ease-in-out infinite;
        pointer-events: none;
    }}
    .login-bg::after {{
        content: '';
        position: absolute;
        bottom: -10%; left: 50%;
        transform: translateX(-50%);
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(123,97,255,0.12) 0%, transparent 60%);
        animation: divineGlow 8s ease-in-out infinite reverse;
        pointer-events: none;
    }}
    @keyframes divineGlow {{
        0%, 100% {{ opacity: 0.6; transform: translateX(-50%) scale(1); }}
        50%      {{ opacity: 1; transform: translateX(-50%) scale(1.15); }}
    }}

    /* ─── Rotating logo ─── */
    .rotating-logo {{
        width: 200px !important; height: 200px !important;
        border-radius: 50%;
        animation: gentleSpin 20s linear infinite, logoPulse 4s ease-in-out infinite;
        box-shadow:
            0 0 40px rgba(255,181,71,0.6),
            0 0 80px rgba(0,212,255,0.4),
            0 0 120px rgba(123,97,255,0.3);
        border: 4px solid rgba(255,181,71,0.5);
        display: block;
        margin: 0 auto 20px auto;
    }}
    @keyframes gentleSpin {{
        from {{ transform: rotate(0deg) scale(1); }}
        to   {{ transform: rotate(360deg) scale(1); }}
    }}
    @keyframes logoPulse {{
        0%, 100% {{ filter: brightness(1) saturate(1); }}
        50%      {{ filter: brightness(1.2) saturate(1.3); }}
    }}

    /* ─── Welcome banner ─── */
    .welcome-banner {{
        text-align: center;
        animation: fadeInUp 0.8s ease-out;
        padding: 30px 20px 20px 20px;
        position: relative;
        z-index: 10;
    }}
    .welcome-om {{
        font-size: 2.5rem;
        color: #ffb547;
        text-shadow: 0 0 20px rgba(255,181,71,0.8);
        animation: float 3s ease-in-out infinite;
        display: inline-block;
        margin-bottom: 10px;
    }}
    @keyframes float {{
        0%, 100% {{ transform: translateY(0); }}
        50%      {{ transform: translateY(-8px); }}
    }}

    .welcome-title {{
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 3.5rem !important;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #ffb547 0%, #ff8c42 30%, #c41e3a 60%, #ffb547 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s linear infinite;
        margin: 0.2rem 0;
        text-shadow: 0 4px 20px rgba(255,140,66,0.3);
        line-height: 1.1;
    }}
    @keyframes gradientShift {{
        0%   {{ background-position: 0% center; }}
        100% {{ background-position: 200% center; }}
    }}

    .welcome-subtitle {{
        font-size: 0.95rem;
        color: #8892b0;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 8px;
        animation: fadeIn 1.2s ease-out;
    }}

    .welcome-tamil {{
        font-size: 1.4rem;
        color: #ffb547;
        margin-top: 12px;
        letter-spacing: 1px;
        animation: fadeInUp 1s ease-out 0.3s backwards;
    }}

    /* ─── Decorative divider ─── */
    .divine-divider {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin: 20px auto;
        max-width: 500px;
        animation: fadeIn 1s ease-out 0.5s backwards;
    }}
    .divine-divider-line {{
        height: 1px;
        flex: 1;
        background: linear-gradient(90deg, transparent, rgba(255,181,71,0.6), transparent);
    }}
    .divine-divider-icon {{
        color: #ffb547;
        font-size: 1.2rem;
        text-shadow: 0 0 12px rgba(255,181,71,0.8);
    }}

    /* ─── Login button container ─── */
    .login-btn-wrap {{
        animation: fadeInUp 1.2s ease-out 0.6s backwards;
        margin-top: 20px;
    }}

    /* ─── Devotional blessing text ─── */
    .blessing {{
        text-align: center;
        color: #8892b0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-top: 20px;
        margin-bottom: 20px;
        font-style: italic;
        animation: fadeIn 1.5s ease-out 1s backwards;
    }}

    /* Reduce gap between hero and buttons */
    .element-container:has(+ .element-container button),
    div[data-testid="stVerticalBlock"] > div:has(button) {{
        margin-top: -10px !important;
    }}

    /* Make button row narrower + centered */
    div[data-testid="stHorizontalBlock"]:has(button) {{
        margin-top: -20px !important;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to   {{ opacity: 1; }}
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ─── Hero content ───
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="rotating-logo" alt="Meena Agencies" />'
    else:
        logo_html = '<div class="rotating-logo" style="background:linear-gradient(135deg,#ffb547,#c41e3a);display:flex;align-items:center;justify-content:center;font-size:4rem;">🕉️</div>'

    st.markdown(f"""
    <div class="login-bg">
        <div class="welcome-banner">
            <div class="welcome-om">🕉️</div>
            {logo_html}
            <div class="welcome-title">MEENA AGENCIES</div>
            <div class="welcome-subtitle">Trusted Pharma Wholesale Partner</div>
            <div class="welcome-tamil">🪔 வணக்கம் · Welcome · स्वागत 🪔</div>
        </div>
        <div class="divine-divider">
            <div class="divine-divider-line"></div>
            <span class="divine-divider-icon">✨</span>
            <span class="divine-divider-icon">🔱</span>
            <span class="divine-divider-icon">✨</span>
            <div class="divine-divider-line"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="blessing">🙏 "வெற்றி வேல், வீர வேல்" — Lord Murugan blesses your business 🙏</div>', unsafe_allow_html=True)



def sign_out():
    """Logout: return to role selection. Gate stays unlocked this process."""
    # Clear session state EXCEPT gate flags
    _keep = {
        "_ma_gate_unlocked": st.session_state.get("_ma_gate_unlocked", False),
        "_ma_gate_error": st.session_state.get("_ma_gate_error", False),
        "password_correct": st.session_state.get("password_correct", False),
    }
    for _k in list(st.session_state.keys()):
        del st.session_state[_k]
    for _k, _v in _keep.items():
        st.session_state[_k] = _v

    # Fresh session defaults — will land on role selection
    st.session_state["role"] = None
    st.session_state["cart"] = []
    st.session_state["retailer"] = None
    st.session_state["pending_order"] = None
    st.session_state["login_attempts"] = 0

    try:
        track("SYSTEM", "SIGNOUT", page="signout")
    except Exception:
        pass

    st.rerun()

def _cached_daily(wm, orders, retailers, breaks, _key):
    return generate_daily_report(wm, orders, retailers, breaks)

@st.cache_data(ttl=300, show_spinner=False)
def _cached_weekly(wm, orders, retailers, breaks, _key):
    return generate_weekly_insights(wm, orders, retailers, breaks)

@st.cache_data(ttl=300, show_spinner=False)
def _cached_monthly(wm, orders, retailers, breaks, _key):
    return generate_monthly_report(wm, orders, retailers, breaks)

@st.cache_data(ttl=300, show_spinner=False)
def _cached_yearly(wm, orders, retailers, breaks, _key):
    return generate_yearly_report(wm, orders, retailers, breaks)

from notify import send_notification, get_active_channel, format_order_sms, format_otp_sms
import notify_pro
import order_notifier
import pharma_intel
import storage

st.set_page_config(page_title="Meena Agencies", page_icon="logo.png", layout="wide", initial_sidebar_state="collapsed")

# PWA: make installable on mobile + logo icons
st.markdown("""
<link rel="manifest" href="/app/static/manifest.json">
<link rel="icon" type="image/png" sizes="32x32" href="/app/static/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/app/static/icon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/app/static/apple-touch-icon.png">
<meta name="theme-color" content="#00d4ff">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Meena">
<meta name="mobile-web-app-capable" content="yes">
""", unsafe_allow_html=True)

theme.apply_theme()
ux_flow.inject_shortcuts()
hx_personas.apply_persona_style()
hx_personas.large_touch_targets()

# ── Crash guard: makes every button/action safe ──
try:
    import crash_guard
    crash_guard.install_guard()
except Exception as _cg_e:
    print('crash_guard skipped:', _cg_e)

# ── Access gate ──
try:
    import auth_gate
    if not auth_gate.check_password():
        st.stop()
except Exception as _e:
    print('auth_gate skipped:', _e)

# Fluid water-flow responsive theme — safe to remove, app works without it
try:
    import fluid_theme as _fluid
    _fluid.apply()
except Exception as _e:
    print('fluid_theme skipped:', _e)

navigation.init_nav()

# ═══════════════════════════════════════════════════════════
# GLOBAL BACK BAR — appears on every screen
# ═══════════════════════════════════════════════════════════
try:
    if st.session_state.get("role") is not None:
        _gb1, _gb2, _gb3 = st.columns([1, 1, 6])
        with _gb1:
            if st.button("← Back", key="global_back_btn", use_container_width=True,
                         disabled=not navigation.can_go_back()):
                navigation.go_back()
        with _gb2:
            if st.button("🏠 Home", key="global_home_btn", use_container_width=True):
                navigation.clear_history()
                for _gk in list(st.session_state.keys()):
                    try:
                        del st.session_state[_gk]
                    except Exception:
                        pass
                st.rerun()
except Exception:
    pass

responsive.inject_responsive()

# ═══════════════════════════════════════════════════════════
# CORPORATE OVERHAUL — Full-width, Tesla-style layout
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
/* FULL WIDTH LAYOUT — kill Streamlit's narrow container */
.block-container {
    max-width: 100% !important;
    padding: 0 3rem 3rem 3rem !important;
}
@media (min-width: 1400px) {
    .block-container { padding: 0 5rem 3rem 5rem !important; }
}

/* Kill default top padding so hero touches the top */
.stApp > header { display: none !important; }
[data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; }
[data-testid="stVerticalBlock"] { gap: 0.8rem !important; }

/* Dark premium background */
.stApp {
    background: #0a0e27 !important;
}

/* ============ TESLA-STYLE HERO ============ */
.corp-hero {
    position: relative;
    max-width: 100% !important;
    width: 100% !important;
    background: linear-gradient(135deg, #0a1535 0%, #0f1e4a 40%, #1a2851 100%);
    padding: 4rem 3rem 3rem 3rem;
    margin: -1rem -3rem 2rem -3rem;
    border-bottom: 1px solid rgba(0,212,255,0.2);
    overflow: hidden;
}
@media (min-width: 1400px) {
    .corp-hero { margin: -1rem -5rem 2rem -5rem; padding: 5rem 5rem 4rem 5rem; }
}
.corp-hero::before {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 800px; height: 800px;
    background: radial-gradient(circle, rgba(0,212,255,0.15) 0%, transparent 60%);
    pointer-events: none;
    animation: heroGlow 8s ease-in-out infinite;
}
.corp-hero::after {
    content: '';
    position: absolute;
    bottom: -30%; left: -10%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(123,97,255,0.12) 0%, transparent 60%);
    pointer-events: none;
    animation: heroGlow 10s ease-in-out infinite reverse;
}
@keyframes heroGlow {
    0%, 100% { transform: translate(0,0) scale(1); opacity: 1; }
    50%      { transform: translate(30px,-30px) scale(1.1); opacity: 0.7; }
}

.corp-hero-inner {
    position: relative;
    z-index: 1;
    max-width: 100%;
    margin: 0;
    padding-left: clamp(1rem, 3vw, 3rem);
    padding-right: clamp(1rem, 3vw, 3rem);
    display: grid;
    grid-template-columns: 1.6fr 1fr;
    gap: 40px;
    align-items: start;
}
.corp-hero-left { min-width: 0; }
.corp-hero-right { min-width: 0; padding-top: 8px; }
@media (max-width: 900px) {
    .corp-hero-inner { grid-template-columns: 1fr; gap: 20px; }
}

.corp-eyebrow {
    display: inline-block;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    background: rgba(0,212,255,0.12);
    border: 1px solid rgba(0,212,255,0.35);
    color: #00d4ff;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.corp-title {
    font-size: 4rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.05;
    letter-spacing: -2px;
    margin: 0.5rem 0 1rem 0;
}
.corp-title-accent {
    background: linear-gradient(90deg, #00d4ff 0%, #7b61ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.corp-subtitle {
    font-size: 1.15rem;
    color: #a8b2d1;
    max-width: 700px;
    line-height: 1.6;
    margin-bottom: 2rem;
}

.corp-meta-row {
    display: flex;
    gap: 3rem;
    flex-wrap: wrap;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.08);
}
.corp-meta-item {
    color: #8892b0;
    font-size: 0.85rem;
}
.corp-meta-item strong {
    display: block;
    color: #e8eaf6;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 2px;
}

/* ============ SECTION TITLES ============ */
.corp-section {
    margin: 2.5rem 0 1.5rem 0;
}
.corp-section-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
}
.corp-section-sub {
    font-size: 0.9rem;
    color: #8892b0;
}

/* ============ PREMIUM METRIC CARDS ============ */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0f1a3a 0%, #0a0e27 100%) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    border-radius: 16px !important;
    padding: 1.8rem 1.5rem !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
    position: relative !important;
}
[data-testid="stMetric"]::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 4px !important;
    background: linear-gradient(90deg, #00d4ff, #7b61ff) !important;
    border-radius: 16px 16px 0 0 !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(0,212,255,0.5) !important;
    box-shadow: 0 20px 60px rgba(0,212,255,0.25) !important;
}
[data-testid="stMetricLabel"] {
    color: #8892b0 !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    letter-spacing: -1px !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }

/* ============ TABS — AMAZON-STYLE NAV ============ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    background: transparent !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border-bottom: 1px solid rgba(0,212,255,0.15) !important;
    margin-bottom: 2rem !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0 !important;
    padding: 1rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #8892b0 !important;
    border: none !important;
    background: transparent !important;
    position: relative !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #00d4ff !important;
    background: rgba(0,212,255,0.04) !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    font-weight: 700 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"]::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 1rem; right: 1rem;
    height: 3px;
    background: linear-gradient(90deg, #00d4ff, #7b61ff);
    border-radius: 2px;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ============ BUTTONS ============ */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 1.5rem !important;
    border: 1px solid rgba(0,212,255,0.35) !important;
    background: rgba(15,26,58,0.8) !important;
    color: #e8eaf6 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    box-shadow: 0 8px 24px rgba(0,212,255,0.3) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 12px 36px rgba(0,212,255,0.5) !important;
}

/* ============ HEADERS ============ */
h1, h2, h3, h4 {
    color: #ffffff !important;
    letter-spacing: -0.5px !important;
}
h1 { font-size: 2.5rem !important; font-weight: 900 !important; }
h2 { font-size: 2rem !important; font-weight: 800 !important; }
h3 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    margin-top: 2rem !important;
    color: #ffffff !important;
}

/* ============ INPUTS ============ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea,
.stDateInput > div > div > input {
    background: rgba(15,26,58,0.8) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.15) !important;
}

/* ============ ALERTS ============ */
.stAlert {
    border-radius: 12px !important;
    font-size: 0.9rem !important;
    border-left-width: 4px !important;
}

/* ============ DATAFRAMES ============ */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    box-shadow: 0 6px 24px rgba(0,0,0,0.3) !important;
}

/* ============ EXPANDERS ============ */
.streamlit-expanderHeader {
    background: rgba(15,26,58,0.7) !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: rgba(10,14,39,0.6) !important;
    border: 1px solid rgba(0,212,255,0.1) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* ============ DIVIDERS ============ */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent) !important;
    margin: 2.5rem 0 !important;
}

/* ============ CAPTIONS ============ */
[data-testid="stCaptionContainer"] {
    color: #8892b0 !important;
    font-size: 0.85rem !important;
}

/* ============ SIGN OUT BUTTON (top right) ============ */
.topnav-signout button {
    background: transparent !important;
    border: 1px solid rgba(255,77,109,0.4) !important;
    color: #ff4d6d !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.85rem !important;
}
.topnav-signout button:hover {
    background: rgba(255,77,109,0.1) !important;
    border-color: #ff4d6d !important;
    color: #ff4d6d !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CORPORATE HERO BUILDER
# ─────────────────────────────────────────────────────────────
def render_corp_hero(title, accent, subtitle, eyebrow="", meta=None, show_intel=False):
    meta = meta or []
    meta_html = ""
    if meta:
        meta_html = '<div class="corp-meta-row">'
        for item in meta:
            meta_html += f'<div class="corp-meta-item"><strong>{item["value"]}</strong>{item["label"]}</div>'
        meta_html += '</div>'

    # Optional right-side intelligence card
    intel_html = ""
    if show_intel:
        try:
            import pharma_intel
            intel_html = pharma_intel.get_intel_css() + pharma_intel.get_intel_html()
        except Exception as e:
            intel_html = ""

    right_col = f'<div class="corp-hero-right">{intel_html}</div>' if intel_html else ''

    st.markdown(f"""
    <div class="corp-hero">
        <div class="corp-hero-inner">
            <div class="corp-hero-left">
                {f'<div class="corp-eyebrow">{eyebrow}</div>' if eyebrow else ''}
                <h1 class="corp-title">{title} <span class="corp-title-accent">{accent}</span></h1>
                <p class="corp-subtitle">{subtitle}</p>
                {meta_html}
            </div>
            {right_col}
        </div>
    </div>
    """, unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# BEAUTY OVERHAUL — Applied globally with !important flags
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Force dark background everywhere */
.stApp, [data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at top left, #0f1535 0%, #050818 60%) !important;
    background-attachment: fixed !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* Global font + color */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #e8eaf6 !important;
}

/* Beautiful metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(26,31,58,0.95) 0%, rgba(15,20,40,0.95) 100%) !important;
    border: 1px solid rgba(123,97,255,0.25) !important;
    border-radius: 18px !important;
    padding: 1.5rem 1.2rem !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00d4ff, #7b61ff);
    opacity: 0.8;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-6px) !important;
    border-color: rgba(0,212,255,0.6) !important;
    box-shadow: 0 16px 48px rgba(0,212,255,0.25), 0 0 0 1px rgba(0,212,255,0.4) !important;
}
[data-testid="stMetricLabel"] {
    color: #8892b0 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #00d4ff, #7b61ff) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.5px !important;
}

/* Buttons — bold, lifted, gradient on primary */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    border: 1px solid rgba(123,97,255,0.4) !important;
    background: linear-gradient(145deg, rgba(26,31,58,0.9), rgba(15,20,40,0.9)) !important;
    color: #e8eaf6 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 10px 28px rgba(0,212,255,0.35) !important;
    color: #00d4ff !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%) !important;
    color: #fff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 12px 32px rgba(0,212,255,0.55) !important;
    transform: translateY(-2px) scale(1.01) !important;
}

/* Tabs — modern pill style */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    background: rgba(15,20,40,0.6) !important;
    padding: 6px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(123,97,255,0.15) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 8px 18px !important;
    font-weight: 500 !important;
    color: #8892b0 !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(0,212,255,0.10) !important;
    color: #00d4ff !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.20), rgba(123,97,255,0.20)) !important;
    color: #00d4ff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(0,212,255,0.25) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }

/* Inputs — deep, clean */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: rgba(15,20,40,0.9) !important;
    border: 1px solid rgba(123,97,255,0.3) !important;
    border-radius: 10px !important;
    color: #e8eaf6 !important;
    padding: 0.6rem 0.8rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.15) !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: rgba(26,31,58,0.7) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(123,97,255,0.2) !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(0,212,255,0.08) !important;
    border-color: rgba(0,212,255,0.4) !important;
}
.streamlit-expanderContent {
    background: rgba(15,20,40,0.6) !important;
    border: 1px solid rgba(123,97,255,0.15) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* Alerts */
.stAlert {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    font-size: 0.9rem !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(123,97,255,0.2) !important;
    box-shadow: 0 6px 24px rgba(0,0,0,0.25) !important;
}

/* Progress bars */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00d4ff, #7b61ff) !important;
    border-radius: 6px !important;
}

/* Radio buttons */
.stRadio > div {
    gap: 8px !important;
}
.stRadio label {
    background: rgba(26,31,58,0.6) !important;
    padding: 8px 14px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(123,97,255,0.2) !important;
    transition: all 0.2s ease !important;
}
.stRadio label:hover {
    background: rgba(0,212,255,0.08) !important;
    border-color: rgba(0,212,255,0.4) !important;
}

/* Multiselect / selectbox dropdowns */
[data-baseweb="popover"], [data-baseweb="menu"] {
    background: #1a1f3a !important;
    border-radius: 12px !important;
    border: 1px solid rgba(123,97,255,0.3) !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #e8eaf6 !important;
    letter-spacing: -0.3px !important;
}
h3 {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    border-left: 4px solid #00d4ff !important;
    padding-left: 12px !important;
    margin-top: 1.5rem !important;
}
h4 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #00d4ff !important;
    margin-top: 1.2rem !important;
}

/* Horizontal rules */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent) !important;
    margin: 2rem 0 !important;
}

/* Captions */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #8892b0 !important;
    font-size: 0.8rem !important;
}

/* Containers get subtle glow */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
    border-radius: 16px;
}

/* Success/error/info messages bigger */
.stSuccess, .stError, .stWarning, .stInfo {
    padding: 1rem 1.2rem !important;
    font-weight: 500 !important;
}

/* Logo animation at top */
.logo-pulse {
    display: inline-block;
    animation: logoPulse 3s ease-in-out infinite;
}
@keyframes logoPulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px rgba(0,212,255,0.4)); }
    50%      { transform: scale(1.05); filter: drop-shadow(0 0 32px rgba(123,97,255,0.6)); }
}
</style>
""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════

animations.inject_animations()

medicine_cards.inject_card_styles()

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #e8eaf6; }
    .title { font-size: 2.2rem; font-weight: 700; background: linear-gradient(90deg,#00d4ff,#7b61ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub { color: #8892b0; margin-bottom: 2rem; }
    .lock-badge { display:inline-block; padding: 0.2rem 0.6rem; background: rgba(0,212,255,0.15); border:1px solid #00d4ff; border-radius:6px; font-size:0.7rem; color:#00d4ff; }
    .mask { color: #ffb547; font-family: monospace; }
    .otp-box { background: rgba(0,212,255,0.08); border: 2px solid #00d4ff; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; text-align: center; }
    .otp-code { font-size: 2.5rem; font-weight: 700; color: #00d4ff; letter-spacing: 0.5rem; }
    .card { background: rgba(26,31,58,0.7); border: 1px solid rgba(123,97,255,0.3); border-radius: 12px; padding: 1rem; margin: 0.5rem 0; }
    .flag { background: rgba(255,77,109,0.15); border-left: 3px solid #ff4d6d; padding: 0.5rem 1rem; margin: 0.3rem 0; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

def fmt(dt): return dt.strftime("%d-%b-%Y").upper() if dt else "N/A"
def fmt_dt(dt): return dt.strftime("%d-%b-%Y %H:%M").upper()
def hash_pin(p): return hash_secret(p)
def verify_pin(p, h): return verify_secret(p, h)
def gen_otp(): return ''.join(random.choices(string.digits, k=6))
def mask_phone(p):
    if not p or len(p) < 4: return "****"
    return p[:2] + "X"*(len(p)-4) + p[-2:]

if 'pending_stock' not in st.session_state:
    st.session_state.pending_stock = None
for k in ["role","cart","retailer","pending_order","login_attempts"]:
    if k not in st.session_state:
        st.session_state[k] = None if k != "cart" else []
if st.session_state.login_attempts is None: st.session_state.login_attempts = {}
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now().isoformat()
if "last_visibility" not in st.session_state:
    st.session_state.last_visibility = "visible"

@st.cache_data(ttl=300, show_spinner=False)
def load_inventory():
    """Read from SQLite — 100x faster than CSV for 10,000+ rows."""
    import sqlite3
    conn = sqlite3.connect("inventory.db")
    try:
        df = pd.read_sql("SELECT * FROM inventory", conn)
    finally:
        conn.close()
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], format="mixed")
    today = pd.Timestamp.now()
    df["days_to_expiry"] = (df["expiry_date"] - today).dt.days
    df["status"] = df["days_to_expiry"].apply(lambda x: "Expired" if x<0 else ("Critical" if x<30 else ("Warning" if x<90 else "Healthy")))
    df["selling_price"] = (df["cost_price"] * 1.25).round(2)
    df["inventory_value"] = df["quantity"] * df["cost_price"]
    return df

@st.cache_data(ttl=120, show_spinner=False)

# ── PERFORMANCE: Cached JSON loader (used across app) ──
@st.cache_data(ttl=60, show_spinner=False)
def _cached_load_json(path_str: str):
    """Load JSON with 60s cache. Use for read-only data."""
    try:
        return json.loads(Path(path_str).read_text())
    except Exception:
        return []

def load_retailers():
    if os.path.exists("retailers.json"):
        with open("retailers.json") as f: return json.load(f)
    retailers = [
        {"id":"RET001","shop":"Sri Balaji Medicals","owner":"Chitra","phone":"6382130536","pin_hash":hash_pin("3210"),"credit_limit":200000,"outstanding":145000,"payment_days":90,"status":"Active","telegram_chat_id":""},
        {"id":"RET002","shop":"Annai Pharmacy","owner":"Lakshmi Devi","phone":"9876543211","pin_hash":hash_pin("3211"),"credit_limit":150000,"outstanding":180000,"payment_days":120,"status":"Blocked","telegram_chat_id":""},
        {"id":"RET003","shop":"Vetri Medicals","owner":"Suresh B","phone":"9876543212","pin_hash":hash_pin("3212"),"credit_limit":100000,"outstanding":35000,"payment_days":90,"status":"Active","telegram_chat_id":""}
    ]
    storage.atomic_write_json("retailers.json", retailers)
    return retailers

def save_retailers(r):
    storage.atomic_write_json("retailers.json", r)

@st.cache_data(ttl=300, show_spinner=False)
def load_owner():
    if os.path.exists("owner.json"):
        with open("owner.json") as f: return json.load(f)
    o = {"username":"owner","pin_hash":hash_pin("owner2026"),"phone":"9999999999","telegram_chat_id":""}
    storage.atomic_write_json("owner.json", o)
    return o

def save_owner(o):
    storage.atomic_write_json("owner.json", o)

@st.cache_data(ttl=120, show_spinner=False)
def load_orders():
    if os.path.exists("orders.json"):
        with open("orders.json") as f: return json.load(f)
    return []

def save_orders(o):
    storage.atomic_write_json("orders.json", o)

# ============ LOGIN ============
if st.session_state.get("role") is None:
    login_ui.render_login_page()
    st.stop()

elif st.session_state.role == "retailer_login":
    st.markdown('<div class="title">🏪 Retailer Login</div>', unsafe_allow_html=True)
    retailers = load_retailers()
    with st.form("rl"):
        rid = st.text_input("Retailer ID", placeholder="RET001")
        pin = st.text_input("PIN", type="password", max_chars=4)
        if st.form_submit_button("🔓 Login", use_container_width=True):
            attempts = st.session_state.login_attempts.get(rid, 0)
            if attempts >= 3:
                st.error("🚫 Too many attempts")
            else:
                ret = next((r for r in retailers if r["id"] == rid.strip().upper()), None)
                if ret and verify_pin(pin, ret["pin_hash"]):
                    st.session_state.retailer = ret
                    st.session_state.role = "retailer"
                    st.session_state.login_attempts[rid] = 0
                    log_action(rid, "LOGIN_SUCCESS")
                    track(rid, "LOGIN_SUCCESS", page="login")
                    track(rid, "LOGIN_SUCCESS", page="login")
                    st.rerun()
                else:
                    st.session_state.login_attempts[rid] = attempts + 1
                    st.error(f"❌ Invalid. Attempts left: {2-attempts}")
    if st.button("← Back"):
        st.session_state.role = None; st.rerun()

# ============ OWNER LOGIN ============
elif st.session_state.role == "owner_login":
    st.markdown('<div class="title">👔 Owner Login</div>', unsafe_allow_html=True)
    owner = load_owner()
    with st.form("ol"):
        pin = st.text_input("Owner Password", type="password")
        if st.form_submit_button("🔓 Login", use_container_width=True):
            if verify_pin(pin, owner["pin_hash"]):
                st.session_state.role = "owner"
                log_action("OWNER", "LOGIN_SUCCESS")
                track("OWNER", "LOGIN_SUCCESS", page="login")
                track("OWNER", "LOGIN_SUCCESS", page="login")
                st.rerun()
            else:
                st.error("❌ Invalid")
    if st.button("← Back"):
        st.session_state.role = None; st.rerun()

# ============ RETAILER VIEW ============

    # ── Floating cart bubble ──
    try:
        render_customer_cart_bubble()
    except Exception:
        pass

    # ── Floating cart bubble ──
    try:
        render_customer_cart_bubble()
    except Exception:
        pass
elif st.session_state.role in ("retailer", "customer"):
    # ── Easy-order CSS cleanup ──
    try:
        _inject_customer_easy_css()
    except Exception:
        pass
    # ── TEST: Hard-coded bubble at top of retailer view ──
    if st.session_state.get("cart"):
        st.markdown("""
        <style>
        div[data-testid="stButton"]:has(> button[key="hard_test_bubble"]) {
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            z-index: 999999 !important;
        }
        div[data-testid="stButton"]:has(> button[key="hard_test_bubble"]) > button {
            width: 72px !important;
            height: 72px !important;
            min-height: 72px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #00d4aa, #7b61ff) !important;
            color: white !important;
            font-size: 1.5rem !important;
            font-weight: 800 !important;
            border: 2px solid white !important;
            box-shadow: 0 10px 30px rgba(0,212,170,0.6) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        _cnt = sum(int(x.get("qty",1) or 1) for x in st.session_state["cart"])
        if st.button(f"🛒 {_cnt}", key="hard_test_bubble"):
            st.session_state["show_cart_popup"] = True
            st.rerun()

    retailers = load_retailers()
    r = next((x for x in retailers if x["id"] == st.session_state.retailer["id"]), st.session_state.retailer)
    st.session_state.retailer = r

    # ── Corporate Hero for Retailer ──
    render_corp_hero(
        title="Meena",
        accent="Agencies",
        subtitle=f"Welcome back, {r['owner']}. Place orders, track balance, and manage your pharmacy with {r['shop']}.",
        eyebrow=f"Retailer Portal · {r['id']}",
        meta=[
            {"value": f"₹{r['credit_limit']:,}", "label": "Credit Limit"},
            {"value": f"₹{r['outstanding']:,}", "label": "Outstanding"},
            {"value": f"₹{r['credit_limit'] - r['outstanding']:,}", "label": "Available"},
            {"value": r['owner'], "label": "Contact"},
            {"value": mask_phone(r['phone']), "label": "Phone"},
        ],
        show_intel=True
    )
    # Sign Out — top right
    _t1, _t2 = st.columns([5, 1])
    with _t2:
        st.markdown('<div class="topnav-signout">', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="hero_signout_ret", use_container_width=True):
            try:
                log_activity(r["id"], "SIGNOUT")
            except Exception:
                pass
            navigation.clear_history()
            sign_out()
        st.markdown('</div>', unsafe_allow_html=True)


    used_pct = (r["outstanding"]/r["credit_limit"])*100
    c1, c2, c3 = st.columns(3)
    c1.metric("Credit Limit", f"₹{r['credit_limit']:,}")
    c2.metric("Outstanding", f"₹{r['outstanding']:,}", delta=f"{used_pct:.0f}% used", delta_color="inverse")
    c3.metric("Available", f"₹{r['credit_limit']-r['outstanding']:,}")

    if r["status"] == "Blocked": st.error("🚫 Account BLOCKED. Contact owner.")
    elif used_pct > 90: st.warning(f"⚠️ {used_pct:.0f}% credit used.")
    else: st.success(f"✅ Active. Available: ₹{r['credit_limit']-r['outstanding']:,}")

    # ===== AUTO BREAK TRACKER (no buttons — fully automatic) =====
    st.markdown("---")
    # ─── Break tracking runs silently in the background ───
    # UI removed for privacy — owner can see the data in Audit tab
    try:
        inject_tracker(r["id"])
    except Exception:
        pass

    st.markdown("---")

    st.markdown("---")
    # Check for pending Telegram order popup
    try:
        _check_pending_telegram_order(r)
    except Exception as _e:
        print(f'[TG_CHECK] {_e}')

    if st.session_state.pending_order is not None:
        po = st.session_state.pending_order
        st.markdown("### 🔐 OTP Verification Required")
        st.info(f"OTP sent to your registered contact via {get_active_channel()}.")
        if get_active_channel() == "console":
            st.markdown(f'<div class="otp-box"><div class="otp-code">{po["otp"]}</div></div>', unsafe_allow_html=True)
        entered = st.text_input("Enter 6-digit OTP", max_chars=6, key="otp_input")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Verify & Confirm", use_container_width=True):
                if entered == po["otp"]:
                    orders = load_orders()
                    order = po["order"]; order["status"] = "Pending"
                    order["otp_verified_at"] = fmt_dt(datetime.now())
                    orders.append(order); save_orders(orders)
                    log_activity(r["id"], "ORDER_PLACED", f"order={order['order_id']} total=₹{order['total']:.0f}")
                    
                    # Send welcome (if first order) + thank you
                    prior_count = len([o for o in orders if o.get("retailer_id") == r["id"] and o.get("status") != "Awaiting OTP"]) - 1
                    if prior_count <= 0:
                        notify_pro.notify_retailer(r, notify_pro.format_welcome(r), prefer_sms=False)
                    notify_pro.notify_retailer(r, notify_pro.format_thank_you(r, order), prefer_sms=False)
                    try:
                        order_notifier.on_new_order(order, r)
                    except Exception as _one:
                        print('order_notifier:', _one)
                    ret_msg = format_order_sms(order, r, include_balance=True, for_owner=False)
                    send_notification(get_active_channel(), r.get("telegram_chat_id",""), ret_msg)
                    owner = load_owner()
                    own_msg = format_order_sms(order, r, include_balance=False, for_owner=True)
                    send_notification(get_active_channel(), owner.get("telegram_chat_id",""), own_msg)
                    st.session_state.pending_order = None
                    st.session_state.cart = []
                    st.success("✅ Order confirmed!")
                    st.balloons(); st.rerun()
                else: st.error("❌ Wrong OTP")
        with c2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.pending_order = None; st.rerun()
        st.stop()

    
    # ═══════════════════════════════════════════════════════════
    # QUICK DASHBOARD — fills the gap between hero and Place Order
    # ═══════════════════════════════════════════════════════════

    # Pull this retailer's order history
    _my_orders = [o for o in load_orders()
                  if o.get("retailer_id") == r["id"] and o.get("status") != "Awaiting OTP"]
    _my_approved = [o for o in _my_orders if o.get("status") == "Approved"]
    _my_pending = [o for o in _my_orders if o.get("status") == "Pending"]
    _my_total_spent = sum(o.get("total", 0) for o in _my_approved)
    _my_last_order = _my_orders[-1] if _my_orders else None
    _my_avg_order = _my_total_spent / len(_my_approved) if _my_approved else 0

    # ─── Quick Stats Row ───
    st.markdown('<div class="corp-section"><div class="corp-section-title">Your Dashboard</div>'
                '<div class="corp-section-sub">Everything about your pharmacy at a glance</div></div>',
                unsafe_allow_html=True)

    _qs1, _qs2, _qs3, _qs4 = st.columns(4)
    with _qs1:
        st.metric("📦 Total Orders", len(_my_orders), help="All your orders till date")
    with _qs2:
        st.metric("💰 Total Spent", f"₹{_my_total_spent:,.0f}", help="Approved orders only")
    with _qs3:
        st.metric("🛒 Avg Order", f"₹{_my_avg_order:,.0f}", help="Average per approved order")
    with _qs4:
        _last_dt = _my_last_order.get("placed_at", "—").split(" ")[0] if _my_last_order else "—"
        st.metric("🕐 Last Order", _last_dt, help="Date of your most recent order")

    st.markdown("---")

    # ─── Quick Actions + Seasonal Recs (2 columns) ───
    _qa_col, _rec_col = st.columns([1, 1])

    with _qa_col:
        st.markdown('<div class="corp-section"><div class="corp-section-title">⚡ Quick Actions</div>'
                    '<div class="corp-section-sub">One click to get things done</div></div>',
                    unsafe_allow_html=True)

        _a1, _a2 = st.columns(2)
        with _a1:
            if st.button("🔄 Reorder Last", key="qa_reorder", use_container_width=True,
                         help="Add your last order items to cart"):
                if _my_last_order and _my_last_order.get("items"):
                    for _it in _my_last_order["items"]:
                        st.session_state.cart.append({
                            "item_id": _it.get("item_id", ""),
                            "medicine": _it.get("medicine", ""),
                            "batch": _it.get("batch", ""),
                            "qty": _it.get("qty", 1),
                            "price": _it.get("price", 0),
                        })
                    st.session_state["_meena_reorder_flash"] = True
                    st.success(f"✅ {len(_my_last_order['items'])} items added to cart — scroll down to review and click PLACE ORDER")
                    st.rerun()
                else:
                    st.info("No previous order to reorder.")

            # ── INLINE CART PREVIEW (immediate visual feedback) ──
            if st.session_state.get("cart"):
                st.markdown("---")
                st.success(f"🛒 **{len(st.session_state['cart'])} item(s) in your cart right now**")
                _inline_total = 0.0
                for _i, _item in enumerate(st.session_state["cart"]):
                    _med   = _item.get("medicine") or _item.get("name") or "Item"
                    _qty   = int(_item.get("qty") or 1)
                    _price = float(_item.get("price") or 0)
                    _line  = _qty * _price
                    _inline_total += _line
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**{_i+1}.** {_med} — {_qty} × ₹{_price:,.2f} = **₹{_line:,.2f}**")
                st.markdown(f"### Cart Total: ₹{_inline_total:,.2f}")
                st.info("👉 Scroll down to the **📦 Place Order** section to confirm and get OTP")

            # ── Statement Download (PDF + PNG) ──
            if st.button("📄 Generate Statement", key="qa_statement", use_container_width=True,
                         help="Download your account statement"):
                try:
                    import json as _json_stmt
                    from pathlib import Path as _P_stmt
                    _company = {}
                    if _P_stmt("company.json").exists():
                        _company = _json_stmt.loads(_P_stmt("company.json").read_text())

                    _ts = datetime.now().strftime('%Y%m%d_%H%M')

                    # ── PDF Version ──
                    try:
                        _pdf_bytes = statement_pdf.generate_statement_pdf(r, _my_orders, _company)
                        st.download_button(
                            "📥 Download PDF (printable)",
                            data=_pdf_bytes,
                            file_name=f"MeenaStatement_{r['id']}_{_ts}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="qa_statement_pdf_dl"
                        )
                        st.caption("✅ PDF — white background, print-ready, professional format")
                    except Exception as _e_pdf:
                        st.warning(f"PDF generation failed: {_e_pdf}")

                    # ── PNG Version ──
                    try:
                        _png_bytes = statement_png.generate_statement_png(r, _my_orders, _company)
                        st.download_button(
                            "📥 Download PNG (screenshot-friendly)",
                            data=_png_bytes,
                            file_name=f"MeenaStatement_{r['id']}_{_ts}.png",
                            mime="image/png",
                            use_container_width=True,
                            key="qa_statement_png_dl"
                        )
                        st.caption("✅ PNG — dark theme, share via WhatsApp/email")
                    except Exception as _e_png:
                        st.warning(f"PNG generation failed: {_e_png}")

                    st.success("✅ Both formats generated. Choose your download above.")
                    st.caption("🔒 Both are non-editable formats — cannot be modified like text.")
                except Exception as _e:
                    st.error(f"Statement generation failed: {_e}")

        with _a2:
            if st.button("📞 Contact Us", key="qa_contact", use_container_width=True,
                         help="Call or message us"):
                st.info(f"📞 Call: 6382130536\n✉️ meena.agencies@gmail.com")

            if st.button("📊 Payment History", key="qa_pay_hist", use_container_width=True,
                         help="View all payments recorded against your account"):
                _pays = r.get("payment_history", [])
                if not _pays:
                    st.info("💡 No payments recorded yet. Your account shows an outstanding balance. Contact us to settle.")
                else:
# import pandas as _pd_ph  # perf: dedup
                    _ph_df = _pd_ph.DataFrame([{
                        "Date": p["date"][:16].replace("T", " "),
                        "Amount": f"₹{p['amount']:,.0f}",
                        "Mode": p.get("mode", "cash").upper(),
                        "Reference": p.get("reference", "—"),
                        "Note": p.get("note", ""),
                    } for p in reversed(_pays[-20:])])
                    st.dataframe(_ph_df, use_container_width=True, hide_index=True, height=200)

                    _total_paid = sum(p["amount"] for p in _pays)
                    st.success(f"💰 Total paid to Meena Agencies: **₹{_total_paid:,.0f}**")
                    st.caption(f"Outstanding balance: ₹{r['outstanding']:,.0f}")

    with _rec_col:
        st.markdown('<div class="corp-section"><div class="corp-section-title">🌦️ Seasonal Picks</div>'
                    '<div class="corp-section-sub">Recommended for this season</div></div>',
                    unsafe_allow_html=True)

        try:
            import forecast_pro as _fp
            _season_key, _season_info = _fp.current_season()
            _season_diseases = _fp.SEASON_DISEASES.get(_season_key, [])
            _season_meds = set()
            for _d in _season_diseases:
                for _m in _fp.DISEASE_MEDICINES.get(_d, []):
                    _season_meds.add(_m)

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(0,212,255,0.10),rgba(123,97,255,0.10));
                        border:1px solid rgba(0,212,255,0.3);border-radius:14px;
                        padding:1rem 1.2rem;margin-bottom:1rem;">
                <div style="font-size:0.75rem;color:#8892b0;letter-spacing:1.5px;">CURRENT SEASON</div>
                <div style="font-size:1.6rem;font-weight:800;color:#00d4ff;margin:0.3rem 0;">
                    {_season_info['emoji']} {_season_info['name']}
                </div>
                <div style="color:#8892b0;font-size:0.8rem;">
                    Watch for: {', '.join(_season_diseases[:3])}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Match against inventory to show 4 suggestions
            _df_sugg = load_inventory()
            _shown = set()
            _count = 0
            for _, _row in _df_sugg.iterrows():
                if _count >= 4:
                    break
                _matches = _fp.match_medicine(_row["medicine_name"])
                for _m in _matches:
                    if _m in _season_meds and _row["medicine_name"] not in _shown:
                        _shown.add(_row["medicine_name"])
                        st.markdown(f"""
                        <div style="background:rgba(26,31,58,0.7);border-left:3px solid #00d47a;
                                    border-radius:8px;padding:0.5rem 0.8rem;margin:0.3rem 0;">
                            <b>{_row['medicine_name']}</b>
                            <span style="color:#00d47a;font-size:0.75rem;float:right;">
                                ₹{_row['selling_price']:.2f}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        _count += 1
                        break
        except Exception as _e:
            st.caption(f"Seasonal picks unavailable: {_e}")

    st.markdown("---")

    # ─── Spending Trend Chart (last 6 months) ───
    if _my_approved:
        try:
            import plotly.graph_objects as _go_gap
            from datetime import datetime as _dt_gap, timedelta as _td_gap
            _now_gap = _dt_gap.now()
            _months = []
            _totals = []
            for _i in range(5, -1, -1):
                _m_start = (_now_gap.replace(day=1) - _td_gap(days=_i * 30)).replace(day=1)
                _m_end = (_m_start.replace(day=28) + _td_gap(days=4)).replace(day=1)
                _month_total = 0
                for _o in _my_approved:
                    try:
                        _od = _dt_gap.strptime(_o.get("placed_at", "")[:11], "%d-%b-%Y")
                        if _m_start <= _od < _m_end:
                            _month_total += _o.get("total", 0)
                    except Exception:
                        pass
                _months.append(_m_start.strftime("%b"))
                _totals.append(_month_total)

            st.markdown('<div class="corp-section"><div class="corp-section-title">📈 Your Spending</div>'
                        '<div class="corp-section-sub">Last 6 months trend</div></div>',
                        unsafe_allow_html=True)

            _fig_gap = _go_gap.Figure(data=[_go_gap.Bar(
                x=_months, y=_totals,
                marker=dict(color="#00d4ff", line=dict(color="#7b61ff", width=2)),
                text=[f"₹{v:,.0f}" if v > 0 else "" for v in _totals],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
            )])
            _fig_gap.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaf6"),
                height=280,
                margin=dict(l=20, r=20, t=20, b=40),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="Amount (₹)"),
                showlegend=False,
            )
            st.plotly_chart(_fig_gap, use_container_width=True, key="gap_spend_chart")
        except Exception:
            pass



    # ═══ NEW: Amazon-style order UI ═══
    try:
        customer_order_ui.render(r)
    except Exception as _co_e:
        st.error(f"Order UI error: {_co_e}")
    st.stop()

    st.markdown("### 📦 Place Order")

    # Build catalog (cached)
    @st.cache_data(show_spinner=False, ttl=300)
    def _get_catalog(_df):
        return catalog.build_catalog(_df)

    df = load_inventory()
    _cat = _get_catalog(df)

    # Session state
    if "catalog_category" not in st.session_state:
        st.session_state.catalog_category = None
    if "catalog_search" not in st.session_state:
        st.session_state.catalog_search = ""
    if "catalog_medicine" not in st.session_state:
        st.session_state.catalog_medicine = None

    # ─── Breadcrumb ───
    _bc = []
    if st.session_state.catalog_category:
        _bc.append(st.session_state.catalog_category)
# ═══════════════════════════════════════════════════════════
# OLD CATALOG DISABLED — new UI is at customer_order_ui.render()
# This was causing DuplicateWidgetID + empty space
# ═══════════════════════════════════════════════════════════
    pass

# ═══════ SAFE MODE WRAPPER ═══════
# Any unhandled error after this point is caught and logged, never crashes the UI.
# Remove this wrapper if you want to see full tracebacks during debugging.

    with tab14:
        owner_staff_report.render()


    with tab15:
        toolbox_demo.render()
