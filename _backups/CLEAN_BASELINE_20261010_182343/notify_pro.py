"""
notify_pro.py — Multi-channel notifications with SMS limit + Telegram fallback.
Supports: Telegram, SMS (Fast2SMS / MSG91 / Twilio / Mock), Console.
Daily SMS limit with auto-fallback to Telegram.
Welcome + Thank You message templates.
"""
import os

# ── Auto-load .env (so TELEGRAM_BOT_TOKEN works when run as script) ──
def _load_env_auto():
    try:
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass
_load_env_auto()


# ── Auto-load .env so TELEGRAM_BOT_TOKEN is available ──
def _load_env():
    try:
        from pathlib import Path as _P
        env_path = _P(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass
_load_env()

import json
from datetime import datetime
from pathlib import Path

COUNTER_FILE = "sms_counter.json"
DAILY_SMS_LIMIT = 100
COMPANY_NAME = os.getenv("COMPANY_NAME", "Meena Agencies Wholesale")


# ────────────────────────────────────────────────
# SMS DAILY COUNTER
# ────────────────────────────────────────────────
def _today_key():
    return datetime.now().strftime("%Y-%m-%d")


def _load_counter():
    if not Path(COUNTER_FILE).exists():
        return {}
    try:
        return json.loads(Path(COUNTER_FILE).read_text())
    except Exception:
        return {}


def _save_counter(data):
    Path(COUNTER_FILE).write_text(json.dumps(data, indent=2))


def get_sms_used_today():
    """Return number of SMS sent today."""
    return _load_counter().get(_today_key(), 0)


def can_send_sms():
    """Check if under daily limit."""
    return get_sms_used_today() < DAILY_SMS_LIMIT


def increment_sms_counter():
    """Increment today's SMS counter."""
    data = _load_counter()
    key = _today_key()
    data[key] = data.get(key, 0) + 1
    _save_counter(data)


def sms_remaining():
    return max(0, DAILY_SMS_LIMIT - get_sms_used_today())


# ────────────────────────────────────────────────
# SMS PROVIDERS
# ────────────────────────────────────────────────
def _send_fast2sms(phone, message):
    """Fast2SMS (India) — https://fast2sms.com"""
    import requests
    key = os.getenv("FAST2SMS_API_KEY", "").strip()
    if not key:
        return False, "FAST2SMS_API_KEY missing"
    try:
        r = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": key},
            data={
                "route": "q",
                "message": message[:160],
                "language": "english",
                "flash": 0,
                "numbers": phone,
            },
            timeout=15,
        )
        return r.status_code == 200, r.text[:150]
    except Exception as e:
        return False, str(e)


def _send_msg91(phone, message):
    """MSG91 (India)"""
    import requests
    key = os.getenv("MSG91_AUTH_KEY", "").strip()
    sender = os.getenv("MSG91_SENDER_ID", "").strip()
    if not key:
        return False, "MSG91_AUTH_KEY missing"
    try:
        r = requests.post(
            "https://api.msg91.com/api/v2/sendsms",
            headers={"authkey": key, "Content-Type": "application/json"},
            json={
                "sender": sender,
                "route": "4",
                "country": "91",
                "sms": [{"message": message[:160], "to": [phone]}],
            },
            timeout=15,
        )
        return r.status_code == 200, r.text[:150]
    except Exception as e:
        return False, str(e)


def _send_twilio(phone, message):
    """Twilio (international)"""
    import requests
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_num = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    if not (sid and token and from_num):
        return False, "Twilio credentials incomplete"
    try:
        r = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            auth=(sid, token),
            data={"From": from_num, "To": f"+91{phone}" if not phone.startswith("+") else phone, "Body": message[:160]},
            timeout=15,
        )
        return r.status_code in (200, 201), r.text[:150]
    except Exception as e:
        return False, str(e)


def _send_mock(phone, message):
    """Mock — logs to file for testing"""
    log_file = Path("sms_outbox.log")
    with open(log_file, "a") as f:
        f.write(f"\n[{datetime.now().isoformat()}] TO: {phone}\n{message}\n{'-'*60}\n")
    return True, "Mock SMS logged to sms_outbox.log"


def send_sms(phone, message):
    """
    Send SMS via configured provider.
    Returns (ok, detail).
    """
    provider = os.getenv("SMS_PROVIDER", "mock").lower().strip()
    if not phone or len(phone) < 10:
        return False, "Invalid phone number"

    # Strip non-digits
    phone = "".join(c for c in phone if c.isdigit())[-10:]

    if provider == "fast2sms":
        return _send_fast2sms(phone, message)
    elif provider == "msg91":
        return _send_msg91(phone, message)
    elif provider == "twilio":
        return _send_twilio(phone, message)
    elif provider == "mock":
        return _send_mock(phone, message)
    else:
        return False, f"Unknown SMS_PROVIDER: {provider}"


# ────────────────────────────────────────────────
# TELEGRAM
# ────────────────────────────────────────────────
def send_telegram(chat_id, message):
    """Send via Telegram bot. Returns (ok, detail)."""
    import requests
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return False, "TELEGRAM_BOT_TOKEN missing"
    if not chat_id:
        return False, "No chat_id"
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=15,
        )
        if r.status_code == 200:
            return True, "Telegram sent"
        return False, r.text[:150]
    except Exception as e:
        return False, str(e)


# ────────────────────────────────────────────────
# SMART ROUTER — Telegram first, SMS fallback
# ────────────────────────────────────────────────
def notify_retailer(retailer, message, prefer_sms=False):
    """
    Send to retailer via best available channel.
    - If retailer has Telegram AND (SMS limit reached OR not prefer_sms): use Telegram
    - If prefer_sms and SMS available: use SMS
    - Else: fallback to Telegram
    Returns dict with what actually happened.
    """
    result = {
        "telegram_sent": False,
        "sms_sent": False,
        "channel_used": None,
        "sms_remaining": sms_remaining(),
        "reason": "",
    }

    has_telegram = bool(retailer.get("telegram_chat_id", "").strip())
    has_phone = bool(retailer.get("phone", "").strip())

    # Decide channel
    use_sms = (
        prefer_sms
        and has_phone
        and can_send_sms()
    )

    if use_sms:
        ok, detail = send_sms(retailer["phone"], message)
        if ok:
            increment_sms_counter()
            result["sms_sent"] = True
            result["channel_used"] = "sms"
            result["reason"] = f"SMS sent ({sms_remaining()} remaining today)"
            return result
        else:
            result["reason"] = f"SMS failed: {detail}. Falling back to Telegram."

    # Fallback or primary: Telegram
    if has_telegram:
        ok, detail = send_telegram(retailer["telegram_chat_id"], message)
        if ok:
            result["telegram_sent"] = True
            result["channel_used"] = "telegram"
            if not result["reason"]:
                result["reason"] = "Telegram sent"
            return result
        else:
            result["reason"] = f"Telegram failed: {detail}"

    # Last resort: console
    print(f"\n{'='*60}\n📱 NOTIFICATION for {retailer.get('id','?')}:\n{'='*60}\n{message}\n{'='*60}\n")
    result["channel_used"] = "console"
    result["reason"] = "Only console available (no valid Telegram/phone)"
    return result


# ────────────────────────────────────────────────
# MESSAGE TEMPLATES
# ────────────────────────────────────────────────
def format_welcome(retailer):
    """Welcome message on first order."""
    return (
        f"🎉 <b>Welcome to {COMPANY_NAME}!</b>\n\n"
        f"Dear <b>{retailer.get('owner', 'Partner')}</b>,\n\n"
        f"Thank you for placing your first order with us at <b>{retailer.get('shop', '')}</b>.\n\n"
        f"We're honored to serve your pharmacy. Every order will be handled with care, and we'll keep you updated at every step.\n\n"
        f"<i>— Team {COMPANY_NAME}</i>"
    )


def format_thank_you(retailer, order):
    """Thank you note after each order."""
    items_txt = "\n".join([f"  • {it['medicine']} × {it['qty']}" for it in order.get("items", [])[:5]])
    more = f"\n  • ...and {len(order['items']) - 5} more" if len(order.get("items", [])) > 5 else ""
    return (
        f"✅ <b>Order Confirmed — {order['order_id']}</b>\n\n"
        f"Dear <b>{retailer.get('owner', '')}</b> ({retailer.get('shop', '')}),\n\n"
        f"Thank you for your order! 🙏\n\n"
        f"<b>Items:</b>\n{items_txt}{more}\n\n"
        f"<b>Total:</b> ₹{order['total']:,.2f}\n"
        f"<b>Delivery to:</b> {order.get('location', '')}\n"
        f"<b>Placed at:</b> {order.get('placed_at', '')}\n\n"
        f"We'll notify you once it's approved and dispatched.\n\n"
        f"<i>— Team {COMPANY_NAME}</i>"
    )


def format_otp(order, otp):
    """OTP message (short — fits in one SMS)."""
    return (
        f"🔐 {COMPANY_NAME} OTP: {otp}\n"
        f"Order: {order['order_id']}\n"
        f"Amount: Rs {order['total']:.0f}\n"
        f"Valid 10 min. Do not share."
    )
