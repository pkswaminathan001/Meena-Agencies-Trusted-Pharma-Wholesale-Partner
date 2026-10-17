"""
block1_helpers.py — Payments, Telegram, AI Approvals
Pure addition. No existing code touched.
"""
import json, os, urllib.request, urllib.parse, hashlib
from datetime import datetime, timedelta
from pathlib import Path

PARENT = Path(__file__).parent.parent
PAYMENTS_FILE = PARENT / "payments.json"
ENV_FILE_CANDIDATES = [
    Path.home() / ".config" / "meena" / ".env",
    PARENT / ".env",
]


# ═══════════════════════════════════════════════════════════════
#  ENV LOADER
# ═══════════════════════════════════════════════════════════════
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


def _send_telegram(text, chat_id=None):
    """Send a message via Telegram bot."""
    env = _load_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    cid = chat_id or env.get("OWNER_CHAT_ID", "")
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


# ═══════════════════════════════════════════════════════════════
#  PAYMENTS
# ═══════════════════════════════════════════════════════════════
def load_payments():
    for p in (PAYMENTS_FILE, Path("payments.json")):
        if p.exists():
            try:
                d = json.loads(p.read_text())
                return d if isinstance(d, list) else list(d.values())
            except Exception:
                pass
    return []


def save_payments(data):
    for p in (PAYMENTS_FILE, Path("payments.json")):
        try:
            p.write_text(json.dumps(data, indent=2))
            try:
                import stat as _s
                os.chmod(p, _s.S_IRUSR | _s.S_IWUSR)
            except Exception:
                pass
            return True
        except Exception:
            pass
    return False


def record_payment(retailer_id, amount, method, reference="", notes="",
                   date=None, status="cleared", recorded_by="OWNER"):
    """Add a payment record. Returns the created record."""
    payments = load_payments()
    seq = len([p for p in payments if p.get("date", "").startswith(
        (date or datetime.now().strftime("%Y-%m-%d"))
    )]) + 1
    pid = f"PAY-{datetime.now():%Y%m%d}-{seq:04d}"
    rec = {
        "payment_id": pid,
        "retailer_id": str(retailer_id).upper(),
        "amount": float(amount),
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "method": method,
        "reference": reference,
        "notes": notes,
        "status": status,  # cleared | pending_clearance | bounced
        "recorded_by": recorded_by,
        "recorded_at": datetime.now().strftime("%d-%b-%Y %H:%M"),
    }
    payments.append(rec)
    save_payments(payments)

    # If cleared, reduce retailer's outstanding
    if status == "cleared":
        _adjust_outstanding(retailer_id, -float(amount))
    return rec


def _adjust_outstanding(retailer_id, delta):
    """Add delta (negative to reduce) to a retailer's outstanding."""
    for p in (PARENT / "retailers.json", Path("retailers.json")):
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
            arr = data if isinstance(data, list) else list(data.values())
            for r in arr:
                if str(r.get("id", "")).upper() == str(retailer_id).upper():
                    new_out = max(0, float(r.get("outstanding") or 0) + delta)
                    r["outstanding"] = round(new_out, 2)
                    # Auto-release credit hold if outstanding is now 0
                    if new_out == 0 and "hold" in str(r.get("status", "")).lower():
                        r["status"] = "Active"
                        r["hold_released_at"] = datetime.now().strftime("%d-%b-%Y %H:%M")
                    break
            p.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            pass
    return False


def clear_pending_payment(payment_id):
    """Mark a pending payment as cleared and reduce outstanding."""
    payments = load_payments()
    for p in payments:
        if p.get("payment_id") == payment_id:
            if p.get("status") == "pending_clearance":
                p["status"] = "cleared"
                p["cleared_at"] = datetime.now().strftime("%d-%b-%Y %H:%M")
                _adjust_outstanding(p["retailer_id"], -float(p["amount"]))
                save_payments(payments)
                return True
    return False


def mark_bounced(payment_id):
    """Mark cheque as bounced."""
    payments = load_payments()
    for p in payments:
        if p.get("payment_id") == payment_id:
            p["status"] = "bounced"
            p["bounced_at"] = datetime.now().strftime("%d-%b-%Y %H:%M")
            save_payments(payments)
            return True
    return False


def retailer_payments(retailer_id):
    """All payments for a retailer."""
    return [p for p in load_payments()
            if str(p.get("retailer_id", "")).upper() == str(retailer_id).upper()]


def total_cleared(retailer_id=None):
    """Sum of cleared payments."""
    payments = load_payments()
    if retailer_id:
        payments = retailer_payments(retailer_id)
    return sum(float(p["amount"]) for p in payments if p.get("status") == "cleared")


# ═══════════════════════════════════════════════════════════════
#  TELEGRAM MESSAGE BUILDER
# ═══════════════════════════════════════════════════════════════
def build_telegram_message(recipient_name, body, sender="Meena Agencies"):
    """Format a message for Telegram (HTML-safe)."""
    body = body.replace("<", "&lt;").replace(">", "&gt;")
    return f"<b>🙏 Vanakkam {recipient_name}</b>\n\n{body}\n\n— <i>{sender}</i>"
