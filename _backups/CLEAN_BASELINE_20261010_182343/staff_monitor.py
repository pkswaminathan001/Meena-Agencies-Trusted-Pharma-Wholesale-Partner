"""
staff_monitor.py — Full silent audit for staff.
Logs every action, data access, blocked attempt. Owner-only reports.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = Path("staff_activity_log.jsonl")
ALERTS_FILE = Path("staff_alerts.json")
RETAIN_DAYS = 30

# High-risk action names → trigger Telegram alert
HIGH_RISK = {
    "BLOCKED_ACCESS", "DATA_ACCESS_DENIED", "TRIED_DELETE",
    "TRIED_FINANCIAL", "MULTI_RETAILER_SCAN",
}


def _write(entry: dict):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def log_action(staff_id: str, staff_name: str, action: str,
               details: str = "", extra: dict = None):
    """Basic action log."""
    _write({
        "ts": datetime.now().isoformat(),
        "date": datetime.now().strftime("%d-%b-%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "staff_id": staff_id,
        "staff_name": staff_name,
        "action": action,
        "details": details,
        "extra": extra or {},
        "risk": "high" if action in HIGH_RISK else "normal",
    })
    if action in HIGH_RISK:
        _push_alert(staff_name, action, details)


def log_page(staff_id: str, staff_name: str, page: str):
    """Log which page staff opened."""
    _write({
        "ts": datetime.now().isoformat(),
        "date": datetime.now().strftime("%d-%b-%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "staff_id": staff_id, "staff_name": staff_name,
        "action": "PAGE_VIEW", "details": page, "extra": {},
        "risk": "normal",
    })


def log_data_access(staff_id: str, staff_name: str, what: str,
                    scope: str = "", allowed: bool = True):
    """Log when staff looks up data."""
    action = "DATA_ACCESS" if allowed else "DATA_ACCESS_DENIED"
    _write({
        "ts": datetime.now().isoformat(),
        "date": datetime.now().strftime("%d-%b-%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "staff_id": staff_id, "staff_name": staff_name,
        "action": action, "details": f"{what} · {scope}",
        "extra": {"scope": scope}, "risk": "high" if not allowed else "normal",
    })
    if not allowed:
        _push_alert(staff_name, action, f"{what} · {scope}")


def log_blocked(staff_id: str, staff_name: str, what: str):
    """Staff tried to access something they can't."""
    _write({
        "ts": datetime.now().isoformat(),
        "date": datetime.now().strftime("%d-%b-%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "staff_id": staff_id, "staff_name": staff_name,
        "action": "BLOCKED_ACCESS", "details": what, "extra": {},
        "risk": "high",
    })
    _push_alert(staff_name, "BLOCKED_ACCESS", what)


def log_session(staff_id: str, staff_name: str, event: str):
    """Login / Logout."""
    _write({
        "ts": datetime.now().isoformat(),
        "date": datetime.now().strftime("%d-%b-%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "staff_id": staff_id, "staff_name": staff_name,
        "action": f"SESSION_{event}", "details": "", "extra": {},
        "risk": "normal",
    })


def _push_alert(staff_name, action, details):
    """Send alert to owner via Telegram."""
    try:
        import notify_pro
        env = Path(".env").read_text() if Path(".env").exists() else ""
        chat = ""
        for line in env.splitlines():
            if line.startswith("OWNER_CHAT_ID="):
                chat = line.split("=", 1)[1].strip()
                break
        if chat:
            notify_pro.send_telegram(chat, (
                f"🚨 <b>Staff Alert</b>\n\n"
                f"Staff: <b>{staff_name}</b>\n"
                f"Action: <code>{action}</code>\n"
                f"Details: {details}\n\n"
                f"<i>Open app → Staff Mon. tab</i>"
            ))
    except Exception:
        pass


def _load_all():
    if not LOG_FILE.exists():
        return []
    out = []
    try:
        for line in LOG_FILE.read_text().splitlines():
            line = line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except Exception: continue
    except Exception: pass
    return out


def _filter(entries, date_str=None, staff_id=None, since_hours=None):
    out = entries
    if date_str:
        out = [e for e in out if e.get("date") == date_str]
    if staff_id:
        out = [e for e in out if e.get("staff_id") == staff_id]
    if since_hours:
        cutoff = datetime.now() - timedelta(hours=since_hours)
        out = [e for e in out if datetime.fromisoformat(e["ts"]) >= cutoff]
    return out


# ═══════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════

def today_summary() -> dict:
    today = datetime.now().strftime("%d-%b-%Y")
    entries = _filter(_load_all(), date_str=today)
    by_staff, by_action = {}, {}
    high_risk = []
    for e in entries:
        sid = e.get("staff_id", "?")
        if sid not in by_staff:
            by_staff[sid] = {
                "id": sid, "name": e.get("staff_name", "?"),
                "actions": 0, "first": e.get("time"), "last": e.get("time"),
                "breakdown": {}, "high_risk_count": 0,
            }
        by_staff[sid]["actions"] += 1
        by_staff[sid]["last"] = e.get("time")
        a = e.get("action", "?")
        by_staff[sid]["breakdown"][a] = by_staff[sid]["breakdown"].get(a, 0) + 1
        by_action[a] = by_action.get(a, 0) + 1
        if e.get("risk") == "high":
            by_staff[sid]["high_risk_count"] += 1
            high_risk.append(e)
    return {
        "date": today, "total_actions": len(entries),
        "active_staff": len(by_staff), "by_staff": by_staff,
        "by_action": by_action, "high_risk": high_risk,
        "entries": entries[-200:],
    }


def weekly_summary() -> list:
    out = []
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime("%d-%b-%Y")
        entries = _filter(_load_all(), date_str=d)
        out.append({
            "date": d, "actions": len(entries),
            "staff_count": len(set(e.get("staff_id") for e in entries)),
            "high_risk": len([e for e in entries if e.get("risk") == "high"]),
        })
    return out


def recent_actions(limit=100, staff_id=None):
    entries = _load_all()
    if staff_id:
        entries = [e for e in entries if e.get("staff_id") == staff_id]
    return list(reversed(entries[-limit:]))


def suspicious_activity() -> list:
    """Detect anomalies."""
    entries = _filter(_load_all(), since_hours=24)
    alerts = []

    # Rule 1: Many retailer lookups in short time
    lookups = [e for e in entries if e.get("action") == "RETAILER_LOOKUP"]
    if len(lookups) >= 10:
        alerts.append({
            "severity": "high",
            "title": "Mass retailer scan detected",
            "detail": f"{len(lookups)} retailer lookups in last 24h",
        })

    # Rule 2: Blocked access attempts
    blocked = [e for e in entries if e.get("action") == "BLOCKED_ACCESS"]
    if blocked:
        alerts.append({
            "severity": "high",
            "title": f"{len(blocked)} blocked access attempt(s)",
            "detail": "Staff tried to reach owner-only data",
        })

    # Rule 3: Unusual hours (before 8 AM or after 9 PM)
    weird_hours = []
    for e in entries:
        try:
            h = int(e.get("time", "12:00:00").split(":")[0])
            if h < 8 or h >= 21:
                weird_hours.append(e)
        except Exception:
            pass
    if weird_hours:
        alerts.append({
            "severity": "low",
            "title": f"{len(weird_hours)} action(s) outside work hours",
            "detail": "Before 8 AM or after 9 PM",
        })

    # Rule 4: Rapid orders (more than 5 in 1 minute)
    orders = [e for e in entries if "ORDER" in e.get("action", "")]
    for i in range(len(orders) - 5):
        try:
            t1 = datetime.fromisoformat(orders[i]["ts"])
            t2 = datetime.fromisoformat(orders[i+5]["ts"])
            if (t2 - t1).total_seconds() < 60:
                alerts.append({
                    "severity": "medium",
                    "title": "Unusually rapid orders",
                    "detail": "5+ orders in under 60 seconds",
                })
                break
        except Exception:
            pass

    return alerts


def send_owner_alert(message, severity="info"):
    _push_alert("System", severity.upper(), message)


def cleanup_old():
    """Delete entries older than RETAIN_DAYS."""
    if not LOG_FILE.exists(): return 0
    cutoff = datetime.now() - timedelta(days=RETAIN_DAYS)
    kept, removed = [], 0
    for line in LOG_FILE.read_text().splitlines():
        line = line.strip()
        if not line: continue
        try:
            e = json.loads(line)
            if datetime.fromisoformat(e["ts"]) >= cutoff:
                kept.append(line)
            else:
                removed += 1
        except Exception:
            kept.append(line)
    LOG_FILE.write_text("\n".join(kept) + "\n")
    return removed
