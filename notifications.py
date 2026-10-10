"""
notifications.py — In-app notification system for owner dashboard.
Reads/writes notifications.json. Provides add/read/mark-read helpers.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

NOTIF_FILE = "notifications.json"
MAX_KEEP = 500


def _load():
    p = Path(NOTIF_FILE)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(items):
    items = sorted(items, key=lambda x: x.get("ts", ""), reverse=True)[:MAX_KEEP]
    Path(NOTIF_FILE).write_text(json.dumps(items, indent=2, ensure_ascii=False))


def add(actor_id, actor_name, actor_role, type, message,
        severity="info", link=None):
    """Append a notification. Returns the new record."""
    items = _load()
    ntf = {
        "id": "NTF-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6],
        "ts": datetime.now().isoformat(),
        "type": type,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "actor_role": actor_role,
        "message": message,
        "severity": severity,
        "read": False,
        "link": link,
    }
    items.append(ntf)
    _save(items)
    return ntf


def get_recent(limit=20, unread_only=False, role_filter=None):
    """Return newest-first list. Optional filters."""
    items = _load()
    if unread_only:
        items = [x for x in items if not x.get("read")]
    if role_filter:
        items = [x for x in items if x.get("actor_role") == role_filter]
    items.sort(key=lambda x: x.get("ts", ""), reverse=True)
    return items[:limit]


def unread_count():
    return sum(1 for x in _load() if not x.get("read"))


def mark_all_read():
    items = _load()
    n = 0
    for x in items:
        if not x.get("read"):
            x["read"] = True
            n += 1
    _save(items)
    return n


def mark_read(ntf_id):
    items = _load()
    for x in items:
        if x.get("id") == ntf_id:
            x["read"] = True
            _save(items)
            return True
    return False
