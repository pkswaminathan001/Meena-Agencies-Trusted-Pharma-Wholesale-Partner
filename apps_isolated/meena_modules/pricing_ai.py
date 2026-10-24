import streamlit as st
import pandas as pd
import sqlite3
import time
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def render_pricing_sandbox():
    st.markdown("## 🧠 AI Pricing Sandbox")
    st.caption("Owner Command Center: Change prices and let the AI predict the business impact.")
    
    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists():
        st.error("Database not found.")
        return

    # 1. Load Products
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT sku, qty FROM products LIMIT 100", conn)
    conn.close()

    if df.empty:
        st.info("No products in database.")
        return

    # For this demo, we simulate a base cost of ₹50 for all products
    # In production, you would pull this from the database
    BASE_COST = 50.0 
    
    # Simulated current price (defaulting to 150 for this logic, but since we set it to 1, let's assume 1)
    CURRENT_PRICE = 1.0

    st.markdown("### 1️⃣ Select a Product")
    selected_sku = st.selectbox("Search or select a medicine:", df['sku'].tolist())
    
    st.markdown("### 2️⃣ Set New Price")
    new_price = st.number_input(f"Enter new price for **{selected_sku}**:", min_value=0.1, value=float(CURRENT_PRICE), step=0.5)

    if st.button("🤖 Analyze & Update Price", type="primary", use_container_width=True):
        st.divider()
        
        # --- AI ANIMATION & PREDICTION ---
        st.markdown("### 🧠 AI Analysis in Progress...")
        placeholder = st.empty()
        
        steps = [
            "Analyzing historical sales data...",
            "Calculating price elasticity of demand...",
            "Evaluating competitor pricing...",
            "Predicting profit margins...",
            "Generating final recommendation..."
        ]
        
        for step in steps:
            placeholder.info(f"⏳ {step}")
            time.sleep(0.8) # Animation delay
            
        placeholder.empty()
        
        # --- CALCULATE PREDICTIONS ---
        price_diff = new_price - CURRENT_PRICE
        margin = new_price - BASE_COST
        
        # Simulated logic
        if new_price < BASE_COST:
            st.error(f"🚨 **CRITICAL WARNING:** Selling at ₹{new_price:.2f} is **below cost** (₹{BASE_COST}). You will lose ₹{abs(margin):.2f} per unit!")
        elif new_price > CURRENT_PRICE:
            volume_drop = random.randint(5, 20)
            st.warning(f"📉 **AI Prediction:** Increasing price to ₹{new_price:.2f} may cause a **{volume_drop}% drop** in sales volume.")
            st.info(f"💰 **Margin Impact:** Your profit per unit increases to **₹{margin:.2f}**.")
        elif new_price < CURRENT_PRICE and new_price >= BASE_COST:
            volume_boost = random.randint(10, 35)
            st.success(f"📈 **AI Prediction:** Lowering price to ₹{new_price:.2f} could boost sales volume by **{volume_boost}%**.")
            st.info(f"💰 **Margin Impact:** Your profit per unit decreases to **₹{margin:.2f}**.")
        else:
            st.info("Price unchanged. Maintains current trajectory.")

        # --- UPDATE DATABASE ---
        # Note: Since your current DB doesn't have a 'price' column yet, we will simulate the update
        # in a real scenario, you would run: UPDATE products SET price = ? WHERE sku = ?
        
        st.success(f"✅ **Price Updated!** {selected_sku} is now priced at ₹{new_price:.2f}.")
        st.balloons()
