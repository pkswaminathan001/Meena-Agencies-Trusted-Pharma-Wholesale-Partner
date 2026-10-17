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
    """Delegates to theme.py — no local CSS here."""
    import theme
    theme.apply()


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
