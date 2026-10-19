"""
block15_otp.py — OTP flow + order notifications via Telegram
"""
import json, os, random, urllib.request, urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

PARENT = Path(__file__).parent.parent
OTP_FILE = PARENT / "otp_store.json"
ENV_FILE_CANDIDATES = [
    Path.home() / ".config" / "meena" / ".env",
    PARENT / ".env",
]

OTP_TTL_MINUTES = 5
OTP_LENGTH = 6


def _load_env():
    env = {}
    for p in ENV_FILE_CANDIDATES:
        if p.exists():
            try:
                for line in p.read_text().split("\n"):
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
    return env


def _tg_send(text, chat_id=None):
    env = _load_env()
    # Prefer os.environ (Streamlit Secrets injects here) over .env file
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or env.get("TELEGRAM_BOT_TOKEN", "")
    cid = chat_id or os.environ.get("OWNER_CHAT_ID") or env.get("OWNER_CHAT_ID", "")
    if not token or not cid:
        return False, "Telegram not configured"
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": cid,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read())
            return (d.get("ok", False), "sent" if d.get("ok") else str(d))
    except Exception as e:
        return False, str(e)


def _load_otps():
    if OTP_FILE.exists():
        try:
            return json.loads(OTP_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_otps(d):
    try:
        OTP_FILE.write_text(json.dumps(d, indent=2))
        try:
            import stat as _s
            os.chmod(OTP_FILE, _s.S_IRUSR | _s.S_IWUSR)
        except Exception:
            pass
    except Exception:
        pass


def generate_otp(retailer_id, order_payload):
    """Create a fresh OTP bound to an order payload."""
    code = "".join(str(random.randint(0, 9)) for _ in range(OTP_LENGTH))
    otps = _load_otps()
    otps[str(retailer_id).upper()] = {
        "code": code,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=OTP_TTL_MINUTES)).isoformat(),
        "order_payload": order_payload,
        "attempts": 0,
    }
    _save_otps(otps)
    return code


def verify_otp(retailer_id, entered_code):
    """Check code. Returns (ok, message, order_payload).
    Looks in own otp_store.json first, falls back to shared_otps.json."""
    rid = str(retailer_id).upper()
    code = str(entered_code or "").strip()

    otps = _load_otps()
    entry = otps.get(rid)
    if entry:
        try:
            expires = datetime.fromisoformat(entry["expires_at"])
            if datetime.now() > expires:
                del otps[rid]; _save_otps(otps)
                return False, "OTP expired. Request a new one.", None
        except Exception:
            return False, "OTP invalid.", None
        if entry.get("attempts", 0) >= 5:
            del otps[rid]; _save_otps(otps)
            return False, "Too many attempts. Request a new code.", None
        if str(entry.get("code", "")) != code:
            entry["attempts"] = entry.get("attempts", 0) + 1
            otps[rid] = entry; _save_otps(otps)
            return False, "Invalid OTP.", None
        payload = entry.get("order_payload")
        del otps[rid]; _save_otps(otps)
        return True, "OTP verified.", payload

    shared = PARENT / "shared_otps.json"
    if shared.exists():
        try:
            import json as _j
            data = _j.loads(shared.read_text() or "{}")
        except Exception:
            data = {}
        mk = mv = None
        for k, v in data.items():
            if not isinstance(v, dict): continue
            if str(v.get("retailer_id", "")).upper() != rid: continue
            if v.get("status") != "pending": continue
            if str(v.get("code", "")) != code: continue
            exp = v.get("expires_at")
            if exp:
                try:
                    if datetime.now() > datetime.fromisoformat(exp): continue
                except Exception: pass
            mk, mv = k, v; break
        if mv is None:
            return False, "No pending OTP. Please request a new code.", None
        mv["status"] = "verified"
        mv["verified_at"] = datetime.now().isoformat()
        mv["verified_via"] = "web"
        data[mk] = mv
        try:
            import json as _j
            shared.write_text(_j.dumps(data, indent=2))
        except Exception: pass
        payload = mv.get("cart") or mv.get("order_payload") or mv
        return True, "OTP verified.", payload

    return False, "No pending OTP. Please request a new code.", None


def send_otp_telegram(retailer_id, retailer_shop, otp_code, order_total, item_count):
    """Send OTP + order summary to the OWNER via Telegram."""
    text = (
        f"🔐 <b>New Order — OTP Confirmation</b>\n\n"
        f"<b>Retailer:</b> {retailer_shop} ({retailer_id})\n"
        f"<b>Total:</b> Rs.{order_total:,.2f}\n"
        f"<b>Items:</b> {item_count}\n\n"
        f"<b>OTP:</b> <code>{otp_code}</code>\n\n"
        f"<i>Valid for {OTP_TTL_MINUTES} minutes.</i>"
    )
    return _tg_send(text)


def notify_order_placed(order):
    """Notify owner that a new order has been placed (post-OTP)."""
    items = order.get("items", []) or []
    lines = [f"🧾 <b>Order Placed</b>",
             f"<b>ID:</b> {order.get('order_id','?')}",
             f"<b>Retailer:</b> {order.get('shop','?')} ({order.get('retailer_id','?')})",
             f"<b>Total:</b> Rs.{float(order.get('total',0)):,.2f}",
             f"<b>Status:</b> {order.get('status','pending')}",
             ""]
    for i, it in enumerate(items, 1):
        nm = it.get("medicine") or it.get("name") or "?"
        q = it.get("qty") or it.get("quantity") or 0
        p = float(it.get("price") or 0)
        lines.append(f"{i}. {nm} x {q} = Rs.{p*q:,.2f}")
    reason = order.get("approval_reason", "")
    if reason:
        lines.append(f"\n<i>{reason}</i>")
    return _tg_send("\n".join(lines))
