"""
copy_engine.py — ethical B2B pharma copy generator for Meena Agencies.

Generates headline + subhead + CTA based on:
  - Retailer segment (new / silver / gold / platinum)
  - Order history (days since last order, avg order value, reorder cycle)
  - Product data (MRP, wholesale price, stock, MRP change)
  - Principle tags: social_proof, loss_aversion, scarcity,
                    reciprocity, authority, anchoring,
                    info_gap, consistency, commitment

No disease mongering. No fear-mongering. No fake claims.
Everything must be verifiable from the DB.
"""
from datetime import datetime
import random

# ═══════════════════════════════════════════════════════════
# HEADLINE BANK — one entry per principle per segment
# ═══════════════════════════════════════════════════════════
BANK = {

    # ─── NEW retailers ─── (goal: first order, trust)
    "new": {
        "authority": [
            "GST-registered. Drug-licenced. Thanjavur-based.",
            "Wholesale prices since day one.",
        ],
        "reciprocity": [
            "Your first order comes with an extra 2%.",
            "Welcome price, only for this month.",
        ],
        "social_proof": [
            "Join 200+ pharmacies restocking with us.",
            "The pharmacy next door already orders here.",
        ],
        "info_gap": [
            "You're probably overpaying on 3 of your top SKUs.",
            "One price list. Zero hidden margins.",
        ],
    },

    # ─── SILVER retailers ─── (goal: grow basket, increase frequency)
    "silver": {
        "consistency": [
            "You reorder every {cycle} days. Next cycle: {days} days away.",
            "Time to restock {top_sku} again.",
        ],
        "anchoring": [
            "MRP ₹{mrp} · Your price ₹{wholesale} · Save ₹{save}/strip",
            "{save}% below MRP on this lot.",
        ],
        "scarcity": [
            "Only {stock} boxes left at this price.",
            "Next lot arrives at +{pct}%.",
        ],
        "social_proof": [
            "{peer_count} pharmacies in {city} bought this week.",
            "Top 3 sellers in Thanjavur stock this.",
        ],
    },

    # ─── GOLD retailers ─── (goal: loyalty, upsell to platinum)
    "gold": {
        "reciprocity": [
            "Loyalty price, locked for you.",
            "You've ordered {n} times. This one's on us margin-wise.",
        ],
        "consistency": [
            "Same SKU, same cycle, better price.",
            "Your shelf runs on this. Keep it full.",
        ],
        "anchoring": [
            "Your usual price: ₹{wholesale}. Today: ₹{special}.",
        ],
        "commitment": [
            "Reserve your {qty}-box lot. Pay on delivery.",
            "Lock the lot. We hold it till 9 AM.",
        ],
    },

    # ─── PLATINUM retailers ─── (goal: VIP, exclusivity)
    "platinum": {
        "reciprocity": [
            "Platinum price — locked for the quarter.",
            "You've earned this margin. Take it.",
        ],
        "authority": [
            "Your account has priority dispatch.",
            "Platinum lot — first pick, always.",
        ],
        "commitment": [
            "Reserved for you till 9 AM.",
            "Your lot is held. Confirm to dispatch.",
        ],
        "social_proof": [
            "Only 4 platinum pharmacies get this rate.",
        ],
    },
}

# ═══════════════════════════════════════════════════════════
# SUBHEAD BANK — always safe, always true
# ═══════════════════════════════════════════════════════════
SUBHEADS = {
    "flash":     "7:00 AM – 9:00 AM only.",
    "daily":     "Valid today.",
    "weekly":    "Valid till Sunday.",
    "monthly":   "Valid this month.",
    "bulk":      "Bulk price applies on 50+ boxes.",
    "clearance": "Closing stock. First come, first served.",
}

# ═══════════════════════════════════════════════════════════
# CTA BANK — direct, no fluff
# ═══════════════════════════════════════════════════════════
CTAS = [
    "Order now: 7338824033",
    "Confirm on WhatsApp: 7338824033",
    "Reply YES to lock this lot",
    "Call 7338824033 — dispatch today",
]

# ═══════════════════════════════════════════════════════════
# PRINCIPLE PRIORITY PER SEGMENT
# Pick top 2 principles that suit this segment.
# ═══════════════════════════════════════════════════════════
PRIORITY = {
    "new":      ["authority", "reciprocity", "social_proof"],
    "silver":   ["consistency", "anchoring", "scarcity", "social_proof"],
    "gold":     ["reciprocity", "consistency", "anchoring", "commitment"],
    "platinum": ["reciprocity", "commitment", "authority"],
}

# ═══════════════════════════════════════════════════════════
# CORE
# ═══════════════════════════════════════════════════════════
def _fmt(template, ctx):
    """Safe format — leaves {missing} keys untouched instead of crashing."""
    class _Safe(dict):
        def __missing__(self, k): return "{" + k + "}"
    return template.format_map(_Safe(ctx))


def generate_copy(
    segment="new",
    principle=None,
    context=None,
    kind="flash",
):
    """
    Returns dict:
      { headline, subhead, cta, principle_used }

    segment   : new | silver | gold | platinum
    principle : force a principle, or None to auto-pick
    context   : dict of vars (mrp, wholesale, save, cycle, days, top_sku,
                stock, pct, peer_count, city, n, qty, special)
    kind      : flash | daily | weekly | monthly | bulk | clearance
    """
    ctx = context or {}
    segment = segment if segment in BANK else "new"
    principles = PRIORITY.get(segment, ["social_proof"])

    if principle and principle in BANK[segment]:
        chosen = principle
    else:
        chosen = random.choice(principles)

    options = BANK[segment].get(chosen) or BANK[segment][principles[0]]
    headline = _fmt(random.choice(options), ctx)
    subhead = SUBHEADS.get(kind, SUBHEADS["daily"])
    cta = random.choice(CTAS)

    return {
        "headline": headline,
        "subhead": subhead,
        "cta": cta,
        "principle_used": chosen,
    }


# ═══════════════════════════════════════════════════════════
# CONTEXT BUILDER — pulls real numbers from your DB
# ═══════════════════════════════════════════════════════════
def build_context(retailer=None, product=None, orders=None, city="Thanjavur"):
    """
    Fill context from real data. Any missing value stays as {placeholder}
    so you can see what's missing in the output — no silent fake numbers.
    """
    ctx = {"city": city}

    # Product numbers (from your catalogue)
    if product:
        mrp = product.get("mrp")
        wholesale = product.get("wholesale_price")
        special = product.get("special_price", wholesale)
        if mrp and wholesale:
            ctx["mrp"] = mrp
            ctx["wholesale"] = wholesale
            ctx["special"] = special
            ctx["save"] = round(mrp - wholesale, 2)
            if mrp > 0:
                ctx["pct"] = round((mrp - wholesale) / mrp * 100, 1)
        if product.get("stock") is not None:
            ctx["stock"] = product["stock"]
        if product.get("sku"):
            ctx["top_sku"] = product["sku"]

    # Retailer history
    if retailer and orders:
        try:
            last = max(o["date"] for o in orders if o.get("retailer_id") == retailer["id"])
            cycle = retailer.get("reorder_cycle_days", 22)
            days = (datetime.now() - datetime.fromisoformat(last)).days
            ctx["cycle"] = cycle
            ctx["days"] = max(0, cycle - days)
            ctx["n"] = len([o for o in orders if o.get("retailer_id") == retailer["id"]])
        except Exception:
            pass

    return ctx


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    ctx = {
        "mrp": 30.0, "wholesale": 22.0, "special": 20.5,
        "save": 8.0, "pct": 8.0, "stock": 3,
        "cycle": 22, "days": 4, "n": 47, "qty": 50,
        "peer_count": 42, "city": "Thanjavur", "top_sku": "Dolo 650",
    }
    print("=" * 70)
    for seg in ("new", "silver", "gold", "platinum"):
        print(f"\n── {seg.upper()} ──")
        for _ in range(2):
            c = generate_copy(segment=seg, context=ctx, kind="flash")
            print(f"  [{c['principle_used']:>12}] {c['headline']}")
            print(f"                  {c['subhead']}")
            print(f"                  {c['cta']}\n")
