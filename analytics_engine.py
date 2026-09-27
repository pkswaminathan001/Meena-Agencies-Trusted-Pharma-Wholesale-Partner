"""analytics_engine.py — Behavioral analytics over audit_pro.jsonl.
Produces: per-user click stats, section time, repetition detection,
automation candidates, efficiency scores, idle gaps."""
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os, json

AUDIT_FILE = "audit_pro.jsonl"


_CACHE = {"events": [], "loaded_at": 0}

def _load_events(days_back: int = 1):
    """Load events with 60s cache and hard cap of 1000 events."""
    import time as _t
    global _CACHE
    now = _t.time()
    if _CACHE["events"] and now - _CACHE["loaded_at"] < 60:
        return _CACHE["events"]
    if not os.path.exists(AUDIT_FILE):
        return []
    cutoff = datetime.now() - timedelta(days=days_back)
    events = []
    with open(AUDIT_FILE) as f:
        for line in f:
            try:
                e = json.loads(line)
                ts = datetime.fromisoformat(e.get("ts_iso", ""))
                if ts >= cutoff:
                    events.append(e)
            except Exception:
                continue
    events = events[-1000:]  # hard cap
    _CACHE["events"] = events
    _CACHE["loaded_at"] = now
    return events


def per_user_clicks(days_back=1):
    """Return {user: {'total': N, 'by_label': Counter, 'by_page': Counter}}."""
    events = _load_events(days_back)
    out = defaultdict(lambda: {"total": 0, "by_label": Counter(), "by_page": Counter()})
    for e in events:
        if e.get("action") != "CLICK":
            continue
        u = e["user"]
        out[u]["total"] += 1
        # Extract label from details
        details = e.get("details", "")
        if 'label="' in details:
            label = details.split('label="', 1)[1].split('"', 1)[0]
            out[u]["by_label"][label] += 1
        out[u]["by_page"][e.get("page", "")] += 1
    return dict(out)


def section_time(days_back=1):
    """Return {user: {page: minutes_spent}} using event-gap estimation."""
    events = _load_events(days_back)
    by_user = defaultdict(list)
    for e in events:
        by_user[e["user"]].append(e)
    out = {}
    for u, evs in by_user.items():
        evs.sort(key=lambda x: x.get("ts_iso", ""))
        pages = defaultdict(float)
        current_page = None
        last_ts = None
        for e in evs:
            if e.get("action") == "PAGE_VIEW" and e.get("page"):
                current_page = e["page"]
            ts = None
            try:
                ts = datetime.fromisoformat(e.get("ts_iso", ""))
            except Exception:
                continue
            if last_ts and current_page:
                gap = (ts - last_ts).total_seconds()
                if gap < 600:  # ignore gaps > 10 min
                    pages[current_page] += gap / 60.0
            last_ts = ts
        out[u] = {p: round(m, 1) for p, m in pages.items()}
    return out


def repetition_detector(days_back=1, window_min=5, min_repeats=3):
    """Find actions repeated N+ times in a short window — automation candidates."""
    events = _load_events(days_back)
    by_user = defaultdict(list)
    for e in events:
        if e.get("action") in ("CLICK", "PAGE_VIEW"):
            try:
                ts = datetime.fromisoformat(e["ts_iso"])
                by_user[e["user"]].append((ts, e))
            except Exception:
                continue
    candidates = []
    for u, evs in by_user.items():
        evs.sort(key=lambda x: x[0])
        if len(evs) > 300:  # cap to avoid O(n²) blowup
            evs = evs[-300:]
        for i, (t0, e0) in enumerate(evs):
            label0 = e0.get("details", "")
            if 'label="' not in label0:
                continue
            lbl = label0.split('label="', 1)[1].split('"', 1)[0]
            if len(lbl) < 3:
                continue
            # count same label within window
            count = 1
            for j in range(i + 1, len(evs)):
                t1, e1 = evs[j]
                if (t1 - t0).total_seconds() > window_min * 60:
                    break
                if lbl in e1.get("details", ""):
                    count += 1
            if count >= min_repeats:
                candidates.append({
                    "user": u, "label": lbl, "repeats": count,
                    "window_min": window_min, "first_at": t0.strftime("%H:%M:%S")
                })
    # Deduplicate by (user, label)
    seen = {}
    for c in candidates:
        k = (c["user"], c["label"])
        if k not in seen or c["repeats"] > seen[k]["repeats"]:
            seen[k] = c
    return list(seen.values())


def efficiency_score(days_back=1):
    """Per-user 0-100 score based on productive vs navigational clicks."""
    events = _load_events(days_back)
    by_user = defaultdict(lambda: {"clicks": 0, "productive": 0, "sections": set()})
    nav_labels = {"next", "back", "tab", "menu", "close"}
    for e in events:
        if e.get("action") != "CLICK":
            continue
        u = e["user"]
        by_user[u]["clicks"] += 1
        d = e.get("details", "").lower()
        is_nav = any(n in d for n in nav_labels)
        if not is_nav:
            by_user[u]["productive"] += 1
        if e.get("page"):
            by_user[u]["sections"].add(e["page"])
    out = {}
    for u, d in by_user.items():
        if d["clicks"] == 0:
            out[u] = 0
        else:
            ratio = d["productive"] / d["clicks"]
            variety = min(len(d["sections"]) / 8, 1.0)
            out[u] = int((ratio * 70) + (variety * 30))
    return out


def idle_gaps(days_back=1, min_gap_min=5):
    """Find gaps > N minutes where user was idle but 'logged in'."""
    events = _load_events(days_back)
    by_user = defaultdict(list)
    for e in events:
        try:
            ts = datetime.fromisoformat(e["ts_iso"])
            by_user[e["user"]].append(ts)
        except Exception:
            continue
    out = {}
    for u, times in by_user.items():
        times.sort()
        gaps = []
        for i in range(1, len(times)):
            delta = (times[i] - times[i-1]).total_seconds() / 60
            if delta >= min_gap_min:
                gaps.append({
                    "from": times[i-1].strftime("%H:%M:%S"),
                    "to": times[i].strftime("%H:%M:%S"),
                    "minutes": int(delta)
                })
        out[u] = gaps
    return out


def automation_opportunities(days_back=1):
    """Combine repetition + idle to suggest automations with ₹ savings estimate."""
    reps = repetition_detector(days_back)
    ops = []
    for r in reps:
        # Assume each repeat costs 15 seconds of work
        saved_min_per_day = (r["repeats"] * 15) / 60
        saved_inr_per_month = saved_min_per_day * 22 * 3  # ~₹3/min labour proxy
        ops.append({
            "user": r["user"],
            "action": r["label"],
            "occurrences": r["repeats"],
            "estimated_min_saved_per_day": round(saved_min_per_day, 1),
            "estimated_inr_saved_per_month": int(saved_inr_per_month),
            "suggestion": f"Automate '{r['label']}' — repeated {r['repeats']}× in {r['window_min']} min"
        })
    return sorted(ops, key=lambda x: -x["estimated_inr_saved_per_month"])


def full_report(days_back=1):
    return {
        "clicks": per_user_clicks(days_back),
        "section_time": section_time(days_back),
        "repetitions": repetition_detector(days_back),
        "efficiency": efficiency_score(days_back),
        "idle_gaps": idle_gaps(days_back),
        "automations": automation_opportunities(days_back),
    }
