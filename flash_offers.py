"""
flash_offers.py — Time-gated per-customer flash discounts.
7 AM - 9 AM offers. Owner approves. Auto-broadcast to Telegram.
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

FLASH_FILE = "flash_offers.json"
OFFER_WINDOW_START = 7   # 7 AM
OFFER_WINDOW_END = 9     # 9 AM


# ═══════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════
def _load():
    if Path(FLASH_FILE).exists():
        try:
            return json.loads(Path(FLASH_FILE).read_text())
        except Exception:
            return []
    return []


def _save(data):
    Path(FLASH_FILE).write_text(json.dumps(data, indent=2))


# ═══════════════════════════════════════════════════════════
# TIME WINDOW CHECK
# ═══════════════════════════════════════════════════════════
def is_flash_window():
    """Return True if current time is within 7 AM - 9 AM."""
    hour = datetime.now().hour
    return OFFER_WINDOW_START <= hour < OFFER_WINDOW_END


def window_status_text():
    now = datetime.now()
    h = now.hour
    if h < OFFER_WINDOW_START:
        mins = (OFFER_WINDOW_START - h - 1) * 60 + (60 - now.minute)
        return f"⏰ Opens in {mins} min (at 7 AM)"
    if OFFER_WINDOW_START <= h < OFFER_WINDOW_END:
        mins_left = (OFFER_WINDOW_END - h - 1) * 60 + (60 - now.minute)
        return f"🔥 ACTIVE — {mins_left} min remaining"
    return "😴 Closed — opens tomorrow 7 AM"


# ═══════════════════════════════════════════════════════════
# CREATE FLASH OFFER (owner creates for ONE customer)
# ═══════════════════════════════════════════════════════════
def create_flash_offer(retailer_id, shop_name, discount_pct,
                       ad_text, valid_days=1,
                       categories=None, notes=""):
    """
    Create a per-customer flash offer.
    Owner creates one offer per customer with different %.
    Returns offer dict.
    """
    offer_id = f"FLASH-{datetime.now().strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    offer = {
        "id": offer_id,
        "retailer_id": retailer_id,
        "shop_name": shop_name,
        "discount_pct": float(discount_pct),
        "ad_text": ad_text,
        "categories": categories or ["all"],
        "valid_date": datetime.now().strftime("%Y-%m-%d"),
        "valid_from_hour": OFFER_WINDOW_START,
        "valid_to_hour": OFFER_WINDOW_END,
        "valid_days": valid_days,
        "notes": notes,
        "status": "DRAFT",         # DRAFT → APPROVED → SENT → EXPIRED
        "created_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
        "approved_at": "",
        "sent_at": "",
    }
    data = _load()
    data.append(offer)
    _save(data)
    return offer


# ═══════════════════════════════════════════════════════════
# APPROVE
# ═══════════════════════════════════════════════════════════
def approve_offer(offer_id):
    data = _load()
    for o in data:
        if o["id"] == offer_id:
            o["status"] = "APPROVED"
            o["approved_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
            _save(data)
            return True, f"✅ Approved: {offer_id}"
    return False, "Offer not found"


def reject_offer(offer_id, reason=""):
    data = _load()
    for o in data:
        if o["id"] == offer_id:
            o["status"] = "REJECTED"
            o["notes"] = reason or o.get("notes", "")
            _save(data)
            return True, f"❌ Rejected: {offer_id}"
    return False, "Offer not found"


# ═══════════════════════════════════════════════════════════
# BUILD PERSONALIZED MESSAGE
# ═══════════════════════════════════════════════════════════
def build_flash_message(offer, retailer):
    """Build the Telegram message for this specific customer."""
    return (
        f"🌅 <b>Good Morning, {retailer.get('owner', 'Partner')}!</b>\n\n"
        f"🎉 <b>FLASH SALE — Today Only</b>\n"
        f"⏰ <b>{OFFER_WINDOW_START}:00 AM – {OFFER_WINDOW_END}:00 AM</b>\n\n"
        f"{offer['ad_text']}\n\n"
        f"🎁 <b>YOUR Exclusive Discount:</b>\n"
        f"┌─────────────────────────\n"
        f"│ <b>{offer['discount_pct']:.1f}% OFF</b>\n"
        f"│ on orders placed 7–9 AM\n"
        f"└─────────────────────────\n\n"
        f"🏪 Store: <b>{retailer.get('shop', '')}</b>\n"
        f"📅 Valid: {offer['valid_date']}\n\n"
        f"🔒 <i>This offer is unique to you. Not shareable.</i>\n"
        f"🏃 Login now: meena-agencies.com"
    )


# ═══════════════════════════════════════════════════════════
# SEND OFFER (single)
# ═══════════════════════════════════════════════════════════
def send_flash_offer(offer_id, dry_run=False):
    """Send approved offer to its specific customer via Telegram."""
    data = _load()
    offer = next((o for o in data if o["id"] == offer_id), None)
    if not offer:
        return {"ok": False, "msg": "Offer not found"}
    if offer["status"] != "APPROVED":
        return {"ok": False, "msg": f"Cannot send — status is {offer['status']}"}

    # Load retailer
    try:
        import json as _j
        retailers = _j.loads(Path("retailers.json").read_text())
        retailer = next((r for r in retailers if r["id"] == offer["retailer_id"]), None)
        if not retailer:
            return {"ok": False, "msg": "Retailer not found"}
    except Exception as e:
        return {"ok": False, "msg": f"Retailer load failed: {e}"}

    msg = build_flash_message(offer, retailer)

    if dry_run:
        return {"ok": True, "dry_run": True, "preview": msg}

    # Send via notify_pro (returns a dict)
    try:
        import notify_pro
        result = notify_pro.notify_retailer(retailer, msg)
        if result.get("telegram_sent") or result.get("sms_sent"):
            offer["status"] = "SENT"
            offer["sent_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
            _save(data)
            channel = result.get("channel_used", "unknown")
            return {"ok": True, "msg": f"Sent to {retailer['shop']} via {channel}"}
        return {"ok": False, "msg": f"Send failed: {result.get('reason','unknown')}"}
    except Exception as e:
        return {"ok": False, "msg": f"Notify error: {e}"}


# ═══════════════════════════════════════════════════════════
# AUTO-SEND SCHEDULER
# ═══════════════════════════════════════════════════════════
def auto_send_due_offers():
    """
    Called by the scheduler at 7 AM.
    Sends all APPROVED offers for today.
    """
    data = _load()
    today = datetime.now().strftime("%Y-%m-%d")
    results = {"sent": 0, "failed": 0, "skipped": 0}

    for o in data:
        if o["status"] != "APPROVED":
            continue
        if o["valid_date"] != today:
            results["skipped"] += 1
            continue
        res = send_flash_offer(o["id"])
        if res.get("ok"):
            results["sent"] += 1
        else:
            results["failed"] += 1

    return results


def mark_expired_offers():
    """Mark old offers as EXPIRED."""
    data = _load()
    today = datetime.now().strftime("%Y-%m-%d")
    now_hour = datetime.now().hour
    changed = 0
    for o in data:
        if o["status"] in ("SENT", "APPROVED") and o["valid_date"] < today:
            o["status"] = "EXPIRED"
            changed += 1
        elif (o["status"] == "APPROVED" and
              o["valid_date"] == today and
              now_hour >= OFFER_WINDOW_END):
            o["status"] = "EXPIRED"
            changed += 1
    if changed:
        _save(data)
    return changed


# ═══════════════════════════════════════════════════════════
# LIST / QUERY
# ═══════════════════════════════════════════════════════════
def list_offers(status=None):
    data = _load()
    if status:
        return [o for o in data if o["status"] == status]
    return data


def today_offers():
    today = datetime.now().strftime("%Y-%m-%d")
    return [o for o in _load() if o["valid_date"] == today]


def summary():
    data = _load()
    return {
        "total": len(data),
        "draft": len([o for o in data if o["status"] == "DRAFT"]),
        "approved": len([o for o in data if o["status"] == "APPROVED"]),
        "sent": len([o for o in data if o["status"] == "SENT"]),
        "expired": len([o for o in data if o["status"] == "EXPIRED"]),
    }


# ═══════════════════════════════════════════════════════════
# MARKETING AD TEMPLATES
# ═══════════════════════════════════════════════════════════
AD_TEMPLATES = {
    "morning_boost": {
        "name": "🌅 Morning Boost",
        "text": (
            "Start your day right! Stock up on fast-moving medicines "
            "and save big during our 7-9 AM window. Limited time only!"
        ),
    },
    "festival_special": {
        "name": "🪔 Festival Special",
        "text": (
            "Celebrate with savings! Our festival flash offer brings you "
            "exclusive discounts — available only this morning."
        ),
    },
    "monsoon_care": {
        "name": "🌧️ Monsoon Care",
        "text": (
            "Seasonal demand is rising! Get ORS, antibiotics, and cough syrups "
            "at special morning rates before 9 AM."
        ),
    },
    "chronic_refill": {
        "name": "💊 Chronic Refill",
        "text": (
            "Time to restock chronic medications! Get your diabetes, BP, "
            "and cardiac medicines with an exclusive morning discount."
        ),
    },
    "clearance": {
        "name": "📦 Clearance Deal",
        "text": (
            "Near-expiry stock clearance! Limited quantity at massive discount. "
            "First-come, first-served between 7-9 AM only."
        ),
    },
    "loyalty_thanks": {
        "name": "⭐ Loyalty Thank You",
        "text": (
            "Thank you for being our loyal partner! Here's a special morning "
            "reward just for you — because you deserve it."
        ),
    },
}


def get_template_text(template_key):
    t = AD_TEMPLATES.get(template_key, AD_TEMPLATES["morning_boost"])
    return t["name"], t["text"]


# ═══════════════════════════════════════════════════════════
# AUTO-SCHEDULER SCRIPT
# ═══════════════════════════════════════════════════════════
def run_scheduler_once():
    """
    Called by cron/systemd at 7 AM daily.
    - Marks old offers as expired
    - Sends all APPROVED offers for today
    """
    mark_expired_offers()
    if is_flash_window():
        result = auto_send_due_offers()
        print(f"✅ Auto-send complete: {result}")
        return result
    else:
        print(f"⏰ Not in window. {window_status_text()}")
        return {"sent": 0, "skipped": 0}


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═" * 70)
    print("  FLASH OFFERS TEST")
    print("═" * 70)

    # Clear old
    if Path(FLASH_FILE).exists():
        Path(FLASH_FILE).unlink()

    print(f"\n⏰ Window status: {window_status_text()}")
    print(f"   Current hour: {datetime.now().hour}")
    print(f"   Is flash window? {is_flash_window()}")

    # Create 3 offers for 3 different customers
    test_data = [
        ("RET001", "Sri Balaji Medicals", 12.0, "morning_boost"),
        ("RET002", "Annai Pharmacy",      8.0,  "chronic_refill"),
        ("RET003", "Vetri Medicals",      15.0, "loyalty_thanks"),
    ]

    for rid, shop, pct, tmpl in test_data:
        _, ad = get_template_text(tmpl)
        offer = create_flash_offer(
            retailer_id=rid,
            shop_name=shop,
            discount_pct=pct,
            ad_text=ad,
        )
        print(f"✅ Created {offer['id']} → {shop} @ {pct}%")

    # Approve all
    for o in list_offers():
        ok, msg = approve_offer(o["id"])
        print(f"   {msg}")

    # Preview message for RET001
    print("\n═══ SAMPLE MESSAGE (RET001) ═══")
    try:
        retailers = json.loads(Path("retailers.json").read_text())
        r = next((x for x in retailers if x["id"] == "RET001"), None)
        if r:
            o = list_offers()[0]
            print(build_flash_message(o, r))
    except Exception as e:
        print(f"(skip preview: {e})")

    # Summary
    print("\n═══ SUMMARY ═══")
    for k, v in summary().items():
        print(f"   {k}: {v}")

    print("\n📌 SCHEDULER: run `python3 flash_offers.py --schedule` at 7 AM daily")
