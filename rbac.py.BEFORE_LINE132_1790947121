"""
rbac.py — Role-Based Access Control for Meena Agencies.
3 roles: owner, staff, customer. 5 security layers.
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

USERS_FILE = "users.json"
SESSION_CONFIG = {
    "customer": {"timeout_min": 15,  "max_attempts": 3},
    "staff":    {"timeout_min": 30,  "max_attempts": 3},
    "owner":    {"timeout_min": 20,  "max_attempts": 5},
}

# ═══════════════════════════════════════════════════════════
# PERMISSIONS MATRIX
# ═══════════════════════════════════════════════════════════
PERMISSIONS = {
    # Owner: full access
    "owner": {
        "view": ["approvals", "health", "fraud", "autopos", "forecast",
                 "whatif", "intelligence", "settings", "audit", "ops",
                 "accounting", "climate", "delivery", "staff", "returns",
                 "customers"],
        "actions": ["approve_order", "reject_order", "dispatch_order",
                    "pack_order", "mark_delivered", "add_stock",
                    "record_payment", "edit_retailer", "delete_retailer",
                    "add_staff", "remove_staff", "wipe_audit",
                    "change_owner_password", "process_returns",
                    "create_return", "override_warnings", "send_alerts",
                    "view_accounting", "export_data"],
    },
    # Staff: operational
    "staff": {
        "view": ["queue", "dispatch", "stock", "returns",
                 "performance", "profile"],
        "actions": ["dispatch_order", "pack_order", "mark_delivered",
                    "add_stock", "process_returns", "create_return",
                    "view_queue"],
    },
    # Customer: self-service
    "customer": {
        "view": ["place_order", "my_orders", "track_delivery",
                 "payment_history", "my_returns", "profile"],
        "actions": ["place_order", "create_return", "change_own_pin",
                    "update_own_contact"],
    },
}


# ═══════════════════════════════════════════════════════════
# USERS STORAGE
# ═══════════════════════════════════════════════════════════
def _get_salt():
    """Reuse existing .salt if available."""
    p = Path(".salt")
    if p.exists():
        return p.read_bytes()
    salt = b"meena_default_salt_change_me"
    p.write_bytes(salt)
    return salt


def hash_secret(secret):
    salt = _get_salt()
    return hashlib.pbkdf2_hmac("sha256", str(secret).encode(), salt, 100000).hex()


def load_users():
    """Load users.json. Create default owner if missing."""
    if Path(USERS_FILE).exists():
        try:
            return json.loads(Path(USERS_FILE).read_text())
        except Exception:
            return _default_users()
    return _default_users()


def _default_users():
    """Seed with owner + a demo staff."""
    users = {
        "owner": {
            "id": "OWNER",
            "name": "Swaminathan (Owner)",
            "role": "owner",
            "pin_hash": hash_secret("owner2026"),
            "active": True,
            "created_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
        },
        "staff": [
            # Example staff — edit in Settings
            # {
            #   "id": "STAFF001",
            #   "name": "Rajesh (Packer)",
            #   "role": "staff",
            #   "pin_hash": hash_secret("123456"),
            #   "active": True,
            # }
        ],
    }
    Path(USERS_FILE).write_text(json.dumps(users, indent=2))
    return users


def save_users(data):
    Path(USERS_FILE).write_text(json.dumps(data, indent=2))


# ═══════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════
def verify_login(role, user_id, pin, retailers=None):
    """
    Return (success, user_dict, error_msg).
    role: 'owner' | 'staff' | 'customer'
    """
    users = load_users()

    if role == "owner":
        o = users.get("owner", {})
        if user_id != "OWNER" and user_id.lower() != "owner":
            return False, None, "Owner ID must be 'OWNER'"
        if not o.get("active", True):
            return False, None, "Owner account disabled"
        if hash_secret(pin) != o.get("pin_hash", ""):
            return False, None, "Wrong password"
        return True, o, None

    if role == "staff":
        for s in users.get("staff", []):
            if s["id"] == user_id:
                if not s.get("active", True):
                    return False, None, "Staff account disabled"
                if hash_secret(pin) != s.get("pin_hash", ""):
                    return False, None, "Wrong PIN"
                return True, s, None
        return False, None, "Staff ID not found"

    if role == "customer":
        if not retailers:
            return False, None, "System error — no retailers loaded"
        for r in retailers:
            if r["id"] == user_id.upper():
                if r.get("status") == "Blocked":
                    return False, None, "Account BLOCKED. Contact owner."
                if hash_secret(pin) != r.get("pin_hash", ""):
                    return False, None, "Wrong PIN"
                return True, {**r, "role": "customer"}, None
        return False, None, "Retailer ID not found"

    return False, None, "Unknown role"


# ═══════════════════════════════════════════════════════════
# PERMISSION CHECKS
# ═══════════════════════════════════════════════════════════
def can_view(role, module):
    if role not in PERMISSIONS:
        return False
    return module in PERMISSIONS[role]["view"]


def can_do(role, action):
    if role not in PERMISSIONS:
        return False
    return action in PERMISSIONS[role]["actions"]


def guard_view(role, module, show_error=True):
    """Streamlit helper — call at top of each tab."""
    if not can_view(role, module):
        if show_error:
            try:
                import streamlit as st
                st.error(f"🚫 Access denied: your role ({role}) cannot view '{module}'")
                st.stop()
            except Exception:
                pass
        return False
    return True


def guard_action(role, action, show_error=True):
    """Guard a button click."""
    if not can_do(role, action):
        if show_error:
            try:
                import streamlit as st
                st.error(f"🚫 Action denied: '{action}' not permitted for {role}")
            except Exception:
                pass
        return False
    return True


# ═══════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════
def create_session(role, user_id):
    """Return session dict."""
    cfg = SESSION_CONFIG.get(role, {"timeout_min": 15})
    now = datetime.now()
    return {
        "role": role,
        "user_id": user_id,
        "started_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=cfg["timeout_min"])).isoformat(),
    }


def is_session_valid(session):
    if not session:
        return False
    try:
        exp = datetime.fromisoformat(session["expires_at"])
        return datetime.now() < exp
    except Exception:
        return False


def touch_session(session):
    """Extend session on activity."""
    if not session:
        return session
    cfg = SESSION_CONFIG.get(session.get("role", "customer"), {"timeout_min": 15})
    now = datetime.now()
    session["expires_at"] = (now + timedelta(minutes=cfg["timeout_min"])).isoformat()
    return session


# ═══════════════════════════════════════════════════════════
# SECURITY MODES
# ═══════════════════════════════════════════════════════════
def get_security_mode(company):
    """Return 'normal' | 'strict' | 'lockdown'."""
    return company.get("security_mode", "normal")


def is_login_allowed(role, company):
    """Check security mode before allowing login."""
    mode = get_security_mode(company)
    if mode == "lockdown":
        return role == "owner"
    return True


# ═══════════════════════════════════════════════════════════
# STAFF MANAGEMENT (owner only)
# ═══════════════════════════════════════════════════════════
def add_staff(name, pin, role="staff"):
    """Add new staff. Returns (ok, msg, staff_id)."""
    if not pin or len(str(pin)) < 6:
        return False, "PIN must be at least 6 digits", None
    users = load_users()
    existing = [s["id"] for s in users.get("staff", [])]
    # Generate next ID
    n = 1
    while f"STAFF{n:03d}" in existing:
        n += 1
    new_id = f"STAFF{n:03d}"
    users.setdefault("staff", []).append({
        "id": new_id,
        "name": name,
        "role": "staff",
        "pin_hash": hash_secret(pin),
        "active": True,
        "created_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
    })
    save_users(users)
    return True, f"✅ Staff {new_id} added", new_id


def toggle_staff(staff_id, active):
    users = load_users()
    for s in users.get("staff", []):
        if s["id"] == staff_id:
            s["active"] = active
            save_users(users)
            return True
    return False


def reset_staff_pin(staff_id, new_pin):
    users = load_users()
    for s in users.get("staff", []):
        if s["id"] == staff_id:
            s["pin_hash"] = hash_secret(new_pin)
            save_users(users)
            return True
    return False


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("  RBAC TEST — 3 Roles")
    print("═" * 70)

    # 1. Init users
    users = load_users()
    print(f"✅ Users file: {USERS_FILE}")
    print(f"   Owner: {users['owner']['name']}")
    print(f"   Staff: {len(users.get('staff', []))}")

    # 2. Test owner login
    ok, u, err = verify_login("owner", "OWNER", "owner2026")
    print(f"\n👔 Owner login: {'✅' if ok else '❌'} {err or u['name']}")

    # 3. Test wrong password
    ok, u, err = verify_login("owner", "OWNER", "wrong")
    print(f"👔 Wrong password: {'❌ (correctly rejected)' if not ok else '⚠️ BUG'} — {err}")

    # 4. Test customer login
    retailers = json.loads(Path("retailers.json").read_text()) if Path("retailers.json").exists() else []
    if retailers:
        r = retailers[0]
        # Try with correct PIN from retailer (may not exist — test with generated)
        for test_pin in ["3210", "1234"]:
            ok, u, err = verify_login("customer", r["id"], test_pin, retailers)
            if ok:
                print(f"🏪 Customer login: ✅ {u['shop']}")
                break
        else:
            print(f"🏪 Customer login: PIN not matched (needs reset)")

    # 5. Test permissions
    print("\n─── Permissions Matrix ───")
    for role in ["owner", "staff", "customer"]:
        views = PERMISSIONS[role]["view"]
        actions = PERMISSIONS[role]["actions"]
        print(f"{role.upper():10s} → {len(views)} views, {len(actions)} actions")

    # 6. Test guard
    print("\n─── Guard Tests ───")
    print(f"  Owner can view 'accounting':   {can_view('owner', 'accounting')}  (should be True)")
    print(f"  Staff can view 'accounting':   {can_view('staff', 'accounting')}  (should be False)")
    print(f"  Customer can view 'accounting':{can_view('customer', 'accounting')}  (should be False)")
    print(f"  Customer can do 'place_order': {can_do('customer', 'place_order')}  (should be True)")
    print(f"  Staff can do 'approve_order':  {can_do('staff', 'approve_order')}  (should be False)")
    print(f"  Owner can do 'wipe_audit':     {can_do('owner', 'wipe_audit')}  (should be True)")
