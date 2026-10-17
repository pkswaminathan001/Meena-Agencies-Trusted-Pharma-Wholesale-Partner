"""
block4_audit.py — Owner Activity History + Calendar
Every owner action is logged here with a precise timestamp.
"""
import json, os
from datetime import datetime, timedelta
from pathlib import Path

PARENT = Path(__file__).parent.parent
AUDIT_FILE = PARENT / "owner_audit.jsonl"
ENV_FILE_CANDIDATES = [
    Path.home() / ".config" / "meena" / ".env",
    PARENT / ".env",
]


def log_action(action_type, target="", details=None, severity="info"):
    """Append one action to the immutable audit log."""
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "day": datetime.now().strftime("%A"),
        "actor": "OWNER",
        "action": action_type,
        "target": target,
        "details": details or {},
        "severity": severity,
    }
    try:
        with open(AUDIT_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        try:
            import stat as _s
            os.chmod(AUDIT_FILE, _s.IRUSR | _s.IWUSR)
        except Exception:
            pass
    except Exception:
        pass
    return entry


def read_all(limit=None):
    """Read the full audit log. Returns list of entries (newest first)."""
    if not AUDIT_FILE.exists():
        return []
    try:
        entries = []
        for line in AUDIT_FILE.read_text().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
        # Sort newest first
        entries.sort(key=lambda e: e.get("ts", ""), reverse=True)
        if limit:
            entries = entries[:limit]
        return entries
    except Exception:
        return []


def filter_entries(entries, action_type=None, target=None,
                   date_from=None, date_to=None, search=None):
    """Filter audit entries."""
    out = entries
    if action_type and action_type != "All":
        out = [e for e in out if e.get("action") == action_type]
    if target and target != "All":
        out = [e for e in out if e.get("target") == target]
    if date_from:
        out = [e for e in out if e.get("date", "") >= date_from]
    if date_to:
        out = [e for e in out if e.get("date", "") <= date_to]
    if search:
        s = search.lower()
        out = [e for e in out if s in str(e).lower()]
    return out


def activity_by_date(days_back=60):
    """Return a dict {date_str: {'total': N, 'approved': N, 'rejected': N}}"""
    entries = read_all()
    cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    out = {}
    for e in entries:
        d = e.get("date", "")
        if d < cutoff:
            continue
        if d not in out:
            out[d] = {"total": 0, "approved": 0, "rejected": 0, "logins": 0}
        out[d]["total"] += 1
        act = e.get("action", "")
        if act.endswith("approved") or act == "approve":
            out[d]["approved"] += 1
        elif act.endswith("rejected") or act == "reject":
            out[d]["rejected"] += 1
        elif "login" in act.lower():
            out[d]["logins"] += 1
    return out


def stats_summary():
    """Get summary counts."""
    entries = read_all()
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    return {
        "total_all_time": len(entries),
        "total_today": len([e for e in entries if e.get("date") == today]),
        "total_week": len([e for e in entries if e.get("date", "") >= week_ago]),
        "approved_total": len([e for e in entries if "approved" in e.get("action", "")]),
        "rejected_total": len([e for e in entries if "rejected" in e.get("action", "")]),
    }


def export_csv():
    """Return CSV text of the full audit log."""
    entries = read_all()
    if not entries:
        return "ts,action,target,severity,details\n"
    lines = ["ts,date,time,day,action,target,severity,details"]
    for e in entries:
        d = json.dumps(e.get("details", {})).replace(",", ";").replace('"', "'")
        lines.append(f'"{e.get("ts","")}","{e.get("date","")}","{e.get("time","")}",'
                     f'"{e.get("day","")}","{e.get("action","")}","{e.get("target","")}",'
                     f'"{e.get("severity","")}","{d}"')
    return "\n".join(lines)
