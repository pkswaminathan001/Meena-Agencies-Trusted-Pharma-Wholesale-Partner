"""Seed accounting books with realistic demo entries. Run once. Delete later when real data comes."""
import os, json, hashlib
from datetime import datetime, timedelta

JOURNAL_FILE = "journal.json"
CHAIN_FILE = "audit_chain.json"

CHART = {
    "1000": "Cash A/c", "1010": "Bank A/c", "1100": "Sundry Debtors",
    "1200": "Closing Stock", "2000": "Sundry Creditors",
    "2100": "GST Output Payable", "2200": "GST Input Credit",
    "3000": "Capital A/c", "4000": "Sales A/c", "4100": "Sales Returns A/c",
    "5000": "Purchases A/c", "5100": "Purchase Returns A/c",
    "6000": "Salary A/c", "6100": "Rent A/c", "6200": "Electricity A/c",
    "6300": "Telephone & Internet", "6400": "Transport & Freight",
    "6500": "Discount Allowed", "7000": "Miscellaneous Expenses",
}


def load_journal():
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE) as f: return json.load(f)
    return []


def save_journal(data):
    with open(JOURNAL_FILE, "w") as f: json.dump(data, f, indent=2)


def mk_entry(date_offset_days, entry_num, description, lines, ref, source="SEED"):
    """Create a journal entry with custom date."""
    d = datetime.now() + timedelta(days=date_offset_days)
    total_dr = round(sum(l.get("debit", 0) for l in lines), 2)
    total_cr = round(sum(l.get("credit", 0) for l in lines), 2)
    if total_dr != total_cr:
        raise ValueError(f"Entry {entry_num}: Dr {total_dr} != Cr {total_cr}")
    return {
        "entry_id": f"JV-SEED-{entry_num:04d}",
        "date": d.isoformat(),
        "date_display": d.strftime("%d-%b-%Y").upper(),
        "description": description,
        "ref": ref,
        "source": source,
        "user": "OWNER",
        "lines": [
            {
                "account_code": l["account_code"],
                "account_name": CHART.get(l["account_code"], "Unknown"),
                "debit": round(l.get("debit", 0), 2),
                "credit": round(l.get("credit", 0), 2),
                "narration": l.get("narration", "")
            }
            for l in lines
        ],
        "total_debit": total_dr,
        "total_credit": total_cr
    }


def seed():
    journal = load_journal()

    # Idempotency check
    if any(j.get("entry_id", "").startswith("JV-SEED-") for j in journal):
        print("⚠️  Seed data already present. Skipping.")
        print(f"   To re-seed: delete journal.json and run again (WILL WIPE REAL DATA)")
        return

    new_entries = []

    # 1. Opening entry (day -30)
    new_entries.append(mk_entry(-30, 1, "Opening balances brought forward", [
        {"account_code": "1000", "debit": 500000, "narration": "Opening cash in hand"},
        {"account_code": "1010", "debit": 200000, "narration": "Opening bank balance"},
        {"account_code": "1100", "debit": 360000, "narration": "Opening debtors (RET001+002+003)"},
        {"account_code": "1200", "debit": 400000, "narration": "Opening stock valuation"},
        {"account_code": "2000", "credit": 200000, "narration": "Opening creditors"},
        {"account_code": "3000", "credit": 1260000, "narration": "Capital brought in by owner"},
    ], ref="OPENING-2026"))

    # 2. Purchase from Sun Pharma (day -25)
    new_entries.append(mk_entry(-25, 2, "Credit purchase from Sun Pharma — Paracetamol + Amoxicillin", [
        {"account_code": "5000", "debit": 50000, "narration": "Goods purchased on credit"},
        {"account_code": "2200", "debit": 6000, "narration": "GST input credit @ 12%"},
        {"account_code": "2000", "credit": 56000, "narration": "Payable to Sun Pharma"},
    ], ref="PO-SUN-001"))

    # 3. Purchase from Cipla (day -22)
    new_entries.append(mk_entry(-22, 3, "Credit purchase from Cipla — Azithromycin + Cough Syrup", [
        {"account_code": "5000", "debit": 40000, "narration": "Goods purchased on credit"},
        {"account_code": "2200", "debit": 4800, "narration": "GST input credit @ 12%"},
        {"account_code": "2000", "credit": 44800, "narration": "Payable to Cipla"},
    ], ref="PO-CIPLA-001"))

    # 4. Cash sale (day -20)
    new_entries.append(mk_entry(-20, 4, "Cash sale over counter — walk-in customer", [
        {"account_code": "1000", "debit": 15680, "narration": "Cash received from customer"},
        {"account_code": "4000", "credit": 14000, "narration": "Sales"},
        {"account_code": "2100", "credit": 1680, "narration": "GST output @ 12%"},
    ], ref="CS-2026-001"))

    # 5. Payment from RET001 (day -15)
    new_entries.append(mk_entry(-15, 5, "Payment received from Sri Balaji Medicals via NEFT", [
        {"account_code": "1010", "debit": 50000, "narration": "NEFT credited to bank"},
        {"account_code": "1100", "credit": 50000, "narration": "Dues reduced"},
    ], ref="PAY-RET001-001"))

    # 6. Payment to Sun Pharma (day -12)
    new_entries.append(mk_entry(-12, 6, "Payment made to Sun Pharma via NEFT", [
        {"account_code": "2000", "debit": 56000, "narration": "Creditors reduced"},
        {"account_code": "1010", "credit": 56000, "narration": "NEFT paid"},
    ], ref="PAY-SUN-001"))

    # 7. Salary paid (day -10)
    new_entries.append(mk_entry(-10, 7, "Staff salary paid for the month", [
        {"account_code": "6000", "debit": 25000, "narration": "Salaries to staff"},
        {"account_code": "1000", "credit": 25000, "narration": "Cash paid"},
    ], ref="SAL-2026-09"))

    # 8. Rent paid (day -8)
    new_entries.append(mk_entry(-8, 8, "Warehouse rent paid", [
        {"account_code": "6100", "debit": 15000, "narration": "Monthly warehouse rent"},
        {"account_code": "1010", "credit": 15000, "narration": "Paid by bank"},
    ], ref="RENT-2026-09"))

    # 9. Electricity bill (day -5)
    new_entries.append(mk_entry(-5, 9, "Electricity bill paid — Tamil Nadu EB", [
        {"account_code": "6200", "debit": 3500, "narration": "EB bill"},
        {"account_code": "1000", "credit": 3500, "narration": "Cash paid"},
    ], ref="EB-2026-09"))

    # 10. Sales return from RET001 (day -3)
    new_entries.append(mk_entry(-3, 10, "Sales return from Sri Balaji Medicals — damaged stock", [
        {"account_code": "4100", "debit": 5000, "narration": "Sales return"},
        {"account_code": "2100", "debit": 600, "narration": "GST reversed"},
        {"account_code": "1100", "credit": 5600, "narration": "Debit note issued"},
    ], ref="SR-2026-001"))

    # 11. Purchase return to Cipla (day -2)
    new_entries.append(mk_entry(-2, 11, "Purchase return to Cipla — near-expiry stock", [
        {"account_code": "2000", "debit": 2240, "narration": "Creditors reduced"},
        {"account_code": "5100", "credit": 2000, "narration": "Purchase return"},
        {"account_code": "2200", "credit": 240, "narration": "GST input reversed"},
    ], ref="PR-2026-001"))

    # 12. Telephone & Internet (day -1)
    new_entries.append(mk_entry(-1, 12, "Airtel Business Broadband — monthly bill", [
        {"account_code": "6300", "debit": 1800, "narration": "Internet + phone"},
        {"account_code": "1010", "credit": 1800, "narration": "Paid by bank"},
    ], ref="AIRTEL-2026-09"))

    # 13. Transport & Freight (day -1)
    new_entries.append(mk_entry(-1, 13, "Transport charges paid for delivery van", [
        {"account_code": "6400", "debit": 4200, "narration": "Delivery van diesel"},
        {"account_code": "1000", "credit": 4200, "narration": "Cash paid"},
    ], ref="TRANS-2026-09"))

    # Insert seed entries at the beginning (they're historical)
    journal = new_entries + journal
    save_journal(journal)

    # Log to audit chain
    try:
        from audit_chain import record as audit_record
        audit_record("SYSTEM", "SEED_STARTED", f"Inserted {len(new_entries)} demo journal entries")
    except Exception:
        pass

    print(f"✅ Seeded {len(new_entries)} journal entries")
    print(f"   Date range: 30 days ago → yesterday")
    print(f"   Total journal entries: {len(journal)}")


if __name__ == "__main__":
    seed()
