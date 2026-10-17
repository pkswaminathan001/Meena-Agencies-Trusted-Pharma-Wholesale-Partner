"""
login_ui.py — Beautiful 3-way login screen (Owner / Staff / Customer).
Uses rbac.py for authentication.
"""
import streamlit as st
import base64
from pathlib import Path
from datetime import datetime
import rbac


def _logo_b64():
    if Path("logo.png").exists():
        try:
            return base64.b64encode(Path("logo.png").read_bytes()).decode()
        except Exception:
            return ""
    return ""


def _inject_css():
    """Premium login screen CSS."""
    st.markdown("""
    <style>
    @keyframes lpFade {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes lpGlow {
        0%,100% { box-shadow: 0 0 40px rgba(0,212,170,0.3); }
        50%     { box-shadow: 0 0 80px rgba(0,212,170,0.55); }
    }
    @keyframes lpFloat {
        0%,100% { transform: translateY(0); }
        50%     { transform: translateY(-6px); }
    }
    @keyframes lpShimmer {
        0%   { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    /* Hide the tiny default logo top-left */
    header[data-testid="stHeader"] { display: none !important; }
    .stApp > header { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }

    /* Hide every Streamlit default chrome element */
    header[data-testid="stHeader"] { display: none !important; height: 0 !important; }
    [data-testid="stHeader"] { display: none !important; height: 0 !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    .stApp > header { display: none !important; }
    .stApp > div:first-child > header { display: none !important; }
    #MainMenu { display: none !important; visibility: hidden !important; }
    [data-testid="baseButton-headerNoPadding"] { display: none !important; }
    button[kind="headerNoPadding"] { display: none !important; }
    .stAppToolbar { display: none !important; }
    img[alt="Logo"] { display: none !important; }
    img[alt="app-logo"] { display: none !important; }
    [data-testid="stHeaderLogo"] { display: none !important; }
    .stApp > header > div:first-child { display: none !important; }

    /* Also hide the auto-generated Streamlit favicon/title area */
    .stApp > div[class*="stApp"] > header { display: none !important; }

    /* Full-page cinematic background */
    .stApp {
        background:
            radial-gradient(ellipse 800px 400px at 10% 0%, rgba(0,212,170,0.10), transparent 60%),
            radial-gradient(ellipse 800px 400px at 90% 100%, rgba(123,97,255,0.14), transparent 60%),
            linear-gradient(180deg, #0a0e27 0%, #050810 100%) !important;
    }
    .block-container {
        padding-top: 0.4rem !important;
        max-width: 100% !important;
    }

    /* Hide default Streamlit header */
    .stApp > header { display: none !important; }

    /* ── The premium card ── */
    .lp-wrap {
        animation: lpFade 0.6s ease-out;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
        padding: 40px 20px;
    }
    .lp-card {
        position: relative;
        width: 100%;
        max-width: 460px;
        padding: 44px 40px 40px;
        border-radius: 24px;
        background: linear-gradient(160deg, rgba(16,22,54,0.95), rgba(10,14,39,0.95));
        border: 1px solid rgba(0,212,170,0.25);
        box-shadow:
            0 32px 80px rgba(0,0,0,0.6),
            0 0 60px rgba(0,212,170,0.08),
            inset 0 1px 0 rgba(255,255,255,0.05);
        animation: lpFade 0.7s ease-out;
    }
    .lp-card::before {
        content: "";
        position: absolute;
        top: -1px; left: 20%; right: 20%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4aa, #7b61ff, transparent);
        animation: lpShimmer 3s linear infinite;
        background-size: 200% 100%;
    }

    /* Brand block */
    .lp-brand-row {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 26px;
    }
    .lp-brand-logo {
        width: 64px; height: 64px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(0,212,170,0.15), rgba(123,97,255,0.15));
        border: 1px solid rgba(0,212,170,0.35);
        display: flex; align-items: center; justify-content: center;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0,212,170,0.3);
        animation: lpFloat 4s ease-in-out infinite;
    }
    .lp-brand-logo img {
        width: 100%; height: 100%;
        object-fit: contain;
    }
    .lp-brand-name {
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #00d4aa, #7b61ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }
    .lp-brand-tag {
        font-size: 0.68rem;
        color: #8892b0;
        letter-spacing: 3px;
        margin-top: 4px;
        text-transform: uppercase;
    }

    /* Role picker */
    .lp-role-label {
        font-size: 0.72rem;
        color: #8892b0;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
        font-weight: 700;
    }

    /* Form fields */
    .stTextInput > div > div input,
    .stTextInput > div > div > input {
        background: rgba(10,14,39,0.7) !important;
        border: 1px solid rgba(0,212,170,0.2) !important;
        border-radius: 10px !important;
        color: #e8eaf6 !important;
        transition: border-color .18s ease, box-shadow .18s ease !important;
    }
    .stTextInput > div > div input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 3px rgba(0,212,170,0.18) !important;
    }

    /* Login button */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00d4aa, #7b61ff) !important;
        color: #fff !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        transition: transform .15s ease, box-shadow .15s ease !important;
        box-shadow: 0 8px 24px rgba(0,212,170,0.35) !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(0,212,170,0.55) !important;
    }

    /* Role tab buttons */
    .stButton > button[kind="secondary"] {
        background: rgba(10,14,39,0.5) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #cbd5f0 !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all .18s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: rgba(0,212,170,0.5) !important;
        background: rgba(0,212,170,0.08) !important;
        transform: translateY(-1px) !important;
        color: #00d4aa !important;
    }

    /* Trust row */
    .lp-trust {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 22px;
        padding-top: 18px;
        border-top: 1px solid rgba(255,255,255,0.06);
        font-size: 0.72rem;
        color: #6b7490;
        letter-spacing: 1px;
    }
    .lp-trust span {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
    """, unsafe_allow_html=True)



    # Aggressive hide for Streamlit's top-left logo/header
    st.markdown("""
    <style>
    /* Hide EVERY element that might render a top-left logo */
    header, [data-testid="stHeader"] { display: none !important; height: 0 !important; }
    [data-testid="stHeaderLogo"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { display: none !important; }
    .stApp > header { display: none !important; }
    .stAppHeader { display: none !important; }
    [class*="stAppHeader"] { display: none !important; }
    [class*="header"] { }
    img[alt="Logo"], img[alt="app-logo"], img[alt="logo"] { display: none !important; }
    [data-testid="stImage"]:first-child { display: none !important; }
    div[data-testid="stVerticalBlock"] > div > div[data-testid="stImage"] {
        display: none !important;
    }
    /* Aggressive: any image in first 100px vertical space */
    section.main > div > div > div > div[data-testid="stImage"]:nth-of-type(1) {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _load_company():
    try:
        import json
        return json.loads(Path("company.json").read_text())
    except Exception:
        return {}


def render_login_page():
    """
    Main entry point. Renders 3-role login.
    Returns True if login succeeded (session is set).
    """
    _inject_css()


    company = _load_company()
    mode = rbac.get_security_mode(company)
    mode_class = f"mode-{mode}"

    # Current selected role (default: customer)
    if "login_role" not in st.session_state:
        st.session_state.login_role = "customer"

    # ─── Security mode banner (owner only visible) ───
    if mode != "normal":
        st.markdown(f"""
        <div style="text-align:center;">
            <span class="security-badge {mode_class}">
                {'🔒 STRICT MODE' if mode == 'strict' else '🚨 LOCKDOWN — Owner only'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ─── Logo + title ───
    logo = _logo_b64()
    if logo:
        st.markdown(f'<div class="login-wrap">'
                    f'<img src="data:image/png;base64,{logo}" class="login-logo" />'
                    f'<div class="login-title">MEENA AGENCIES</div>'
                    f'<div class="login-sub">Trusted Pharma Wholesale Partner</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="login-wrap">'
                    '<div class="login-title">MEENA AGENCIES</div>'
                    '<div class="login-sub">Trusted Pharma Wholesale Partner</div>',
                    unsafe_allow_html=True)

    # ─── Role selector (3 pills) ───
    _role_labels = {"customer": "🏪 Customer", "staff": "👨‍💼 Staff", "owner": "👔 Owner"}
    _lockdown = mode == "lockdown"

    # Build as native Streamlit buttons for reliability
    _c1, _c2, _c3 = st.columns(3)
    with _c1:
        if st.button("🏪 Customer", use_container_width=True,
                     type="primary" if st.session_state.login_role == "customer" else "secondary",
                     key="role_customer_btn"):
            st.session_state.login_role = "customer"
            st.rerun()
    with _c2:
        if st.button("👨‍💼 Staff", use_container_width=True,
                     type="primary" if st.session_state.login_role == "staff" else "secondary",
                     key="role_staff_btn",
                     disabled=_lockdown):
            if not _lockdown:
                st.session_state.login_role = "staff"
                st.rerun()
    with _c3:
        if st.button("👔 Owner", use_container_width=True,
                     type="primary" if st.session_state.login_role == "owner" else "secondary",
                     key="role_owner_btn"):
            st.session_state.login_role = "owner"
            st.rerun()

    role = st.session_state.login_role

    # ─── Check if login allowed under current mode ───
    if not rbac.is_login_allowed(role, company):
        st.error(f"🚨 {role.title()} login is disabled in lockdown mode.")
        st.caption("Only the Owner can log in during lockdown.")
        return False

    # ─── Role-specific form ───
    _render_login_form(role)

    # ─── Close wrap ───
    st.markdown('</div>', unsafe_allow_html=True)

    return st.session_state.get("role") is not None


def _render_login_form(role):
    """Uniform login form for all 3 roles — centered, same width."""
    _l, _mid, _r = st.columns([1, 2, 1])
    with _mid:
        if role == "customer":
            st.markdown("##### 🏪 Retailer Login")
            st.caption("Enter your Retailer ID and 4-digit PIN")
            with st.form("login_customer", clear_on_submit=False):
                rid = st.text_input("Retailer ID", placeholder="RET001", key="cust_rid")
                pin = st.text_input("PIN (4 digits)", type="password", max_chars=4, key="cust_pin")
                if st.form_submit_button("🔓 Login", use_container_width=True, type="primary"):
                    _attempt_login("customer", rid, pin)

        elif role == "staff":
            st.markdown("##### 👨\u200d💼 Staff Login")
            st.caption("Enter your Staff ID and 6-digit PIN")
            with st.form("login_staff", clear_on_submit=False):
                sid = st.text_input("Staff ID", placeholder="STAFF001", key="staff_sid")
                pin = st.text_input("PIN (6 digits)", type="password", max_chars=6, key="staff_pin")
                if st.form_submit_button("🔓 Login", use_container_width=True, type="primary"):
                    _attempt_login("staff", sid, pin)

        elif role == "owner":
            st.markdown("##### 👔 Owner Login")
            st.caption("Full access to all modules")
            with st.form("login_owner", clear_on_submit=False):
                pin = st.text_input("Owner Password", type="password", key="owner_pin")
                if st.form_submit_button("🔓 Login", use_container_width=True, type="primary"):
                    _attempt_login("owner", "OWNER", pin)

        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:8px 0;"></div>', unsafe_allow_html=True)
        st.caption("🔒 All logins are logged with timestamp and IP.")


def _attempt_login(role, user_id, pin):
    """Common login handler with rate limiting."""
    if not user_id or not pin:
        st.error("Please fill in all fields.")
        return

    # Load retailers for customer lookup
    retailers = []
    if role == "customer":
        try:
            import json
            retailers = json.loads(Path("retailers.json").read_text())
        except Exception:
            pass

    ok, user, err = rbac.verify_login(role, user_id, pin, retailers)

    if not ok:
        st.error(f"❌ {err}")
        # Log failed attempt
        try:
            from security import log_action
            log_action(user_id, "LOGIN_FAILED", f"role={role}")
        except Exception:
            pass
        return

    # SUCCESS — create session
    st.session_state.role = role
    st.session_state.session = rbac.create_session(role, user.get("id", user_id))
    st.session_state.user = user

    if role == "customer":
        st.session_state.retailer = user
    elif role == "staff":
        st.session_state.staff = user
    elif role == "owner":
        st.session_state.owner_user = user

    # Fire in-app notification for the owner bell
    try:
        import notifications
        notifications.add(
            actor_id=user.get("id", user_id),
            actor_name=user.get("name", user.get("shop", "User")),
            actor_role=role,
            type=role + "_login",
            message=(user.get("name", user.get("shop", "User"))) + " logged in",
            severity="info",
        )
        print("[notif] added login notification for " + str(user.get("id", user_id)))
    except Exception as e:
        print("[notif] FAILED to add: " + str(e))

    # Log successful login
    try:
        from security import log_action
        log_action(user.get("id", user_id), "LOGIN_SUCCESS", f"role={role}")
    except Exception:
        pass
    try:
        from audit_pro import log_event
        log_event(user.get("id", user_id), "LOGIN_SUCCESS", page="login")
    except Exception:
        pass

    st.success(f"✅ Welcome, {user.get('name', user.get('shop', 'User'))}!")
    st.rerun()


# ═══════════════════════════════════════════════════════════
# LOGOUT HELPER
# ═══════════════════════════════════════════════════════════
def logout():
    """Clear session and return to login."""
    try:
        role = st.session_state.get("role", "unknown")
        uid = "UNKNOWN"
        if role == "customer" and st.session_state.get("retailer"):
            uid = st.session_state.retailer.get("id", "UNKNOWN")
        elif role == "staff" and st.session_state.get("staff"):
            uid = st.session_state.staff.get("id", "UNKNOWN")
        elif role == "owner":
            uid = "OWNER"
        from security import log_action
        log_action(uid, "LOGOUT", f"role={role}")
    except Exception:
        pass

    # Clear all state
    for k in list(st.session_state.keys()):
        try:
            del st.session_state[k]
        except Exception:
            pass
    st.rerun()


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("✅ login_ui.py compiles")
    print("   Roles supported: customer, staff, owner")
    print("   Security modes: normal, strict, lockdown")
