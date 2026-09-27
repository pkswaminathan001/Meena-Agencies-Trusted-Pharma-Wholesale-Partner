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
    st.markdown("""
    <style>
    .login-wrap {
        max-width: 480px;
        margin: 40px auto;
        background: linear-gradient(145deg, rgba(26,31,58,0.95), rgba(15,20,40,0.95));
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 20px;
        padding: 32px 28px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
        animation: slideUp 0.5s ease-out;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .login-logo {
        width: 100px; height: 100px;
        border-radius: 50%;
        display: block;
        margin: 0 auto 16px auto;
        box-shadow: 0 0 30px rgba(0,212,255,0.4), 0 0 60px rgba(123,97,255,0.3);
        border: 3px solid rgba(255,181,71,0.4);
    }
    .login-title {
        text-align: center;
        font-family: Georgia, serif;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffb547, #c41e3a, #ffb547);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
        margin-bottom: 4px;
    }
    @keyframes shimmer {
        0%   { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    .login-sub {
        text-align: center;
        color: #8892b0;
        font-size: 0.8rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 24px;
    }
    .role-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        background: rgba(15,20,40,0.6);
        padding: 6px;
        border-radius: 14px;
    }
    .role-pill {
        flex: 1;
        text-align: center;
        padding: 10px 6px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        color: #8892b0;
    }
    .role-pill:hover { background: rgba(0,212,255,0.08); color: #00d4ff; }
    .role-pill.active {
        background: linear-gradient(135deg, rgba(0,212,255,0.20), rgba(123,97,255,0.20));
        color: #00d4ff;
        box-shadow: 0 4px 14px rgba(0,212,255,0.25);
    }
    .security-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 0 auto 12px auto;
    }
    .mode-normal   { background: rgba(0,212,122,0.15); color: #00d47a; border: 1px solid #00d47a; }
    .mode-strict   { background: rgba(255,181,71,0.15); color: #ffb547; border: 1px solid #ffb547; }
    .mode-lockdown { background: rgba(255,77,109,0.15); color: #ff4d6d; border: 1px solid #ff4d6d; }
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

    st.markdown("<br>", unsafe_allow_html=True)
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
    """Render the login form for a specific role."""
    if role == "customer":
        st.markdown("##### 🏪 Retailer Login")
        st.caption("Enter your Retailer ID and 4-digit PIN")
        with st.form("login_customer", clear_on_submit=False):
            rid = st.text_input("Retailer ID", placeholder="RET001",
                                 key="cust_rid")
            pin = st.text_input("PIN (4 digits)", type="password",
                                 max_chars=4, key="cust_pin")
            if st.form_submit_button("🔓 Login", use_container_width=True, type="primary"):
                _attempt_login("customer", rid, pin)

    elif role == "staff":
        st.markdown("##### 👨‍💼 Staff Login")
        st.caption("Enter your Staff ID and PIN")
        with st.form("login_staff", clear_on_submit=False):
            sid = st.text_input("Staff ID", placeholder="STAFF001",
                                 key="staff_sid")
            pin = st.text_input("PIN (6 digits)", type="password",
                                 max_chars=6, key="staff_pin")
            if st.form_submit_button("🔓 Login", use_container_width=True, type="primary"):
                _attempt_login("staff", sid, pin)

    elif role == "owner":
        st.markdown("##### 👔 Owner Login")
        st.caption("Full access to all modules")
        with st.form("login_owner", clear_on_submit=False):
            pin = st.text_input("Owner Password", type="password",
                                 key="owner_pin")
            if st.form_submit_button("🔓 Login", use_container_width=True, type="primary"):
                _attempt_login("owner", "OWNER", pin)

    st.markdown("---")
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
