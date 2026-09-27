"""
order_intelligence.py — Self-contained order scoring engine.
Reads orders, retailers, aging → returns decision + notification.
"""
import json
from datetime import datetime
from pathlib import Path


# ═══════════════════════════════════════════════════════════
# SCORING WEIGHTS (tune to your business)
# ═══════════════════════════════════════════════════════════
WEIGHTS = {
    "credit_utilization": 25,   # lower better
    "payment_behavior":   20,   # higher better
    "order_size_anomaly": 15,   # flag big jumps
    "aging_health":       15,   # fresh debt better
    "history_depth":      10,   # more orders = safer
    "time_of_day":         5,   # business hours better
    "status_flag":        10,   # Blocked = big penalty
}


def _fmt(v):
    try: return f"₹{float(v):,.0f}"
    except: return "₹0"


def _parse_date(s):
    try: return datetime.strptime(str(s)[:11], "%d-%b-%Y")
    except: return None


# ═══════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════
def score_retailer(retailer, orders):
    """Return score 0-100 with breakdown for one retailer."""
    score = 100
    breakdown = {}
    warnings = []

    # ─── 1. Credit utilization ───
    limit = float(retailer.get("credit_limit", 0) or 0)
    outstanding = float(retailer.get("outstanding", 0) or 0)
    if limit > 0:
        util = outstanding / limit
        if util >= 1.0:
            score -= WEIGHTS["credit_utilization"]
            breakdown["credit"] = 0
            warnings.append(f"Credit limit reached ({util*100:.0f}%)")
        elif util >= 0.9:
            score -= WEIGHTS["credit_utilization"] * 0.7
            breakdown["credit"] = 30
            warnings.append(f"Credit {util*100:.0f}% used")
        elif util >= 0.75:
            score -= WEIGHTS["credit_utilization"] * 0.3
            breakdown["credit"] = 70
        else:
            breakdown["credit"] = 100
    else:
        breakdown["credit"] = 50

    # ─── 2. Payment behavior (from history) ───
    payments = retailer.get("payment_history", []) or []
    if payments:
        # Score based on how many payments made
        pay_score = min(100, len(payments) * 20)
        breakdown["payment"] = pay_score
        score -= WEIGHTS["payment_behavior"] * (1 - pay_score / 100)
    else:
        breakdown["payment"] = 30
        score -= WEIGHTS["payment_behavior"] * 0.7
        warnings.append("No payment history")

    # ─── 3. Order history depth ───
    my_orders = [o for o in orders if o.get("retailer_id") == retailer["id"]]
    approved = [o for o in my_orders if o.get("status") == "Approved"]
    if len(approved) >= 10:
        breakdown["history"] = 100
    elif len(approved) >= 5:
        breakdown["history"] = 80
        score -= WEIGHTS["history_depth"] * 0.2
    elif len(approved) >= 1:
        breakdown["history"] = 50
        score -= WEIGHTS["history_depth"] * 0.5
    else:
        breakdown["history"] = 20
        score -= WEIGHTS["history_depth"] * 0.8
        warnings.append("First-time or no approved orders")

    # ─── 4. Aging health ───
    aging_score = 100
    if approved:
        # Oldest unpaid age
        oldest = min((_parse_date(o.get("placed_at", "")) for o in approved), default=None)
        if oldest:
            age_days = (datetime.now() - oldest).days
            if age_days > 365:
                aging_score = 20; warnings.append(f"Oldest order {age_days} days old")
            elif age_days > 180:
                aging_score = 50; warnings.append(f"Oldest order {age_days} days old")
            elif age_days > 90:
                aging_score = 75
    breakdown["aging"] = aging_score
    score -= WEIGHTS["aging_health"] * (1 - aging_score / 100)

    # ─── 5. Status flag ───
    status = retailer.get("status", "Active")
    if status == "Blocked":
        score -= WEIGHTS["status_flag"] * 3
        breakdown["status"] = 0
        warnings.append("🚫 Retailer is BLOCKED")
    else:
        breakdown["status"] = 100

    return {
        "score": max(0, min(100, int(score))),
        "breakdown": breakdown,
        "warnings": warnings,
    }


def score_order(order, retailer, orders):
    """Score a specific order in context of the retailer's history."""
    base = score_retailer(retailer, orders)
    score = base["score"]
    warnings = list(base["warnings"])

    # ─── Order size anomaly ───
    my_approved = [o for o in orders
                   if o.get("retailer_id") == retailer["id"] and o.get("status") == "Approved"]
    if my_approved:
        avg = sum(float(o.get("total", 0) or 0) for o in my_approved) / len(my_approved)
        this_amt = float(order.get("total", 0) or 0)
        if avg > 0 and this_amt > avg * 3:
            score -= WEIGHTS["order_size_anomaly"]
            warnings.append(f"Order is {this_amt/avg:.1f}x bigger than usual ({_fmt(avg)} avg)")
        elif avg > 0 and this_amt > avg * 2:
            score -= WEIGHTS["order_size_anomaly"] * 0.5
            warnings.append(f"Order is {this_amt/avg:.1f}x bigger than usual")

    # ─── Order value vs available credit ───
    limit = float(retailer.get("credit_limit", 0) or 0)
    outstanding = float(retailer.get("outstanding", 0) or 0)
    available = limit - outstanding
    order_amt = float(order.get("total", 0) or 0)
    if order_amt > available:
        score -= 20
        warnings.append(f"Order {_fmt(order_amt)} exceeds available credit {_fmt(available)}")

    # ─── Time-of-day check ───
    try:
        placed = str(order.get("placed_at", ""))
        hour = int(placed.split(" ")[-1].split(":")[0])
        if hour < 6 or hour > 22:
            score -= WEIGHTS["time_of_day"]
            warnings.append(f"Order placed at {hour}:00 (off-hours)")
    except Exception:
        pass

    # ─── Decision ───
    if score >= 75:
        decision = "auto_approve"
        action_label = "✅ Auto-approved"
    elif score >= 50:
        decision = "soft_review"
        action_label = "⚠️ Review recommended"
    else:
        decision = "hard_review"
        action_label = "🔴 Owner approval required"

    return {
        "order_id": order.get("order_id"),
        "retailer_id": retailer["id"],
        "shop": retailer.get("shop", ""),
        "order_amount": order_amt,
        "score": score,
        "breakdown": base["breakdown"],
        "warnings": warnings,
        "decision": decision,
        "action_label": action_label,
        "available_credit": available,
    }


# ═══════════════════════════════════════════════════════════
# TELEGRAM NOTIFICATION
# ═══════════════════════════════════════════════════════════
def notify_owner(result, owner_chat_id=None):
    """Send decision summary to owner via Telegram."""
    try:
        import os, requests
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = owner_chat_id
        if not chat_id:
            # Load from owner.json
            try:
                o = json.loads(Path("owner.json").read_text())
                chat_id = o.get("telegram_chat_id", "")
            except Exception:
                pass
        if not token or not chat_id:
            return False, "No token/chat_id"

        emoji = {"auto_approve": "✅", "soft_review": "⚠️", "hard_review": "🔴"}
        msg = (
            f"{emoji.get(result['decision'], '❓')} <b>Order Intelligence</b>\n\n"
            f"<b>Order:</b> {result['order_id']}\n"
            f"<b>Shop:</b> {result['shop']} ({result['retailer_id']})\n"
            f"<b>Amount:</b> {_fmt(result['order_amount'])}\n"
            f"<b>Score:</b> {result['score']}/100\n"
            f"<b>Decision:</b> {result['action_label']}\n"
        )
        if result["warnings"]:
            msg += "\n<b>Warnings:</b>\n"
            for w in result["warnings"][:5]:
                msg += f"• {w}\n"
        msg += f"\n<b>Credit available:</b> {_fmt(result['available_credit'])}"

        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
        return r.status_code == 200, r.text[:100]
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════
# BATCH CHECK
# ═══════════════════════════════════════════════════════════
def check_pending_orders(orders, retailers):
    """Score all pending orders. Return sorted list + summary."""
    pending = [o for o in orders if o.get("status") == "Pending"]
    results = []
    for o in pending:
        r = next((x for x in retailers if x["id"] == o.get("retailer_id")), None)
        if r:
            results.append(score_order(o, r, orders))
    results.sort(key=lambda x: x["score"])
    summary = {
        "total": len(results),
        "auto_approve": sum(1 for r in results if r["decision"] == "auto_approve"),
        "soft_review": sum(1 for r in results if r["decision"] == "soft_review"),
        "hard_review": sum(1 for r in results if r["decision"] == "hard_review"),
    }
    return results, summary


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    retailers = json.loads(Path("retailers.json").read_text())
    orders = json.loads(Path("orders.json").read_text()) if Path("orders.json").exists() else []

    print("═" * 75)
    print("  ORDER INTELLIGENCE — Retailer Scores")
    print("═" * 75)
    for r in retailers:
        s = score_retailer(r, orders)
        bar = "█" * (s["score"] // 5) + "░" * (20 - s["score"] // 5)
        print(f"\n{r['shop']} ({r['id']})")
        print(f"  Score: {s['score']:3d}/100  [{bar}]")
        print(f"  Credit: {s['breakdown'].get('credit',0)} | "
              f"Payment: {s['breakdown'].get('payment',0)} | "
              f"History: {s['breakdown'].get('history',0)} | "
              f"Aging: {s['breakdown'].get('aging',0)}")
        for w in s["warnings"]:
            print(f"  ⚠️  {w}")

    # Check pending orders
    pending_results, summary = check_pending_orders(orders, retailers)
    print("\n" + "═" * 75)
    print(f"  PENDING ORDERS: {summary['total']}")
    print(f"  ✅ Auto-approve: {summary['auto_approve']}  "
          f"⚠️ Soft review: {summary['soft_review']}  "
          f"🔴 Hard review: {summary['hard_review']}")
    print("═" * 75)
    for r in pending_results:
        print(f"{r['action_label']:<35} {r['shop'][:20]:<22} ₹{r['order_amount']:>10,.0f}  Score:{r['score']}")
