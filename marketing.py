"""
marketing.py — Privacy-first promotions. No public price display.
Each customer sees ONLY their own price.
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

PROMOS_FILE = "promotions.json"
CAMPAIGNS_FILE = "campaigns.json"


# ═══════════════════════════════════════════════════════════
# PROMOTION TYPES (no prices in public text)
# ═══════════════════════════════════════════════════════════
PROMO_TYPES = {
    "seasonal":   {"emoji": "🌦️", "label": "Seasonal Sale"},
    "festival":   {"emoji": "🪔", "label": "Festival Offer"},
    "clearance":  {"emoji": "📦", "label": "Clearance"},
    "new_stock":  {"emoji": "✨", "label": "New Arrival"},
    "loyalty":    {"emoji": "⭐", "label": "Loyalty Reward"},
    "bulk":       {"emoji": "🎯", "label": "Bulk Bonus"},
    "custom":     {"emoji": "🎁", "label": "Special"},
}


# ═══════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════
def _load(path, default):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text())
        except Exception:
            return default
    return default


def _save(path, data):
    Path(path).write_text(json.dumps(data, indent=2))


def load_promos():
    return _load(PROMOS_FILE, [])


def load_campaigns():
    return _load(CAMPAIGNS_FILE, [])


# ═══════════════════════════════════════════════════════════
# CREATE PROMOTION — Public text, no prices
# ═══════════════════════════════════════════════════════════
def create_promotion(title, promo_type, public_text, category="",
                     extra_discount_pct=0.0, valid_days=30,
                     audience="all", target_retailers=None):
    """
    Create a promotion.
    public_text: what everyone sees — NO PRICES.
    extra_discount_pct: hidden from public, applied at their price.
    audience: 'all' | 'tier' | 'specific'
    """
    promo_id = f"PROMO-{datetime.now().strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    promo = {
        "id": promo_id,
        "title": title,
        "type": promo_type,
        "public_text": public_text,          # Safe — no prices
        "category": category,                 # Which medicines (or all)
        "extra_discount_pct": extra_discount_pct,   # Hidden
        "audience": audience,
        "target_retailers": target_retailers or [],
        "valid_from": datetime.now().strftime("%Y-%m-%d"),
        "valid_until": (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d"),
        "active": True,
        "created_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
        "sent_to": [],
    }
    promos = load_promos()
    promos.append(promo)
    _save(PROMOS_FILE, promos)
    return promo


def deactivate_promo(promo_id):
    promos = load_promos()
    for p in promos:
        if p["id"] == promo_id:
            p["active"] = False
            _save(PROMOS_FILE, promos)
            return True
    return False


# ═══════════════════════════════════════════════════════════
# PUBLIC MESSAGE — what everyone sees (no price)
# ═══════════════════════════════════════════════════════════
def build_public_message(promo):
    """Safe public message. NO prices. NO discounts."""
    t = PROMO_TYPES.get(promo["type"], PROMO_TYPES["custom"])
    msg = (
        f"{t['emoji']} <b>{promo['title']}</b>\n\n"
        f"{promo['public_text']}\n\n"
        f"📅 Valid: {promo['valid_from']} to {promo['valid_until']}\n"
        f"👤 Login to your account to see your exclusive price."
    )
    return msg


# ═══════════════════════════════════════════════════════════
# PERSONAL MESSAGE — private, price included
# ═══════════════════════════════════════════════════════════
def build_personal_message(promo, retailer, base_price, retailer_tier_pct):
    """
    Personalized message. Shows ONLY this retailer's price.
    Never share this with other customers.
    """
    t = PROMO_TYPES.get(promo["type"], PROMO_TYPES["custom"])
    total_pct = retailer_tier_pct + promo["extra_discount_pct"]
    final_price = base_price * (100 - total_pct) / 100

    msg = (
        f"{t['emoji']} <b>{promo['title']}</b>\n"
        f"Hi <b>{retailer.get('owner', '')}</b>,\n\n"
        f"{promo['public_text']}\n\n"
        f"<b>YOUR Exclusive Price:</b>\n"
        f"• Base: ₹{base_price:,.2f}\n"
        f"• Your discount: {total_pct:.1f}%\n"
        f"• <b>You pay: ₹{final_price:,.2f}</b>\n\n"
        f"🔒 This price is unique to you. Do not share.\n"
        f"📅 Valid until {promo['valid_until']}"
    )
    return msg


# ═══════════════════════════════════════════════════════════
# SEND PROMOTION
# ═══════════════════════════════════════════════════════════
def send_promotion(promo_id, retailers, orders=None, dry_run=False):
    """
    Send promotion to target audience.
    - Public message: title + valid until (no price)
    - Personal message: only sent if audience='specific'
    Returns summary dict.
    """
    promos = load_promos()
    promo = next((p for p in promos if p["id"] == promo_id), None)
    if not promo:
        return {"ok": False, "msg": "Promotion not found"}

    # Determine recipients
    recipients = []
    if promo["audience"] == "all":
        recipients = retailers
    elif promo["audience"] == "specific":
        recipients = [r for r in retailers if r["id"] in promo["target_retailers"]]
    elif promo["audience"] == "tier":
        # Requires discounts module
        try:
            import discounts as dc
            for r in retailers:
                tier, _ = dc.get_customer_tier(r["id"])
                if tier in promo.get("target_tiers", []):
                    recipients.append(r)
        except Exception:
            pass

    if dry_run:
        return {"ok": True, "dry_run": True, "recipients": len(recipients)}

    # Send via notify_pro
    sent = 0
    failed = 0
    try:
        import notify_pro
        for r in recipients:
            if not r.get("telegram_chat_id"):
                failed += 1
                continue
            # Everyone gets the SAME public message — no prices
            msg = build_public_message(promo)
            try:
                ok = False
                # Try sending per-retailer banner image first
                try:
                    import marketing_ads
                    promo["orders"] = orders or []
                    png = marketing_ads.generate_marketing_ad(promo, retailer=r)
                    if png and hasattr(notify_pro, "notify_retailer_photo"):
                        ok, _ = notify_pro.notify_retailer_photo(r, png, msg)
                except Exception:
                    ok = False
                if not ok:
                    ok, _ = notify_pro.notify_retailer(r, msg)
                if ok:
                    sent += 1
                    promo["sent_to"].append({
                        "retailer_id": r["id"],
                        "at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
                    })
                else:
                    failed += 1
            except Exception:
                failed += 1
    except Exception as e:
        return {"ok": False, "msg": f"Notify error: {e}"}

    _save(PROMOS_FILE, promos)
    return {"ok": True, "sent": sent, "failed": failed, "total": len(recipients)}


# ═══════════════════════════════════════════════════════════
# CUSTOMER-VIEW PROMOTIONS (only their tier shown)
# ═══════════════════════════════════════════════════════════
def active_promos_for_retailer(retailer_id):
    """Return promotions valid for this customer (no prices)."""
    today = datetime.now().strftime("%Y-%m-%d")
    promos = load_promos()
    result = []
    for p in promos:
        if not p.get("active"):
            continue
        if p["valid_from"] > today or p["valid_until"] < today:
            continue
        # Check audience
        if p["audience"] == "specific" and retailer_id not in p["target_retailers"]:
            continue
        result.append(p)
    return result


# ═══════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════
def campaign_summary():
    """Overall stats."""
    promos = load_promos()
    active = [p for p in promos if p.get("active")]
    total_sent = sum(len(p.get("sent_to", [])) for p in promos)
    return {
        "total_promos": len(promos),
        "active": len(active),
        "total_sent": total_sent,
        "types": {t: len([p for p in promos if p["type"] == t]) for t in PROMO_TYPES},
    }


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("  MARKETING SYSTEM TEST")
    print("═" * 70)

    # Create a monsoon promo
    promo = create_promotion(
        title="Monsoon Health Drive",
        promo_type="seasonal",
        public_text="Stock up on ORS, Zinc, and Antibiotics for the monsoon season. "
                    "Special offers for our valued retailers.",
        category="seasonal_medicines",
        extra_discount_pct=3.0,
        valid_days=20,
        audience="all",
    )
    print(f"\n✅ Promotion created: {promo['id']}")

    # Show public message (safe)
    print("\n═══ PUBLIC MESSAGE (no prices — safe to share) ═══")
    print(build_public_message(promo))

    # Show personal message (private)
    retailer = {"id": "RET001", "shop": "Sri Balaji Medicals",
                "owner": "Chitra", "telegram_chat_id": "953358258"}
    print("\n═══ PERSONAL MESSAGE (private — only this retailer gets this) ═══")
    print(build_personal_message(promo, retailer, base_price=100.0, retailer_tier_pct=12.0))

    # Analytics
    print("\n═══ SUMMARY ═══")
    s = campaign_summary()
    for k, v in s.items():
        print(f"   {k}: {v}")

    print("\n🔒 KEY FEATURE: Public text has NO prices. Only personal messages do.")
