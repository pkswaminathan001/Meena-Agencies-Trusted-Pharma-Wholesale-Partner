"""
middleware.py — Multi-tenant isolation for Meena Agencies Telegram bot.

LAWS enforced here:
  1. Retailer identity comes ONLY from incoming chat_id, never message body.
  2. Every order/query filters by resolved retailer.
  3. Owner commands only work for OWNER_CHAT_ID.
  4. No group chats. No fallthrough to "unknown" user data.
  5. Every cross-tenant attempt is logged.
"""
import os, json, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    filename="security.log",
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

RETAILERS_FILE = Path("retailers.json")
ENV_FILE = Path(".env")


def _load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0") or 0)


def _load_retailers():
    if not RETAILERS_FILE.exists():
        return []
    try:
        return json.loads(RETAILERS_FILE.read_text())
    except Exception:
        return []


def resolve_identity(chat_id):
    """
    Return the identity of the person on the other end of this chat_id.
    NEVER trust anything else.

    Returns:
      {"role": "owner"|"retailer"|"unknown",
       "chat_id": int,
       "retailer": dict|None}
    """
    chat_id = int(chat_id)

    # Owner check FIRST — owner is a separate role
    if OWNER_CHAT_ID and chat_id == OWNER_CHAT_ID:
        return {"role": "owner", "chat_id": chat_id, "retailer": None}

    # Retailer: match chat_id exactly
    for r in _load_retailers():
        tid = str(r.get("telegram_chat_id", "")).strip()
        if tid and tid == str(chat_id):
            return {"role": "retailer", "chat_id": chat_id, "retailer": r}

    # Unknown caller — log and reject
    logging.warning(f"UNKNOWN_CHAT_ID chat_id={chat_id} — not owner, not registered retailer")
    return {"role": "unknown", "chat_id": chat_id, "retailer": None}


def require_owner(chat_id):
    """Raise if not owner. Use in every owner-only command."""
    ident = resolve_identity(chat_id)
    if ident["role"] != "owner":
        logging.warning(f"OWNER_COMMAND_DENIED chat_id={chat_id} role={ident['role']}")
        raise PermissionError("Owner-only command.")
    return ident


def require_retailer(chat_id):
    """Return retailer dict or raise. Use in every retailer command."""
    ident = resolve_identity(chat_id)
    if ident["role"] != "retailer":
        logging.warning(f"RETAILER_COMMAND_DENIED chat_id={chat_id} role={ident['role']}")
        raise PermissionError("Not a registered retailer.")
    return ident["retailer"]


def filter_orders_for(chat_id, orders):
    """Given a list of all orders, return only those for the caller's retailer."""
    ident = resolve_identity(chat_id)
    if ident["role"] == "owner":
        return list(orders)   # owner sees all
    if ident["role"] == "retailer":
        rid = ident["retailer"]["id"]
        return [o for o in orders if o.get("retailer_id") == rid]
    return []  # unknown gets nothing


def audit(chat_id, action, extra=""):
    """Log every sensitive action for traceability."""
    ident = resolve_identity(chat_id)
    line = f"AUDIT chat_id={chat_id} role={ident['role']} action={action} {extra}"
    logging.warning(line)
    # Also append a plain-text audit trail
    with open("security_audit.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} | {line}\n")


if __name__ == "__main__":
    print("=== middleware self-test ===")
    print(f"OWNER_CHAT_ID from .env: {OWNER_CHAT_ID}")
    for tid in [OWNER_CHAT_ID, 953358258, 111111, 0]:
        ident = resolve_identity(tid)
        print(f"  chat_id={tid:>12} -> role={ident['role']:9} "
              f"retailer={ident['retailer']['id'] if ident['retailer'] else '-'}")
