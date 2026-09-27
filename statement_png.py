"""
statement_png.py — Render account statements as PNG images.
Non-editable format. Includes verification hash + timestamp.
"""
import io
import hashlib
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load_fonts():
    """Load TrueType fonts. Fallback to default if not found."""
    try:
        bold_path = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
        regular_path = bold_path.replace("-Bold", "") if bold_path else None
        if bold_path:
            return {
                "h1":     ImageFont.truetype(bold_path, 34),
                "h2":     ImageFont.truetype(bold_path, 22),
                "h3":     ImageFont.truetype(bold_path, 16),
                "bold":   ImageFont.truetype(bold_path, 14),
                "body":   ImageFont.truetype(regular_path or bold_path, 13),
                "small":  ImageFont.truetype(regular_path or bold_path, 11),
                "tiny":   ImageFont.truetype(regular_path or bold_path, 9),
            }
    except Exception:
        d = ImageFont.load_default()
        return {k: d for k in ["h1", "h2", "h3", "bold", "body", "small", "tiny"]}


def _verification_hash(retailer_id, total, order_count, ts):
    """Generate a short verification hash."""
    data = f"{retailer_id}|{total}|{order_count}|{ts}"
    return hashlib.sha256(data.encode()).hexdigest()[:12].upper()


def generate_statement_png(retailer: dict, orders: list, company: dict = None) -> bytes:
    """
    Generate a branded statement PNG.
    Returns PNG bytes ready for download.
    """
    if not HAS_PIL:
        raise RuntimeError("Pillow not installed. Run: pip install --user --break-system-packages pillow")

    # Safe defaults + merge with whatever was passed
    defaults = {
        "name": "Meena Agencies",
        "tagline": "Trusted Pharma Wholesale Partner",
        "address1": "2661, South Main Street, near Indian Bank",
        "address2": "Rajakrishnapuram, Thanjavur, Tamilnadu — 613009",
        "phone": "6382130536",
        "email": "meena.agencies@gmail.com",
        "gstin": "33AAIFM8119N1ZW",
    }

    raw = company or {}
    merged = dict(defaults)
    # Map company.json key variants to statement keys
    merged["name"] = raw.get("name", defaults["name"])
    merged["phone"] = raw.get("phone", defaults["phone"])
    merged["email"] = raw.get("email", defaults["email"])
    merged["gstin"] = raw.get("gstin", defaults["gstin"])
    merged["tagline"] = raw.get("tagline", defaults["tagline"])
    # company.json uses address_line1 / address_line2
    merged["address1"] = raw.get("address1") or raw.get("address_line1", defaults["address1"])
    merged["address2"] = raw.get("address2") or raw.get("address_line2", defaults["address2"])
    company = merged

    fonts = _load_fonts()

    # ─── Canvas setup ───
    W = 1100
    # Dynamic height based on order count
    base_h = 700  # header + summary
    per_order = 40
    max_orders_to_show = min(15, len(orders))
    H = base_h + (max_orders_to_show * per_order) + 350  # footer space

    img = Image.new("RGB", (W, H), "#0a0e27")
    draw = ImageDraw.Draw(img)

    # ─── Background gradient (simulated with bands) ───
    for y in range(H):
        r = int(10 + (y / H) * 8)
        g = int(14 + (y / H) * 12)
        b = int(39 + (y / H) * 20)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ─── Top accent bar ───
    draw.rectangle([(0, 0), (W, 6)], fill="#00d4ff")
    draw.rectangle([(0, 6), (int(W * 0.6), 8)], fill="#7b61ff")

    # ─── Header: Company info ───
    y = 40
    # Draw logo image if available, else fall back to "M" box
    logo_x, logo_y = 60, y
    logo_size = 50
    _logo_drawn = False
    try:
        from pathlib import Path as _PL
        if _PL("logo.png").exists():
            _logo_img = Image.open("logo.png").convert("RGBA")
            _logo_img = _logo_img.resize((logo_size, logo_size), Image.LANCZOS)
            # Round crop using mask
            from PIL import ImageDraw as _ID
            _mask = Image.new("L", (_logo_size_m, _logo_size_m), 0) if False else Image.new("L", (logo_size, logo_size), 0)
            _ID.Draw(_mask).ellipse((0, 0, logo_size, logo_size), fill=255)
            img.paste(_logo_img, (logo_x, logo_y), _mask)
            _logo_drawn = True
    except Exception:
        pass

    if not _logo_drawn:
        # Fallback "M" box
        draw.rounded_rectangle(
            [(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)],
            radius=10, fill="#00d4ff"
        )
        _m_font = fonts["h2"]
        _m_w = draw.textlength("M", font=_m_font)
        draw.text((logo_x + (logo_size - _m_w) / 2, logo_y + 8), "M",
                  font=_m_font, fill="#0a0e27")

    draw.text((130, y + 4), company.get("name", "Meena Agencies"), font=fonts["h1"], fill="#ffffff")
    y += 50
    draw.text((120, y), company.get("tagline", "Trusted Pharma Wholesale Partner").upper(), font=fonts["small"], fill="#8892b0")
    y += 30

    # Contact line — use text labels instead of emojis (PIL can't render them)
    draw.text((60, y), f"PHONE: {company.get('phone', '')}", font=fonts["small"], fill="#a8b2d1")
    draw.text((260, y), f"EMAIL: {company.get('email', '')}", font=fonts["small"], fill="#a8b2d1")
    y += 20
    draw.text((60, y), company.get("address1", ""), font=fonts["small"], fill="#8892b0")
    y += 18
    draw.text((60, y), company.get("address2", ""), font=fonts["small"], fill="#8892b0")
    y += 18
    draw.text((60, y), f"GSTIN: {company['gstin']}", font=fonts["small"], fill="#8892b0")
    y += 35

    # Divider
    draw.line([(60, y), (W - 60, y)], fill="#00d4ff", width=1)
    y += 25

    # ─── Title ───
    draw.text((60, y), "ACCOUNT STATEMENT", font=fonts["h2"], fill="#00d4ff")
    ts = datetime.now()
    ts_str = ts.strftime("%d-%b-%Y %H:%M:%S").upper()
    # Right-align timestamp
    ts_w = draw.textlength(ts_str, font=fonts["small"])
    draw.text((W - 60 - ts_w, y + 8), ts_str, font=fonts["small"], fill="#8892b0")
    y += 40

    # ─── Retailer details box ───
    box_top = y
    box_h = 140
    draw.rectangle([(60, box_top), (W - 60, box_top + box_h)],
                   fill=(15, 22, 50), outline="#00d4ff", width=1)

    y_inner = box_top + 18
    draw.text((80, y_inner), "BILL TO", font=fonts["tiny"], fill="#00d4ff")
    y_inner += 22
    draw.text((80, y_inner), retailer.get("shop", "—"), font=fonts["h3"], fill="#ffffff")
    y_inner += 26
    draw.text((80, y_inner), f"Retailer ID: {retailer.get('id', '—')}", font=fonts["body"], fill="#e8eaf6")
    y_inner += 20
    draw.text((80, y_inner), f"Owner: {retailer.get('owner', '—')}", font=fonts["body"], fill="#e8eaf6")
    y_inner += 20
    draw.text((80, y_inner), f"Phone: {retailer.get('phone', '—')}", font=fonts["body"], fill="#e8eaf6")

    # Right column — account summary
    rx = W // 2 + 30
    ry = box_top + 18
    draw.text((rx, ry), "ACCOUNT SUMMARY", font=fonts["tiny"], fill="#00d4ff")
    ry += 22

    credit_limit = retailer.get("credit_limit", 0)
    outstanding = retailer.get("outstanding", 0)
    available = max(0, credit_limit - outstanding)

    draw.text((rx, ry), "Credit Limit", font=fonts["body"], fill="#8892b0")
    draw.text((W - 100 - draw.textlength(f"Rs. {credit_limit:,.0f}", font=fonts["bold"]), ry),
              f"Rs. {credit_limit:,.0f}", font=fonts["bold"], fill="#e8eaf6")
    ry += 24
    draw.text((rx, ry), "Outstanding", font=fonts["body"], fill="#8892b0")
    _out_color = "#ff4d6d" if outstanding > 0 else "#00d47a"
    draw.text((W - 100 - draw.textlength(f"Rs. {outstanding:,.0f}", font=fonts["bold"]), ry),
              f"Rs. {outstanding:,.0f}", font=fonts["bold"], fill=_out_color)
    ry += 24
    draw.text((rx, ry), "Available", font=fonts["body"], fill="#8892b0")
    draw.text((W - 100 - draw.textlength(f"Rs. {available:,.0f}", font=fonts["bold"]), ry),
              f"Rs. {available:,.0f}", font=fonts["bold"], fill="#00d47a")
    ry += 24
    draw.text((rx, ry), "Status", font=fonts["body"], fill="#8892b0")
    _status = retailer.get("status", "Active")
    draw.text((W - 100 - draw.textlength(_status, font=fonts["bold"]), ry),
              _status, font=fonts["bold"], fill="#e8eaf6")

    y = box_top + box_h + 35

    # ─── Order history table ───
    draw.text((60, y), "RECENT ORDERS", font=fonts["h3"], fill="#00d4ff")
    y += 32

    # Table header
    draw.rectangle([(60, y), (W - 60, y + 30)], fill=(20, 28, 60))
    draw.text((75, y + 8), "DATE", font=fonts["small"], fill="#8892b0")
    draw.text((220, y + 8), "ORDER ID", font=fonts["small"], fill="#8892b0")
    draw.text((500, y + 8), "AMOUNT", font=fonts["small"], fill="#8892b0")
    draw.text((700, y + 8), "STATUS", font=fonts["small"], fill="#8892b0")
    draw.text((870, y + 8), "LOCATION", font=fonts["small"], fill="#8892b0")
    y += 30

    # Filter & sort orders newest first
    valid_orders = [o for o in orders if o.get("status") != "Awaiting OTP"]
    valid_orders.sort(key=lambda o: o.get("placed_at", ""), reverse=True)

    if not valid_orders:
        draw.text((75, y + 15), "No orders recorded yet.", font=fonts["body"], fill="#8892b0")
        y += 50
    else:
        for i, o in enumerate(valid_orders[:max_orders_to_show]):
            row_color = (15, 22, 50) if i % 2 == 0 else (12, 18, 42)
            draw.rectangle([(60, y), (W - 60, y + 36)], fill=row_color)

            _date = o.get("placed_at", "—")[:11]
            _oid = o.get("order_id", "—")
            if len(_oid) > 28:
                _oid = _oid[:25] + "..."
            _amt = o.get("total", 0)
            _stat = o.get("status", "—")
            _loc = o.get("location", "")[:22]

            draw.text((75, y + 10), _date, font=fonts["body"], fill="#e8eaf6")
            draw.text((220, y + 10), _oid, font=fonts["body"], fill="#a8b2d1")

            _amt_str = f"Rs. {_amt:,.0f}"
            _amt_w = draw.textlength(_amt_str, font=fonts["bold"])
            draw.text((640 - _amt_w, y + 10), _amt_str, font=fonts["bold"], fill="#00d4ff")

            _stat_color = {
                "Approved": "#00d47a",
                "Pending": "#ffb547",
                "Cancelled": "#ff4d6d",
                "Rejected": "#ff4d6d",
            }.get(_stat, "#8892b0")
            draw.text((700, y + 10), _stat, font=fonts["body"], fill=_stat_color)

            draw.text((870, y + 10), _loc, font=fonts["small"], fill="#8892b0")
            y += 36

        if len(valid_orders) > max_orders_to_show:
            draw.text((75, y + 8),
                      f"... and {len(valid_orders) - max_orders_to_show} more orders",
                      font=fonts["small"], fill="#8892b0")
            y += 30

    y += 25

    # ─── Summary totals ───
    total_spent = sum(o.get("total", 0) for o in valid_orders if o.get("status") == "Approved")
    total_orders = len(valid_orders)
    approved = len([o for o in valid_orders if o.get("status") == "Approved"])
    pending = len([o for o in valid_orders if o.get("status") == "Pending"])

    summary_box_h = 130
    draw.rectangle([(60, y), (W - 60, y + summary_box_h)],
                   fill=(15, 22, 50), outline="#7b61ff", width=1)

    draw.text((85, y + 18), "SUMMARY", font=fonts["tiny"], fill="#7b61ff")
    yy = y + 42
    draw.text((85, yy), f"Total Orders: {total_orders}", font=fonts["body"], fill="#e8eaf6")
    draw.text((350, yy), f"Approved: {approved}", font=fonts["body"], fill="#00d47a")
    draw.text((550, yy), f"Pending: {pending}", font=fonts["body"], fill="#ffb547")
    yy += 28
    draw.text((85, yy), f"Total Approved Value:", font=fonts["h3"], fill="#ffffff")
    draw.text((450, yy - 3), f"Rs. {total_spent:,.2f}", font=fonts["h2"], fill="#00d4ff")

    yy += 40
    draw.text((85, yy), f"Outstanding Balance: Rs. {outstanding:,.2f}",
              font=fonts["body"], fill="#ff4d6d")

    y += summary_box_h + 35

    # ─── Verification hash footer ───
    verify = _verification_hash(
        retailer.get("id", "?"),
        total_spent,
        total_orders,
        ts.strftime("%Y-%m-%d")
    )
    draw.line([(60, y), (W - 60, y)], fill=(60, 70, 100), width=1)
    y += 15

    draw.text((60, y), f"Verification Code: {verify}",
              font=fonts["small"], fill="#8892b0")
    draw.text((60, y + 18),
              f"This statement is computer-generated on {ts_str}. Any alteration renders it invalid.",
              font=fonts["tiny"], fill="#6b7ba0")
    draw.text((60, y + 34),
              f"To verify: contact {company['phone']} or email {company['email']}",
              font=fonts["tiny"], fill="#6b7ba0")

    y += 60

    # ─── Bottom watermark strip ───
    draw.rectangle([(0, H - 40), (W, H)], fill=(8, 11, 30))
    _footer = f"© {ts.year} {company['name']} · {company['tagline']} · Official Document"
    _fw = draw.textlength(_footer, font=fonts["tiny"])
    draw.text(((W - _fw) // 2, H - 25), _footer, font=fonts["tiny"], fill="#6b7ba0")

    # ─── Convert to bytes ───
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
