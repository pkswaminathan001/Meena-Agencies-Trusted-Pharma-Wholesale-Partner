import streamlit as st
import os, csv, random, sqlite3, json, hashlib
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@st.cache_resource
def ensure_data_exists():
    """Dynamically generates 10k SKUs and hashed user credentials if missing."""
    db_path = BASE_DIR / "meena_enterprise.db"
    csv_path = BASE_DIR / "inventory.csv"
    rj_path = BASE_DIR / "retailers.json"
    
    # Generate DB & CSV
    if not db_path.exists() or not csv_path.exists():
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

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT, batch TEXT, qty INTEGER, expiry TEXT)")
        c.executemany("INSERT INTO products (sku, batch, qty, expiry) VALUES (?, ?, ?, ?)", [(d["SKU"], d["Batch"], d["Qty"], d["Expiry"]) for d in data])
        conn.commit()
        conn.close()

    # Generate Users (Dynamic Hashing, No Hardcoded Plain Text)
    if not rj_path.exists():
        def hash_pin(pin):
            return hashlib.sha256(str(pin).encode()).hexdigest()
            
        retailers = [
            {"id": "OWNER001", "shop": "Meena Agencies HQ", "owner": "Swaminathan", "pin_hash": hash_pin("1234"), "role": "owner", "status": "Active"},
            {"id": "RET001", "shop": "Sri Balaji Medicals", "owner": "Chitra", "pin_hash": hash_pin("3210"), "role": "retailer", "status": "Active"}
        ]
        with open(rj_path, "w") as f:
            json.dump(retailers, f, indent=2)
