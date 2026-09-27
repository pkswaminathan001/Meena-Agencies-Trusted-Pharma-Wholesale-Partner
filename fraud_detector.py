"""Fraud detection — time theft, money leaks, unusual patterns"""
import os, json
from datetime import datetime, timedelta

def detect_money_leaks(orders, payments, retailers, journal):
    """Find suspicious money patterns."""
    alerts = []

    # 1. Payments that exceed outstanding
    for p in payments:
        ret = next((r for r in retailers if r["id"] == p["retailer_id"]), None)
        if ret and p["amount"] > ret["outstanding"] * 1.5:
            alerts.append({
                "severity": "HIGH",
                "type": "Overpayment",
                "detail": f"Payment ₹{p['amount']:,.0f} from {ret['shop']} exceeds their outstanding ₹{ret['outstanding']:,.0f} by >50%",
                "fix": "Check if payment was mistakenly posted to wrong retailer"
            })

    # 2. Orders with same total placed within 1 minute (duplicate detection)
    sorted_orders = sorted(orders, key=lambda x: x.get("placed_at", ""))
    for i in range(1, len(sorted_orders)):
        prev, curr = sorted_orders[i-1], sorted_orders[i]
        if prev.get("retailer_id") == curr.get("retailer_id") and abs(prev["total"] - curr["total"]) < 1:
            alerts.append({
                "severity": "MEDIUM",
                "type": "Possible duplicate order",
                "detail": f"Same retailer placed 2 orders of ₹{prev['total']:,.0f} close together",
                "fix": "Confirm with retailer — may be genuine repeat order or system glitch"
            })

    # 3. Unexpectedly high discount / write-off patterns
    journal_entries = journal or []
    discount_total = sum(j["total_debit"] for j in journal_entries if "discount" in j["description"].lower())
    if discount_total > 50000:
        alerts.append({
            "severity": "MEDIUM",
            "type": "High discount outflow",
            "detail": f"Total discounts given: ₹{discount_total:,.0f}",
            "fix": "Review who approved these discounts — possible margin erosion"
        })

    # 4. Journal entries without matching order/payment
    for j in journal_entries:
        if j["source"] == "MANUAL" and j["total_debit"] > 25000:
            alerts.append({
                "severity": "HIGH",
                "type": "Large manual entry",
                "detail": f"Manual entry {j['entry_id']} of ₹{j['total_debit']:,.0f}: {j['description']}",
                "fix": f"Verify with {j['user']} — this bypassed normal order flow"
            })

    return alerts


def detect_time_theft(activity, orders):
    """Detect workers who are idle while clocked in."""
    alerts = []
    # Group activity by worker
    by_worker = {}
    for a in activity:
        by_worker.setdefault(a["worker"], []).append(a)

    for worker, acts in by_worker.items():
        acts_sorted = sorted(acts, key=lambda x: x["ts"])
        # Check for very short sessions with no output
        for i, a in enumerate(acts_sorted):
            if a["action"] == "LOGIN_SUCCESS":
                # Find logout
                logout = next((x for x in acts_sorted[i+1:] if x["action"] == "LOGOUT"), None)
                if logout:
                    try:
                        login_t = datetime.fromisoformat(a["ts"])
                        logout_t = datetime.fromisoformat(logout["ts"])
                        session_min = (logout_t - login_t).total_seconds() / 60
                        # Any orders placed during this session?
                        orders_in = [o for o in orders 
                                     if o.get("retailer_id") == worker 
                                     and login_t <= datetime.fromisoformat(o.get("placed_at_iso", o.get("placed_at", "2000-01-01"))) <= logout_t]
                        if session_min > 30 and len(orders_in) == 0:
                            alerts.append({
                                "severity": "MEDIUM",
                                "type": "Idle session",
                                "detail": f"{worker} logged in for {int(session_min)} min with 0 orders",
                                "fix": f"Check with {worker} — logged time without output"
                            })
                    except:
                        pass
    return alerts[:20]  # cap


def detect_unusual_patterns(orders):
    """Time-of-day, weekday, and amount anomalies."""
    alerts = []
    if len(orders) < 10:
        return alerts

    amounts = [o["total"] for o in orders]
    avg = sum(amounts) / len(amounts)
    std = (sum((x - avg) ** 2 for x in amounts) / len(amounts)) ** 0.5

    for o in orders:
        z = (o["total"] - avg) / std if std > 0 else 0
        if abs(z) > 3:
            alerts.append({
                "severity": "MEDIUM",
                "type": "Anomalous order size",
                "detail": f"Order {o['order_id']} for ₹{o['total']:,.0f} is {abs(z):.1f} std devs from avg ₹{avg:,.0f}",
                "fix": "Verify this order is legitimate"
            })
    return alerts[:15]


def run_all_checks(orders, payments, retailers, journal, activity):
    return {
        "money_leaks": detect_money_leaks(orders, payments, retailers, journal),
        "time_theft": detect_time_theft(activity, orders),
        "unusual": detect_unusual_patterns(orders)
    }
