import pandas as pd
import random
from datetime import datetime, timedelta

medicines = [
    "Paracetamol 500mg", "Amoxicillin 250mg", "Ibuprofen 400mg",
    "Metformin 500mg", "Atorvastatin 10mg", "Omeprazole 20mg",
    "Cetirizine 10mg", "Azithromycin 500mg", "Cough Syrup 100ml",
    "Insulin Glargine", "Salbutamol Inhaler", "ORS Powder"
]

suppliers = ["Sun Pharma", "Cipla", "Dr. Reddy's", "Lupin", "Aurobindo", "Zydus"]

data = []
for i in range(200):
    medicine = random.choice(medicines)
    batch = f"B{random.randint(1000,9999)}"
    expiry = datetime.now() + timedelta(days=random.randint(-30, 730))
    quantity = random.randint(10, 1000)
    cost_price = round(random.uniform(5, 500), 2)
    supplier = random.choice(suppliers)
    data.append({
        "item_id": f"MED{i+1:04d}",
        "medicine_name": medicine,
        "batch_number": batch,
        "expiry_date": expiry.strftime("%Y-%m-%d"),
        "quantity": quantity,
        "cost_price": cost_price,
        "supplier": supplier
    })

df = pd.DataFrame(data)
df.to_csv("inventory.csv", index=False)
print("inventory.csv created with 200 items.")
