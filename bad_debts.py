"""
bad_debts.py — Track bad debts, aging, recovery status.
Helps you legally write off unrecoverable amounts.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

BAD_DEBT_FILE = "bad_debts.json"


def load_bad_debts():
    if Path(BAD_DEBT_FILE).exists():
        return json.loads(Path(BAD_DEBT_FILE).read_text())
    return {"written_off": [], "provision": []}


def save_bad_debts(data):
    Path(BAD_DEBT_FILE).write_text(json.dumps(data, indent=2))


def classify_by_age(outstanding, last_order_date):
    """Return category: Recoverable / At Risk / Doubtful / Bad"""
    if not last_order_date:
        return "Unknown"
    try:
        last = datetime.strptime(str(last_order_date)[:11], "%d-%b-%Y")
        age_days = (datetime.now() - last).days
    except Exception:
        return "Unknown"

    if age_days < 90:
        return "🟢 Recoverable"
    if age_days < 180:
        return "🟡 At Risk"
    if age_days < 365:
        return "🟠 Doubtful"
    return "🔴 Bad Debt (write off recommended)"


def debt_report(retailers, orders):
    """Return categorized report of all outstanding debts."""
    report = []
    for r in retailers:
        outstanding = float(r.get("outstanding", 0) or 0)
        if outstanding <= 0:
            continue

        # Find last order date
        my_orders = [o for o in orders if o.get("retailer_id") == r.get("id")]
        last_order = max((o.get("placed_at", "") for o in my_orders), default="")

        category = classify_by_age(outstanding, last_order)

        report.append({
            "id": r.get("id"),
            "shop": r.get("shop", ""),
            "owner": r.get("owner", ""),
            "phone": r.get("phone", ""),
            "outstanding": outstanding,
            "last_order": last_order or "Never",
            "category": category,
            "status": r.get("status", "Active"),
        })

    report.sort(key=lambda x: (
        {"🔴 Bad Debt (write off recommended)": 0,
         "🟠 Doubtful": 1,
         "🟡 At Risk": 2,
         "🟢 Recoverable": 3,
         "Unknown": 4}.get(x["category"], 5),
        -x["outstanding"]
    ))
    return report


def summary(report):
    """Summary of bad debt exposure."""
    by_cat = {}
    for r in report:
        cat = r["category"]
        if cat not in by_cat:
            by_cat[cat] = {"count": 0, "amount": 0}
        by_cat[cat]["count"] += 1
        by_cat[cat]["amount"] += r["outstanding"]

    total = sum(r["outstanding"] for r in report)
    bad = by_cat.get("🔴 Bad Debt (write off recommended)", {}).get("amount", 0)
    doubtful = by_cat.get("🟠 Doubtful", {}).get("amount", 0)

    return {
        "total_outstanding": total,
        "by_category": by_cat,
        "likely_bad": bad,
        "at_risk": doubtful,
        "recovery_pct": round((total - bad - doubtful) / total * 100, 1) if total else 0,
    }


if __name__ == "__main__":
    retailers = json.loads(Path("retailers.json").read_text())
    orders = json.loads(Path("orders.json").read_text()) if Path("orders.json").exists() else []

    report = debt_report(retailers, orders)
    s = summary(report)

    print("═" * 75)
    print("  BAD DEBT ANALYSIS")
    print("═" * 75)
    for r in report:
        print(f"{r['category']:<35} {r['shop'][:25]:<26} ₹{r['outstanding']:>10,.0f}")
    print("─" * 75)
    print(f"Total outstanding    : ₹{s['total_outstanding']:>12,.0f}")
    print(f"Likely bad debt      : ₹{s['likely_bad']:>12,.0f}")
    print(f"At risk              : ₹{s['at_risk']:>12,.0f}")
    print(f"Expected recovery %  : {s['recovery_pct']}%")
