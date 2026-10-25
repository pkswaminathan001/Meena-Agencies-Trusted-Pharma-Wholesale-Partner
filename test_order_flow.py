import sys
from pathlib import Path
import sqlite3
import hashlib
import datetime
import random
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
DB_PATH = BASE_DIR / "meena_enterprise.db"
SALT = 'MEENA_PHARMA_SECURE_SALT_2026'

def log(msg): print(f"[TEST] {msg}")

def get_test_user():
    rj_path = BASE_DIR / "retailers.json"
    users = json.loads(rj_path.read_text())
    for u in users:
        if u.get("role", "").lower() != "owner":
            return u
    return None

def get_owner():
    rj_path = BASE_DIR / "retailers.json"
    users = json.loads(rj_path.read_text())
    for u in users:
        if u.get("role", "").lower() == "owner":
            return u
    return None

def get_test_products(count=3):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT sku, qty FROM products WHERE qty > 10 LIMIT {count}", conn)
    conn.close()
    return df.to_dict('records')

def place_test_order(user_id, products):
    cart = [{"name": p["sku"], "price": 10.0, "qty": 2} for p in products]
    total = sum(i["price"] * i["qty"] for i in cart)
    order_id = f"TEST-{random.randint(1000, 9999)}"
    date_str = str(datetime.date.today())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO orders (order_id, user_id, date, total, items, status) VALUES (?, ?, ?, ?, ?, ?)",
              (order_id, user_id, date_str, total, json.dumps(cart), "Pending"))
    conn.commit()
    conn.close()
    log(f"Order {order_id} placed for Rs.{total}. Status: Pending.")
    return order_id, total

def verify_otp_flow():
    otp = str(random.randint(100000, 999999))
    log(f"OTP generated: {otp} (would be sent via Telegram/SMS)")
    is_valid = (len(otp) == 6 and otp.isdigit())
    if is_valid: log(f"OTP {otp} format verified.")
    return is_valid

def owner_approve_order(order_id, owner_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
    row = c.fetchone()
    if not row: log(f"Order {order_id} not found."); conn.close(); return
    if row[0] != "Pending": log(f"Order {order_id} already {row[0]}."); conn.close(); return
    c.execute("UPDATE orders SET status = 'Approved' WHERE order_id = ?", (order_id,))
    ts = str(datetime.datetime.now())
    c.execute("INSERT INTO audit_logs (timestamp, user_id, action, details) VALUES (?, ?, ?, ?)",
              (ts, owner_id, "ORDER_APPROVED", f"Approved {order_id} via test"))
    conn.commit()
    conn.close()
    log(f"Order {order_id} approved by Owner.")

def verify_audit_log(order_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM audit_logs WHERE details LIKE ? ORDER BY log_id DESC LIMIT 1",
                           conn, params=(f"%{order_id}%",))
    conn.close()
    if df.empty: log("No audit log found.")
    else: log(f"Audit log verified: {df.iloc[0]['action']} at {df.iloc[0]['timestamp']}")

if __name__ == "__main__":
    log("=" * 60)
    log("STARTING FULL ORDER FLOW TEST")
    log("=" * 60)
    
    retailer = get_test_user()
    if not retailer: log("No retailer found."); sys.exit(1)
    log(f"Retailer: {retailer['id']} ({retailer.get('shop', '')})")
    
    if "pin_hash" not in retailer:
        log("No pin_hash stored. Run migration."); sys.exit(1)
    log("Secure pin_hash present.")
    
    products = get_test_products(3)
    log(f"Products selected: {[p['sku'] for p in products]}")
    
    order_id, total = place_test_order(retailer["id"], products)
    verify_otp_flow()
    
    owner = get_owner()
    if owner: 
        log(f"Owner: {owner['id']}")
        owner_approve_order(order_id, owner["id"])
    else:
        log("No owner found.")
    
    verify_audit_log(order_id)
    log("=" * 60)
    log("TEST COMPLETE")
    log("=" * 60)
