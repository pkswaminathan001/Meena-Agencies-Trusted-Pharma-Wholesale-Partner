"""Tax Center — GST, TDS, Income Tax filing helpers"""
import os, json
from datetime import datetime, timedelta

JOURNAL_FILE = "journal.json"


def load_journal():
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE) as f: return json.load(f)
    return []


def _in_period(date_iso, from_date, to_date):
    try:
        d = datetime.fromisoformat(date_iso).date()
        return from_date <= d <= to_date
    except:
        return False


def get_gstr1_data(from_date, to_date, retailers):
    """B2B sales invoices for GSTR-1 filing."""
    journal = load_journal()
    invoices = []
    for j in journal:
        if j.get("source") != "AUTO_ORDER":
            continue
        if not _in_period(j["date"], from_date, to_date):
            continue
        # Find retailer GSTIN
        retailer_id = ""
        for r in retailers:
            if r["shop"] in j["description"]:
                retailer_id = r["id"]
                gstin = r.get("gst_number", "URP")  # URP = Unregistered Person
                break
        else:
            gstin = "URP"

        base = sum(l["credit"] for l in j["lines"] if l["account_code"] == "4000")
        gst = sum(l["credit"] for l in j["lines"] if l["account_code"] == "2100")
        total = base + gst

        invoices.append({
            "invoice_no": j["ref"],
            "date": j["date_display"],
            "customer_gstin": gstin,
            "customer_name": j["description"].split("(")[0].replace("Credit sale to ", "").strip(),
            "invoice_value": round(total, 2),
            "taxable_value": round(base, 2),
            "igst": 0,
            "cgst": round(gst / 2, 2),
            "sgst": round(gst / 2, 2),
            "place_of_supply": "33-Tamil Nadu",  # Update per retailer state
            "hsn": "3004",
            "reverse_charge": "N"
        })
    return invoices


def calculate_gstr3b(from_date, to_date):
    """GSTR-3B summary — output tax vs ITC."""
    journal = load_journal()
    output_tax = 0  # GST collected on sales
    itc = 0         # GST paid on purchases

    for j in journal:
        if not _in_period(j["date"], from_date, to_date):
            continue
        for l in j["lines"]:
            # Output tax = credit side of GST Output Payable (2100)
            if l["account_code"] == "2100":
                output_tax += l["credit"] - l["debit"]
            # ITC = debit side of GST Input Credit (2200)
            elif l["account_code"] == "2200":
                itc += l["debit"] - l["credit"]

    net_payable = round(output_tax - itc, 2)
    return {
        "output_tax": round(output_tax, 2),
        "itc": round(itc, 2),
        "net_payable": max(0, net_payable),
        "carry_forward": max(0, -net_payable),
        "period_from": from_date.strftime("%d-%b-%Y").upper(),
        "period_to": to_date.strftime("%d-%b-%Y").upper()
    }


def get_tax_calendar():
    """Upcoming GST & Income Tax due dates."""
    today = datetime.now()
    events = []

    # GST monthly (for turnover > 5 Cr) or QRMP
    for month_offset in [0, 1]:
        d = today.replace(day=1) + timedelta(days=32 * month_offset)
        year, month = d.year, d.month

        # GSTR-1 (11th of next month)
        g1 = datetime(year, month, 1) + timedelta(days=40)
        g1 = g1.replace(day=11)
        events.append({"date": g1, "event": f"GSTR-1 filing ({g1.strftime('%b %Y')})", "type": "GST"})

        # GSTR-3B (20th of next month)
        g3 = datetime(year, month, 1) + timedelta(days=50)
        g3 = g3.replace(day=20)
        events.append({"date": g3, "event": f"GSTR-3B filing + Payment ({g3.strftime('%b %Y')})", "type": "GST"})

    # TDS payment (7th of next month)
    tds = today.replace(day=1) + timedelta(days=40)
    tds = tds.replace(day=7)
    events.append({"date": tds, "event": f"TDS Payment ({tds.strftime('%b %Y')})", "type": "TDS"})

    # Advance Tax (15 Jun, 15 Sep, 15 Dec, 15 Mar)
    for m, d in [(6, 15), (9, 15), (12, 15), (3, 15)]:
        y = today.year if today.month <= m else today.year + 1
        adv = datetime(y, m, d)
        if adv > today:
            events.append({"date": adv, "event": f"Advance Tax Q ({adv.strftime('%d-%b-%Y')})", "type": "IT"})

    # Annual ITR (31 July)
    itr = datetime(today.year, 7, 31)
    if itr < today:
        itr = datetime(today.year + 1, 7, 31)
    events.append({"date": itr, "event": f"Income Tax Return (FY {today.year - 1}-{str(today.year)[2:]})", "type": "IT"})

    events.sort(key=lambda x: x["date"])
    return events[:12]


def get_itc_summary(from_date=None, to_date=None):
    """Input Tax Credit tracker."""
    if not from_date:
        from_date = datetime.now().replace(day=1)
    if not to_date:
        to_date = datetime.now()

    journal = load_journal()
    itc_entries = []
    total_itc = 0
    for j in journal:
        if not _in_period(j["date"], from_date, to_date):
            continue
        for l in j["lines"]:
            if l["account_code"] == "2200" and l["debit"] > 0:
                itc_entries.append({
                    "date": j["date_display"],
                    "ref": j["ref"],
                    "description": j["description"],
                    "amount": l["debit"]
                })
                total_itc += l["debit"]
    return {"entries": itc_entries, "total": round(total_itc, 2)}


def get_tds_summary():
    """TDS liability tracker."""
    journal = load_journal()
    tds_entries = []
    total = 0
    for j in journal:
        if "tds" in j["description"].lower() or "rent" in j["description"].lower():
            for l in j["lines"]:
                if "tds" in l.get("narration", "").lower():
                    tds_entries.append({
                        "date": j["date_display"],
                        "ref": j["ref"],
                        "description": j["description"],
                        "amount": l.get("credit", 0)
                    })
                    total += l.get("credit", 0)
    return {"entries": tds_entries, "total": round(total, 2)}


def generate_gstr1_excel(from_date, to_date, retailers):
    """Return GSTR-1 rows ready for upload to GST portal."""
    return get_gstr1_data(from_date, to_date, retailers)
