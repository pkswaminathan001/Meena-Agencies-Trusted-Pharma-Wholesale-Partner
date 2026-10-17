"""
shared_otp_store.py — OTP store shared between Streamlit app and Telegram bot.
Both read/write this file. Thread-safe with file locking.
"""
import json, os, secrets, time, threading
from datetime import datetime, timedelta
from pathlib import Path

PARENT = Path(__file__).parent.parent
OTP_FILE = PARENT / "shared_otps.json"
_LOCK = threading.Lock()
OTP_TTL_MIN = 5
MAX_ATTEMPTS = 5


def _load():
    if OTP_FILE.exists():
        try:
            return json.loads(OTP_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(data):
    try:
        OTP_FILE.write_text(json.dumps(data, indent=2))
        try:
            os.chmod(OTP_FILE, 0o600)
        except Exception:
            pass
    except Exception:
        pass


def create_otp(retailer_id, shop, cart, total, ttl_min=OTP_TTL_MIN):
    """Generate a new OTP bound to cart data. Returns (order_id, code)."""
    with _LOCK:
        data = _load()
        now = datetime.now()

        # Cleanup expired
        for k in list(data.keys()):
            try:
                if datetime.fromisoformat(data[k]["expires_at"]) < now:
                    del data[k]
            except Exception:
                pass

        code = "".join(str(secrets.randbelow(10)) for _ in range(6))
        oid = "OTP-" + secrets.token_hex(6)
        data[oid] = {
            "code": code,
            "retailer_id": str(retailer_id).upper(),
            "shop": shop,
            "cart": cart,
            "total": float(total),
            "status": "pending",
            "attempts": 0,
            "created_at": now.isoformat(timespec="seconds"),
            "expires_at": (now + timedelta(minutes=ttl_min)).isoformat(timespec="seconds"),
            "verified_at": None,
            "verified_via": None,
        }
        _save(data)
        return oid, code


def verify_otp(oid, entered, via="streamlit"):
    """Verify OTP by order_id + code. Returns (ok, msg, entry)."""
    with _LOCK:
        data = _load()
        now = datetime.now()
        entry = data.get(oid)
        if not entry:
            return False, "OTP not found", None
        if entry["status"] != "pending":
            return False, f"OTP already {entry['status']}", None
        try:
            if datetime.fromisoformat(entry["expires_at"]) < now:
                entry["status"] = "expired"
                _save(data)
                return False, "OTP expired", None
        except Exception:
            pass
        if entry["attempts"] >= MAX_ATTEMPTS:
            entry["status"] = "locked"
            _save(data)
            return False, "Too many attempts. Request new OTP.", None
        if str(entered).strip() != entry["code"]:
            entry["attempts"] += 1
            _save(data)
            left = MAX_ATTEMPTS - entry["attempts"]
            return False, f"Wrong OTP. {left} attempts left.", None
        entry["status"] = "verified"
        entry["verified_at"] = now.isoformat(timespec="seconds")
        entry["verified_via"] = via
        _save(data)
        return True, "OK", entry


def find_pending_by_code(code):
    """For Telegram: find pending OTPs matching a code."""
    with _LOCK:
        data = _load()
        now = datetime.now()
        matches = []
        for oid, v in data.items():
            if v["status"] != "pending":
                continue
            if str(v["code"]) != str(code).strip():
                continue
            try:
                if datetime.fromisoformat(v["expires_at"]) < now:
                    continue
            except Exception:
                continue
            matches.append((oid, v))
        return matches


def find_pending_by_retailer(retailer_id):
    """Find pending OTP for a specific retailer."""
    with _LOCK:
        data = _load()
        rid = str(retailer_id).upper()
        for oid, v in data.items():
            if v["status"] == "pending" and v["retailer_id"] == rid:
                try:
                    if datetime.fromisoformat(v["expires_at"]) > datetime.now():
                        return oid, v
                except Exception:
                    pass
        return None, None


def get_verified_since(iso_ts):
    """Return OTPs verified at or after a given timestamp."""
    with _LOCK:
        data = _load()
        try:
            cutoff = datetime.fromisoformat(iso_ts)
        except Exception:
            return []
        out = []
        for oid, v in data.items():
            if v.get("status") == "verified" and v.get("verified_at"):
                try:
                    if datetime.fromisoformat(v["verified_at"]) >= cutoff:
                        out.append((oid, v))
                except Exception:
                    pass
        return out


def get_otp(oid):
    with _LOCK:
        return _load().get(oid)


def cleanup_old(max_hours=24):
    with _LOCK:
        data = _load()
        now = datetime.now()
        for k in list(data.keys()):
            try:
                created = datetime.fromisoformat(data[k]["created_at"])
                if (now - created).total_seconds() > max_hours * 3600:
                    del data[k]
            except Exception:
                pass
        _save(data)
