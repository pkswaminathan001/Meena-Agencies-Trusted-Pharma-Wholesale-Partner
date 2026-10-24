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
from datetime import datetime

load_dotenv()

import os
ENV = os.getenv("ENV", "development")
app = FastAPI(title="Meena Agencies Enterprise API", docs_url="/docs" if ENV != "production" else None, redoc_url="/redoc" if ENV != "production" else None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# In-memory storage for locations (clears on restart, perfect for testing)
active_locations = {}

# In-memory storage for OTPs
active_otps = {}

class TelegramAuthRequest(BaseModel):
    init_data: str

class OTPRequest(BaseModel):
    telegram_id: str

class SaveOrderRequest(BaseModel):
    telegram_id: str
    cart_items: list
    payment_id: str

class LocationUpdate(BaseModel):
    telegram_id: str
    name: str
    lat: float
    lon: float

# ─── LOCATION ENDPOINTS ───
@app.post("/api/update_location")
def update_location(req: LocationUpdate):
    active_locations[req.telegram_id] = {
        "name": req.name,
        "lat": req.lat,
        "lon": req.lon,
        "time": datetime.now().strftime("%I:%M:%S %p")
    }
    return {"status": "success"}

@app.get("/api/get_locations")
def get_locations():
    return active_locations

# ─── EXISTING ENDPOINTS ───
def send_telegram_message(chat_id, text):
    if not BOT_TOKEN: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except: pass

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
                "telegram_chat_id": str(user_data.get('id', '123456789'))
            }
        return None
    except: return None

@app.post("/api/telegram_login")
def telegram_login(req: TelegramAuthRequest):
    if req.init_data == "mock_data_for_demo":
        return {"id": "TG_DEMO_123", "shop": "Meena Agencies (Demo)", "role": "owner", "phone": "Telegram", "telegram_chat_id": "8205802064"}
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
    products = [{"name": row[0], "price": 1.0, "stock": row[1]} for row in c.fetchall()]
    conn.close()
    return products
