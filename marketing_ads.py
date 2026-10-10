"""
marketing_ads.py v3 — per-customer pharma banner generator (fixed).
"""
import io, random
from pathlib import Path
try:
    import copy_engine
    HAS_COPY = True
except ImportError:
    HAS_COPY = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── Fonts ──
BOLD  = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
REG   = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
SERIF = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]

def _f(size, kind="bold"):
    paths = BOLD if kind == "bold" else (SERIF if kind == "serif" else REG)
    for p in paths:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except Exception: continue
    return ImageFont.load_default()

# ── Brand palette ──
BRAND = {
    "red":   (176, 42, 55),
    "gold":  (212, 175, 55),
    "cream": (250, 246, 240),
    "ink":   (35, 30, 28),
    "white": (255, 255, 255),
    "grey":  (110, 105, 100),
}

# ── AI headline engine ──
HEADLINES = {
    "platinum": ["You've earned our best price.",
                 "Top retailer. Top offer.",
                 "Premium partner — premium deal."],
    "gold":     ["A deal built for your shelf.",
                 "Restock smarter this week.",
                 "Higher margin. Same quality."],
    "silver":   ["Fast-moving stock, ready to ship.",
                 "Your shelf's best seller — now cheaper.",
                 "Stock up before the rush."],
    "new":      ["Welcome. Here's your first deal.",
                 "New partner, new price.",
                 "Try us. Save from day one."],
}

def pick_headline(tier="new", history_days=0):
    if history_days > 180 and tier in ("gold", "platinum"):
        return "Loyal partner. Locked-in price."
    return random.choice(HEADLINES.get(tier, HEADLINES["new"]))

# ── Text wrap ──
def _wrap(draw, text, font, max_w):
    words = text.split(); lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] > max_w and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    if cur: lines.append(cur)
    return lines

# ── Backgrounds ──
def _bg_cream(w, h):
    img = Image.new("RGB", (w, h), BRAND["cream"])
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy, r = int(w*0.82), int(h*0.18), int(w*0.55)
    for rad in range(r, 0, -20):
        a = int(60 * (1 - rad/r))
        d.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=(*BRAND["red"], a))
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

def _bg_warehouse(w, h):
    img = Image.new("RGB", (w, h), (60, 30, 20))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 60):
        d.rectangle([(0, y), (w, y+6)], fill=(120, 60, 35))
    for x in range(0, w, 180):
        d.rectangle([(x, 0), (x+8, h)], fill=(90, 45, 25))
    return img.filter(ImageFilter.GaussianBlur(22))

# ── Product paste (with placeholder fallback) ──
def _paste_product(img, product_path, center, max_w, max_h):
    cx, cy = center
    if Path(product_path).exists():
        p = Image.open(product_path).convert("RGBA")
        p.thumbnail((max_w, max_h), Image.LANCZOS)
        x = cx - p.width // 2
        y = cy - p.height // 2

        # Drop shadow
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.ellipse([x + p.width*0.15, y + p.height*0.92,
                    x + p.width*0.85, y + p.height*1.02],
                   fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(24))
        img_rgba = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
        img.paste(img_rgba, (0, 0))
        img.paste(p, (x, y), p)
    else:
        # Placeholder so you can see the layout
        d = ImageDraw.Draw(img)
        bw, bh = max_w, max_h
        x = cx - bw // 2
        y = cy - bh // 2
        d.rounded_rectangle([(x, y), (x+bw, y+bh)],
                            radius=24, fill=(230, 225, 218),
                            outline=BRAND["grey"], width=3)
        txt = "PUT products/dolo650.png HERE"
        f = _f(28, "bold")
        bb = d.textbbox((0, 0), txt, font=f)
        d.text((cx - (bb[2]-bb[0])//2, cy - (bb[3]-bb[1])//2),
               txt, font=f, fill=BRAND["grey"])

# ── Offer badge ──
def _draw_offer_badge(draw, x, y, text_lines, w=360, h=180):
    draw.rounded_rectangle([(x, y), (x+w, y+h)], radius=16,
                           fill=BRAND["gold"], outline=BRAND["red"], width=4)
    fy = y + 26
    for i, line in enumerate(text_lines):
        f = _f(36 if i == 0 else 44, "bold")
        bb = draw.textbbox((0, 0), line, font=f)
        tw = bb[2] - bb[0]
        draw.text((x + (w - tw)//2, fy), line, font=f,
                  fill=BRAND["ink"] if i == 0 else BRAND["red"])
        fy += (bb[3] - bb[1]) + 14

# ── Main ──
def generate_marketing_ad(promo, retailer=None, company=None,
                          size=(1080, 1350),
                          product_path="products/dolo650.png",
                          bg="cream"):
    if not HAS_PIL:
        return None
    W, H = size

    tier, base_pct, history = "new", promo.get("extra_discount_pct", 0), 0
    if retailer:
        try:
            import discounts as _dc
            t = _dc.get_customer_tier(retailer["id"])
            if isinstance(t, tuple): tier, base_pct = t
            if hasattr(_dc, "get_history_days"):
                history = _dc.get_history_days(retailer["id"])
        except Exception:
            pass

    img = _bg_cream(W, H) if bg == "cream" else _bg_warehouse(W, H)
    d = ImageDraw.Draw(img)

    # Top bar
    d.rectangle([(0, 0), (W, 10)], fill=BRAND["red"])

    # Header
    logo_sz = 90
    lx, ly = 40, 40
    try:
        if Path("logo.png").exists():
            lo = Image.open("logo.png").convert("RGBA")
            lo.thumbnail((logo_sz, logo_sz), Image.LANCZOS)
            img.paste(lo, (lx, ly), lo)
    except Exception:
        pass
    d.text((lx + logo_sz + 16, ly + 8),  "MEENA AGENCIES",
           font=_f(34, "serif"), fill=BRAND["red"])
    d.text((lx + logo_sz + 16, ly + 56), "Wholesale Pharma · Thanjavur",
           font=_f(16, "regular"), fill=BRAND["grey"])

    # Badge
    badge_lines = promo.get("badge_lines", ["BUY 50 BOXES", "GET 1 BOX FREE"])
    _draw_offer_badge(d, W - 400, 40, badge_lines)

    # Product
    _paste_product(img, product_path, (W//2, int(H*0.42)),
                   int(W*0.70), int(H*0.46))

    # Headline
    headline = pick_headline(tier=tier, history_days=history)
    hf = _f(38, "serif")
    lines = _wrap(d, headline, hf, W - 160)
    y = int(H*0.70)
    for ln in lines[:2]:
        bb = d.textbbox((0, 0), ln, font=hf)
        d.text(((W - (bb[2]-bb[0]))//2, y), ln, font=hf, fill=BRAND["ink"])
        y += (bb[3]-bb[1]) + 8

    # Offer sentence
    offer_text = promo.get("offer_text", "Dolo 650mg · 10 strips × 10 tablets")
    of = _f(22, "regular")
    bb = d.textbbox((0, 0), offer_text, font=of)
    d.text(((W - (bb[2]-bb[0]))//2, y + 14), offer_text,
           font=of, fill=BRAND["grey"])

    # Customer name pill
    if retailer and retailer.get("shop"):
        ptxt = f"Prepared for: {retailer['shop']}"
        pf = _f(20, "bold")
        bb = d.textbbox((0, 0), ptxt, font=pf)
        pad = 24
        bw = bb[2]-bb[0] + pad*2
        bx = (W - bw)//2
        by = y + 70
        d.rounded_rectangle([(bx, by), (bx+bw, by+44)],
                            radius=22, fill=BRAND["red"])
        d.text((bx+pad, by+10), ptxt, font=pf, fill=BRAND["white"])

    # CTA
    cta = cta_txt
    cf = _f(30, "bold")
    bb = d.textbbox((0, 0), cta, font=cf)
    d.text(((W - (bb[2]-bb[0]))//2, H - 170), cta, font=cf, fill=BRAND["red"])

    # Footer
    d.rectangle([(0, H-70), (W, H)], fill=BRAND["ink"])
    foot = "GST: 33AIMB1112W · WBB-27-00012w · Drug Licence-series · Thanjavur · @7338824033"
    ff = _f(14, "regular")
    bb = d.textbbox((0, 0), foot, font=ff)
    d.text(((W - (bb[2]-bb[0]))//2, H-44), foot, font=ff, fill=(210, 205, 200))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

SIZE_PRESETS = {
    "telegram": (1080, 1350),
    "whatsapp": (1080, 1080),
    "story":    (1080, 1920),
    "print":    (2480, 3508),
}

def generate_all_sizes(promo, retailer=None, company=None,
                       product_path="products/dolo650.png"):
    return {n: generate_marketing_ad(promo, retailer, company, s, product_path)
            for n, s in SIZE_PRESETS.items()}

if __name__ == "__main__":
    promo = {
        "badge_lines": ["BUY 50 BOXES", "GET 1 BOX FREE"],
        "offer_text":  "Dolo 650mg · 10 strips × 10 tablets",
    }
    r = {"id": "RET001", "shop": "Sri Balaji Medicals", "owner": "Chitra"}
    img = generate_marketing_ad(promo, r)
    if img:
        Path("/tmp/ad_v3.png").write_bytes(img)
        print(f"OK  {len(img):,} bytes -> /tmp/ad_v3.png")
    else:
        print("FAIL — Pillow missing")
