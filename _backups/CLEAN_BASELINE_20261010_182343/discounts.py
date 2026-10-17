"""
discounts.py — Discount rules, staff proposals, approval workflow, analytics.
Owner sets tiers. Staff proposes. Owner approves.
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

RULES_FILE = "discount_rules.json"
REQUESTS_FILE = "discount_requests.json"
HISTORY_FILE = "discount_history.json"


# ═══════════════════════════════════════════════════════════
# TIERS (owner-configurable)
# ═══════════════════════════════════════════════════════════
DEFAULT_TIERS = {
    # Pharma-appropriate partner tiers (not metal!)
    "Apex Partner":      {"discount_pct": 15.0, "min_orders": 100, "color": "#00d4ff"},
    "Prime Partner":     {"discount_pct": 12.0, "min_orders": 50,  "color": "#7b61ff"},
    "Preferred Partner": {"discount_pct": 8.0,  "min_orders": 20,  "color": "#00d47a"},
    "Standard Partner":  {"discount_pct": 5.0,  "min_orders": 5,   "color": "#ffb547"},
    "New Partner":       {"discount_pct": 0.0,  "min_orders": 0,   "color": "#8892b0"},
}

# Product-level max discount (owner can override per product)
DEFAULT_PRODUCT_LIMITS = {
    "vaccine":    8.0,
    "insulin":    10.0,
    "controlled": 0.0,   # never discount controlled substances
    "default":    15.0,
}

# Rules:
# - Staff cannot give > their max (owner sets in users.json)
# - Staff discount > 8% → owner approval required
STAFF_AUTO_APPROVE_LIMIT = 8.0


# ═══════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════
def _load(path, default):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text())
        except Exception:
            return default
    return default

def _save(path, data):
    Path(path).write_text(json.dumps(data, indent=2))


def load_rules():
    data = _load(RULES_FILE, {})
    if not data:
        data = {"tiers": DEFAULT_TIERS, "product_limits": DEFAULT_PRODUCT_LIMITS,
                "customer_tiers": {}}
        _save(RULES_FILE, data)
    return data


def save_rules(data):
    _save(RULES_FILE, data)


def load_requests():
    return _load(REQUESTS_FILE, [])


def save_requests(data):
    _save(REQUESTS_FILE, data)


def load_history():
    return _load(HISTORY_FILE, [])


def save_history(data):
    _save(HISTORY_FILE, data)


# ═══════════════════════════════════════════════════════════
# CUSTOMER TIERS
# ═══════════════════════════════════════════════════════════
def set_customer_tier(retailer_id, tier_name):
    """Owner action — assign customer to a tier."""
    rules = load_rules()
    if tier_name not in rules["tiers"]:
        return False, f"Unknown tier: {tier_name}"
    rules["customer_tiers"][retailer_id] = {
        "tier": tier_name,
        "set_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
    }
    save_rules(rules)
    return True, f"✅ {retailer_id} → {tier_name}"


def get_customer_tier(retailer_id):
    """Return (tier_name, discount_pct)."""
    rules = load_rules()
    tier_name = rules["customer_tiers"].get(retailer_id, {}).get("tier", "New Partner")
    pct = rules["tiers"].get(tier_name, {}).get("discount_pct", 0.0)
    return tier_name, pct


def auto_assign_tier(retailer, orders):
    """Based on order count, suggest a tier."""
    count = len([o for o in orders
                 if o.get("retailer_id") == retailer["id"]
                 and o.get("status") == "Approved"])
    rules = load_rules()
    # Highest threshold passed
    best = "New Partner"
    best_min = -1
    for tier, data in rules["tiers"].items():
        if count >= data["min_orders"] and data["min_orders"] > best_min:
            best = tier
            best_min = data["min_orders"]
    return best, count


# ═══════════════════════════════════════════════════════════
# DISCOUNT CALCULATION
# ═══════════════════════════════════════════════════════════
def compute_discount(order_amount, base_pct, extra_pct=0.0, cap_pct=None):
    """Return dict with discount amount and final payable."""
    pct = base_pct + extra_pct
    if cap_pct is not None:
        pct = min(pct, cap_pct)
    disc_amount = round(order_amount * pct / 100, 2)
    return {
        "order_amount": round(order_amount, 2),
        "base_pct": base_pct,
        "extra_pct": extra_pct,
        "total_pct": round(pct, 2),
        "discount_amount": disc_amount,
        "payable": round(order_amount - disc_amount, 2),
    }


def check_product_limit(medicine_name, proposed_pct):
    """Ensure discount doesn't exceed product-level max."""
    rules = load_rules()
    n = str(medicine_name).lower()
    if "controlled" in n or "morphine" in n or "schedule" in n:
        cap = rules["product_limits"].get("controlled", 0.0)
        cat = "controlled"
    elif "vaccine" in n:
        cap = rules["product_limits"].get("vaccine", 8.0)
        cat = "vaccine"
    elif "insulin" in n:
        cap = rules["product_limits"].get("insulin", 10.0)
        cat = "insulin"
    else:
        cap = rules["product_limits"].get("default", 15.0)
        cat = "default"
    return proposed_pct <= cap, cap, cat


# ═══════════════════════════════════════════════════════════
# STAFF PROPOSAL WORKFLOW
# ═══════════════════════════════════════════════════════════
def staff_propose_discount(staff_id, staff_name, retailer, order, extra_pct, reason):
    """
    Staff proposes an extra discount on top of base tier.
    Returns (ok, msg, request_id).
    """
    if extra_pct <= 0:
        return False, "Extra discount must be > 0", None

    # Check product limits
    for item in order.get("items", []):
        ok, cap, cat = check_product_limit(item.get("medicine", ""), extra_pct)
        if not ok:
            return False, f"❌ {item.get('medicine')} ({cat}) caps at {cap}%", None

    # Auto-approve if under threshold and staff's own limit
    auto = extra_pct <= STAFF_AUTO_APPROVE_LIMIT
    status = "Auto-Approved" if auto else "Pending Owner Approval"

    req_id = f"DR-{datetime.now().strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    req = {
        "request_id": req_id,
        "staff_id": staff_id,
        "staff_name": staff_name,
        "retailer_id": retailer["id"],
        "retailer_shop": retailer["shop"],
        "order_id": order.get("order_id", ""),
        "order_amount": float(order.get("total", 0)),
        "extra_pct": float(extra_pct),
        "reason": reason,
        "status": status,
        "created_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
        "approved_by": "SYSTEM" if auto else "",
        "approved_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper() if auto else "",
    }
    reqs = load_requests()
    reqs.append(req)
    save_requests(reqs)
    return True, f"✅ Request {req_id} — {status}", req_id


def owner_decide(request_id, decision, owner_name="OWNER"):
    """Owner approves or rejects a pending request."""
    reqs = load_requests()
    for r in reqs:
        if r["request_id"] == request_id:
            if decision.lower() == "approve":
                r["status"] = "Approved"
            elif decision.lower() == "reject":
                r["status"] = "Rejected"
            else:
                return False, "Decision must be 'approve' or 'reject'"
            r["approved_by"] = owner_name
            r["approved_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
            save_requests(reqs)
            # Record history
            hist = load_history()
            hist.append({**r})
            save_history(hist)
            return True, f"✅ {request_id} → {r['status']}"
    return False, "Request not found"


def pending_requests():
    return [r for r in load_requests() if r["status"] == "Pending Owner Approval"]


# ═══════════════════════════════════════════════════════════
# ANALYTICS — patterns & stages
# ═══════════════════════════════════════════════════════════
def customer_discount_analysis(orders, retailers):
    """Return per-customer discount stats."""
    hist = load_history()
    pending = load_requests()
    rules = load_rules()
    rows = []
    for r in retailers:
        # Current tier
        tier, base_pct = get_customer_tier(r["id"])
        # Total orders
        my_orders = [o for o in orders
                     if o.get("retailer_id") == r["id"] and o.get("status") == "Approved"]
        # Discount history
        my_hist = [h for h in hist if h["retailer_id"] == r["id"]]
        total_extra = sum(h["extra_pct"] for h in my_hist)
        avg_extra = total_extra / len(my_hist) if my_hist else 0
        # Pending
        my_pending = [p for p in pending if p["retailer_id"] == r["id"]]
        # Auto-assign suggestion
        suggested, order_count = auto_assign_tier(r, orders)
        rows.append({
            "retailer_id": r["id"],
            "shop": r["shop"],
            "current_tier": tier,
            "base_discount_pct": base_pct,
            "orders": order_count,
            "avg_extra_discount_pct": round(avg_extra, 2),
            "total_discount_events": len(my_hist),
            "pending_requests": len(my_pending),
            "suggested_tier": suggested,
            "should_upgrade": suggested != tier,
            "tier_color": rules["tiers"].get(tier, {}).get("color", "#8892b0"),
        })
    return rows


def product_discount_analysis(orders):
    """Return per-product discount stats."""
    hist = load_history()
    prod_stats = {}
    for h in hist:
        # We don't have per-item breakdown in hist — approximate by counting the order
        for o in orders:
            if o.get("order_id") == h["order_id"]:
                for item in o.get("items", []):
                    key = item.get("medicine", "unknown")[:30]
                    if key not in prod_stats:
                        prod_stats[key] = {
                            "medicine": key,
                            "discount_events": 0,
                            "total_extra_pct": 0,
                            "customers": set(),
                        }
                    prod_stats[key]["discount_events"] += 1
                    prod_stats[key]["total_extra_pct"] += h["extra_pct"]
                    prod_stats[key]["customers"].add(h["retailer_id"])
    result = []
    for v in prod_stats.values():
        avg = v["total_extra_pct"] / v["discount_events"] if v["discount_events"] else 0
        result.append({
            "medicine": v["medicine"],
            "discount_events": v["discount_events"],
            "avg_extra_pct": round(avg, 2),
            "customers_affected": len(v["customers"]),
        })
    result.sort(key=lambda x: -x["discount_events"])
    return result


def staff_discount_analysis():
    """Return per-staff discount stats — who gives how much."""
    hist = load_history() + [r for r in load_requests() if r["status"] != "Pending Owner Approval"]
    pending = pending_requests()
    staff_stats = {}
    for h in hist:
        s = h.get("staff_id", "UNKNOWN")
        if s not in staff_stats:
            staff_stats[s] = {
                "staff_id": s,
                "staff_name": h.get("staff_name", s),
                "total_discounts": 0,
                "approved": 0,
                "rejected": 0,
                "total_extra_pct": 0,
                "total_value": 0,
                "pending": 0,
            }
        if h["status"] == "Approved" or h["status"] == "Auto-Approved":
            staff_stats[s]["approved"] += 1
            staff_stats[s]["total_discounts"] += 1
            staff_stats[s]["total_extra_pct"] += h["extra_pct"]
            staff_stats[s]["total_value"] += h["order_amount"] * h["extra_pct"] / 100
        elif h["status"] == "Rejected":
            staff_stats[s]["rejected"] += 1
    for p in pending:
        s = p.get("staff_id", "UNKNOWN")
        if s not in staff_stats:
            staff_stats[s] = {
                "staff_id": s, "staff_name": p.get("staff_name", s),
                "total_discounts": 0, "approved": 0, "rejected": 0,
                "total_extra_pct": 0, "total_value": 0, "pending": 0,
            }
        staff_stats[s]["pending"] += 1
    result = list(staff_stats.values())
    for v in result:
        v["avg_extra_pct"] = round(v["total_extra_pct"] / v["approved"], 2) if v["approved"] else 0
    return result


def discount_stage_summary(orders, retailers):
    """
    Overall stage: what % of customers at each tier, health score.
    """
    rules = load_rules()
    tiers_count = {t: 0 for t in rules["tiers"]}
    for r in retailers:
        t, _ = get_customer_tier(r["id"])
        tiers_count[t] = tiers_count.get(t, 0) + 1

    hist = load_history()
    total_disc_value = sum(h["order_amount"] * h["extra_pct"] / 100
                           for h in hist if h["status"] in ("Approved", "Auto-Approved"))
    pending_count = len(pending_requests())

    return {
        "tier_distribution": tiers_count,
        "total_customers": len(retailers),
        "total_discount_value": round(total_disc_value, 2),
        "total_discount_events": len([h for h in hist if h["status"] in ("Approved", "Auto-Approved")]),
        "pending_approval": pending_count,
        "avg_discount_pct": round(sum(h["extra_pct"] for h in hist) / len(hist), 2) if hist else 0,
    }


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("  DISCOUNT SYSTEM TEST")
    print("═" * 70)

    rules = load_rules()
    print(f"\n✅ Tiers:")
    for t, d in rules["tiers"].items():
        print(f"   {t:10s} → {d['discount_pct']:5.1f}% (min {d['min_orders']} orders)")

    # Set a tier
    ok, msg = set_customer_tier("RET001", "Gold")
    print(f"\n{msg}")

    # Compute a discount
    calc = compute_discount(10000, 12.0, 3.0)
    print(f"\n💰 Order ₹10,000 + Gold 12% + Staff extra 3%:")
    print(f"   Total discount: ₹{calc['discount_amount']:.2f} ({calc['total_pct']}%)")
    print(f"   Payable: ₹{calc['payable']:.2f}")

    # Staff proposal
    retailer = {"id": "RET001", "shop": "Sri Balaji Medicals"}
    order = {"order_id": "ORD-TEST", "total": 10000,
             "items": [{"medicine": "Paracetamol 500mg"}]}
    ok, msg, rid = staff_propose_discount("STAFF001", "Rajesh", retailer, order, 5.0, "Bulk order")
    print(f"\n{msg}")

    # Test high-discount proposal (needs approval)
    ok, msg, rid2 = staff_propose_discount("STAFF001", "Rajesh", retailer, order, 12.0, "Special case")
    print(f"{msg}")

    # Owner approves
    if rid2:
        ok, msg = owner_decide(rid2, "approve")
        print(f"\n{msg}")

    # Summary
    print("\n═══ STAGE SUMMARY ═══")
    s = discount_stage_summary([], [retailer])
    for k, v in s.items():
        print(f"   {k}: {v}")

    # Product limits test
    print("\n═══ PRODUCT LIMIT TEST ═══")
    for med, pct in [("Paracetamol 500mg", 10), ("Insulin Glargine", 15), ("Morphine 10mg", 5)]:
        ok, cap, cat = check_product_limit(med, pct)
        print(f"   {med[:25]:25s} @ {pct}% → {'✅' if ok else '❌'} (cap {cap}%, cat {cat})")
