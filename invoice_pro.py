"""
invoice_pro.py — GST-compliant wholesale pharma invoice generator.
Outputs HTML (printable to PDF from browser).
"""
import json
from datetime import datetime
from pathlib import Path


# ────────────────────────────────────────────────
# GST RATE MAP (default; can be overridden per item)
# ────────────────────────────────────────────────
# Pharma GST rates:
#   5%  — most medicines, vaccines
#   12% — some formulations, medical devices
#   18% — cosmetics, some devices
GST_RATE_MAP = {
    "default": 5.0,
    "medicine": 5.0,
    "vaccine": 5.0,
    "device": 12.0,
    "cosmetic": 18.0,
}

# HSN codes for pharma (last 4 digits commonly used)
HSN_CODES = {
    "default": "3004",
    "medicine": "3004",     # Medicaments for therapeutic use
    "vaccine": "3002",      # Vaccines
    "syrup": "3004",
    "injection": "3004",
    "inhaler": "3005",      # Wadding, bandages
    "device": "9018",       # Medical devices
}


def load_company():
    """Load company.json. Return dict."""
    p = Path("company.json")
    if not p.exists():
        return {
            "name": "Your Company",
            "gstin": "GSTIN-PENDING",
            "pan": "PAN-PENDING",
            "state": "Tamil Nadu",
            "state_code": "33",
            "terms": ["Standard terms apply."],
        }
    return json.loads(p.read_text())


def next_invoice_number(existing_orders: list) -> str:
    """Generate next invoice number based on order count."""
    company = load_company()
    prefix = company.get("invoice_prefix", "INV")
    year = datetime.now().strftime("%y")
    count = len(existing_orders) + 1
    return f"{prefix}/{year}/{count:04d}"


def gst_rate_for(medicine_name: str) -> float:
    """Return GST rate for a medicine based on its name."""
    n = medicine_name.lower()
    if "vaccine" in n:
        return 5.0
    if "device" in n or "monitor" in n or "glucometer" in n:
        return 12.0
    return 5.0  # default for medicines


def hsn_for(medicine_name: str) -> str:
    n = medicine_name.lower()
    if "vaccine" in n:
        return "3002"
    if "inhaler" in n:
        return "3005"
    if "device" in n:
        return "9018"
    return "3004"


def compute_taxes(order: dict, retailer: dict, company: dict) -> dict:
    """
    Compute GST split (CGST/SGST vs IGST) based on inter/intra state.
    Returns dict with line items, subtotal, tax breakdown, total.
    """
    company_state_code = company.get("state_code", "33")
    retailer_state_code = (retailer or {}).get("state_code", company_state_code)

    is_intra_state = (company_state_code == retailer_state_code)

    line_items = []
    subtotal = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_igst = 0.0

    for item in order.get("items", []):
        name = item.get("medicine", "")
        qty = item.get("qty", 0)
        price = item.get("price", 0)
        amount = qty * price
        rate = gst_rate_for(name)
        tax_amount = amount * rate / 100.0

        if is_intra_state:
            cgst = tax_amount / 2
            sgst = tax_amount / 2
            igst = 0.0
        else:
            cgst = 0.0
            sgst = 0.0
            igst = tax_amount

        line_items.append({
            "name": name,
            "hsn": hsn_for(name),
            "qty": qty,
            "price": price,
            "rate": rate,
            "amount": amount,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
        })

        subtotal += amount
        total_cgst += cgst
        total_sgst += sgst
        total_igst += igst

    total_tax = total_cgst + total_sgst + total_igst
    grand_total = subtotal + total_tax

    return {
        "line_items": line_items,
        "subtotal": subtotal,
        "total_cgst": total_cgst,
        "total_sgst": total_sgst,
        "total_igst": total_igst,
        "total_tax": total_tax,
        "grand_total": grand_total,
        "is_intra_state": is_intra_state,
    }


def number_to_words(n: float) -> str:
    """Convert number to Indian words. Simple implementation."""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def two_digits(x):
        if x < 20:
            return ones[x]
        return tens[x // 10] + (" " + ones[x % 10] if x % 10 else "")

    rupees = int(n)
    paise = int(round((n - rupees) * 100))

    if rupees == 0:
        words = "Zero"
    else:
        parts = []
        # Crores
        cr = rupees // 10000000
        rupees %= 10000000
        # Lakhs
        lk = rupees // 100000
        rupees %= 100000
        # Thousands
        th = rupees // 1000
        rupees %= 1000
        # Hundreds
        hu = rupees // 100
        rupees %= 100
        # Last two
        last = rupees

        if cr:
            parts.append(two_digits(cr) + " Crore")
        if lk:
            parts.append(two_digits(lk) + " Lakh")
        if th:
            parts.append(two_digits(th) + " Thousand")
        if hu:
            parts.append(ones[hu] + " Hundred")
        if last:
            parts.append(two_digits(last))
        words = " ".join(parts)

    result = f"Rupees {words} Only"
    if paise:
        result = f"Rupees {words} and {two_digits(paise)} Paise Only"
    return result


def build_invoice_html(order: dict, retailer: dict, existing_orders: list = None) -> str:
    """Return full HTML for the invoice — professional GST-compliant layout."""
    company = load_company()
    taxes = compute_taxes(order, retailer, company)
    invoice_no = next_invoice_number(existing_orders or [])

    c = company
    r = retailer or {}
    t = taxes

    # ─── Embed logo as base64 (self-contained HTML) ───
    _logo_data_uri = ""
    try:
        from pathlib import Path as _PL
        import base64 as _b64
        if _PL("logo.png").exists():
            _logo_bytes = _PL("logo.png").read_bytes()
            _logo_b64 = _b64.b64encode(_logo_bytes).decode()
            _logo_data_uri = f"data:image/png;base64,{_logo_b64}"
    except Exception:
        pass

    # ─── Line items ───
    items_html = ""
    for i, li in enumerate(t["line_items"], 1):
        items_html += f"""
        <tr>
            <td class="num">{i}</td>
            <td>
                <div class="med-name">{li['name']}</div>
                <div class="med-meta">HSN: {li['hsn']} · GST: {li['rate']}%</div>
            </td>
            <td class="num">{li['qty']}</td>
            <td class="num">₹{li['price']:,.2f}</td>
            <td class="num">₹{li['cgst'] + li['sgst'] + li['igst']:,.2f}</td>
            <td class="num total">₹{li['amount']:,.2f}</td>
        </tr>"""

    # Pad to min 6 rows
    padding = max(0, 6 - len(t["line_items"]))
    for _ in range(padding):
        items_html += '<tr class="empty"><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td></tr>'

    # ─── Tax rows ───
    if t["is_intra_state"]:
        tax_rows = f"""
        <tr><td class="lbl">CGST</td><td class="amt">₹{t['total_cgst']:,.2f}</td></tr>
        <tr><td class="lbl">SGST</td><td class="amt">₹{t['total_sgst']:,.2f}</td></tr>"""
    else:
        tax_rows = f"""
        <tr><td class="lbl">IGST</td><td class="amt">₹{t['total_igst']:,.2f}</td></tr>"""

    # ─── Terms ───
    _days = r.get("payment_days", c.get("default_payment_days", 15))
    _mode = r.get("preferred_mode", "cash")
    _mode_display = {"cash": "Cash", "cheque": "Cheque", "upi": "UPI",
                     "neft": "NEFT", "rtgs": "RTGS", "card": "Card"}.get(_mode, _mode.title())
    _terms_list = list(c.get("terms", [])) + [
        f"Payment due within {_days} days from invoice date.",
        f"Preferred payment mode: {_mode_display}.",
    ]
    terms_html = "".join(f"<li>{x}</li>" for x in _terms_list)

    # ─── Retailer data with fallbacks ───
    _ret_address = r.get("address") or "Address on file"
    _ret_gstin = r.get("gstin", "—") or "—"
    _ret_state = r.get("state") or c.get("state", "Tamil Nadu")
    _ship_to = order.get("location") or _ret_address
    _outstanding = r.get("outstanding", 0)
    _credit_limit = r.get("credit_limit", 0)

    # ─── Bank details ───
    _bank = c.get("bank", {})

    def _safe(v):
        return v if v and "ENTER_" not in str(v) else "—"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Invoice {invoice_no} — {c.get('name','Meena Agencies')}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter','Segoe UI',Arial,sans-serif; background: #f5f6fa; padding: 30px 20px; color: #1a1a2e; }}
  .invoice {{ max-width: 900px; margin: 0 auto; background: #fff; box-shadow: 0 4px 24px rgba(0,0,0,0.08); border-radius: 8px; overflow: hidden; }}

  .header {{ background: linear-gradient(135deg, #0a1535 0%, #1a2851 100%); color: #fff; padding: 30px 40px; display: flex; justify-content: space-between; align-items: flex-start; position: relative; }}
  .header::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #00d4ff, #7b61ff); }}
  .brand {{ display: flex; align-items: center; gap: 16px; }}
  .brand-icon {{ width: 56px; height: 56px; border-radius: 12px; overflow: hidden; background: linear-gradient(135deg, #00d4ff, #7b61ff); display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 900; font-size: 26px; }}
  .brand-icon img {{ width: 56px; height: 56px; object-fit: cover; }}
  .brand-name {{ font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }}
  .brand-tagline {{ font-size: 11px; color: #a8b2d1; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px; }}
  .invoice-title h1 {{ font-size: 30px; font-weight: 900; letter-spacing: -1px; color: #00d4ff; }}
  .invoice-title .meta {{ color: #a8b2d1; font-size: 12px; margin-top: 6px; line-height: 1.6; }}
  .invoice-title .meta strong {{ color: #fff; }}

  .info-strip {{ background: #f8f9fc; padding: 20px 40px; display: flex; justify-content: space-between; border-bottom: 1px solid #e8ecf3; font-size: 12px; color: #4a5568; }}
  .info-strip .col {{ line-height: 1.7; }}
  .info-strip .col strong {{ color: #1a1a2e; font-weight: 700; }}

  .addresses {{ display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid #e8ecf3; }}
  .address-block {{ padding: 24px 40px; }}
  .address-block:first-child {{ border-right: 1px solid #e8ecf3; }}
  .address-block h3 {{ font-size: 11px; color: #7b61ff; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; font-weight: 700; }}
  .address-block .name {{ font-size: 16px; font-weight: 700; color: #1a1a2e; margin-bottom: 6px; }}
  .address-block .line {{ font-size: 12px; color: #4a5568; line-height: 1.7; }}

  table.items {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  table.items thead th {{ background: #0a1535; color: #fff; padding: 14px 20px; text-align: left; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; font-weight: 700; }}
  table.items thead th.num {{ text-align: right; }}
  table.items tbody td {{ padding: 14px 20px; border-bottom: 1px solid #f0f2f8; vertical-align: top; }}
  table.items tbody tr:nth-child(even) {{ background: #fafbfd; }}
  table.items tbody td.num {{ text-align: right; font-weight: 600; }}
  table.items tbody td.total {{ color: #1a3a7c; font-weight: 700; }}
  table.items tr.empty td {{ padding: 14px 20px; height: 36px; }}
  .med-name {{ font-weight: 600; color: #1a1a2e; margin-bottom: 3px; }}
  .med-meta {{ font-size: 11px; color: #8892b0; }}

  .bottom {{ display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid #e8ecf3; }}
  .bottom-left {{ padding: 24px 40px; border-right: 1px solid #e8ecf3; }}
  .bottom-right {{ padding: 24px 40px; }}
  .section-label {{ font-size: 10px; color: #7b61ff; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }}
  .bank-row {{ display: flex; justify-content: space-between; font-size: 12px; padding: 5px 0; }}
  .bank-row .lbl {{ color: #8892b0; }}
  .bank-row .val {{ font-weight: 600; color: #1a1a2e; text-align: right; }}
  .totals-table {{ width: 100%; font-size: 13px; }}
  .totals-table td {{ padding: 8px 0; }}
  .totals-table td.lbl {{ color: #4a5568; }}
  .totals-table td.amt {{ text-align: right; font-weight: 600; color: #1a1a2e; }}
  .totals-table tr.grand td {{ padding: 14px 0 8px 0; border-top: 2px solid #0a1535; font-size: 18px; font-weight: 900; color: #1a3a7c; }}
  .totals-table tr.grand td.amt {{ color: #1a3a7c; }}

  .words {{ background: #f8f9fc; padding: 14px 40px; font-size: 12px; color: #4a5568; border-top: 1px solid #e8ecf3; font-style: italic; }}
  .words strong {{ color: #1a1a2e; font-style: normal; }}

  .terms {{ padding: 24px 40px; border-top: 1px solid #e8ecf3; background: #fafbfd; }}
  .terms h4 {{ font-size: 11px; color: #7b61ff; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; font-weight: 700; }}
  .terms ol {{ padding-left: 20px; font-size: 12px; color: #4a5568; line-height: 1.8; }}

  .signatures {{ display: flex; justify-content: space-between; padding: 40px; gap: 40px; }}
  .sig-block {{ flex: 1; text-align: center; }}
  .sig-line {{ border-top: 1px solid #999; padding-top: 8px; margin-top: 60px; font-size: 12px; color: #4a5568; }}

  .footer-bar {{ background: #0a1535; color: #a8b2d1; padding: 16px 40px; text-align: center; font-size: 11px; letter-spacing: 0.5px; }}
  .footer-bar strong {{ color: #00d4ff; }}

  @media print {{ body {{ background: #fff; padding: 0; }} .invoice {{ box-shadow: none; border-radius: 0; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
<div class="invoice">

  <div class="header">
    <div class="brand">
      <div class="brand-icon">{("<img src='" + _logo_data_uri + "' style='width:56px;height:56px;object-fit:cover;border-radius:12px;' />") if _logo_data_uri else "M"}</div>
      <div>
        <div class="brand-name">{c.get('name', 'Meena Agencies')}</div>
        <div class="brand-tagline">{c.get('tagline', 'Trusted Pharma Wholesale Partner')}</div>
      </div>
    </div>
    <div class="invoice-title">
      <h1>TAX INVOICE</h1>
      <div class="meta">
        <strong>Invoice No:</strong> {invoice_no}<br>
        <strong>Date:</strong> {datetime.now().strftime('%d %B %Y')}<br>
        <strong>Order ID:</strong> {order.get('order_id', '')}
      </div>
    </div>
  </div>

  <div class="info-strip">
    <div class="col">
      <strong>GSTIN:</strong> {c.get('gstin', '—')}<br>
      <strong>PAN:</strong> {c.get('pan', '—')}<br>
      <strong>State:</strong> {c.get('state', '')} ({c.get('state_code', '')})
    </div>
    <div class="col" style="text-align: right;">
      <strong>Phone:</strong> {c.get('phone', '')}<br>
      <strong>Email:</strong> {c.get('email', '')}<br>
      <strong>Place of Supply:</strong> {_ret_state}
    </div>
  </div>

  <div class="addresses">
    <div class="address-block">
      <h3>Bill To</h3>
      <div class="name">{r.get('owner', '')}</div>
      <div class="line">
        {r.get('shop', '')}<br>
        {_ret_address}<br>
        Phone: {r.get('phone', '—')}<br>
        GSTIN: {_ret_gstin}<br>
        State: {_ret_state}
      </div>
    </div>
    <div class="address-block">
      <h3>Ship To</h3>
      <div class="name">{r.get('shop', '')}</div>
      <div class="line">
        {_ship_to}<br>
        Phone: {r.get('phone', '—')}<br>
        &nbsp;<br>&nbsp;<br>&nbsp;
      </div>
    </div>
  </div>

  <table class="items">
    <thead>
      <tr>
        <th style="width: 6%;" class="num">#</th>
        <th style="width: 42%;">Item Description</th>
        <th style="width: 10%;" class="num">Qty</th>
        <th style="width: 14%;" class="num">Rate</th>
        <th style="width: 14%;" class="num">Tax</th>
        <th style="width: 14%;" class="num">Amount</th>
      </tr>
    </thead>
    <tbody>{items_html}</tbody>
  </table>

  <div class="bottom">
    <div class="bottom-left">
      <div class="section-label">Bank Details</div>
      <div class="bank-row"><span class="lbl">Account Holder</span><span class="val">{_safe(_bank.get('account_holder'))}</span></div>
      <div class="bank-row"><span class="lbl">Account No.</span><span class="val">{_safe(_bank.get('account_number'))}</span></div>
      <div class="bank-row"><span class="lbl">Bank</span><span class="val">{_safe(_bank.get('bank_name'))}</span></div>
      <div class="bank-row"><span class="lbl">Branch</span><span class="val">{_safe(_bank.get('branch'))}</span></div>
      <div class="bank-row"><span class="lbl">IFSC</span><span class="val">{_safe(_bank.get('ifsc'))}</span></div>
      <div class="bank-row"><span class="lbl">UPI</span><span class="val">{_safe(_bank.get('upi'))}</span></div>
    </div>
    <div class="bottom-right">
      <div class="section-label">Payment Summary</div>
      <table class="totals-table">
        <tr><td class="lbl">Sub Total</td><td class="amt">₹{t['subtotal']:,.2f}</td></tr>
        {tax_rows}
        <tr class="grand"><td class="lbl">Grand Total</td><td class="amt">₹{t['grand_total']:,.2f}</td></tr>
      </table>
      <div style="margin-top: 14px; padding-top: 12px; border-top: 1px dashed #d0d5e0; font-size: 11px; color: #8892b0;">
        <div style="display: flex; justify-content: space-between; padding: 3px 0;">
          <span>Outstanding Balance</span><span style="font-weight: 600; color: #ff4d6d;">₹{_outstanding:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 3px 0;">
          <span>Credit Limit</span><span style="font-weight: 600; color: #1a1a2e;">₹{_credit_limit:,.2f}</span>
        </div>
      </div>
    </div>
  </div>

  <div class="words"><strong>Amount in Words:</strong> {number_to_words(t['grand_total'])}</div>

  <div class="terms">
    <h4>Terms &amp; Conditions</h4>
    <ol>{terms_html}</ol>
  </div>

  <div class="signatures">
    <div class="sig-block"><div class="sig-line">Customer Signature</div></div>
    <div class="sig-block">
      <div class="sig-line">
        <div style="font-weight: 700; color: #1a1a2e; margin-bottom: 4px;">For {c.get('name', 'Meena Agencies')}</div>
        Authorised Signatory
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <strong>{c.get('name', 'Meena Agencies')}</strong> ·
    {c.get('address_line1', '')} · {c.get('address_line2', '')} ·
    Phone: {c.get('phone', '')} ·
    This is a computer-generated invoice.
  </div>
</div>

<div class="no-print" style="max-width: 900px; margin: 24px auto; text-align: center;">
  <button onclick="window.print()" style="padding: 12px 32px; background: linear-gradient(135deg, #00d4ff, #7b61ff); color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 14px;">
    🖨️ Print / Save as PDF
  </button>
</div>

</body>
</html>"""
    return html
