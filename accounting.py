"""Accounting — payments, ledger, aging, cash flow, GST, P&L"""
import os, json
from datetime import datetime, timedelta

PAY_FILE = "payments.json"
INV_FILE = "invoices.json"


def load_payments():
    if os.path.exists(PAY_FILE):
        with open(PAY_FILE) as f: return json.load(f)
    return []


def save_payments(data):
    with open(PAY_FILE, "w") as f: json.dump(data, f, indent=2)


def record_payment(retailer_id, shop, amount, method, ref="", notes=""):
    """Record a payment from a retailer."""
    data = load_payments()
    entry = {
        "payment_id": f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(data)+1}",
        "retailer_id": retailer_id,
        "shop": shop,
        "amount": float(amount),
        "method": method,
        "ref": ref,
        "notes": notes,
        "date": datetime.now().isoformat(),
        "date_display": datetime.now().strftime("%d-%b-%Y %H:%M").upper()
    }
    data.append(entry)
    save_payments(data)
    return entry


def load_invoices():
    if os.path.exists(INV_FILE):
        with open(INV_FILE) as f: return json.load(f)
    return []


def save_invoices(data):
    with open(INV_FILE, "w") as f: json.dump(data, f, indent=2)


def record_invoice(order, retailer, gst_rate=12):
    """Create invoice from approved order."""
    invoices = load_invoices()
    base = order["total"]
    gst = round(base * gst_rate / 100, 2)
    total = round(base + gst, 2)
    inv = {
        "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{len(invoices)+1:04d}",
        "order_id": order["order_id"],
        "retailer_id": retailer["id"],
        "shop": retailer["shop"],
        "gstin": retailer.get("gst_number", ""),
        "items": order["items"],
        "base_amount": base,
        "gst_rate": gst_rate,
        "gst_amount": gst,
        "total": total,
        "date": datetime.now().isoformat(),
        "date_display": datetime.now().strftime("%d-%b-%Y").upper(),
        "status": "Unpaid"
    }
    invoices.append(inv)
    save_invoices(invoices)
    return inv


def get_retailer_ledger(retailer_id, orders, payments):
    """Build ledger entries for a retailer."""
    entries = []
    for o in orders:
        if o.get("retailer_id") == retailer_id and o.get("status") == "Approved":
            entries.append({
                "date": o.get("approved_at", o.get("placed_at", "")),
                "type": "INVOICE",
                "ref": o["order_id"],
                "debit": o["total"],
                "credit": 0
            })
    for p in payments:
        if p.get("retailer_id") == retailer_id:
            entries.append({
                "date": p["date_display"],
                "type": f"PAYMENT ({p['method']})",
                "ref": p.get("ref", p["payment_id"]),
                "debit": 0,
                "credit": p["amount"]
            })
    entries.sort(key=lambda x: x["date"])
    balance = 0
    for e in entries:
        balance += e["debit"] - e["credit"]
        e["balance"] = balance
    return entries


def aging_report(retailers, orders):
    """Aging buckets: current, 30, 60, 90, 90+ days"""
    now = datetime.now()
    report = []
    for r in retailers:
        buckets = {"current": 0, "30": 0, "60": 0, "90": 0, "90plus": 0}
        r_orders = [o for o in orders if o.get("retailer_id") == r["id"] and o.get("status") == "Approved"]
        for o in r_orders:
            try:
                placed = datetime.fromisoformat(o.get("approved_at", o.get("placed_at", "")).replace(" ", "T").replace("-SEP-", "-09-").replace("-OCT-", "-10-"))
            except:
                placed = now
            days = (now - placed).days
            if days <= 30: buckets["current"] += o["total"]
            elif days <= 60: buckets["30"] += o["total"]
            elif days <= 90: buckets["60"] += o["total"]
            elif days <= 120: buckets["90"] += o["total"]
            else: buckets["90plus"] += o["total"]
        report.append({"retailer": r, "buckets": buckets, "total": sum(buckets.values())})
    return report


def cash_flow(payments, orders, days=30):
    """Money in vs money out over N days"""
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    cash_in = sum(p["amount"] for p in payments 
                  if datetime.fromisoformat(p["date"]) >= cutoff)
    invoiced = sum(o["total"] for o in orders 
                   if o.get("status") == "Approved")
    return {
        "cash_in": cash_in,
        "invoiced": invoiced,
        "receivable": invoiced - cash_in
    }


def gst_summary(orders, gst_rate=12):
    """Monthly GST collected"""
    now = datetime.now()
    month_str = now.strftime("%b-%Y").upper()
    month_orders = [o for o in orders if o.get("status") == "Approved"]
    base = sum(o["total"] for o in month_orders)
    gst = round(base * gst_rate / 100, 2)
    return {
        "month": month_str,
        "base": base,
        "gst_rate": gst_rate,
        "gst_amount": gst,
        "total_invoice_value": base + gst,
        "order_count": len(month_orders)
    }


def profit_loss(orders, inventory_df, days=30):
    """Revenue - Cost = Gross Margin"""
    approved = [o for o in orders if o.get("status") == "Approved"]
    revenue = sum(o["total"] for o in approved)
    # Estimate cost as 75% of revenue (typical pharma wholesale margin)
    cost = revenue * 0.75
    return {
        "revenue": revenue,
        "estimated_cost": cost,
        "gross_margin": revenue - cost,
        "margin_pct": ((revenue - cost) / revenue * 100) if revenue else 0,
        "order_count": len(approved)
    }


def day_book(orders, payments, days=7):
    """Chronological list of all transactions"""
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    entries = []
    
    for o in orders:
        if o.get("status") == "Approved":
            entries.append({
                "date": o.get("approved_at", o.get("placed_at", "")),
                "type": "SALE",
                "party": o.get("shop", ""),
                "ref": o["order_id"],
                "amount": o["total"],
                "direction": "in"
            })
    for p in payments:
        entries.append({
            "date": p["date_display"],
            "type": f"PAYMENT-{p['method']}",
            "party": p.get("shop", ""),
            "ref": p.get("ref", p["payment_id"]),
            "amount": p["amount"],
            "direction": "in"
        })
    entries.sort(key=lambda x: x["date"], reverse=True)
    return entries
