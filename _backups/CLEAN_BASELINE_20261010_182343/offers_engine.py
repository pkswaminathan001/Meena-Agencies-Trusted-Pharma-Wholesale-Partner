"""
offers_engine.py — Offers data store, matching, tracking.

Offer schema:
  id           : "OFF001"
  type         : "reorder" | "bulk" | "expiry" | "custom"
  title        : "Reorder Bonus"
  subtitle     : "Order 2× within 15 days"
  discount_pct : 2.0
  min_qty      : 0
  sku_filter   : []                # empty = all SKUs
  valid_from   : "YYYY-MM-DD"
  valid_to     : "YYYY-MM-DD"
  enabled      : True
  views        : [{"rid": "RET001", "at": "..."}]
  claims       : [{"rid": "RET001", "at": "...", "items": [...]}]
"""
from pathlib import Path
from datetime import datetime, date, timedelta
import json

OFFERS_FILE = Path("offers.json")


# ── Default seed offers ──
def default_offers():
    today = date.today()
    end = today + timedelta(days=30)
    end_expiry = today + timedelta(days=21)
    return [
        {
            "id": "OFF001",
            "type": "reorder",
            "title": "🔁 Reorder Bonus",
            "subtitle": "Order 2× within 15 days",
            "discount_pct": 2.0,
            "min_qty": 0,
            "sku_filter": [],
            "valid_from": today.isoformat(),
            "valid_to": end.isoformat(),
            "enabled": True,
            "views": [],
            "claims": [],
        },
        {
            "id": "OFF002",
            "type": "bulk",
            "title": "💊 Bulk Deal",
            "subtitle": "Buy 50 boxes of any SKU — get 1 box free",
            "discount_pct": 2.0,
            "min_qty": 50,
            "sku_filter": [],
            "valid_from": today.isoformat(),
            "valid_to": end.isoformat(),
            "enabled": True,
            "views": [],
            "claims": [],
        },
        {
            "id": "OFF003",
            "type": "expiry",
            "title": "📅 Expiry Saver",
            "subtitle": "Special prices on near-expiry stock",
            "discount_pct": 15.0,
            "min_qty": 0,
            "sku_filter": [],
            "valid_from": today.isoformat(),
            "valid_to": end_expiry.isoformat(),
            "enabled": True,
            "views": [],
            "claims": [],
        },
    ]


def _read_file():
    if not OFFERS_FILE.exists():
        offers = default_offers()
        _write_file(offers)
        return offers
    try:
        return json.loads(OFFERS_FILE.read_text())
    except Exception:
        return default_offers()


def _write_file(offers):
    OFFERS_FILE.write_text(json.dumps(offers, indent=2))


def load_all():
    """Return every offer (including disabled)."""
    return _read_file()


def save_all(offers):
    _write_file(offers)


def create_offer(type_, title, subtitle, discount_pct, min_qty, valid_days=30, sku_filter=None):
    """Create a new offer. Returns the new offer dict."""
    offers = _read_file()
    next_n = max([int(o["id"][3:]) for o in offers if o["id"].startswith("OFF")] + [0]) + 1
    today = date.today()
    new = {
        "id": f"OFF{next_n:03d}",
        "type": type_,
        "title": title,
        "subtitle": subtitle,
        "discount_pct": float(discount_pct),
        "min_qty": int(min_qty),
        "sku_filter": sku_filter or [],
        "valid_from": today.isoformat(),
        "valid_to": (today + timedelta(days=int(valid_days))).isoformat(),
        "enabled": True,
        "views": [],
        "claims": [],
    }
    offers.append(new)
    _write_file(offers)
    return new


def toggle_offer(offer_id):
    offers = _read_file()
    for o in offers:
        if o["id"] == offer_id:
            o["enabled"] = not o.get("enabled", True)
            break
    _write_file(offers)


def delete_offer(offer_id):
    offers = [o for o in _read_file() if o["id"] != offer_id]
    _write_file(offers)


def _is_active(o):
    """Enabled + today within date range."""
    if not o.get("enabled", True):
        return False
    try:
        today = date.today()
        vfrom = datetime.fromisoformat(o["valid_from"]).date()
        vto = datetime.fromisoformat(o["valid_to"]).date()
        return vfrom <= today <= vto
    except Exception:
        return False


def days_left(o):
    try:
        vto = datetime.fromisoformat(o["valid_to"]).date()
        return max(0, (vto - date.today()).days)
    except Exception:
        return 0


def get_offers_for_retailer(retailer):
    """Return offers visible to this retailer (active only)."""
    if not retailer:
        return []
    rid = retailer.get("id", "")
    return [o for o in _read_file() if _is_active(o) and _matches(o, retailer, rid)]


def _matches(o, retailer, rid):
    """Simplified: all offers visible to all retailers (extendable)."""
    # Future: check tier, past purchases, region
    return True


def track_view(offer_id, retailer_id):
    """Record a view (dedup per retailer per day)."""
    offers = _read_file()
    today = date.today().isoformat()
    for o in offers:
        if o["id"] == offer_id:
            views = o.setdefault("views", [])
            already = any(
                v.get("rid") == retailer_id and v.get("at", "").startswith(today)
                for v in views
            )
            if not already:
                views.append({"rid": retailer_id, "at": datetime.now().isoformat(timespec="seconds")})
                _write_file(offers)
            return


def track_claim(offer_id, retailer_id, items=None):
    """Record a claim."""
    offers = _read_file()
    for o in offers:
        if o["id"] == offer_id:
            o.setdefault("claims", []).append({
                "rid": retailer_id,
                "at": datetime.now().isoformat(timespec="seconds"),
                "items": items or [],
            })
            _write_file(offers)
            return


def stats(offer_id):
    """Return (views_count, claims_count, unique_viewers, unique_claimers)."""
    for o in _read_file():
        if o["id"] == offer_id:
            views = o.get("views", [])
            claims = o.get("claims", [])
            return (
                len(views),
                len(claims),
                len({v.get("rid") for v in views}),
                len({c.get("rid") for c in claims}),
            )
    return 0, 0, 0, 0


if __name__ == "__main__":
    print("Seeding offers.json...")
    _write_file(default_offers())
    print("✅ offers.json created with 3 default offers")
    for o in load_all():
        print(f"   {o['id']}  {o['title']}  ·  {o['discount_pct']}%  ·  ends {o['valid_to']}")
