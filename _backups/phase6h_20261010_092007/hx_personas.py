"""hx_personas.py - HX (Human Experience) helpers for Meena Agencies.
Dad mode, staff tutorial, rep motivation, accessibility.
Nothing replaced - only new helpers."""
import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path


# ═══════════════════════════════════════════════
# PERSONA MODES
# ═══════════════════════════════════════════════

PERSONAS = {
    "owner": {
        "icon": "👔",
        "title": "Owner Mode",
        "desc": "Full access · All tabs visible",
        "font_scale": 1.0,
        "simplified": False,
    },
    "dad": {
        "icon": "🧓",
        "title": "Dad Mode (Simplified)",
        "desc": "Large fonts · Only essential tabs · One-tap actions",
        "font_scale": 1.35,
        "simplified": True,
        "essential_tabs": ["📋 Approvals", "💰 Payments", "🧠 AI Chat", "🔒 Audit"],
    },
    "staff": {
        "icon": "👨‍💼",
        "title": "Staff Mode",
        "desc": "Guided workflow · Tutorial mode ON · Keyboard shortcuts",
        "font_scale": 1.0,
        "simplified": False,
        "tutorial": True,
    },
    "accountant": {
        "icon": "📊",
        "title": "Accountant Mode",
        "desc": "Read-only financials · Exports enabled",
        "font_scale": 1.0,
        "simplified": False,
        "read_only": True,
    },
}


def get_persona() -> str:
    """Get current persona (defaults to owner)."""
    return st.session_state.get("_persona", "owner")


def set_persona(name: str):
    """Set the current persona."""
    if name in PERSONAS:
        st.session_state["_persona"] = name


def apply_persona_style():
    """Apply font scale and styling based on persona."""
    persona = get_persona()
    config = PERSONAS.get(persona, PERSONAS["owner"])

    scale = config.get("font_scale", 1.0)

    if scale != 1.0:
        st.markdown(f"""
        <style>
        html, body, [class*="css"] {{
            font-size: {scale}em !important;
        }}
        h1 {{ font-size: {2.5 * scale}rem !important; }}
        h2 {{ font-size: {2 * scale}rem !important; }}
        h3 {{ font-size: {1.5 * scale}rem !important; }}
        .stButton > button {{
            font-size: {1.1 * scale}rem !important;
            padding: {0.6 * scale}rem {1.5 * scale}rem !important;
            min-height: {44 * scale}px !important;
        }}
        input, textarea, select {{
            font-size: {1 * scale}rem !important;
            padding: {0.6 * scale}rem !important;
        }}
        </style>
        """, unsafe_allow_html=True)


def persona_selector():
    """Small persona selector for the top of the app."""
    current = get_persona()
    with st.expander("👤 Switch View Mode", expanded=False):
        st.caption("Choose how you want the app to look and behave.")
        cols = st.columns(len(PERSONAS))
        for col, (key, config) in zip(cols, PERSONAS.items()):
            with col:
                is_active = key == current
                label = f"{config['icon']} {config['title']}"
                if is_active:
                    label = f"✅ {label}"
                if st.button(label, key=f"persona_{key}", use_container_width=True):
                    set_persona(key)
                    st.rerun()


def should_show_tab(tab_name: str) -> bool:
    """Check if a tab should be visible for the current persona."""
    persona = get_persona()
    config = PERSONAS.get(persona, PERSONAS["owner"])

    if not config.get("simplified"):
        return True

    essential = config.get("essential_tabs", [])
    return any(word in tab_name for word in essential)


def is_read_only() -> bool:
    """Check if current persona is read-only (e.g., accountant)."""
    persona = get_persona()
    return PERSONAS.get(persona, {}).get("read_only", False)


# ═══════════════════════════════════════════════
# STAFF TUTORIAL
# ═══════════════════════════════════════════════

TUTORIALS = {
    "orders": {
        "title": "How to Handle Orders",
        "steps": [
            "Go to 📋 Approvals tab",
            "Review each pending order",
            "Click ✅ Approve or ❌ Reject",
            "Approved orders reduce your stock automatically",
        ],
    },
    "retailers": {
        "title": "Managing Retailers",
        "steps": [
            "Go to ⚙️ Settings tab",
            "See all registered retailers",
            "Use ➕ Add Retailer to onboard new ones",
            "Block a retailer if they exceed credit limits",
        ],
    },
    "inventory": {
        "title": "Tracking Inventory",
        "steps": [
            "Go to 💼 Ops → 📦 Add Stock",
            "Enter medicine name, batch, expiry, qty",
            "Click 🔍 Review Before Saving",
            "Confirm to add to inventory",
        ],
    },
    "ask": {
        "title": "Using AI Chat (/ask)",
        "steps": [
            "Open Telegram and message the bot",
            "Type /ask followed by any question",
            "Example: /ask how many orders do we have",
            "The bot replies with real data in seconds",
        ],
    },
}


def render_tutorial(screen_key: str, force: bool = False):
    """Show tutorial overlay for a screen if not seen before."""
    if screen_key not in TUTORIALS:
        return

    flag = f"_tutorial_seen_{screen_key}"
    if st.session_state.get(flag) and not force:
        return

    tutorial = TUTORIALS[screen_key]

    with st.expander(f"📚 {tutorial['title']}", expanded=True):
        for i, step in enumerate(tutorial["steps"], 1):
            st.markdown(f"**{i}.** {step}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Got it", key=f"tut_done_{screen_key}", use_container_width=True):
                st.session_state[flag] = True
                st.rerun()
        with c2:
            if st.button("📖 Re-open later", key=f"tut_later_{screen_key}", use_container_width=True):
                st.session_state[flag] = True
                st.rerun()


def tutorial_button(screen_key: str):
    """Small button to re-open tutorial anytime."""
    if screen_key in TUTORIALS:
        if st.button(f"❓ Help", key=f"help_{screen_key}", help="Show tutorial"):
            st.session_state[f"_tutorial_seen_{screen_key}"] = False
            st.rerun()


# ═══════════════════════════════════════════════
# REP MOTIVATION
# ═══════════════════════════════════════════════

def calculate_rep_score(rep_id: str, visits: int, orders: int, idle_minutes: int) -> dict:
    """Calculate a rep's daily motivation score (0-100)."""
    score = 0
    score += min(visits * 4, 40)   # up to 40 from visits
    score += min(orders * 8, 40)   # up to 40 from orders
    score -= min(idle_minutes, 20) # penalty for idle

    score = max(0, min(100, score))

    if score >= 80:
        tier = "🏆 Champion"
    elif score >= 60:
        tier = "⭐ Star"
    elif score >= 40:
        tier = "👍 Solid"
    else:
        tier = "🎯 Needs Push"

    return {"score": score, "tier": tier}


def render_rep_scorecard(rep_name: str, score_data: dict):
    """Show a rep's daily score card."""
    score = score_data["score"]
    tier = score_data["tier"]

    color = "#00d47a" if score >= 70 else ("#ffb547" if score >= 40 else "#ff4d6d")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(0,212,255,0.10), rgba(123,97,255,0.10));
                border:1px solid {color};border-radius:14px;padding:1.25rem;margin:0.5rem 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="color:#8892b0;font-size:0.75rem;letter-spacing:1px;">TODAY'S SCORE</div>
                <div style="font-size:2rem;font-weight:900;color:{color};">{score}/100</div>
                <div style="color:{color};font-size:0.85rem;font-weight:600;">{tier}</div>
            </div>
            <div style="font-size:3rem;opacity:0.3;">{tier.split()[0]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_leaderboard(reps: list):
    """
    Show a weekly leaderboard.
    reps = [{"name": "Ravi", "score": 85, "visits": 12}]
    """
    if not reps:
        st.info("No reps to rank yet.")
        return

    sorted_reps = sorted(reps, key=lambda x: -x.get("score", 0))

    st.markdown("### 🏆 Weekly Leaderboard")
    for i, rep in enumerate(sorted_reps[:10], 1):
        medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"#{i}"))
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:0.75rem 1rem;
                    background:rgba(15,26,58,0.7);border-radius:10px;margin:0.3rem 0;
                    border-left:4px solid {'#ffb547' if i <= 3 else '#8892b0'};">
            <div>
                <b>{medal} {rep.get('name','?')}</b>
            </div>
            <div style="color:#00d4ff;font-weight:700;">
                {rep.get('score',0)}/100 · {rep.get('visits',0)} visits
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# ACCESSIBILITY
# ═══════════════════════════════════════════════

def high_contrast_mode():
    """Toggle high contrast mode."""
    enabled = st.session_state.get("_high_contrast", False)
    if st.button(
        f"{'✅' if enabled else '🔲'} High Contrast",
        key="contrast_toggle",
        use_container_width=True
    ):
        st.session_state["_high_contrast"] = not enabled
        st.rerun()

    if enabled:
        st.markdown("""
        <style>
        .stApp { background: #000000 !important; }
        * { color: #ffffff !important; }
        .stButton > button {
            background: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #ffff00 !important;
            font-weight: 700 !important;
        }
        .stButton > button:hover {
            background: #ffff00 !important;
            color: #000000 !important;
        }
        input, textarea, select {
            background: #000000 !important;
            color: #ffffff !important;
            border: 2px solid #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)


def large_touch_targets():
    """Enable large touch targets for tablets/phones."""
    st.markdown("""
    <style>
    @media (hover: none) and (pointer: coarse) {
        .stButton > button {
            min-height: 56px !important;
            font-size: 1.1rem !important;
        }
        input, textarea, select {
            min-height: 56px !important;
            font-size: 1.1rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            min-height: 56px !important;
            font-size: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
