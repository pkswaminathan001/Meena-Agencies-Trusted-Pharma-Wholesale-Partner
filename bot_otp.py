"""
bot_otp.py — Shared OTP engine for app + Telegram bot.
Uses a single JSON file so OTPs are valid across channels.
"""
import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path


OTP_FILE = Path("bot_otps.json")
OTP_EXPIRY_MINUTES = 10
MAX_ATTEMPTS = 3
LOCK_MINUTES = 30


def _load():
    if not OTP_FILE.exists():
        return {}
    try:
        return json.loads(OTP_FILE.read_text())
    except Exception:
        return {}


def _save(data):
    try:
        OTP_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def _cleanup(data):
    """Remove expired OTPs (older than 1 hour)."""
    cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
    return {k: v for k, v in data.items() if v.get("created_at", "") > cutoff}


def _gen():
    return "".join(random.choices(string.digits, k=6))


def generate(order_id: str, retailer_id: str, chat_id: int = None) -> str:
    """Generate OTP for an order. Returns the 6-digit code."""
    data = _load()
    data = _cleanup(data)

    otp = _gen()
    data[order_id] = {
        "otp": otp,
        "retailer_id": retailer_id,
        "chat_id": chat_id,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat(),
        "attempts": 0,
        "verified": False,
        "locked_until": None,
    }
    _save(data)
    return otp


def verify(order_id: str, entered: str) -> tuple:
    """
    Verify OTP. Returns (success: bool, message: str).
    Handles: expiry, wrong attempts, lockout.
    """
    data = _load()
    entry = data.get(order_id)

    if not entry:
        return False, "No active OTP for this order. Please start over."

    # Locked?
    if entry.get("locked_until"):
        try:
            locked = datetime.fromisoformat(entry["locked_until"])
            if datetime.now() < locked:
                remaining = int((locked - datetime.now()).total_seconds() / 60)
                return False, f"Too many attempts. Try again in {remaining} minutes."
        except Exception:
            pass

    # Expired?
    try:
        expires = datetime.fromisoformat(entry.get("expires_at", ""))
        if datetime.now() > expires:
            return False, "OTP expired. Please request a new one."
    except Exception:
        pass

    # Already verified?
    if entry.get("verified"):
        return False, "OTP already used. Place a new order."

    # Wrong OTP?
    if str(entered).strip() != entry.get("otp"):
        entry["attempts"] = entry.get("attempts", 0) + 1

        if entry["attempts"] >= MAX_ATTEMPTS:
            entry["locked_until"] = (datetime.now() + timedelta(minutes=LOCK_MINUTES)).isoformat()
            _save(data)
            return False, f"❌ 3 wrong attempts. Order locked for {LOCK_MINUTES} min."

        _save(data)
        remaining = MAX_ATTEMPTS - entry["attempts"]
        return False, f"❌ Wrong OTP. {remaining} attempt(s) left."

    # Success
    entry["verified"] = True
    entry["verified_at"] = datetime.now().isoformat()
    _save(data)
    return True, "✅ OTP verified."


def is_verified(order_id: str) -> bool:
    data = _load()
    return data.get(order_id, {}).get("verified", False)


def get_otp(order_id: str) -> str:
    """Get the OTP code (for internal use — sending to user)."""
    data = _load()
    return data.get(order_id, {}).get("otp", "")


def clear(order_id: str):
    data = _load()
    if order_id in data:
        del data[order_id]
        _save(data)


if __name__ == "__main__":
    print("=== bot_otp.py self-test ===")
    oid = "ORD-TEST-001"
    otp = generate(oid, "RET001", 123456)
    print(f"Generated OTP: {otp}")

    ok, msg = verify(oid, "000000")
    print(f"Wrong OTP: {ok} | {msg}")

    ok, msg = verify(oid, otp)
    print(f"Correct OTP: {ok} | {msg}")

    ok, msg = verify(oid, otp)
    print(f"Reuse OTP: {ok} | {msg}")

    clear(oid)
    print("Cleared.")

# ═══════════════════════════════════════════════════════════
# PENDING TELEGRAM ORDERS — for Streamlit popup
# ═══════════════════════════════════════════════════════════
PENDING_ORDERS_FILE = Path("pending_otp_orders.json")


def _load_pending():
    if not PENDING_ORDERS_FILE.exists():
        return {}
    try:
        return json.loads(PENDING_ORDERS_FILE.read_text())
    except Exception:
        return {}


def _save_pending(data):
    try:
        PENDING_ORDERS_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def register_pending_order(retailer_id: str, order: dict):
    """Called by bot.py when a Telegram order reaches OTP stage."""
    data = _load_pending()
    data[str(retailer_id)] = {
        "order": order,
        "created_at": datetime.now().isoformat(),
    }
    _save_pending(data)


def get_pending_for_retailer(retailer_id: str):
    """Called by app.py to check if a Telegram order is awaiting OTP."""
    data = _load_pending()
    entry = data.get(str(retailer_id))
    if not entry:
        return None
    # Auto-expire after 15 minutes
    try:
        created = datetime.fromisoformat(entry["created_at"])
        if (datetime.now() - created).total_seconds() > 900:
            data.pop(str(retailer_id), None)
            _save_pending(data)
            return None
    except Exception:
        pass
    return entry.get("order")


def clear_pending_order(retailer_id: str):
    """Called after OTP verified in app."""
    data = _load_pending()
    data.pop(str(retailer_id), None)
    _save_pending(data)

