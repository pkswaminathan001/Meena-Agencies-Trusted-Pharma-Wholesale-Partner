"""
order_notifier.py — sends order alerts to employee, owner, and customer (with ad).
Called from Streamlit app after order is placed.
"""
import os, json, logging
from pathlib import Path

try:
    import requests
    HAS_REQ = True
except ImportError:
    HAS_REQ = False

RETAILERS_FILE  = Path("retailers.json")
PROMOTIONS_FILE = Path("promotions.json")
LOG             = Path("order_notifications.log")

logging.basicConfig(filename=str(LOG), level=logging.INFO,
                    format="%(asctime)s | %(message)s")


def _env(key, default=""):
    p = Path(".env")
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return default


TOKEN = _env("TELEGRAM_BOT_TOKEN")
OWNER = _env("OWNER_CHAT_ID")
EMPLOYEE = _env("EMPLOYEE_CHAT_ID")  # add to .env if you have staff chat
API = f"https://api.telegram.org/bot{TOKEN}"


def _send(chat_id, text, buttons=None):
    if not chat_id or not HAS_REQ:
        return False
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    try:
        r = requests.post(f"{API}/sendMessage", json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logging.error(f"send to {chat_id} failed: {e}")
        return False


def _active_promotion_for(retailer):
    """Find the best current promo for this retailer's tier."""
    try:
        promos = json.loads(PROMOTIONS_FILE.read_text())
    except Exception:
        return None
    if not promos:
        return None

    tier = "new"
    try:
        import discounts as _dc
        t = _dc.get_customer_tier(retailer["id"])
        if isinstance(t, tuple):
            tier = t[0]
    except Exception:
        pass

    # Prefer tier-matching, then 'all'
    for p in reversed(promos):
        if p.get("status") == "SENT":
            continue
        if p.get("segment") in (tier, "all"):
            return p
    return None


def _order_summary(order):
    items = order.get("items", [])
    lines = []
    for it in items[:5]:
        name = it.get("name") or it.get("product") or "item"
        qty  = it.get("qty") or it.get("quantity") or 1
        lines.append(f"  • {name} × {qty}")
    return "\n".join(lines) if lines else "  (no items)"


# ═══════════════════════════════════════════════════════════
# MAIN ENTRY — call this from the Streamlit app
# ═══════════════════════════════════════════════════════════
def on_new_order(order, retailer):
    """
    order = {order_id, retailer_id, items, total, placed_at, ...}
    retailer = {id, shop, owner, telegram_chat_id, ...}
    """
    oid    = order.get("order_id", "?")
    total  = order.get("total", 0)
    shop   = retailer.get("shop", "?")
    owner_name = retailer.get("owner", "")
    chat   = str(retailer.get("telegram_chat_id", "")).strip()

    logging.info(f"NEW_ORDER {oid} shop={shop} total={total}")

    # ─── 1. EMPLOYEE ───
    if EMPLOYEE:
        _send(EMPLOYEE, (
            f"🔔 <b>New order to process</b>\n\n"
            f"<b>{shop}</b> · {owner_name}\n"
            f"Order: <code>{oid}</code>\n"
            f"Total: ₹{total:,.2f}\n\n"
            f"<b>Items</b>\n{_order_summary(order)}\n\n"
            f"→ Open app to approve & dispatch"
        ))

    # ─── 2. OWNER ───
    if OWNER:
        _send(OWNER, (
            f"💰 <b>New order — ₹{total:,.2f}</b>\n\n"
            f"<b>{shop}</b> ({retailer.get('id','')})\n"
            f"Order: <code>{oid}</code>\n\n"
            f"<b>Items</b>\n{_order_summary(order)}\n\n"
            f"<i>Outstanding: ₹{retailer.get('outstanding',0):,.0f}</i>"
        ))

    # ─── 3. CUSTOMER — confirmation + AD ───
    if chat:
        promo = _active_promotion_for(retailer)
        msg = (
            f"✅ <b>Order confirmed — {oid}</b>\n\n"
            f"Dear {owner_name},\n"
            f"Thank you for your order! 🙏\n\n"
            f"<b>Items</b>\n{_order_summary(order)}\n\n"
            f"<b>Total: ₹{total:,.2f}</b>\n"
            f"Delivery to: {shop}\n"
            f"Placed: {order.get('placed_at','')}"
        )

        if promo:
            msg += (
                f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌟 <b>{promo['title']}</b>\n\n"
                f"{promo.get('offer_text','')}\n"
            )
            if promo.get("valid_until"):
                msg += f"📅 Valid till {promo['valid_until']}\n"
            msg += (
                f"\n🏪 Prepared for: <b>{shop}</b>\n"
                f"📞 Order: 7338824033"
            )

        _send(chat, msg)

    return {"employee": bool(EMPLOYEE), "owner": bool(OWNER), "customer": bool(chat)}


if __name__ == "__main__":
    # Dry self-test with sample data
    sample_order = {
        "order_id": "ORD-TEST-001",
        "retailer_id": "RET001",
        "items": [
            {"name": "Dolo 650", "qty": 20},
            {"name": "ORS Powder", "qty": 10},
        ],
        "total": 8400.0,
        "placed_at": "27-SEP-2026 18:00",
    }
    try:
        sample_retailer = json.loads(RETAILERS_FILE.read_text())[0]
    except Exception:
        sample_retailer = {"id":"RET001","shop":"Sri Balaji Medicals","owner":"Chitra","telegram_chat_id":""}
    print("Self-test result:", on_new_order(sample_order, sample_retailer))
