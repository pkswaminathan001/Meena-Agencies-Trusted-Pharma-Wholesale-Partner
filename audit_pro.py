"""
audit_pro.py — Enterprise-grade audit & workforce analytics.
Append-only, hash-chained, tamper-evident. Owner-only deletion.
"""
import os
import json
import hashlib
from datetime import datetime, timedelta

AUDIT_FILE = "audit_pro.jsonl"
_MEM_CACHE = {"events": [], "loaded_at": 0, "count": 0}
INDEX_FILE = "activity_index.json"


# ────────────────────────────────────────────────────────
# HASH-CHAIN TAMPER PROTECTION
# ────────────────────────────────────────────────────────

def _last_hash():
    if not os.path.exists(AUDIT_FILE):
        return "GENESIS"
    with open(AUDIT_FILE, "rb") as f:
        # read only the tail to avoid loading huge file
        f.seek(max(0, os.path.getsize(AUDIT_FILE) - 4096))
        tail = f.read().decode("utf-8", errors="ignore").strip().splitlines()
        if not tail:
            return "GENESIS"
        try:
            last = json.loads(tail[-1])
            return last.get("hash", "GENESIS")
        except Exception:
            return "GENESIS"


def _compute_hash(entry: dict, prev_hash: str) -> str:
    payload = json.dumps(entry, sort_keys=True) + prev_hash
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


_CHAIN_CACHE = {"result": None, "checked_at": 0}

def verify_chain() -> dict:
    """Return {'ok': bool, 'total': int, 'broken_at': int|None}. Cached 30s."""
    import time as _t
    global _CHAIN_CACHE
    now = _t.time()
    if _CHAIN_CACHE["result"] and now - _CHAIN_CACHE["checked_at"] < 30:
        return _CHAIN_CACHE["result"]
    if not os.path.exists(AUDIT_FILE):
        _CHAIN_CACHE["result"] = {"ok": True, "total": 0, "broken_at": None}
        _CHAIN_CACHE["checked_at"] = now
        return _CHAIN_CACHE["result"]
    prev = "GENESIS"
    total = 0
    with open(AUDIT_FILE, "r") as f:
        for i, line in enumerate(f, 1):
            try:
                e = json.loads(line)
            except Exception:
                continue
            e_stored = e.pop("hash", None)
            expected = _compute_hash(e, prev)
            if e_stored != expected:
                return {"ok": False, "total": total, "broken_at": i}
            prev = e_stored
            total += 1
    return {"ok": True, "total": total, "broken_at": None}


# ────────────────────────────────────────────────────────
# EVENT LOGGING
# ────────────────────────────────────────────────────────

def log_event(user: str, action: str, page: str = "", details: str = ""):
    """
    Append a tamper-evident event to the audit log.
    Format: HH:MM:SS | DD-MMM-YYYY | USER | ACTION | PAGE | DETAILS
    """
    now = datetime.now()
    entry = {
        "ts_iso": now.isoformat(timespec="seconds"),
        "ts_hms": now.strftime("%H:%M:%S"),
        "ts_date": now.strftime("%d-%b-%Y").upper(),
        "epoch": now.timestamp(),
        "user": user,
        "action": action,
        "page": page,
        "details": details,
    }
    prev = _last_hash()
    entry["hash"] = _compute_hash(entry, prev)

    # Append-only (never overwritten except by owner delete)
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    # Update fast-lookup index
    _update_index(entry)
    return entry


def _update_index(entry: dict):
    """Maintain a small index keyed by user → date for fast queries."""
    idx = {}
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE) as f:
                idx = json.load(f)
        except Exception:
            idx = {}
    user = entry["user"]
    date = entry["ts_date"]
    idx.setdefault(user, {}).setdefault(date, {"events": 0, "clicks": 0, "pages": {}})
    idx[user][date]["events"] += 1
    if entry["action"] == "CLICK":
        idx[user][date]["clicks"] += 1
    if entry["page"]:
        idx[user][date]["pages"][entry["page"]] = idx[user][date]["pages"].get(entry["page"], 0) + 1
    with open(INDEX_FILE, "w") as f:
        json.dump(idx, f, indent=2)


# ────────────────────────────────────────────────────────
# READERS
# ────────────────────────────────────────────────────────

def read_events(limit: int = 500, user: str = None, date: str = None) -> list:
    """Return most recent events with in-memory caching (10s TTL)."""
    import time as _t
    global _MEM_CACHE
    now = _t.time()

    if now - _MEM_CACHE["loaded_at"] > 10:
        events = []
        if os.path.exists(AUDIT_FILE):
            with open(AUDIT_FILE, "r") as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        continue
        _MEM_CACHE["events"] = events
        _MEM_CACHE["loaded_at"] = now
        _MEM_CACHE["count"] = len(events)

    events = _MEM_CACHE["events"]
    if user:
        events = [e for e in events if e.get("user") == user]
    if date:
        events = [e for e in events if e.get("ts_date") == date]
    return events[-limit:][::-1]


def user_summary(user: str, date: str = None) -> dict:
    """Aggregate stats for one user on one day (or all-time if date is None)."""
    events = read_events(limit=100000, user=user, date=date)
    if not events:
        return {"user": user, "events": 0, "clicks": 0, "pages": {}, "first": None, "last": None}

    events_sorted = sorted(events, key=lambda x: x["ts_iso"])
    first = events_sorted[0]["ts_hms"]
    last = events_sorted[-1]["ts_hms"]

    pages = {}
    clicks = 0
    for e in events_sorted:
        if e["action"] == "CLICK":
            clicks += 1
        if e["page"]:
            pages[e["page"]] = pages.get(e["page"], 0) + 1

    # total session duration = last - first
    try:
        t0 = datetime.fromisoformat(events_sorted[0]["ts_iso"])
        t1 = datetime.fromisoformat(events_sorted[-1]["ts_iso"])
        duration_min = int((t1 - t0).total_seconds() / 60)
    except Exception:
        duration_min = 0

    return {
        "user": user,
        "events": len(events_sorted),
        "clicks": clicks,
        "pages": pages,
        "first": first,
        "last": last,
        "duration_min": duration_min,
    }


def all_users_summary(date: str = None) -> dict:
    """Return summary per user for a given date (or all-time)."""
    events = read_events(limit=100000, date=date)
    users = set(e["user"] for e in events)
    return {u: user_summary(u, date=date) for u in users}


# ────────────────────────────────────────────────────────
# OWNER-ONLY DELETE
# ────────────────────────────────────────────────────────

def owner_wipe(owner_password_hash: str, provided_password: str, verify_fn) -> dict:
    """
    Only the OWNER can delete the log. Requires password.
    verify_fn(provided_password, hash) -> bool
    """
    if not verify_fn(provided_password, owner_password_hash):
        return {"ok": False, "msg": "Invalid owner password"}
    # Archive first (never truly destroy)
    if os.path.exists(AUDIT_FILE):
        archive = f"audit_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        os.rename(AUDIT_FILE, archive)
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)
    return {"ok": True, "msg": "Log archived. New log started.", "archive": archive if os.path.exists(AUDIT_FILE) else None}
