"""
returns_manager.py — Purchase returns, sales returns, replacements.
Handles damaged/expired goods in both directions.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

RETURNS_FILE = "returns.json"


# ═══════════════════════════════════════════════════════════
# RETURN REASONS (pharma-specific)
# ═══════════════════════════════════════════════════════════
RETURN_REASONS = [
    "Damaged in transit",
    "Broken packaging",
    "Wrong item shipped",
    "Wrong batch",
    "Expired / near-expiry",
    "Quality complaint",
    "Temperature excursion",
    "Short quantity",
    "Discontinued by manufacturer",
    "Other",
]

RETURN_STATUSES = [
    "Initiated",           # just logged
    "Debit Note Sent",     # document sent to supplier
    "Accepted",            # supplier accepted, replacement promised
    "Replacement Received",# goods received back
    "Credit Note Received",# supplier credited us
    "Rejected",            # supplier rejected our claim
    "Closed",              # fully resolved
]


# ═══════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════
def load_returns():
    if Path(RETURNS_FILE).exists():
        try:
            return json.loads(Path(RETURNS_FILE).read_text())
        except Exception:
            return []
    return []


def save_returns(data):
    Path(RETURNS_FILE).write_text(json.dumps(data, indent=2))


# ═══════════════════════════════════════════════════════════
# CREATE RETURN
# ═══════════════════════════════════════════════════════════
def create_return(return_type, party_name, party_id, items, reason,
                  linked_order="", notes=""):
    """
    Create a return entry.
    return_type: 'purchase' (we return to manufacturer)
              or 'sales'    (retailer returns to us)
    items: list of {medicine, batch, expiry, qty, cost_price}
    """
    data = load_returns()
    ret_id = f"RET-{return_type[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    total_value = sum(float(it.get("qty", 0)) * float(it.get("cost_price", 0)) for it in items)

    entry = {
        "return_id": ret_id,
        "type": return_type,                # 'purchase' or 'sales'
        "party_name": party_name,
        "party_id": party_id,
        "items": items,
        "reason": reason,
        "notes": notes,
        "linked_order": linked_order,
        "total_value": round(total_value, 2),
        "status": "Initiated",
        "created_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
        "timeline": [
            {"ts": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
             "status": "Initiated",
             "by": "OWNER"}
        ],
        "replacement_received": False,
        "credit_note_number": "",
        "debit_note_number": f"DN-{datetime.now().strftime('%y%m')}/{len(data)+1:03d}" if return_type == "purchase" else "",
    }

    data.append(entry)
    save_returns(data)
    return entry


# ═══════════════════════════════════════════════════════════
# UPDATE STATUS
# ═══════════════════════════════════════════════════════════
def update_return_status(return_id, new_status, note=""):
    data = load_returns()
    for r in data:
        if r["return_id"] == return_id:
            r["status"] = new_status
            r["timeline"].append({
                "ts": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
                "status": new_status,
                "note": note,
                "by": "OWNER",
            })
            if new_status == "Replacement Received":
                r["replacement_received"] = True
            if new_status == "Credit Note Received" and note:
                r["credit_note_number"] = note
            save_returns(data)
            return r
    return None


# ═══════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════
def return_summary():
    """Return-level stats."""
    data = load_returns()
    if not data:
        return {"total": 0, "purchase": 0, "sales": 0,
                "total_value": 0, "pending_value": 0,
                "suppliers": {}, "reasons": {}}

    purchase = [r for r in data if r["type"] == "purchase"]
    sales = [r for r in data if r["type"] == "sales"]
    suppliers = {}
    reasons = {}
    for r in data:
        suppliers[r["party_name"]] = suppliers.get(r["party_name"], 0) + r["total_value"]
        reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1

    return {
        "total": len(data),
        "purchase": len(purchase),
        "sales": len(sales),
        "total_value": round(sum(r["total_value"] for r in data), 2),
        "pending_value": round(sum(r["total_value"] for r in data
                                   if r["status"] not in ("Closed", "Rejected")), 2),
        "suppliers": dict(sorted(suppliers.items(), key=lambda x: -x[1])[:5]),
        "reasons": reasons,
    }


def supplier_damage_report(supplier_name=None):
    """Detailed damage report filtered by supplier."""
    data = load_returns()
    rows = [r for r in data if r["type"] == "purchase"]
    if supplier_name:
        rows = [r for r in rows if r["party_name"] == supplier_name]
    return rows


# ═══════════════════════════════════════════════════════════
# DEBIT NOTE / CREDIT NOTE TEXT
# ═══════════════════════════════════════════════════════════
def generate_debit_note_text(return_entry, company):
    """Return text for a Debit Note to supplier."""
    lines = []
    lines.append("=" * 70)
    lines.append("              DEBIT NOTE (PURCHASE RETURN)")
    lines.append("=" * 70)
    lines.append(f"Debit Note No : {return_entry['debit_note_number']}")
    lines.append(f"Date          : {return_entry['created_at']}")
    lines.append(f"Return ID     : {return_entry['return_id']}")
    lines.append("")
    lines.append(f"FROM  : {company.get('legal_name', company.get('name', 'Meena Agencies'))}")
    lines.append(f"        GSTIN: {company.get('gstin', '')}")
    lines.append(f"        {company.get('address1', '')}")
    lines.append(f"        {company.get('address2', '')}")
    lines.append("")
    lines.append(f"TO    : {return_entry['party_name']}")
    lines.append(f"        Party ID: {return_entry['party_id']}")
    lines.append("")
    lines.append(f"Reason for return: {return_entry['reason']}")
    if return_entry.get("notes"):
        lines.append(f"Notes: {return_entry['notes']}")
    lines.append("")
    lines.append("-" * 70)
    lines.append(f"{'#':<3} {'Medicine':<30} {'Batch':<10} {'Qty':>6} {'Rate':>10} {'Amount':>10}")
    lines.append("-" * 70)
    for i, it in enumerate(return_entry["items"], 1):
        amt = float(it.get("qty", 0)) * float(it.get("cost_price", 0))
        lines.append(
            f"{i:<3} {str(it.get('medicine', ''))[:30]:<30} "
            f"{str(it.get('batch', ''))[:10]:<10} "
            f"{it.get('qty', 0):>6} "
            f"{float(it.get('cost_price', 0)):>10,.2f} "
            f"{amt:>10,.2f}"
        )
    lines.append("-" * 70)
    lines.append(f"{'TOTAL':<50} Rs. {return_entry['total_value']:>10,.2f}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("We hereby debit your account for the above amount.")
    lines.append("Kindly replace the goods OR issue a credit note within 15 days.")
    lines.append("")
    lines.append(f"For {company.get('legal_name', 'Meena Agencies')}")
    lines.append("Authorised Signatory")
    lines.append("=" * 70)
    return "\n".join(lines)


def generate_credit_note_text(return_entry, company, retailer):
    """Return text for a Credit Note to retailer (sales return)."""
    lines = []
    lines.append("=" * 70)
    lines.append("              CREDIT NOTE (SALES RETURN)")
    lines.append("=" * 70)
    lines.append(f"Credit Note No: CN-{return_entry['return_id'].split('-')[-1]}")
    lines.append(f"Date          : {return_entry['created_at']}")
    lines.append(f"Return ID     : {return_entry['return_id']}")
    lines.append("")
    lines.append(f"FROM  : {company.get('legal_name', 'Meena Agencies')}")
    lines.append(f"        GSTIN: {company.get('gstin', '')}")
    lines.append("")
    lines.append(f"TO    : {return_entry['party_name']}")
    lines.append(f"        Phone: {retailer.get('phone', '') if retailer else ''}")
    lines.append("")
    lines.append(f"Reason: {return_entry['reason']}")
    lines.append("")
    lines.append("-" * 70)
    lines.append(f"{'#':<3} {'Medicine':<30} {'Batch':<10} {'Qty':>6} {'Rate':>10} {'Amount':>10}")
    lines.append("-" * 70)
    for i, it in enumerate(return_entry["items"], 1):
        amt = float(it.get("qty", 0)) * float(it.get("cost_price", 0))
        lines.append(
            f"{i:<3} {str(it.get('medicine', ''))[:30]:<30} "
            f"{str(it.get('batch', ''))[:10]:<10} "
            f"{it.get('qty', 0):>6} "
            f"{float(it.get('cost_price', 0)):>10,.2f} "
            f"{amt:>10,.2f}"
        )
    lines.append("-" * 70)
    lines.append(f"{'TOTAL CREDIT':<50} Rs. {return_entry['total_value']:>10,.2f}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("This amount has been credited to your account.")
    lines.append(f"For {company.get('legal_name', 'Meena Agencies')}")
    lines.append("Authorised Signatory")
    lines.append("=" * 70)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Clear old test data
    if Path(RETURNS_FILE).exists():
        Path(RETURNS_FILE).unlink()
    
    # Test: return damaged goods to Sun Pharma
    entry = create_return(
        return_type="purchase",
        party_name="Sun Pharma",
        party_id="SUP-001",
        items=[
            {"medicine": "Paracetamol 500mg", "batch": "B1234", "expiry": "Dec-2027",
             "qty": 10, "cost_price": 15.00},
            {"medicine": "Cough Syrup 100ml", "batch": "B5678", "expiry": "Jun-2027",
             "qty": 5, "cost_price": 80.00},
        ],
        reason="Damaged in transit",
        linked_order="PO-2026-001",
        notes="Received 10 broken strips, 5 leaking bottles",
    )
    print(f"✅ Return created: {entry['return_id']}")
    print(f"   Debit Note: {entry['debit_note_number']}")
    print(f"   Value: Rs.{entry['total_value']:.2f}")

    # Update status
    update_return_status(entry["return_id"], "Debit Note Sent", "Emailed to supplier")
    update_return_status(entry["return_id"], "Accepted", "Supplier will replace")
    
    # Generate debit note text
    company = {"legal_name": "Meena Agencies", "gstin": "33AAIFM8119N1ZW",
               "address1": "2661, South Main Street", "address2": "Thanjavur"}
    print()
    print(generate_debit_note_text(entry, company))

    # Summary
    print()
    print("═══ SUMMARY ═══")
    s = return_summary()
    print(f"Total returns: {s['total']}  (Purchase: {s['purchase']}, Sales: {s['sales']})")
    print(f"Total value: Rs.{s['total_value']:,.2f}")
    print(f"Pending value: Rs.{s['pending_value']:,.2f}")
