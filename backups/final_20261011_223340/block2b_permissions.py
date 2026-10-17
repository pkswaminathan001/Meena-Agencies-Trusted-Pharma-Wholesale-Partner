"""
block2b_permissions.py — Owner Veto + AI Campaigns
Every AI action requires owner approval. AI only advises.
"""
import json, os, urllib.request, urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

PARENT = Path(__file__).parent.parent
QUEUE_FILE = PARENT / "ai_permission_queue.json"
HISTORY_FILE = PARENT / "ai_action_history.json"
CAMPAIGN_LOG = PARENT / "campaigns.log"
ENV_FILE_CANDIDATES = [
    Path.home() / ".config" / "meena" / ".env",
    PARENT / ".env",
]


def _log(msg):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CAMPAIGN_LOG, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


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


def _tg_send(text, chat_id=None, retries=3):
    import time
    env = _load_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    cid = str(chat_id or env.get("OWNER_CHAT_ID", ""))
    if not token or not cid:
        return False, "Telegram not configured"
    for attempt in range(retries):
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": cid,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": "true",
            }).encode()
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=20) as resp:
                d = json.loads(resp.read())
                if d.get("ok"):
                    return True, "sent"
        except Exception as e:
            _log(f"Telegram attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                import time as _t
                _t.sleep(2 ** attempt)
    return False, "failed after retries"


def _load_json(path, default):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text())
        except Exception:
            return default
    return default


def _save_json(path, data):
    try:
        Path(path).write_text(json.dumps(data, indent=2))
        try:
            import stat as _s
            os.chmod(path, _s.S_IRUSR | _s.S_IWUSR)
        except Exception:
            pass
    except Exception as e:
        _log(f"Save error {path}: {e}")


# ═══════════════════════════════════════════════════════════════
#  PERMISSION QUEUE
# ═══════════════════════════════════════════════════════════════
def queue_action(action_type, summary, payload, severity="info"):
    """Queue an AI action for owner approval."""
    queue = _load_json(QUEUE_FILE, [])
    item = {
        "id": f"ACT-{datetime.now():%Y%m%d%H%M%S}-{len(queue)}",
        "type": action_type,
        "summary": summary,
        "payload": payload,
        "severity": severity,
        "status": "pending",
        "created_at": datetime.now().strftime("%d-%b-%Y %H:%M"),
    }
    queue.append(item)
    _save_json(QUEUE_FILE, queue)

    # Notify owner via Telegram
    emoji = {"info": "💡", "warn": "⚠️", "critical": "🚨"}.get(severity, "💡")
    text = (
        f"{emoji} <b>AI Action Request</b>\n\n"
        f"<b>Type:</b> {action_type}\n"
        f"<b>{summary}</b>\n\n"
        f"<i>Open app → Owner → Permission Queue to approve or reject.</i>"
    )
    try:
        _tg_send(text)
    except Exception:
        pass

    return item["id"]


def get_pending():
    """Return pending actions."""
    queue = _load_json(QUEUE_FILE, [])
    return [a for a in queue if a.get("status") == "pending"]


def get_all():
    """Return all actions (pending + resolved)."""
    return _load_json(QUEUE_FILE, [])


def approve_action(action_id, executor=None):
    """Mark approved + execute if executor provided."""
    queue = _load_json(QUEUE_FILE, [])
    for item in queue:
        if item["id"] == action_id:
            item["status"] = "approved"
            item["resolved_at"] = datetime.now().strftime("%d-%b-%Y %H:%M")
            item["resolved_by"] = "OWNER"
            break
    _save_json(QUEUE_FILE, queue)

    # Log to history
    history = _load_json(HISTORY_FILE, [])
    history.append({"action_id": action_id, "result": "approved",
                    "at": datetime.now().strftime("%d-%b-%Y %H:%M")})
    _save_json(HISTORY_FILE, history)

    _log(f"Approved: {action_id}")
    if executor:
        try:
            executor(item)
        except Exception as e:
            _log(f"Executor failed for {action_id}: {e}")

    return True


def reject_action(action_id, reason=""):
    """Mark rejected."""
    queue = _load_json(QUEUE_FILE, [])
    for item in queue:
        if item["id"] == action_id:
            item["status"] = "rejected"
            item["resolved_at"] = datetime.now().strftime("%d-%b-%Y %H:%M")
            item["rejection_reason"] = reason
            break
    _save_json(QUEUE_FILE, queue)

    history = _load_json(HISTORY_FILE, [])
    history.append({"action_id": action_id, "result": "rejected", "reason": reason,
                    "at": datetime.now().strftime("%d-%b-%Y %H:%M")})
    _save_json(HISTORY_FILE, history)

    _log(f"Rejected: {action_id} — {reason}")
    return True


def bulk_approve(action_ids):
    """Approve multiple actions at once."""
    for aid in action_ids:
        approve_action(aid)
    return len(action_ids)


# ═══════════════════════════════════════════════════════════════
#  CAMPAIGN DETECTORS (queue requests, never act)
# ═══════════════════════════════════════════════════════════════
def _already_queued_for_today(action_type, retailer_id):
    """Check if we already queued this action today."""
    today = datetime.now().strftime("%d-%b-%Y")
    queue = _load_json(QUEUE_FILE, [])
    for a in queue:
        if (a.get("type") == action_type
            and a.get("payload", {}).get("retailer_id") == retailer_id
            and a.get("created_at", "").startswith(today)):
            return True
    return False


def detect_we_miss_you(days=30):
    """Find dormant retailers. Queue action for owner approval."""
    retailers = _load_json(PARENT / "retailers.json", [])
    orders = _load_json(PARENT / "orders.json", [])
    queued = []

    for r in retailers:
        if not isinstance(r, dict):
            continue
        if not r.get("telegram_chat_id"):
            continue
        if str(r.get("status", "")).lower() in ("closed", "suspended"):
            continue
        rid = r.get("id", "")
        if _already_queued_for_today("we_miss_you", rid):
            continue

        # Find last order
        my_orders = [o for o in orders
                     if str(o.get("retailer_id", "")).upper() == rid.upper()]
        last_date = None
        for o in my_orders:
            try:
                d = datetime.strptime(str(o.get("placed_at", "")).split(" ")[0],
                                      "%d-%b-%Y")
                if last_date is None or d > last_date:
                    last_date = d
            except Exception:
                pass
        if last_date is None:
            continue
        days_since = (datetime.now() - last_date).days

        if days_since >= days:
            msg = (
                f"🙏 Vanakkam {r.get('owner','Sir/Madam')}!\n\n"
                f"We noticed it's been {days_since} days since your last order "
                f"from Meena Agencies.\n\n"
                f"As a valued partner, we'd love to have you back. Here's a "
                f"special offer just for you:\n\n"
                f"🎁 <b>5% OFF</b> on your next order\n"
                f"Valid for 7 days\n\n"
                f"Reply YES to place an order, or call us any time.\n\n"
                f"— Meena Agencies"
            )
            aid = queue_action(
                "we_miss_you",
                f"Send 'We Miss You' + 5% offer to {r.get('shop')} ({rid}) — "
                f"dormant {days_since} days",
                {"retailer_id": rid, "shop": r.get("shop"),
                 "chat_id": r.get("telegram_chat_id"), "message": msg,
                 "days_since": days_since},
                severity="warn"
            )
            queued.append(aid)
    return queued


def detect_payment_reminders():
    """Ladder: 30/45/60/90 days overdue. Queue approvals."""
    retailers = _load_json(PARENT / "retailers.json", [])
    queued = []

    for r in retailers:
        if not isinstance(r, dict):
            continue
        out = float(r.get("outstanding") or 0)
        if out <= 0:
            continue
        if not r.get("telegram_chat_id"):
            continue
        rid = r.get("id", "")

        # Estimate days overdue from when last order was
        # (This is a simplification — real system would track invoice dates)
        orders = _load_json(PARENT / "orders.json", [])
        my_orders = [o for o in orders
                     if str(o.get("retailer_id", "")).upper() == rid.upper()
                     and (o.get("status") or "").lower() in ("delivered", "approved")]
        if not my_orders:
            continue

        oldest = None
        for o in my_orders:
            try:
                d = datetime.strptime(str(o.get("placed_at", "")).split(" ")[0],
                                      "%d-%b-%Y")
                if oldest is None or d < oldest:
                    oldest = d
            except Exception:
                pass
        if oldest is None:
            continue
        days_old = (datetime.now() - oldest).days

        ladder_msg = None
        ladder_key = None
        if days_old >= 90:
            ladder_key = "90day"
            ladder_msg = (
                f"🚨 <b>URGENT</b>\n\n"
                f"Vanakkam {r.get('owner','Sir/Madam')},\n\n"
                f"Your outstanding balance of <b>Rs.{out:,.0f}</b> has been "
                f"due for over <b>90 days</b>.\n\n"
                f"<b>Action required:</b> Please settle or contact us today "
                f"to discuss a payment plan.\n\n"
                f"<i>Further credit will be suspended until this is resolved.</i>\n\n"
                f"— Meena Agencies"
            )
        elif days_old >= 60:
            ladder_key = "60day"
            ladder_msg = (
                f"⚠️ <b>Reminder</b>\n\n"
                f"Vanakkam {r.get('owner','Sir/Madam')},\n\n"
                f"Your outstanding of <b>Rs.{out:,.0f}</b> is now over "
                f"<b>60 days</b>.\n\n"
                f"Please clear this at the earliest to keep your account "
                f"in good standing.\n\n"
                f"— Meena Agencies"
            )
        elif days_old >= 45:
            ladder_key = "45day"
            ladder_msg = (
                f"📬 <b>Follow up</b>\n\n"
                f"Vanakkam {r.get('owner','Sir/Madam')},\n\n"
                f"A gentle follow up on your outstanding of "
                f"<b>Rs.{out:,.0f}</b> ({days_old} days).\n\n"
                f"Kindly arrange payment at your convenience.\n\n"
                f"— Meena Agencies"
            )
        elif days_old >= 30:
            ladder_key = "30day"
            ladder_msg = (
                f"🙏 Vanakkam {r.get('owner','Sir/Madam')},\n\n"
                f"A friendly reminder about your outstanding of "
                f"<b>Rs.{out:,.0f}</b>.\n\n"
                f"No rush, but please plan for it this week.\n\n"
                f"— Meena Agencies"
            )

        if ladder_msg and not _already_queued_for_today(f"payment_{ladder_key}", rid):
            aid = queue_action(
                f"payment_{ladder_key}",
                f"[{ladder_key.upper()}] Reminder to {r.get('shop')} ({rid}) — "
                f"Rs.{out:,.0f} outstanding",
                {"retailer_id": rid, "shop": r.get("shop"),
                 "chat_id": r.get("telegram_chat_id"),
                 "message": ladder_msg, "amount": out, "days_old": days_old},
                severity="critical" if days_old >= 60 else "warn"
            )
            queued.append(aid)
    return queued


def detect_birthdays_festivals():
    """Queue birthday + festival wishes."""
    # Placeholder — needs birthday data in retailer profile
    # For now, only queue festival wishes
    import datetime as _dt
    today = _dt.datetime.now()
    festivals = {
        (1, 14): "Pongal",
        (1, 15): "Pongal",
        (1, 16): "Pongal",
        (4, 14): "Tamil New Year",
        (8, 15): "Independence Day",
        (10, 2): "Gandhi Jayanti",
        (11, 1): "Diwali",
        (11, 14): "Children's Day",
        (12, 25): "Christmas",
    }
    festival = festivals.get((today.month, today.day))
    if not festival:
        return []

    retailers = _load_json(PARENT / "retailers.json", [])
    queued = []
    for r in retailers:
        if not isinstance(r, dict) or not r.get("telegram_chat_id"):
            continue
        rid = r.get("id", "")
        if _already_queued_for_today("festival_wish", rid):
            continue
        msg = (
            f"🎉 <b>Happy {festival}!</b>\n\n"
            f"Vanakkam {r.get('owner','Sir/Madam')},\n\n"
            f"Wishing you and your family a very happy {festival}.\n\n"
            f"As a small gift, please enjoy <b>3% OFF</b> on any order this week.\n\n"
            f"— Meena Agencies"
        )
        aid = queue_action(
            "festival_wish",
            f"Send {festival} wish + 3% offer to {r.get('shop')} ({rid})",
            {"retailer_id": rid, "shop": r.get("shop"),
             "chat_id": r.get("telegram_chat_id"),
             "message": msg, "festival": festival},
            severity="info"
        )
        queued.append(aid)
    return queued


def run_all_detectors():
    """Run every detector. Queue actions for owner. Never auto-execute."""
    results = {
        "we_miss_you": len(detect_we_miss_you()),
        "payment_reminders": len(detect_payment_reminders()),
        "festival_wishes": len(detect_birthdays_festivals()),
    }
    _log(f"Detectors ran: {results}")
    return results


# ═══════════════════════════════════════════════════════════════
#  EXECUTORS (called only after owner approval)
# ═══════════════════════════════════════════════════════════════
def execute_send_message(action):
    """Execute an approved send-message action."""
    payload = action.get("payload", {})
    chat_id = payload.get("chat_id")
    message = payload.get("message")
    if not chat_id or not message:
        _log(f"Missing chat_id/message in {action.get('id')}")
        return False
    ok, info = _tg_send(message, chat_id=chat_id)
    _log(f"Executed {action.get('id')} → {ok} ({info})")
    return ok
