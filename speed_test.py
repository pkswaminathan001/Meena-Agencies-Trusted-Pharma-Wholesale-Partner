import time
import sqlite3
import pandas as pd
import os

print("🏁 STARTING SPEED TEST...\n")

# Test 1: Database Load Time (10,000 rows)
if os.path.exists("meena_enterprise.db"):
    start = time.time()
    conn = sqlite3.connect("meena_enterprise.db")
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    end = time.time()
    print(f"✅ 10,000 SKU Database Load: {round((end - start), 3)} seconds")
else:
    print("❌ Database not found.")

# Test 2: Data Processing (Expiry Logic)
start = time.time()
df["Expiry"] = pd.to_datetime(df["expiry"])
df["Days_Left"] = (df["Expiry"] - pd.Timestamp.today()).dt.days
critical = df[df["Days_Left"] <= 30]
end = time.time()
print(f"✅ Expiry Risk Calculation: {round((end - start), 3)} seconds")

# Test 3: Importing Heavy Libraries
start = time.time()
import plotly.express as px
import folium
import statsforecast
end = time.time()
print(f"⚠️ Heavy AI/Map Libraries Import: {round((end - start), 3)} seconds (This is slow on cloud!)")

print("\n🏁 SPEED TEST COMPLETE!")
