from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
import hashlib
import hmac
import os
import random
import requests
from urllib.parse import unquote
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Meena Agencies Enterprise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# In-memory storage for OTPs (Use Redis in production)
active_otps = {}

class TelegramAuthRequest(BaseModel):
    init_data: str

class OTPRequest(BaseModel):
    telegram_id: str

class PlaceOrderRequest(BaseModel):
    telegram_id: str
    otp: str
    cart_items: list

class StockRequest(BaseModel):
    sku: str
    qty: int

def verify_telegram_init_data(init_data: str) -> dict:
    try:
        parsed_data = {}
        for item in init_data.split("&"):
            key, value = item.split("=", 1)
            parsed_data[key] = unquote(value)
        
        received_hash = parsed_data.pop("hash", None)
        if not received_hash: return None
            
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash == received_hash:
            user_data = json.loads(parsed_data.get("user", "{}"))
            return {
                "id": f"TG_{user_data.get('id', 'UNKNOWN')}",
                "shop": f"{user_data.get('first_name', 'Telegram')} {user_data.get('last_name', 'User')}",
                "role": "owner",
                "phone": "Telegram",
                "telegram_chat_id": user_data.get('id')
            }
        return None
    except Exception as e:
        print("Verification error:", e)
        return None

@app.post("/api/telegram_login")
def telegram_login(req: TelegramAuthRequest):
    if req.init_data == "mock_data_for_demo":
        return {"id": "TG_DEMO_123", "shop": "Meena Agencies (Demo)", "role": "owner", "phone": "Telegram", "telegram_chat_id": "123456789"}
    user = verify_telegram_init_data(req.init_data)
    if user: return user
    raise HTTPException(status_code=401, detail="Invalid Telegram Data")

@app.get("/api/products")
def get_products():
    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists(): return []
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT sku, qty FROM products LIMIT 50")
    products = [{"name": row[0], "price": 150.0, "stock": row[1]} for row in c.fetchall()]
    conn.close()
    return products

# ─── NEW: SEND OTP VIA TELEGRAM ───
@app.post("/api/request_order_otp")
def request_otp(req: OTPRequest):
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        # Fallback for demo
        active_otps[req.telegram_id] = "123456"
        return {"status": "demo_mode", "otp": "123456"}

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    active_otps[req.telegram_id] = otp

    # Send via Telegram Bot API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": req.telegram_id,
        "text": f"🦚 *Meena Agencies Security*\n\nYour OTP for placing the order is: *{otp}*\n\nDo not share this code with anyone.",
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to send Telegram message")
    except Exception as e:
        print("Telegram API Error:", e)
        # For local testing without a real chat ID, return the OTP in the response
        return {"status": "error_but_bypassed", "otp": otp}
        
    return {"status": "success"}

# ─── NEW: VERIFY OTP & PLACE ORDER ───
@app.post("/api/place_order")
def place_order(req: PlaceOrderRequest):
    # 1. Verify OTP
    stored_otp = active_otps.get(req.telegram_id)
    
    if not stored_otp or stored_otp != req.otp:
        raise HTTPException(status_code=401, detail="Invalid or Expired OTP")
    
    # Clear OTP after successful use
    del active_otps[req.telegram_id]

    # 2. Save Order to DB (Simulated here)
    order_id = f"ORD-{random.randint(1000, 9999)}"
    total = sum(item.get("price", 0) * item.get("qty", 1) for item in req.cart_items)
    
    # In production, save to SQLite/Postgres `orders` table here

    return {"status": "success", "order_id": order_id, "total": total, "message": "Order Placed Securely!"}

@app.post("/api/add_stock")
def add_stock(req: StockRequest):
    db_path = BASE_DIR / "meena_enterprise.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE products SET qty = qty + ? WHERE sku = ?", (req.qty, req.sku))
    conn.commit()
    conn.close()
    return {"status": "success"}
