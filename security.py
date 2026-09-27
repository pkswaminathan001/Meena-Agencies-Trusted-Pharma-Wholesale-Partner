"""Security utilities — bcrypt-style hashing, session timeout, rate limiting, audit log"""
import hashlib, os, json, time
from datetime import datetime, timedelta

# --- Salted hashing (stronger than plain SHA-256) ---
SALT_FILE = ".salt"
def _get_salt():
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f: return f.read()
    salt = os.urandom(32)
    with open(SALT_FILE, "wb") as f: f.write(salt)
    return salt

def hash_secret(secret):
    salt = _get_salt()
    return hashlib.pbkdf2_hmac('sha256', str(secret).encode(), salt, 100000).hex()

def verify_secret(secret, stored_hash):
    return hash_secret(secret) == stored_hash

# --- Audit log ---
AUDIT_FILE = "audit.log"
def log_action(user, action, details=""):
    ts = datetime.now().strftime("%d-%b-%Y %H:%M:%S").upper()
    with open(AUDIT_FILE, "a") as f:
        f.write(f"{ts} | {user} | {action} | {details}\n")

def read_audit(last_n=100):
    if not os.path.exists(AUDIT_FILE): return []
    with open(AUDIT_FILE) as f: lines = f.readlines()
    return lines[-last_n:]

# --- Rate limiting for OTP ---
RATE_FILE = "rate_limit.json"
def _load_rate():
    if os.path.exists(RATE_FILE):
        with open(RATE_FILE) as f: return json.load(f)
    return {}

def _save_rate(data):
    with open(RATE_FILE, "w") as f: json.dump(data, f)

def check_rate(retailer_id, max_per_hour=3):
    """Returns (allowed, remaining)."""
    now = time.time()
    data = _load_rate()
    entries = [t for t in data.get(retailer_id, []) if now - t < 3600]
    if len(entries) >= max_per_hour:
        return False, 0
    entries.append(now)
    data[retailer_id] = entries
    _save_rate(data)
    return True, max_per_hour - len(entries)

# --- Session timeout ---
SESSION_TIMEOUT = 15 * 60  # 15 minutes
def check_session_timeout():
    now = time.time()
    last = st_session_get("last_active")
    if last and now - last > SESSION_TIMEOUT:
        return False  # expired
    st_session_set("last_active", now)
    return True

def st_session_get(key):
    try:
        import streamlit as st
        return st.session_state.get(key)
    except: return None

def st_session_set(key, val):
    try:
        import streamlit as st
        st.session_state[key] = val
    except: pass

# --- Password strength ---
WEAK_PINS = {"0000","1111","2222","3333","4444","5555","6666","7777","8888","9999","1234","4321","0123","1212"}
def is_weak_pin(pin):
    return pin in WEAK_PINS


def record_rate(retailer_id):
    """Record an actual OTP send. Call only after successful delivery."""
    import time as _time
    now = _time.time()
    data = _load_rate()
    entries = [t for t in data.get(retailer_id, []) if now - t < 3600]
    entries.append(now)
    data[retailer_id] = entries
    _save_rate(data)

def record_rate(retailer_id):
    """Record an actual OTP send. Call only after successful delivery."""
    import time as _time
    now = _time.time()
    data = _load_rate()
    entries = [t for t in data.get(retailer_id, []) if now - t < 3600]
    entries.append(now)
    data[retailer_id] = entries
    _save_rate(data)
