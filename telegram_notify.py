"""
telegram_notify.py — Standalone Telegram order alert.
"""
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

CONFIG = "telegram_config.json"

def load_config():
    if not Path(CONFIG).exists():
        print(f"❌ {CONFIG} not found.")
        return None
    return json.loads(Path(CONFIG).read_text())

def send_message(text: str) -> bool:
    cfg = load_config()
    if not cfg: return False
    
    token = cfg.get("bot_token", "")
    chat_id = cfg.get("owner_chat_id", "")
    if "PASTE" in token or not token:
        print("Config not filled in.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode()).get("ok", False)
    except Exception as e:
        print("Telegram error:", e)
        return False

def send_order_alert(order: dict, retailer: dict) -> bool:
    items = "\n".join(f"• {it.get('name', 'Item')} × {it.get('qty', 1)} = ₹{it.get('qty', 1)*it.get('price', 0):.2f}"
                      for it in order.get("items", []))
    text = (
        f"🛒 NEW ORDER RECEIVED\n"
        f"Order: {order.get('order_id','—')}\n"
        f"Shop: {retailer.get('shop','—')}\n"
        f"Owner: {retailer.get('owner','—')}\n"
        f"Phone: {retailer.get('phone','—')}\n\n"
        f"{items}\n\n"
        f"TOTAL: ₹{order.get('total',0):,.2f}\n"
        f"Placed: {order.get('placed_at', datetime.now().strftime('%d-%b-%Y %H:%M').upper())}"
    )
    return send_message(text)

if __name__ == "__main__":
    ok = send_message("✅ Meena Agencies Telegram test — setup works!")
    print("Sent!" if ok else "Failed. Check token and chat_id.")
