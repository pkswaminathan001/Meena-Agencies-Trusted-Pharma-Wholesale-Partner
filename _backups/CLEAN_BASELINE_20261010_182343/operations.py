"""
operations.py — Business operations for PharmaMind.
Record payments, cancel orders, add stock, search, invoices.
"""
import json
import csv
import os
from datetime import datetime


# ────────────────────────────────────────────────
# PAYMENTS
# ────────────────────────────────────────────────
def record_payment(retailer_id: str, amount: float, note: str = "",
                   mode: str = "cash", reference: str = "", bank: str = "") -> dict:
    """
    Reduce retailer outstanding by amount, log the payment with mode.
    mode: 'cash', 'cheque', 'upi', 'neft', 'rtgs', 'card', 'other'
    reference: cheque number / UTR / UPI ref / transaction ID
    bank: bank name (for cheque/neft/rtgs)
    """
    try:
        retailers = json.load(open("retailers.json"))
    except Exception:
        return {"ok": False, "msg": "Could not load retailers.json"}

    for r in retailers:
        if r["id"] == retailer_id:
            before = r["outstanding"]
            r["outstanding"] = max(0, before - amount)
            payment = {
                "date": datetime.now().isoformat(),
                "amount": amount,
                "mode": mode,
                "reference": reference,
                "bank": bank,
                "note": note,
                "before": before,
                "after": r["outstanding"],
            }
            r.setdefault("payment_history", []).append(payment)
            json.dump(retailers, open("retailers.json", "w"), indent=2)

            # Format reference for message
            ref_txt = f" (Ref: {reference})" if reference else ""
            mode_txt = mode.upper()
            return {
                "ok": True,
                "msg": f"✅ Recorded ₹{amount:,.0f} via {mode_txt}{ref_txt} from {retailer_id}",
                "before": before,
                "after": r["outstanding"],
                "payment": payment,
            }
    return {"ok": False, "msg": f"Retailer {retailer_id} not found"}


# ────────────────────────────────────────────────
# CANCEL ORDER
# ────────────────────────────────────────────────
def cancel_order(order_id: str, reason: str = "") -> dict:
    """Mark order as Cancelled. Does not affect outstanding (approval logic)."""
    try:
        orders = json.load(open("orders.json"))
    except Exception:
        return {"ok": False, "msg": "Could not load orders.json"}

    for o in orders:
        if o["order_id"] == order_id:
            if o["status"] in ("Cancelled", "Rejected"):
                return {"ok": False, "msg": f"Already {o['status']}"}
            was_approved = o["status"] == "Approved"
            o["status"] = "Cancelled"
            o["cancelled_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
            o["cancel_reason"] = reason

            # If was approved, reverse outstanding
            if was_approved:
                try:
                    retailers = json.load(open("retailers.json"))
                    for r in retailers:
                        if r["id"] == o["retailer_id"]:
                            r["outstanding"] = max(0, r["outstanding"] - o["total"])
                            break
                    json.dump(retailers, open("retailers.json", "w"), indent=2)
                except Exception:
                    pass

            json.dump(orders, open("orders.json", "w"), indent=2)
            return {"ok": True, "msg": f"✅ Order {order_id} cancelled"}
    return {"ok": False, "msg": f"Order {order_id} not found"}


# ────────────────────────────────────────────────
# ADD / EDIT STOCK
# ────────────────────────────────────────────────
def add_stock(medicine: str, batch: str, expiry: str, qty: int,
              cost_price: float, supplier: str) -> dict:
    """Add new stock row to inventory.csv."""
    try:
        rows = list(csv.DictReader(open("inventory.csv")))
    except Exception:
        rows = []

    # Generate new item_id
    max_id = 0
    for r in rows:
        try:
            n = int(r.get("item_id", "MED0000").replace("MED", ""))
            max_id = max(max_id, n)
        except Exception:
            pass
    new_id = f"MED{max_id + 1:04d}"

    new_row = {
        "item_id": new_id,
        "medicine_name": medicine,
        "batch_number": batch,
        "expiry_date": expiry,
        "quantity": str(qty),
        "cost_price": str(cost_price),
        "supplier": supplier,
    }
    rows.append(new_row)

    with open("inventory.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["item_id", "medicine_name", "batch_number",
                                                "expiry_date", "quantity", "cost_price", "supplier"])
        writer.writeheader()
        writer.writerows(rows)

    return {"ok": True, "msg": f"✅ Added {new_id} — {medicine} ({qty} units)", "id": new_id}


# ────────────────────────────────────────────────
# SEARCH ORDERS
# ────────────────────────────────────────────────
def search_orders(query: str, orders: list = None) -> list:
    """Search orders by ID, shop name, or item name."""
    if orders is None:
        try:
            orders = json.load(open("orders.json"))
        except Exception:
            return []
    q = query.lower().strip()
    if not q:
        return orders
    results = []
    for o in orders:
        if q in o.get("order_id", "").lower():
            results.append(o); continue
        if q in o.get("shop", "").lower():
            results.append(o); continue
        if q in o.get("retailer_id", "").lower():
            results.append(o); continue
        for item in o.get("items", []):
            if q in item.get("medicine", "").lower():
                results.append(o)
                break
    return results


# ────────────────────────────────────────────────
# INVOICE
# ────────────────────────────────────────────────
def generate_invoice(order: dict, retailer: dict) -> str:
    """Return plain-text invoice for download."""
    lines = []
    lines.append("=" * 60)
    lines.append("        PHARMAMIND WHOLESALE PHARMACEUTICALS")
    lines.append("=" * 60)
    lines.append(f"Invoice Date : {order.get('placed_at', 'N/A')}")
    lines.append(f"Order ID     : {order['order_id']}")
    lines.append(f"Retailer     : {order.get('shop', '')} ({order['retailer_id']})")
    lines.append(f"Location     : {order.get('location', '')}")
    lines.append("-" * 60)
    lines.append(f"{'Medicine':<30} {'Qty':>6} {'Price':>10} {'Total':>10}")
    lines.append("-" * 60)
    for it in order.get("items", []):
        med = it.get("medicine", "")[:30]
        qty = it.get("qty", 0)
        price = it.get("price", 0)
        total = qty * price
        lines.append(f"{med:<30} {qty:>6} {price:>10,.2f} {total:>10,.2f}")
    lines.append("-" * 60)
    lines.append(f"{'GRAND TOTAL':<30} {'':>6} {'':>10} {order.get('total', 0):>10,.2f}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Thank you for your business.")
    lines.append("This is a computer-generated invoice.")
    if retailer:
        lines.append(f"Contact: {retailer.get('phone', '')}")
    lines.append("=" * 60)
    return "\n".join(lines)
