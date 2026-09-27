"""
promotions.py — Marketing promotions for Meena Agencies.
Owner creates a promotion → bot sends personalized message to each retailer.
"""
import json, time, logging, requests
from pathlib import Path

RETAILERS_FILE  = Path("retailers.json")
PROMOTIONS_FILE = Path("promotions.json")
BROADCAST_LOG   = Path("broadcast_log.json")


def _load(p, default=None):
    if not p.exists():
        return default if default is not None else []
    try:
        return json.loads(p.read_text())
    except Exception:
        return default if default is not None else []


def _save(p, data):
    p.write_text(json.dumps(data, indent=2))


# ═══════════════════════════════════════════════════════════
# PROMOTIONS — CRUD
# ═══════════════════════════════════════════════════════════
def create_promotion(title, segment, offer_text, badge_lines=None, valid_until="", kind="daily"):
    """Create a promotion record. segment in [new, silver, gold, platinum, all]."""
    promos = _load(PROMOTIONS_FILE)
    pid = f"P{int(time.time())}"
    promo = {
        "id": pid,
        "title": title,
        "segment": segment,
        "offer_text": offer_text,
        "badge_lines": badge_lines or ["SPECIAL OFFER"],
        "valid_until": valid_until,
        "kind": kind,   # flash | daily | weekly | monthly | bulk | clearance
        "created_at": time.strftime("%d-%b-%Y %H:%M").upper(),
        "status": "DRAFT",
    }
    promos.append(promo)
    _save(PROMOTIONS_FILE, promos)
    return promo


def list_promotions():
    return _load(PROMOTIONS_FILE)


# ═══════════════════════════════════════════════════════════
# PERSONALIZATION — build a per-retailer message
# ═══════════════════════════════════════════════════════════
def build_personal_message(promo, retailer):
    """
    Returns (text, tier) for a specific retailer.
    Uses copy_engine if available for the headline.
    """
    # Determine tier
    tier = "new"
    try:
        import discounts as _dc
        t = _dc.get_customer_tier(retailer["id"])
        if isinstance(t, tuple):
            tier = t[0]
    except Exception:
        pass

    headline = promo["offer_text"]
    try:
        import copy_engine
        ctx = copy_engine.build_context(retailer=retailer, product=None, orders=[])
        c = copy_engine.generate_copy(segment=tier, context=ctx, kind=promo.get("kind", "daily"))
        headline = c["headline"]
        cta = c["cta"]
    except Exception:
        cta = "Order now: 7338824033"

    text = (
        f"🌟 <b>{promo['title']}</b>\n\n"
        f"{headline}\n\n"
        f"<b>Your offer:</b> {promo['badge_lines'][0] if promo['badge_lines'] else ''}\n"
    )
    if promo["valid_until"]:
        text += f"📅 Valid till {promo['valid_until']}\n"
    text += f"\n🏪 Prepared for: <b>{retailer['shop']}</b>\n"
    text += f"\n{cta}"
    return text, tier


# ═══════════════════════════════════════════════════════════
# BROADCAST — send to matching segment
# ═══════════════════════════════════════════════════════════
def send_broadcast(promo_id, bot_send_func, bot=None):
    """
    Send promotion to every retailer whose chat_id is registered
    and whose segment matches (or promo.segment == 'all').
    bot_send_func(chat_id, text) — caller passes the send function.
    """
    promos = _load(PROMOTIONS_FILE)
    promo = next((p for p in promos if p["id"] == promo_id), None)
    if not promo:
        return {"sent": 0, "skipped": 0, "failed": 0, "error": "Promotion not found"}

    retailers = _load(RETAILERS_FILE)
    sent, skipped, failed = 0, 0, 0
    results = []

    for r in retailers:
        chat_id = str(r.get("telegram_chat_id", "")).strip()
        if not chat_id:
            skipped += 1
            continue

        tier = "new"
        try:
            import discounts as _dc
            t = _dc.get_customer_tier(r["id"])
            if isinstance(t, tuple):
                tier = t[0]
        except Exception:
            pass

        if promo["segment"] != "all" and tier != promo["segment"]:
            skipped += 1
            continue

        text, _ = build_personal_message(promo, r)
        try:
            bot_send_func(int(chat_id), text)
            sent += 1
            results.append({"retailer_id": r["id"], "chat_id": chat_id, "status": "SENT"})
        except Exception as e:
            failed += 1
            results.append({"retailer_id": r["id"], "status": "FAILED", "error": str(e)})

    # mark promo as sent
    promo["status"] = "SENT"
    promo["sent_at"] = time.strftime("%d-%b-%Y %H:%M").upper()
    promo["sent_count"] = sent
    _save(PROMOTIONS_FILE, promos)

    # broadcast log
    log = _load(BROADCAST_LOG)
    log.append({
        "promo_id": promo_id,
        "sent_at": promo["sent_at"],
        "sent": sent, "skipped": skipped, "failed": failed,
        "results": results,
    })
    _save(BROADCAST_LOG, log)

    return {"sent": sent, "skipped": skipped, "failed": failed}


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Promotions module loaded.")
    print(f"Existing promos: {len(list_promotions())}")
    p = create_promotion(
        title="Monsoon Health Drive",
        segment="all",
        offer_text="Stock up on ORS, Zinc, and Antibiotics this monsoon.",
        badge_lines=["MONSOON SPECIAL", "12% OFF"],
        valid_until="17-Oct-2026",
        kind="weekly",
    )
    print(f"Created promo: {p['id']}")
