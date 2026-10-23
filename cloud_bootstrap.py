import streamlit as st
import os
import csv
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@st.cache_resource
def ensure_data_exists():

    """Automatically generates 10k SKUs and DB if missing (Cloud Restart Fix)"""
    db_path = BASE_DIR / "meena_enterprise.db"
    csv_path = BASE_DIR / "inventory.csv"
    
    if db_path.exists() and csv_path.exists():
        return # Data is safe
        
    print("⚠️ Data missing on startup. Auto-generating enterprise data...")
    
    # Generate CSV
    prefixes = ["Dolo", "Azithral", "Augmentin", "Pan", "Insulin", "ORS", "Amoxicillin", "Paracetamol", "Metformin", "Atorvastatin"]
    suffixes = ["650", "500mg", "625", "40mg", "10mg", "100ml", "CV", "XP", "Forte"]
    today = datetime.today()
    data = []
    for i in range(10000):
        sku = f"{random.choice(prefixes)} {random.choice(suffixes)} - {i}"
        batch = f"B{i:05d}"
        qty = random.randint(10, 1000)
        expiry = (today + timedelta(days=random.randint(30, 1095))).strftime("%Y-%m-%d")
        data.append({"SKU": sku, "Batch": batch, "Qty": qty, "Expiry": expiry})

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["SKU", "Batch", "Qty", "Expiry"])
        writer.writeheader()
        writer.writerows(data)

    # Generate DB
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT, batch TEXT, qty INTEGER, expiry TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS retailers (id TEXT PRIMARY KEY, shop TEXT, owner TEXT, status TEXT, outstanding REAL)""")
    
    c.executemany("INSERT INTO products (sku, batch, qty, expiry) VALUES (?, ?, ?, ?)", [(d["SKU"], d["Batch"], d["Qty"], d["Expiry"]) for d in data])
    
    retailers = [
        ("RET001", "Sri Balaji Medicals", "Chitra", "Active", 145000),
        ("RET002", "Annai Pharmacy", "Lakshmi Devi", "Blocked", 180000),
        ("OWNER001", "Meena HQ", "Swaminathan", "Active", 0)
    ]
    c.executemany("INSERT OR IGNORE INTO retailers VALUES (?, ?, ?, ?, ?)", retailers)
    conn.commit()
    conn.close()
    print("✅ Auto-seeded 10,000 SKUs and DB.")

    # Ensure owner exists in JSON
    import json
    rj_path = BASE_DIR / "retailers.json"
    if not rj_path.exists():
        rj = [{"id": "OWNER001", "shop": "Meena HQ", "owner": "Swaminathan", "pin_hash": "1234", "status": "Active", "outstanding": 0}, 
              {"id": "RET001", "shop": "Sri Balaji", "pin_hash": "3210", "status": "Active", "outstanding": 145000}]
        rj_path.write_text(json.dumps(rj, indent=2))
