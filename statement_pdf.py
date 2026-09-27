"""statement_pdf.py — Clean rebuild. Grayscale watermark, correct widths."""
import io, hashlib, uuid
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY

try:
    from PIL import Image as PILImage, ImageDraw as PILImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

NAVY       = colors.HexColor("#0a1535")
BLUE       = colors.HexColor("#1a3a7c")
CYAN       = colors.HexColor("#0088cc")
PURPLE     = colors.HexColor("#6b4dff")
LIGHT_GREY = colors.HexColor("#f8f9fc")
MID_GREY   = colors.HexColor("#e8ecf3")
BORDER     = colors.HexColor("#d0d5e0")
TEXT_DARK  = colors.HexColor("#1a1a2e")
TEXT_MID   = colors.HexColor("#4a5568")
TEXT_LIGHT = colors.HexColor("#8892b0")
GREEN      = colors.HexColor("#00a855")
RED        = colors.HexColor("#e63946")

PAGE = A4
MARGIN = 6 * mm
PAGE_W = PAGE[0]
AVAIL_W = PAGE_W - 2*MARGIN


def _full_hash(rid, total, count, ts_iso):
    return hashlib.sha256(f"{rid}|{total}|{count}|{ts_iso}".encode()).hexdigest().upper()


def _fmt(v):
    try: return f"{float(v):,.2f}"
    except: return "0.00"


def _num_to_words(n):
    ones = ["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten",
            "Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen",
            "Eighteen","Nineteen"]
    tens = ["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]
    def two(x):
        if x < 20: return ones[x]
        return tens[x//10] + (" " + ones[x%10] if x%10 else "")
    try: n = float(n)
    except: return "Zero Rupees Only"
    rupees = int(n); paise = int(round((n-rupees)*100))
    if rupees == 0: w = "Zero"
    else:
        parts = []
        cr = rupees//10000000; rupees %= 10000000
        lk = rupees//100000; rupees %= 100000
        th = rupees//1000; rupees %= 1000
        hu = rupees//100; rupees %= 100
        last = rupees
        if cr: parts.append(two(cr)+" Crore")
        if lk: parts.append(two(lk)+" Lakh")
        if th: parts.append(two(th)+" Thousand")
        if hu: parts.append(ones[hu]+" Hundred")
        if last: parts.append(two(last))
        w = " ".join(parts)
    return f"Rs. {w}" + (f" and {two(paise)} Ps" if paise else "") + " Only"


def _load_logo(size_mm=12):
    if not HAS_PIL: return None
    for name in ["logo.png","logo.PNG","Logo.png","logo.jpg","logo.jpeg"]:
        if Path(name).exists():
            try:
                img = PILImage.open(name).convert("RGBA")
                w, h = img.size; s = min(w, h)
                img = img.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s))
                img = img.resize((240, 240), PILImage.LANCZOS)
                mask = PILImage.new("L", (240, 240), 0)
                PILImageDraw.Draw(mask).ellipse((0, 0, 240, 240), fill=255)
                img.putalpha(mask)
                buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
                return RLImage(buf, width=size_mm*mm, height=size_mm*mm)
            except Exception: continue
    return None


def _make_watermark_bytes(opacity=0.12):
    """Grayscale watermark. Pink/purple bg removed via numpy."""
    if not HAS_PIL: return None
    for name in ["logo.png","logo.PNG","Logo.png","logo.jpg","logo.jpeg"]:
        if Path(name).exists():
            try:
                img = PILImage.open(name).convert("RGBA")
                img = img.resize((400, 400), PILImage.LANCZOS)
                if HAS_NUMPY:
                    arr = np.array(img).astype(np.int32)
                    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
                    # Remove pink: high R, high B, mid G
                    pink = (r > 180) & (b > 180) & (g > 90) & (g < 230)
                    # Remove purple: R mid-high, B very high, G low
                    purple = (r > 130) & (b > 180) & (g < 130)
                    arr[:,:,3] = np.where(pink | purple, 0, a)
                    # Grayscale
                    gray = (0.299*r + 0.587*g + 0.114*b).astype(np.uint8)
                    arr[:,:,0] = gray
                    arr[:,:,1] = gray
                    arr[:,:,2] = gray
                    arr[:,:,3] = (arr[:,:,3] * opacity).astype(np.uint8)
                    img = PILImage.fromarray(arr.astype("uint8"), "RGBA")
                else:
                    r, g, b, a = img.split()
                    a = a.point(lambda x: int(x * opacity))
                    img = PILImage.merge("RGBA", (r, g, b, a))
                buf = io.BytesIO()
                try:
                    img.save(buf, format="PNG", optimize=False)
                except AttributeError:
                    # Fallback: save without optimization
                    img.save(buf, format="PNG")
                return buf.getvalue()
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                continue
    return None


def generate_statement_pdf(retailer, orders, company=None):
    c = company or {}
    defaults = {
        "name":"Meena Agencies","legal_name":"Meena Agencies",
        "tagline":"Trusted Pharma Wholesale Partner",
        "address1":"2661, South Main Street, near Indian Bank",
        "address2":"Rajakrishnapuram, Thanjavur, Tamilnadu — 613009",
        "phone":"6382130536","email":"meena.agencies@gmail.com",
        "gstin":"33AAIFM8119N1ZW","pan":"AAIFM8119N",
        "drug_license_20b":"—","drug_license_21b":"—",
        "authorized_signatory":"Authorised Signatory","jurisdiction":"Thanjavur",
        "payment_days":15,
    }
    merged = {k: c.get(k, v) for k, v in defaults.items()}
    merged["address1"] = c.get("address1") or c.get("address_line1", defaults["address1"])
    merged["address2"] = c.get("address2") or c.get("address_line2", defaults["address2"])
    # Sanitize license numbers
    for k in ["drug_license_20b","drug_license_21b"]:
        v = merged.get(k, "")
        if not v or "EDIT_" in str(v) or "—" in str(v):
            merged[k] = "—"
    c = merged

    my_orders = [o for o in orders if o.get("status") != "Awaiting OTP"]
    my_orders.sort(key=lambda o: o.get("placed_at",""))
    approved = [o for o in my_orders if o.get("status") == "Approved"]
    total_approved = sum(o.get("total",0) for o in approved)
    payments = retailer.get("payment_history", [])
    total_paid = sum(p.get("amount",0) for p in payments)
    outstanding = retailer.get("outstanding", 0)
    credit_limit = retailer.get("credit_limit", 0)
    available = max(0, credit_limit - outstanding)

    ts = datetime.now()
    ts_iso = ts.strftime("%Y-%m-%dT%H:%M:%S")
    ts_display = ts.strftime("%d %b %Y · %H:%M").upper()
    doc_uid = uuid.uuid4().hex[:10].upper()
    doc_hash = _full_hash(retailer.get("id","?"), total_approved, len(my_orders), ts_iso)
    verify_code = doc_hash[:12]
    stmt_number = f"STM/{ts.strftime('%y%m')}/{retailer.get('id','X')[-3:]}{len(my_orders):03d}"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAGE,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=11*mm,
        title=f"Statement {stmt_number}",
        author=c["legal_name"],
    )

    # Styles
    s_h1       = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13, textColor=NAVY, leading=15)
    s_body     = ParagraphStyle("body", fontName="Helvetica", fontSize=7, textColor=TEXT_MID, leading=8.5)
    s_sm       = ParagraphStyle("sm", fontName="Helvetica", fontSize=6, textColor=TEXT_LIGHT, leading=7.5)
    s_xs       = ParagraphStyle("xs", fontName="Helvetica", fontSize=5.5, textColor=TEXT_LIGHT, leading=7)
    s_sec      = ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=7.5, textColor=NAVY, leading=9)
    s_right    = ParagraphStyle("right", fontName="Helvetica-Bold", fontSize=7, textColor=TEXT_DARK, alignment=TA_RIGHT, leading=8.5)
    s_right_sm = ParagraphStyle("right_sm", fontName="Helvetica", fontSize=6, textColor=TEXT_MID, alignment=TA_RIGHT, leading=7.5)
    s_center   = ParagraphStyle("center", fontName="Helvetica", fontSize=6, textColor=TEXT_MID, alignment=TA_CENTER, leading=7.5)
    s_center_b = ParagraphStyle("center_b", fontName="Helvetica-Bold", fontSize=6.5, textColor=TEXT_DARK, alignment=TA_CENTER, leading=8)
    s_justify  = ParagraphStyle("justify", fontName="Helvetica", fontSize=5.5, textColor=TEXT_MID, alignment=TA_JUSTIFY, leading=7)

    story = []

    # ═══════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════
    logo = _load_logo(12)
    logo_cell = logo if logo else Paragraph("<b>M</b>",
        ParagraphStyle("m", fontName="Helvetica-Bold", fontSize=18, textColor=CYAN, alignment=TA_CENTER))

    company_block = (
        f"<b><font size='11'>{c['legal_name']}</font></b><br/>"
        f"<font size='5.5' color='#8892b0'>{c['tagline'].upper()}</font><br/>"
        f"<font size='6'>GSTIN: {c['gstin']} | PAN: {c['pan']} | "
        f"DL 20B: {c['drug_license_20b']} | DL 21B: {c['drug_license_21b']}</font><br/>"
        f"<font size='6'>{c['address1']}, {c['address2']}</font><br/>"
        f"<font size='6'>Ph: {c['phone']} | {c['email']}</font>"
    )
    meta_block = (
        f"<font size='5.5'><b>Statement No:</b><br/>"
        f"<font face='Courier-Bold' size='6.5'>{stmt_number}</font><br/>"
        f"<b>Issued:</b> {ts_display}<br/>"
        f"<b>UID:</b> {doc_uid}</font>"
    )

    hdr_tbl = Table(
        [[logo_cell, Paragraph(company_block, s_body), Paragraph(meta_block, s_right_sm)]],
        colWidths=[14*mm, AVAIL_W - 14*mm - 32*mm, 32*mm],
    )
    hdr_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=1.2, color=CYAN, spaceAfter=1, spaceBefore=1))

    # ═══════════════════════════════════════════════════════════
    # PARTY DETAILS
    # ═══════════════════════════════════════════════════════════
    seller_block = (
        f"<b>SELLER</b><br/>"
        f"{c['legal_name']}<br/>"
        f"{c['address1'][:40]}, {c['address2'][:30]}<br/>"
        f"GSTIN: {c['gstin']}"
    )
    buyer_block = (
        f"<b>BILL TO</b><br/>"
        f"<b>{retailer.get('shop','—')}</b> — {retailer.get('owner','')}<br/>"
        f"{retailer.get('address','Chennai')[:40]}, {retailer.get('state','TN')} — {retailer.get('pincode','—')}<br/>"
        f"ID: {retailer.get('id','—')} | Ph: {retailer.get('phone','—')} | GSTIN: {retailer.get('gstin','URP')}"
    )
    title_block = (
        f"<font size='9'><b>ACCOUNT STATEMENT</b></font><br/>"
        f"<font size='6'>&amp; TAX INVOICE RECORD</font><br/>"
        f"<font size='5.5' color='#8892b0'>Per CGST Rule 46 &amp;<br/>S.65B Evidence Act</font>"
    )

    row2_tbl = Table(
        [[Paragraph(title_block, s_body), Paragraph(seller_block, s_body), Paragraph(buyer_block, s_body)]],
        colWidths=[35*mm, (AVAIL_W-35*mm)/2, (AVAIL_W-35*mm)/2],
    )
    row2_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
        ("BOX", (0,0), (-1,-1), 0.4, CYAN),
        ("LINEAFTER", (0,0), (0,0), 0.3, BORDER),
        ("LINEAFTER", (1,0), (1,0), 0.3, BORDER),
    ]))
    story.append(row2_tbl)
    story.append(Spacer(1, 3))

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════
    sum_data = [
        [Paragraph("<font color='white' size='5.5'><b>CREDIT LIMIT</b></font>", s_center),
         Paragraph("<font color='white' size='5.5'><b>TOTAL BILLED</b></font>", s_center),
         Paragraph("<font color='white' size='5.5'><b>TOTAL PAID</b></font>", s_center),
         Paragraph("<font color='white' size='5.5'><b>OUTSTANDING</b></font>", s_center),
         Paragraph("<font color='white' size='5.5'><b>AVAILABLE</b></font>", s_center)],
        [Paragraph(f"<b>{_fmt(credit_limit)}</b>", s_center_b),
         Paragraph(f"<b>{_fmt(total_approved)}</b>", s_center_b),
         Paragraph(f"<b>{_fmt(total_paid)}</b>", s_center_b),
         Paragraph(f"<b><font color='#e63946'>{_fmt(outstanding)}</font></b>", s_center_b),
         Paragraph(f"<b><font color='#00a855'>{_fmt(available)}</font></b>", s_center_b)],
    ]
    sum_tbl = Table(sum_data, colWidths=[AVAIL_W/5]*5)
    sum_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("BACKGROUND", (0,1), (-1,1), LIGHT_GREY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 2), ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("BOX", (0,0), (-1,-1), 0.4, CYAN),
        ("LINEAFTER", (0,0), (-2,-1), 0.25, BORDER),
    ]))
    story.append(sum_tbl)
    story.append(Paragraph(f"<font size='5.5'><b>In words:</b> <i>{_num_to_words(total_approved)}</i></font>", s_sm))
    story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════
    # ITEMS TABLE — ALL WIDTHS IN POINTS
    # ═══════════════════════════════════════════════════════════
    story.append(Paragraph("<b>BILL-WISE ITEMS</b>", s_sec))
    story.append(Spacer(1, 2))

    billed = [o for o in my_orders if o.get("status") in ("Approved","Pending")]
    MAX_ORDERS = 8
    shown = billed[:MAX_ORDERS]
    hidden = len(billed) - len(shown)

    # Column widths — ALL IN POINTS
    col_w = [
        6*mm,      # #
        22*mm,     # ORDER
        AVAIL_W - 6*mm - 22*mm - 16*mm - 13*mm - 9*mm - 17*mm - 19*mm - 16*mm,  # ITEM (points)
        16*mm,     # BATCH
        13*mm,     # EXP
        9*mm,      # QTY
        17*mm,     # RATE
        19*mm,     # AMT
        16*mm,     # STATUS
    ]
    # Safety: ensure ITEM width is positive
    if col_w[2] < 20:
        col_w[2] = 20

    header = [[
        Paragraph("<b>#</b>", s_center),
        Paragraph("<b>ORDER</b>", s_center),
        Paragraph("<b>ITEM</b>", s_center),
        Paragraph("<b>BATCH</b>", s_center),
        Paragraph("<b>EXP</b>", s_center),
        Paragraph("<b>QTY</b>", s_center),
        Paragraph("<b>RATE</b>", s_center),
        Paragraph("<b>AMT</b>", s_center),
        Paragraph("<b>STATUS</b>", s_center),
    ]]
    body_rows = []
    counter = 0
    if not shown:
        body_rows.append([Paragraph("—", s_center)] + [Paragraph("", s_center)]*8)
    else:
        for o in shown:
            short_id = (o.get("order_id","") or "")[-12:]
            status = o.get("status","")
            color = GREEN if status == "Approved" else RED if status == "Cancelled" else colors.HexColor("#e68900")
            for it in o.get("items", []):
                counter += 1
                amt = it.get("qty",0) * it.get("price",0)
                body_rows.append([
                    Paragraph(str(counter), s_center),
                    Paragraph(short_id, s_sm),
                    Paragraph((it.get("medicine","—") or "")[:30], s_sm),
                    Paragraph((it.get("batch","—") or "")[:8], s_center),
                    Paragraph((it.get("expiry","—") or "")[:8], s_center),
                    Paragraph(str(it.get("qty",0)), s_center),
                    Paragraph(_fmt(it.get("price",0)), s_right_sm),
                    Paragraph(f"<b>{_fmt(amt)}</b>", s_right_sm),
                    Paragraph(f"<font color='{color.hexval()}' size='5'>{status[:10]}</font>", s_center),
                ])

    items_tbl = Table(header + body_rows, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 6),
        ("FONTSIZE", (0,1), (-1,-1), 6.5),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GREY]),
        ("LINEBELOW", (0,0), (-1,-1), 0.15, MID_GREY),
        ("BOX", (0,0), (-1,-1), 0.4, CYAN),
    ]))
    story.append(items_tbl)
    if hidden > 0:
        story.append(Paragraph(f"<font size='5.5'><i>… {hidden} more order(s) not shown</i></font>", s_xs))
    story.append(Spacer(1, 5))

    # ═══════════════════════════════════════════════════════════
    # LEGAL + FINGERPRINT
    # ═══════════════════════════════════════════════════════════
    legal_text = (
        f"1. Computer-generated doc. 2. Jurisdiction: {c.get('jurisdiction','Thanjavur')}. "
        f"3. E.&O.E. 4. Payment due within {c.get('payment_days',15)} days. "
        f"<b>S.65B Cert (Evidence Act 1872):</b> Certified computer printout of records "
        f"maintained by {c['legal_name']} (GSTIN: {c['gstin']}) in regular business course. "
        f"Retain 8 yrs per GST Rule 56(17)."
    )
    fingerprint = (
        f"<b>FINGERPRINT</b><br/>"
        f"UID: <font face='Courier'>{doc_uid}</font><br/>"
        f"Hash: <font face='Courier' size='5'>{doc_hash[:20]}…</font><br/>"
        f"Verify: <font face='Courier-Bold'>{verify_code}</font>"
    )
    signature = (
        f"<br/><br/>"
        f"<b>FOR {c['legal_name'].upper()}</b><br/>"
        f"<font size='5.5' color='#8892b0'>{c.get('authorized_signatory','Authorised Signatory')}<br/>"
        f"<i>Computer-generated. No physical signature needed.</i></font>"
    )

    bottom_tbl = Table(
        [[Paragraph(legal_text, s_justify),
          Paragraph(fingerprint, s_body),
          Paragraph(signature, s_center)]],
        colWidths=[AVAIL_W - 70*mm, 40*mm, 30*mm],
    )
    bottom_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
        ("BOX", (0,0), (-1,-1), 0.4, PURPLE),
        ("LINEAFTER", (0,0), (0,0), 0.3, BORDER),
        ("LINEAFTER", (1,0), (1,0), 0.3, BORDER),
    ]))
    story.append(bottom_tbl)
    story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════
    # CONTACT + THANK YOU (fills bottom)
    # ═══════════════════════════════════════════════════════════
    story.append(Paragraph("<b>CONTACT &amp; SUPPORT</b>", s_sec))
    story.append(Spacer(1, 1))

    contact_data = [
        [Paragraph("<b>Phone</b>", s_sm), Paragraph(c['phone'], s_body),
         Paragraph("<b>Email</b>", s_sm), Paragraph(c['email'], s_body)],
        [Paragraph("<b>Address</b>", s_sm),
         Paragraph(f"{c['address1']}, {c['address2']}", s_body),
         Paragraph("<b>Jurisdiction</b>", s_sm),
         Paragraph(c.get("jurisdiction","Thanjavur"), s_body)],
    ]
    contact_tbl = Table(contact_data, colWidths=[15*mm, AVAIL_W/2 - 15*mm, 20*mm, AVAIL_W/2 - 20*mm])
    contact_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
        ("BOX", (0,0), (-1,-1), 0.4, CYAN),
        ("LINEAFTER", (1,0), (1,-1), 0.25, BORDER),
        ("LINEBELOW", (0,0), (-1,-2), 0.15, BORDER),
    ]))
    story.append(contact_tbl)
    story.append(Spacer(1, 3))

    story.append(Paragraph(
        f"<i><b>Thank you for your business.</b> Quote Statement No. <b>{stmt_number}</b> for any query.</i>",
        s_justify
    ))

    # ─── Watermark + Footer callback ───
    wm_bytes = _make_watermark_bytes(opacity=0.12)

    def _draw(canvas, doc_):
        # Watermark BEHIND content
        if wm_bytes:
            try:
                from reportlab.lib.utils import ImageReader
                _size = 60 * mm
                _x = (PAGE_W - _size) / 2
                _y = (PAGE[1] - _size) / 2
                canvas.saveState()
                canvas.drawImage(ImageReader(io.BytesIO(wm_bytes)), _x, _y,
                                width=_size, height=_size, mask='auto')
                canvas.restoreState()
            except Exception:
                pass
        # Footer bar
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, PAGE_W, 8*mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica", 5.5)
        canvas.drawCentredString(PAGE_W/2, 4*mm,
            f"© {ts.year} {c['legal_name']} · UID: {doc_uid} · Hash: {doc_hash[:16]}…")
        canvas.drawRightString(PAGE_W - 6*mm, 4*mm, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_draw, onLaterPages=_draw)
    return buf.getvalue()
