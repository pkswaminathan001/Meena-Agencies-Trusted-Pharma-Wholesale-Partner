"""
auth_screen.py — Linux-style login. Click user → enter password only.
"""
import streamlit as st
import hmac
import json
import hashlib
from pathlib import Path


LOGIN_CSS = """
<style>
/* ── Full-screen peacock login ── */
.stApp { background: #050818 !important; }
header[data-testid="stHeader"], [data-testid="stToolbar"], footer, #MainMenu {
    display: none !important;
}
.block-container { padding: 2vh 1rem !important; max-width: 100% !important; }

/* Background mesh */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: -20%; z-index: 0;
    background:
        radial-gradient(closest-side, rgba(0,212,170,0.28), transparent 70%) 15% 20% / 60% 60% no-repeat,
        radial-gradient(closest-side, rgba(123,97,255,0.32), transparent 70%) 85% 25% / 70% 70% no-repeat,
        radial-gradient(closest-side, rgba(255,180,71,0.18), transparent 70%) 50% 90% / 60% 60% no-repeat,
        linear-gradient(160deg, #050818 0%, #0a1f2f 45%, #0a1830 100%);
    filter: blur(30px); pointer-events: none;
}
.main, .main .block-container, section.main { position: relative; z-index: 2; }

/* Hero card */
.ma-login-wrap {
    max-width: 480px; margin: 3vh auto 0;
    animation: loginRise .6s cubic-bezier(.2,.85,.3,1.05) both;
}
@keyframes loginRise {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
.ma-login-card {
    padding: 36px 38px 30px;
    border-radius: 22px;
    background: linear-gradient(160deg, rgba(20,30,60,0.88), rgba(10,20,45,0.92));
    border: 1px solid rgba(0,212,170,0.25);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 0 60px rgba(0,212,170,0.15), 0 20px 50px rgba(0,0,0,0.5);
    text-align: center;
}
.ma-login-logo {
    display: block; width: 100px; height: 100px;
    margin: 0 auto 16px;
    border-radius: 50%; object-fit: cover;
    background: #fff; padding: 5px;
    box-shadow: 0 0 30px rgba(0,212,170,0.4), 0 0 60px rgba(123,97,255,0.25);
    border: 2px solid rgba(0,212,170,0.4);
}
.ma-login-brand {
    font-family: Georgia, serif; font-size: 1.75rem; font-weight: 800;
    letter-spacing: 1.4px; margin: 0 0 4px;
    background: linear-gradient(90deg, #00d4aa, #7b61ff, #ffb547, #00d4aa);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.ma-login-sub {
    font-size: 0.72rem; letter-spacing: 3px; text-transform: uppercase;
    color: #8892b0; margin: 0 0 6px;
}
.ma-login-title {
    font-size: 1.05rem; font-weight: 600; color: #b8c0d8;
    margin: 18px 0 16px;
}

/* User icon cards */
.ma-user-row {
    display: flex; justify-content: center;
    gap: 14px; margin: 8px 0 4px;
    flex-wrap: wrap;
}
.ma-user-card {
    flex: 1 1 100px; min-width: 100px; max-width: 130px;
    padding: 18px 12px;
    border-radius: 16px;
    background: linear-gradient(160deg, rgba(30,45,80,0.7), rgba(15,25,50,0.8));
    border: 2px solid rgba(0,212,170,0.15);
    text-align: center;
    cursor: pointer;
    transition: all .25s ease;
    animation: userPop .4s ease-out both;
}
.ma-user-card:nth-child(1) { animation-delay: .1s; }
.ma-user-card:nth-child(2) { animation-delay: .18s; }
.ma-user-card:nth-child(3) { animation-delay: .26s; }
.ma-user-card:hover {
    border-color: rgba(0,212,170,0.7);
    background: linear-gradient(160deg, rgba(0,212,170,0.15), rgba(123,97,255,0.1));
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,212,170,0.25);
}
@keyframes userPop {
    from { opacity: 0; transform: scale(0.9); }
    to   { opacity: 1; transform: scale(1); }
}
.ma-user-icon { font-size: 2.4rem; display: block; margin-bottom: 6px; }
.ma-user-name {
    font-size: 0.9rem; font-weight: 700; color: #eaf6ff;
    letter-spacing: 0.3px;
}
.ma-user-sub { font-size: 0.7rem; color: #8892b0; margin-top: 2px; }

/* Password label / input */
div[data-testid="stTextInput"] label {
    color: #8892b0 !important; font-size: 0.72rem !important;
    letter-spacing: 1.8px !important; text-transform: uppercase !important;
    font-weight: 600 !important;
}
div[data-testid="stTextInput"] input {
    background: rgba(8,18,40,0.8) !important;
    border: 1.5px solid rgba(0,212,170,0.3) !important;
    border-radius: 12px !important;
    color: #eaf6ff !important;
    padding: 14px 18px !important;
    font-size: 1rem !important;
    letter-spacing: 3px;
    text-align: center;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,212,170,0.9) !important;
    box-shadow: 0 0 0 4px rgba(0,212,170,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(120deg, #0e8f7a, #1a5fb4) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    min-height: 48px;
    box-shadow: 0 10px 22px -12px rgba(26,95,180,0.7) !important;
    transition: all .2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 32px -14px rgba(0,212,170,0.7) !important;
}

/* User badge when logged in */
.ma-user-badge {
    position: fixed; top: 14px; right: 18px;
    padding: 8px 16px; border-radius: 20px;
    background: linear-gradient(135deg, rgba(0,212,170,0.2), rgba(123,97,255,0.2));
    border: 1px solid rgba(0,212,170,0.4);
    color: #eaf6ff; font-size: 0.85rem; font-weight: 600;
    z-index: 9999;
    backdrop-filter: blur(10px);
}
.ma-user-badge .ma-badge-name { color: #00d4aa; }

@media (max-width: 480px) {
    .ma-user-card { flex: 1 1 90px; padding: 14px 8px; }
    .ma-user-icon { font-size: 2rem; }
    .ma-user-name { font-size: 0.8rem; }
    .ma-login-card { padding: 28px 22px 24px; }
}
</style>
"""


def _get_logo_b64():
    try:
        import base64
        p = Path("logo.png")
        return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""
    except Exception:
        return ""


def _load_users():
    """Load owner, staff, retailers."""
    users = {"owner": [], "staff": [], "retailer": []}

    # Owner
    try:
        o = json.loads(Path("owner.json").read_text())
        users["owner"].append({
            "id": "owner",
            "name": o.get("username", "Owner").title(),
            "sub": "Full access",
            "pin_hash": o.get("pin_hash", ""),
        })
    except Exception:
        pass

    # Staff (optional — check users.json)
    try:
        u = json.loads(Path("users.json").read_text())
        if isinstance(u, list):
            for staff in u:
                if staff.get("role") == "staff":
                    users["staff"].append({
                        "id": staff.get("id", "staff"),
                        "name": staff.get("name", "Staff"),
                        "sub": staff.get("position", "Staff"),
                        "pin_hash": staff.get("pin_hash", ""),
                    })
    except Exception:
        pass

    # Retailers
    try:
        r = json.loads(Path("retailers.json").read_text())
        for ret in r:
            users["retailer"].append({
                "id": ret["id"],
                "name": ret.get("owner", ret["shop"]),
                "sub": ret["shop"],
                "pin_hash": ret.get("pin_hash", ""),
            })
    except Exception:
        pass

    return users


def _verify(pin, pin_hash):
    """Verify pin against stored hash."""
    if not pin or not pin_hash:
        return False
    try:
        import security
        return security.verify_secret(pin, pin_hash)
    except Exception:
        # Fallback: simple sha256
        h = hashlib.sha256(pin.encode()).hexdigest()
        return h == pin_hash


def _render_user_card(icon, name, sub):
    st.markdown(f'''
    <div class="ma-user-card">
        <span class="ma-user-icon">{icon}</span>
        <div class="ma-user-name">{name}</div>
        <div class="ma-user-sub">{sub}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_login():
    """
    Main login flow. Returns:
      None — not logged in yet
      dict {role, id, name} — logged in
    """
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    logo = _get_logo_b64()

    # Initialize session keys
    for k in ["_login_stage", "_login_role", "_login_user_id", "_login_user_name"]:
        if k not in st.session_state:
            st.session_state[k] = None

    stage = st.session_state.get("_login_stage")

    # ═══════════════════════════════════════════════════════════
    # STAGE 1 — Click user type
    # ═══════════════════════════════════════════════════════════
    if stage is None:
        with st.container():
            st.markdown(f'''
            <div class="ma-login-wrap">
                <div class="ma-login-card">
                    {f'<img class="ma-login-logo" src="data:image/png;base64,{logo}" alt="Logo" />' if logo else ''}
                    <div class="ma-login-brand">MEENA AGENCIES</div>
                    <div class="ma-login-sub">Trusted Pharma Wholesale Partner</div>
                    <div class="ma-login-title">Who's logging in?</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👔\n\n**Owner**\n\nFull access", key="pick_owner", use_container_width=True):
                st.session_state["_login_role"] = "owner"
                st.session_state["_login_stage"] = "password"
                st.rerun()
        with col2:
            if st.button("👨‍💼\n\n**Staff**\n\nLimited access", key="pick_staff", use_container_width=True):
                st.session_state["_login_role"] = "staff"
                st.session_state["_login_stage"] = "password"
                st.rerun()
        with col3:
            if st.button("🏪\n\n**Retailer**\n\nPlace orders", key="pick_retailer", use_container_width=True):
                st.session_state["_login_role"] = "retailer"
                st.session_state["_login_stage"] = "pick_user"
                st.rerun()

        return None

    # ═══════════════════════════════════════════════════════════
    # STAGE 1.5 — Retailer picks which shop (only for retailers)
    # ═══════════════════════════════════════════════════════════
    if stage == "pick_user" and st.session_state.get("_login_role") == "retailer":
        users = _load_users()
        retailers = users.get("retailer", [])

        st.markdown(f'''
        <div class="ma-login-wrap">
            <div class="ma-login-card">
                {f'<img class="ma-login-logo" src="data:image/png;base64,{logo}" alt="Logo" />' if logo else ''}
                <div class="ma-login-brand">MEENA AGENCIES</div>
                <div class="ma-login-title">🏪 Which pharmacy?</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        if not retailers:
            st.error("No retailers registered. Contact owner.")
            if st.button("← Back"):
                st.session_state["_login_stage"] = None
                st.rerun()
            return None

        cols = st.columns(min(3, len(retailers)))
        for i, ret in enumerate(retailers):
            with cols[i % len(cols)]:
                if st.button(f"🏪\n\n**{ret['name']}**\n\n{ret['sub']}",
                             key=f"pick_{ret['id']}", use_container_width=True):
                    st.session_state["_login_user_id"] = ret["id"]
                    st.session_state["_login_user_name"] = ret["name"]
                    st.session_state["_login_stage"] = "password"
                    st.rerun()

        if st.button("← Back", key="back_from_pick"):
            st.session_state["_login_stage"] = None
            st.rerun()

        return None

    # ═══════════════════════════════════════════════════════════
    # STAGE 2 — Enter password only
    # ═══════════════════════════════════════════════════════════
    if stage == "password":
        role = st.session_state.get("_login_role")
        uid = st.session_state.get("_login_user_id")
        uname = st.session_state.get("_login_user_name")

        # For owner/staff, uid stays None until now
        users = _load_users()

        if role == "owner":
            user = users["owner"][0] if users["owner"] else {"id": "owner", "name": "Owner", "pin_hash": ""}
        elif role == "staff":
            if uid:
                user = next((s for s in users["staff"] if s["id"] == uid), None)
            else:
                user = users["staff"][0] if users["staff"] else {"id": "staff", "name": "Staff", "pin_hash": ""}
        else:
            user = next((r for r in users["retailer"] if r["id"] == uid), None)

        if user is None:
            st.error("User not found.")
            st.session_state["_login_stage"] = None
            st.rerun()
            return None

        icon = {"owner": "👔", "staff": "👨‍💼", "retailer": "🏪"}.get(role, "👤")
        label = user["name"]
        sub = user.get("sub", "")

        st.markdown(f'''
        <div class="ma-login-wrap">
            <div class="ma-login-card">
                {f'<img class="ma-login-logo" src="data:image/png;base64,{logo}" alt="Logo" />' if logo else ''}
                <div class="ma-login-brand">MEENA AGENCIES</div>
                <div class="ma-login-title">{icon} {label}</div>
                <div style="color:#8892b0;font-size:0.8rem;margin-bottom:8px;">{sub}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            pin = st.text_input("Password", type="password", key="_login_pin",
                                placeholder="Enter password")
            if st.button("🔓  Login", use_container_width=True, key="_login_submit"):
                if _verify(pin, user.get("pin_hash", "")):
                    st.session_state["_login_stage"] = None
                    st.session_state["_login_role"] = None
                    st.session_state["_login_user_id"] = None
                    st.session_state["_login_user_name"] = None
                    return {"role": role, "id": user["id"], "name": user["name"]}
                else:
                    st.error("❌ Wrong password")

            if st.button("← Choose different user", use_container_width=True, key="_login_back"):
                st.session_state["_login_stage"] = None
                st.session_state["_login_role"] = None
                st.session_state["_login_user_id"] = None
                st.rerun()

        return None

    return None


def render_user_badge(role, name):
    """Show current user in top-right."""
    icon = {"owner": "👔", "staff": "👨‍💼", "retailer": "🏪"}.get(role, "👤")
    st.markdown(f'''
    <div class="ma-user-badge">
        {icon} <span class="ma-badge-name">{name}</span>
    </div>
    ''', unsafe_allow_html=True)
