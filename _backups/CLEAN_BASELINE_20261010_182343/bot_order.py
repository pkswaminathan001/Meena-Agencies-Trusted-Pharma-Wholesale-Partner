"""
bot_order.py — Conversation-driven order session engine for Telegram bot.
Tracks multi-turn conversations, matches products, builds cart, and creates orders.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import bot_otp
import bot_query


SESSION_FILE = Path("bot_order_sessions.json")
SESSION_TIMEOUT_MINUTES = 30

# Session states
ST_IDLE = "idle"
ST_PICK_VARIANT = "pick_variant"
ST_PICK_QTY = "pick_qty"
ST_CONFIRMING = "confirming"
ST_AWAITING_OTP = "awaiting_otp"
ST_PLACED = "placed"


def _load_sessions():
    if not SESSION_FILE.exists():
        return {}
    try:
        return json.loads(SESSION_FILE.read_text())
    except Exception:
        return {}


def _save_sessions(data):
    try:
        SESSION_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def _cleanup(data):
    """Remove stale sessions."""
    cutoff = (datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat()
    return {k: v for k, v in data.items() if v.get("updated_at", "") > cutoff}


def get_session(chat_id: int) -> dict:
    """Get or create a session for this chat."""
    data = _load_sessions()
    data = _cleanup(data)
    key = str(chat_id)
    if key not in data:
        data[key] = {
            "chat_id": chat_id,
            "retailer_id": None,
            "state": ST_IDLE,
            "items": [],
            "current_variants": [],
            "current_medicine": None,
            "order_id": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        _save_sessions(data)
    return data[key]


def update_session(chat_id: int, **kwargs):
    data = _load_sessions()
    key = str(chat_id)
    if key not in data:
        data[key] = {}
    data[key].update(kwargs)
    data[key]["updated_at"] = datetime.now().isoformat()
    _save_sessions(data)


def clear_session(chat_id: int):
    data = _load_sessions()
    data.pop(str(chat_id), None)
    _save_sessions(data)


# ═══════════════════════════════════════════════════════════
# PRODUCT SEARCH
# ═══════════════════════════════════════════════════════════

def search_variants(query: str, limit: int = 5) -> list:
    """
    Search inventory for medicines matching the query.
    Returns unique medicine names with lowest price (best deal).
    """
    inv = bot_query._load_inventory()
    if inv is None or len(inv) == 0:
        return []

    # Find all matching rows
    matches = inv[inv["medicine_name"].astype(str)
                  .str.contains(query, case=False, na=False)]

    if len(matches) == 0:
        return []

    # Group by medicine_name, keep cheapest in-stock batch per medicine
    by_name = {}
    for _, row in matches.iterrows():
        name = str(row.get("medicine_name", "")).strip()
        qty = int(row.get("quantity", 0) or 0)
        if qty <= 0:
            continue
        price = float(row.get("selling_price", 0) or row.get("price", 0) or 0)
        if name not in by_name:
            by_name[name] = {
                "medicine_name": name,
                "total_qty": 0,
                "price": price,
                "mrp": float(row.get("mrp", price * 1.3) or 0),
                "batches": 0,
            }
        by_name[name]["total_qty"] += qty
        by_name[name]["batches"] += 1
        # Track cheapest price for this medicine
        if price > 0 and (by_name[name]["price"] == 0 or price < by_name[name]["price"]):
            by_name[name]["price"] = price

    # Sort by quantity (most available first), limit to top N
    result = sorted(by_name.values(), key=lambda x: -x["total_qty"])
    return result[:limit]


def get_medicine_by_name(name: str) -> dict:
    """Get full info for a medicine by exact name."""
    inv = bot_query._load_inventory()
    if inv is None or len(inv) == 0:
        return None

    matches = inv[inv["medicine_name"].astype(str).str.strip() == name.strip()]
    if len(matches) == 0:
        return None

    total_qty = int(matches["quantity"].sum())
    price = float(matches["selling_price"].iloc[0] or 0) if "selling_price" in matches.columns else 0

    return {
        "medicine_name": name,
        "total_qty": total_qty,
        "price": price,
        "batches": len(matches),
    }


# ═══════════════════════════════════════════════════════════
# CART OPERATIONS
# ═══════════════════════════════════════════════════════════

def add_to_cart(chat_id: int, medicine_name: str, qty: int):
    """Add item to session cart."""
    session = get_session(chat_id)
    items = session.get("items", [])

    # Get price
    med = get_medicine_by_name(medicine_name)
    price = med["price"] if med else 0

    # Check if already in cart
    for it in items:
        if it["medicine"] == medicine_name:
            it["qty"] += qty
            update_session(chat_id, items=items)
            return it

    items.append({
        "medicine": medicine_name,
        "qty": qty,
        "price": price,
    })
    update_session(chat_id, items=items)
    return items[-1]


def cart_total(chat_id: int) -> float:
    """Return total ₹ of cart."""
    session = get_session(chat_id)
    total = 0.0
    for it in session.get("items", []):
        total += it.get("qty", 0) * it.get("price", 0)
    return total


def cart_summary(chat_id: int) -> str:
    """Return human-readable cart summary."""
    session = get_session(chat_id)
    items = session.get("items", [])
    if not items:
        return "Cart is empty."

    lines = []
    for it in items:
        line_total = it["qty"] * it["price"]
        lines.append(f"• {it['medicine']} × {it['qty']} = ₹{line_total:,.0f}")

    lines.append("")
    lines.append(f"💰 Total: ₹{cart_total(chat_id):,.0f}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# ORDER CREATION
# ═══════════════════════════════════════════════════════════

def create_order(chat_id: int, retailer: dict) -> dict:
    """
    Create a pending order from the session cart.
    Returns order dict (not yet saved).
    """
    session = get_session(chat_id)
    items = session.get("items", [])
    if not items:
        return None

    order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}"

    order = {
        "order_id": order_id,
        "retailer_id": retailer.get("id"),
        "shop": retailer.get("shop"),
        "items": [
            {
                "medicine": it["medicine"],
                "qty": it["qty"],
                "price": it["price"],
                "batch": "",
            }
            for it in items
        ],
        "total": cart_total(chat_id),
        "status": "Awaiting OTP",
        "placed_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
        "location": retailer.get("address", ""),
        "source": "telegram_chat",
    }
    return order


def save_order(order: dict):
    """Append order to orders.json."""
    orders_file = Path("orders.json")
    try:
        orders = json.loads(orders_file.read_text()) if orders_file.exists() else []
    except Exception:
        orders = []
    orders.append(order)
    orders_file.write_text(json.dumps(orders, indent=2))


if __name__ == "__main__":
    print("=== bot_order.py self-test ===\n")

    # Test variant search
    print("Variants for 'dolo':")
    for v in search_variants("dolo"):
        print(f"  {v['medicine_name']} — ₹{v['price']:.0f} × {v['total_qty']} units")

    print("\nVariants for 'amoxi':")
    for v in search_variants("amoxi"):
        print(f"  {v['medicine_name']} — ₹{v['price']:.0f} × {v['total_qty']} units")

    print("\nVariants for 'insulin':")
    for v in search_variants("insulin"):
        print(f"  {v['medicine_name']} — ₹{v['price']:.0f} × {v['total_qty']} units")

    # Test cart
    print("\n─── Cart test ───")
    test_chat = 999999
    clear_session(test_chat)

    add_to_cart(test_chat, "Amoxicillin 250mg", 10)
    add_to_cart(test_chat, "Paracetamol 500mg", 5)
    add_to_cart(test_chat, "Amoxicillin 250mg", 5)  # merge
    print(cart_summary(test_chat))
    print(f"\nCart total: ₹{cart_total(test_chat):,.2f}")

    clear_session(test_chat)
    print("\n✅ Session cleared.")
