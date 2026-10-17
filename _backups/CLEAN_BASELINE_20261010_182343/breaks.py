"""Break tracking — records locks, unlocks, computes break durations."""
import os, json
from datetime import datetime, timedelta

BREAK_FILE = "breaks.json"

def load_breaks():
    if os.path.exists(BREAK_FILE):
        with open(BREAK_FILE) as f: return json.load(f)
    return []

def save_breaks(data):
    with open(BREAK_FILE, "w") as f: json.dump(data, f, indent=2)

def log_lock(worker):
    """Record that worker's screen was locked (Windows+L)."""
    data = load_breaks()
    # prevent duplicate locks
    active = [b for b in data if b["worker"]==worker and b.get("end") is None]
    if active:
        return  # already locked
    data.append({
        "worker": worker,
        "start": datetime.now().isoformat(),
        "end": None,
        "duration_min": 0
    })
    save_breaks(data)
    print(f"[BREAK START] {worker} at {datetime.now().strftime('%H:%M:%S')}")

def log_unlock(worker):
    """Record that worker's screen was unlocked."""
    data = load_breaks()
    now = datetime.now()
    updated = False
    for b in data:
        if b["worker"]==worker and b.get("end") is None:
            b["end"] = now.isoformat()
            start = datetime.fromisoformat(b["start"])
            b["duration_min"] = int((now - start).total_seconds() / 60)
            updated = True
            print(f"[BREAK END] {worker} duration: {b['duration_min']} min")
    if updated:
        save_breaks(data)

def get_current_break(worker, max_break_minutes=120):
    """Return active break if any. Auto-closes stale breaks > 2 hours."""
    data = load_breaks()
    now = datetime.now()
    changed = False
    for b in data:
        if b["worker"] == worker and b.get("end") is None:
            start = datetime.fromisoformat(b["start"])
            elapsed = int((now - start).total_seconds() / 60)
            # Auto-close if break exceeds max (default 2 hours)
            if elapsed > max_break_minutes:
                b["end"] = now.isoformat()
                b["duration_min"] = max_break_minutes
                b["source"] = (b.get("source", "auto") + "+stale-closed")
                changed = True
                if changed:
                    save_breaks(data)
                return None
            return {"started": b["start"], "elapsed_min": elapsed}
    if changed:
        save_breaks(data)
    return None

def get_today_breaks(worker):
    """Return today's breaks for a worker."""
    data = load_breaks()
    today = datetime.now().date()
    result = []
    total = 0
    for b in data:
        if b["worker"] != worker: continue
        start = datetime.fromisoformat(b["start"])
        if start.date() != today: continue
        result.append(b)
        total += b.get("duration_min", 0)
    return result, total

def get_worker_summary(worker, session_start_iso):
    """Total work + break minutes since session started. Caps unrealistic values."""
    data = load_breaks()
    today = datetime.now().date()
    now = datetime.now()
    total_break = 0
    for b in data:
        if b["worker"] != worker:
            continue
        try:
            start = datetime.fromisoformat(b["start"])
        except Exception:
            continue
        if start.date() != today:
            continue
        # Cap any single break at 120 min
        dur = min(b.get("duration_min", 0), 120)
        total_break += dur
    # Cap total break at 8 hours
    total_break = min(total_break, 480)
    
    try:
        start = datetime.fromisoformat(session_start_iso)
        session_min = int((now - start).total_seconds() / 60)
        session_min = min(session_min, 16 * 60)  # cap at 16h work day
        total_work = max(0, session_min - total_break)
    except Exception:
        total_work = 0
    return {"work_min": total_work, "break_min": total_break}
