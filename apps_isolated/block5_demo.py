"""
block5_demo.py — Demo data generator + cleaner
Generates 10 realistic activities for testing.
Owner can delete all demo data with one click.
"""
import json, os, random, uuid
from datetime import datetime, timedelta
from pathlib import Path

PARENT = Path(__file__).parent.parent
DEMO_MARKER = PARENT / ".demo_active"
AUDIT_FILE = PARENT / "owner_audit.jsonl"
QUEUE_FILE = PARENT / "ai_permission_queue.json"
ORDERS_FILE = PARENT / "orders.json"
PAYMENTS_FILE = PARENT / "payments.json"
RETAILERS_FILE = PARENT / "retailers.json"


def is_demo_active():
    return DEMO_MARKER.exists()


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
            os.chmod(path, _s.IRUSR | _s.IWUSR)
        except Exception:
            pass
        return True
    except Exception:
        return False


def _backup_before_demo():
    """Snapshot key files before demo data is added."""
    import shutil
    backup_dir = PARENT / ".demo_backup"
    backup_dir.mkdir(exist_ok=True)
    for name in ("orders.json", "payments.json", "ai_permission_queue.json",
                 "owner_audit.jsonl", "retailers.json"):
        src = PARENT / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)
    return backup_dir


def _restore_from_backup():
    """Restore files from pre-demo snapshot."""
    import shutil
    backup_dir = PARENT / ".demo_backup"
    if not backup_dir.exists():
        return False
    for name in ("orders.json", "payments.json", "ai_permission_queue.json",
                 "owner_audit.jsonl", "retailers.json"):
        src = backup_dir / name
        dst = PARENT / name
        if src.exists():
            shutil.copy2(src, dst)
    return True


def _cleanup_backup():
    """Remove the backup directory."""
    import shutil
    backup_dir = PARENT / ".demo_backup"
    if backup_dir.exists():
        shutil.rmtree(backup_dir, ignore_errors=True)


def _load_retailers():
    return _load_json(RETAILERS_FILE, [])


def _load_orders():
    return _load_json(ORDERS_FILE, [])


def _load_payments():
    return _load_json(PAYMENTS_FILE, [])


def _load_queue():
    return _load_json(QUEUE_FILE, [])


def _load_audit():
    """Read audit JSONL."""
    if not AUDIT_FILE.exists():
        return []
    entries = []
    for line in AUDIT_FILE.read_text().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries


def _append_audit(entry):
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _rewrite_audit(entries):
    """Write audit entries (non-demo only)."""
    with open(AUDIT_FILE, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _tag_demo(obj, day_offset=0, hour=10, minute=0):
    """Stamp a demo record with a virtual timestamp."""
    ts = datetime.now() - timedelta(days=day_offset)
    ts = ts.replace(hour=hour, minute=minute, second=random.randint(0, 59))
    obj["_demo"] = True
    obj["_demo_ts"] = ts.isoformat(timespec="seconds")
    return ts


# ══════════════════════════════════════════════════════════════
#  GENERATOR
# ══════════════════════════════════════════════════════════════
def generate_demo_data():
    """Generate 10 realistic activities spread over the last 15 days."""
    _backup_before_demo()
    DEMO_MARKER.write_text(datetime.now().isoformat())

    retailers = _load_retailers()
    if isinstance(retailers, dict):
        retailers = list(retailers.values())
    if len(retailers) < 3:
        return {"ok": False, "error": "Need at least 3 retailers"}

    r0, r1, r2 = retailers[0], retailers[1], retailers[2]

    # ── 1. Owner login (3 days ago) ──
    ts = _tag_demo({}, 3, 8, 12)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "owner_login",
        "target": "", "details": {}, "severity": "info",
        "_demo": True,
    })

    # ── 2. Order placed by RET001 (12 days ago) ──
    ts = _tag_demo({}, 12, 14, 30)
    orders = _load_orders()
    o1 = {
        "order_id": f"ORD-DEMO-{uuid.uuid4().hex[:8].upper()}",
        "retailer_id": r0.get("id"),
        "shop": r0.get("shop"),
        "placed_at": ts.strftime("%d-%b-%Y %H:%M"),
        "total": 2450.50,
        "items": [
            {"medicine": "Amoxicillin 250mg", "qty": 3, "price": 540.29, "line_total": 1620.87},
            {"medicine": "Paracetamol 500mg", "qty": 2, "price": 414.82, "line_total": 829.63},
        ],
        "status": "delivered",
        "_demo": True,
    }
    orders.append(o1)

    # ── 3. Order placed by RET002 (8 days ago) ──
    ts = _tag_demo({}, 8, 11, 15)
    o2 = {
        "order_id": f"ORD-DEMO-{uuid.uuid4().hex[:8].upper()}",
        "retailer_id": r1.get("id"),
        "shop": r1.get("shop"),
        "placed_at": ts.strftime("%d-%b-%Y %H:%M"),
        "total": 5840.00,
        "items": [
            {"medicine": "Azithromycin 500mg", "qty": 10, "price": 342.30, "line_total": 3423.00},
            {"medicine": "ORS Powder", "qty": 5, "price": 483.40, "line_total": 2417.00},
        ],
        "status": "pending",
        "_demo": True,
    }
    orders.append(o2)
    _save_json(ORDERS_FILE, orders)

    # ── 4. Order approved (7 days ago) ──
    ts = _tag_demo({}, 7, 9, 45)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "order_approved",
        "target": o1["order_id"],
        "details": {"amount": o1["total"], "retailer": r0.get("id")},
        "severity": "info", "_demo": True,
    })

    # ── 5. Payment recorded — cash (5 days ago) ──
    ts = _tag_demo({}, 5, 16, 20)
    payments = _load_payments()
    payments.append({
        "payment_id": f"PAY-DEMO-{uuid.uuid4().hex[:6].upper()}",
        "retailer_id": r0.get("id"),
        "amount": 2000.00,
        "date": ts.strftime("%Y-%m-%d"),
        "method": "Cash",
        "reference": "",
        "notes": "Partial payment received at shop",
        "status": "cleared",
        "recorded_by": "OWNER",
        "recorded_at": ts.strftime("%d-%b-%Y %H:%M"),
        "_demo": True,
    })
    _save_json(PAYMENTS_FILE, payments)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "payment_recorded",
        "target": r0.get("id"),
        "details": {"amount": 2000.00, "method": "Cash", "status": "cleared"},
        "severity": "info", "_demo": True,
    })

    # ── 6. Payment recorded — cheque (4 days ago) ──
    ts = _tag_demo({}, 4, 11, 0)
    payments = _load_payments()
    payments.append({
        "payment_id": f"PAY-DEMO-{uuid.uuid4().hex[:6].upper()}",
        "retailer_id": r2.get("id"),
        "amount": 15000.00,
        "date": ts.strftime("%Y-%m-%d"),
        "method": "Cheque",
        "reference": "CHQ-847291",
        "notes": "Post-dated cheque for invoice settlement",
        "status": "pending_clearance",
        "recorded_by": "OWNER",
        "recorded_at": ts.strftime("%d-%b-%Y %H:%M"),
        "_demo": True,
    })
    _save_json(PAYMENTS_FILE, payments)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "payment_recorded",
        "target": r2.get("id"),
        "details": {"amount": 15000.00, "method": "Cheque", "status": "pending_clearance", "ref": "CHQ-847291"},
        "severity": "info", "_demo": True,
    })

    # ── 7. AI "We Miss You" approved (2 days ago) ──
    ts = _tag_demo({}, 2, 19, 30)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "ai_action_approved",
        "target": r1.get("id"),
        "details": {"type": "we_miss_you", "campaign": "5% offer"},
        "severity": "info", "_demo": True,
    })

    # ── 8. AI payment reminder rejected (2 days ago) ──
    ts = _tag_demo({}, 2, 19, 32)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "ai_action_rejected",
        "target": r2.get("id"),
        "details": {"type": "payment_60day", "reason": "Owner will call personally"},
        "severity": "warn", "_demo": True,
    })

    # ── 9. Credit limit edited (yesterday) ──
    ts = _tag_demo({}, 1, 15, 45)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "retailer_credit_edited",
        "target": r0.get("id"),
        "details": {"old_limit": 200000, "new_limit": 250000, "reason": "Consistent payer"},
        "severity": "info", "_demo": True,
    })

    # ── 10. Commandments changed (today) ──
    ts = _tag_demo({}, 0, 9, 30)
    _append_audit({
        "ts": ts.isoformat(timespec="seconds"),
        "date": ts.strftime("%Y-%m-%d"),
        "time": ts.strftime("%H:%M:%S"),
        "day": ts.strftime("%A"),
        "actor": "OWNER", "action": "commandments_updated",
        "target": "",
        "details": {"auto_approve_max": "5000 → 7500", "trusted_min_orders": "3 → 5"},
        "severity": "info", "_demo": True,
    })

    # ── Also seed AI permission queue with 3 demo items ──
    queue = _load_queue()
    for i, (rt, kind, sev) in enumerate([
        (r0, "we_miss_you", "warn"),
        (r1, "payment_30day", "warn"),
        (r2, "festival_wish", "info"),
    ]):
        ts = _tag_demo({}, random.randint(0, 3), 7 + i, 30)
        queue.append({
            "id": f"ACT-DEMO-{uuid.uuid4().hex[:8]}",
            "type": kind,
            "summary": f"[DEMO] {kind.replace('_',' ').title()} for {rt.get('shop','?')}",
            "payload": {
                "retailer_id": rt.get("id"),
                "shop": rt.get("shop"),
                "chat_id": rt.get("telegram_chat_id", ""),
                "message": f"[DEMO] This is a sample {kind.replace('_',' ')} message for {rt.get('owner','?')}. Nothing will be sent.",
            },
            "severity": sev,
            "status": "pending",
            "created_at": ts.strftime("%d-%b-%Y %H:%M"),
            "_demo": True,
        })
    _save_json(QUEUE_FILE, queue)

    return {"ok": True, "activities_created": 10, "queue_items": 3}


# ══════════════════════════════════════════════════════════════
#  CLEANER
# ══════════════════════════════════════════════════════════════
def delete_demo_data():
    """Remove every demo entry. Restore from backup if available."""
    removed = {"audit": 0, "orders": 0, "payments": 0, "queue": 0}

    # 1. Audit — remove demo entries, keep real ones
    audit = _load_audit()
    real_audit = [e for e in audit if not e.get("_demo")]
    removed["audit"] = len(audit) - len(real_audit)
    _rewrite_audit(real_audit)

    # 2. Orders — remove demo entries
    orders = _load_orders()
    real_orders = [o for o in orders if not o.get("_demo")]
    removed["orders"] = len(orders) - len(real_orders)
    _save_json(ORDERS_FILE, real_orders)

    # 3. Payments — remove demo entries
    payments = _load_payments()
    real_payments = [p for p in payments if not p.get("_demo")]
    removed["payments"] = len(payments) - len(real_payments)
    _save_json(PAYMENTS_FILE, real_payments)

    # 4. Queue — remove demo entries
    queue = _load_queue()
    real_queue = [q for q in queue if not q.get("_demo")]
    removed["queue"] = len(queue) - len(real_queue)
    _save_json(QUEUE_FILE, real_queue)

    # 5. Remove marker + cleanup backup
    if DEMO_MARKER.exists():
        DEMO_MARKER.unlink()
    _cleanup_backup()

    total = sum(removed.values())
    return {"ok": True, "removed": removed, "total_removed": total}
