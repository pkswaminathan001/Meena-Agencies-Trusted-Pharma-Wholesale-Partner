"""
aging_analysis.py — Accounts Receivable Aging Report.
Shows how old each retailer's outstanding balance is.
Buckets: Current (0-30) | 31-60 | 61-90 | 90+ days.
"""
import json
from datetime import datetime
from pathlib import Path


def _parse_date(s):
    """Parse 'DD-MMM-YYYY HH:MM' into datetime. Return None on failure."""
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:11], "%d-%b-%Y")
    except Exception:
        return None


def compute_aging(retailers, orders, today=None):
    """
    Return list of dicts — one per retailer — with aging buckets.
    Uses FIFO: payments apply to oldest orders first.
    """
    today = today or datetime.now()
    results = []

    for r in retailers:
        rid = r.get("id", "?")
        outstanding = float(r.get("outstanding", 0) or 0)

        # Retailer's approved orders (only these count as sales)
        my_orders = [o for o in orders
                     if o.get("retailer_id") == rid
                     and o.get("status") == "Approved"]
        # Sort oldest first
        my_orders.sort(key=lambda o: o.get("placed_at", ""))

        # Total payments received from this retailer
        payments = r.get("payment_history", []) or []
        total_paid = sum(float(p.get("amount", 0) or 0) for p in payments)

        # Apply payments FIFO to oldest orders
        buckets = {"0_30": 0.0, "31_60": 0.0, "61_90": 0.0, "90_plus": 0.0}
        remaining = total_paid

        for o in my_orders:
            amt = float(o.get("total", 0) or 0)
            if amt <= 0:
                continue
            # Fully paid?
            if remaining >= amt:
                remaining -= amt
                continue
            # Partially or fully unpaid
            unpaid = amt - remaining
            remaining = 0

            # Age bucket based on order date
            placed = _parse_date(o.get("placed_at", ""))
            if placed:
                age_days = (today - placed).days
            else:
                age_days = 0

            if age_days <= 30:
                buckets["0_30"] += unpaid
            elif age_days <= 60:
                buckets["31_60"] += unpaid
            elif age_days <= 90:
                buckets["61_90"] += unpaid
            else:
                buckets["90_plus"] += unpaid

        # If outstanding doesn't match computed (due to opening balance etc.)
        # put the difference into 0-30 as a catch-all
        computed_total = sum(buckets.values())
        if outstanding > computed_total + 1:
            buckets["0_30"] += (outstanding - computed_total)

        # Risk
        if buckets["90_plus"] > 0:
            risk = "🔴 High"
        elif buckets["61_90"] > 0:
            risk = "🟠 Medium"
        elif outstanding > 0:
            risk = "🟡 Watch"
        else:
            risk = "🟢 Clear"

        results.append({
            "id": rid,
            "shop": r.get("shop", ""),
            "outstanding": outstanding,
            "0_30": round(buckets["0_30"], 2),
            "31_60": round(buckets["31_60"], 2),
            "61_90": round(buckets["61_90"], 2),
            "90_plus": round(buckets["90_plus"], 2),
            "risk": risk,
        })

    # Sort by worst risk first
    results.sort(key=lambda x: -(x["90_plus"] + x["61_90"] + x["31_60"]))

    # Summary
    summary = {
        "total_outstanding": sum(x["outstanding"] for x in results),
        "0_30": sum(x["0_30"] for x in results),
        "31_60": sum(x["31_60"] for x in results),
        "61_90": sum(x["61_90"] for x in results),
        "90_plus": sum(x["90_plus"] for x in results),
    }
    summary["overdue"] = summary["31_60"] + summary["61_90"] + summary["90_plus"]
    summary["overdue_pct"] = (
        round(summary["overdue"] / summary["total_outstanding"] * 100, 1)
        if summary["total_outstanding"] else 0
    )

    return results, summary


def aging_summary_text(results, summary):
    """One-line summary for Telegram/reports."""
    return (
        f"📊 Aging: Total ₹{summary['total_outstanding']:,.0f} | "
        f"Overdue ₹{summary['overdue']:,.0f} ({summary['overdue_pct']}%) | "
        f"90+ days ₹{summary['90_plus']:,.0f}"
    )


# ─── Test when run directly ───
if __name__ == "__main__":
    retailers = json.loads(Path("retailers.json").read_text())
    orders = json.loads(Path("orders.json").read_text()) if Path("orders.json").exists() else []
    results, summary = compute_aging(retailers, orders)

    print("═" * 70)
    print(f"{'Retailer':<28} {'Total':>12} {'0-30':>10} {'31-60':>10} {'61-90':>10} {'90+':>10}")
    print("═" * 70)
    for r in results:
        print(f"{r['shop'][:27]:<28} "
              f"₹{r['outstanding']:>10,.0f} "
              f"₹{r['0_30']:>8,.0f} "
              f"₹{r['31_60']:>8,.0f} "
              f"₹{r['61_90']:>8,.0f} "
              f"₹{r['90_plus']:>8,.0f}  {r['risk']}")
    print("─" * 70)
    print(f"{'TOTAL':<28} ₹{summary['total_outstanding']:>10,.0f} "
          f"₹{summary['0_30']:>8,.0f} ₹{summary['31_60']:>8,.0f} "
          f"₹{summary['61_90']:>8,.0f} ₹{summary['90_plus']:>8,.0f}")
    print()
    print(aging_summary_text(results, summary))
