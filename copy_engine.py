"""
copy_engine.py v2 — B2B pharma copy. Offer-first, ethical, verifiable.
Headline = the WIN. Subhead = the WINDOW. Trust = the footer.
"""
from datetime import datetime
import random

BANK = {
    # NEW: give a reason to try once
    "new": {
        "reciprocity": [
            "Your first order comes with an extra 2% off.",
            "One trial. If it doesn't move, return it.",
        ],
        "social_proof": [
            "200+ pharmacies in Thanjavur already stock with us.",
            "The shop next door orders here every week.",
        ],
        "info_gap": [
            "You're probably overpaying on 3 of your top SKUs.",
            "One price list. Zero hidden margins. Zero drama.",
        ],
    },
    # SILVER: grow the basket
    "silver": {
        "consistency": [
            "Time to restock {top_sku} again.",
            "Your shelf runs on this. Keep it full.",
        ],
        "anchoring": [
            "MRP ₹{mrp} · Your price ₹{wholesale} · Save ₹{save}/strip",
            "You save ₹{save} on every strip this week.",
        ],
        "scarcity": [
            "Only {stock} boxes left at this rate.",
            "Next lot arrives at +{pct}%. Lock this one.",
        ],
    },
    # GOLD: reward loyalty, upsell
    "gold": {
        "reciprocity": [
            "You've ordered {n} times. This one's on us margin-wise.",
            "Loyalty price. Locked for you this week.",
        ],
        "consistency": [
            "Same SKU, same cycle, better price.",
            "Your usual order, {pct}% cheaper today.",
        ],
        "commitment": [
            "Reserve your {qty}-box lot. Pay on delivery.",
            "We'll hold your lot till 9 AM. No prepayment.",
        ],
    },
    # PLATINUM: VIP exclusivity
    "platinum": {
        "reciprocity": [
            "Platinum price — locked for the quarter.",
            "You've earned this margin. Take it.",
        ],
        "authority": [
            "Priority dispatch. Your lot ships first.",
            "First pick of every new lot. Always.",
        ],
        "commitment": [
            "Reserved for you till 9 AM.",
            "Your lot is held. One reply to dispatch.",
        ],
    },
}

SUBHEADS = {
    "flash":     "7:00 AM – 9:00 AM only.",
    "daily":     "Valid till 9 PM today.",
    "weekly":    "Valid till Sunday.",
    "monthly":   "Valid this month.",
    "bulk":      "Bulk rate applies on 20+ boxes.",
    "clearance": "Closing stock. First come, first served.",
}

CTAS = [
    "Order now: 7338824033",
    "WhatsApp 7338824033",
    "Reply YES to lock this lot",
    "Call 7338824033 — dispatch today",
]

PRIORITY = {
    "new":      ["social_proof", "reciprocity", "info_gap"],
    "silver":   ["anchoring", "consistency", "scarcity"],
    "gold":     ["reciprocity", "consistency", "commitment"],
    "platinum": ["reciprocity", "authority", "commitment"],
}

def _fmt(template, ctx):
    class _Safe(dict):
        def __missing__(self, k): return "{" + k + "}"
    return template.format_map(_Safe(ctx))

def generate_copy(segment="new", principle=None, context=None, kind="flash"):
    ctx = context or {}
    segment = segment if segment in BANK else "new"
    principles = PRIORITY.get(segment, ["social_proof"])

    if principle and principle in BANK[segment]:
        chosen = principle
    else:
        chosen = random.choice(principles)

    options = BANK[segment].get(chosen) or BANK[segment][principles[0]]
    headline = _fmt(random.choice(options), ctx)
    return {
        "headline": headline,
        "subhead":  SUBHEADS.get(kind, SUBHEADS["daily"]),
        "cta":      random.choice(CTAS),
        "principle_used": chosen,
    }

def build_context(retailer=None, product=None, orders=None, city="Thanjavur"):
    ctx = {"city": city}
    if product:
        mrp = product.get("mrp")
        wholesale = product.get("wholesale_price")
        if mrp and wholesale:
            ctx["mrp"] = mrp
            ctx["wholesale"] = wholesale
            ctx["save"] = round(mrp - wholesale, 2)
            if mrp > 0:
                ctx["pct"] = round((mrp - wholesale) / mrp * 100, 1)
        if product.get("stock") is not None:
            ctx["stock"] = product["stock"]
        if product.get("sku"):
            ctx["top_sku"] = product["sku"]
    if retailer and orders:
        from datetime import datetime as _dt
        mine = [o for o in orders if o.get("retailer_id") == retailer["id"]]
        ctx["n"] = len(mine)
        try:
            last = max(o.get("placed_at", "") for o in mine)
            last_dt = _dt.strptime(last, "%d-%b-%Y %H:%M")
            cycle = retailer.get("reorder_cycle_days", 22)
            days = (_dt.now() - last_dt).days
            ctx["cycle"] = cycle
            ctx["days"] = max(0, cycle - days)
        except Exception:
            pass
    return ctx

if __name__ == "__main__":
    ctx = {"mrp": 30.0, "wholesale": 22.0, "save": 8.0, "pct": 27.0,
           "stock": 3, "cycle": 22, "days": 4, "n": 47, "qty": 20,
           "city": "Thanjavur", "top_sku": "Dolo 650"}
    for seg in ("new", "silver", "gold", "platinum"):
        c = generate_copy(segment=seg, context=ctx, kind="flash")
        print(f"[{seg:>8} | {c['principle_used']:>12}] {c['headline']}")
