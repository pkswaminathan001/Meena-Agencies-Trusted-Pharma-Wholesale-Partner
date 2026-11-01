import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import random

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "meena_enterprise.db"

# ─── AGENT 1: DATA INGESTION ───
def data_ingestion_node():
    """Simulates pulling ERP history and FDA signals."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Pull historical orders (simulated)
        df = pd.read_sql_query("SELECT date, total FROM orders ORDER BY date ASC", conn)
        if df.empty:
            # Generate dummy historical data if DB is empty so the UI works
            dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
            df = pd.DataFrame({'date': dates, 'total': np.random.randint(1000, 5000, size=30)})
        
        # Simulate external market signals
        signals = {
            "flu_season": random.choice([True, False]),
            "gpo_contract_tier_change": random.choice([True, False]),
            "generic_launch_detected": random.choice([True, False])
        }
        return df, signals
    finally:
        conn.close()

# ─── AGENT 2: QUANT MODELING ───
def quant_modeling_node(df, signals):
    """Simulates the TSFM (Time-Series Foundation Model) or LightGBM routing."""
    # Base forecast (simple moving average + trend)
    recent_avg = df['total'].tail(7).mean()
    trend = (df['total'].tail(7).mean() - df['total'].head(7).mean()) / len(df)
    
    forecast = []
    for i in range(7):
        val = recent_avg + (trend * (i + 1))
        # Inject signal impacts
        if signals["flu_season"]:
            val *= 1.15 # 15% spike
        if signals["generic_launch_detected"]:
            val *= 0.80 # 20% drop due to generic erosion
        forecast.append(max(0, val))
        
    model_used = "TimeGPT-2 (Zero-shot)" if signals["flu_season"] else "LightGBM (Gradient Boosting)"
    return forecast, model_used

# ─── AGENT 3: CRITIC & AUDIT ───
def critic_audit_node(forecast, signals):
    """Simulates checking GPO contracts and expiry dates."""
    audit_log = []
    is_valid = True
    
    if signals["gpo_contract_tier_change"]:
        audit_log.append("⚠️ GPO Contract Tier Change detected. Recalculating rebate thresholds.")
        # Simulate an adjustment
        forecast = [f * 0.95 for f in forecast]
        is_valid = False
        
    max_capacity = 10000 # Simulated warehouse max capacity
    if sum(forecast) > max_capacity:
        audit_log.append(f"🚨 Forecast exceeds max warehouse capacity ({max_capacity}). Truncating.")
        forecast = [min(f, max_capacity/7) for f in forecast]
        is_valid = False

    if not audit_log:
        audit_log.append("✅ Forecast audited against GPO contracts and warehouse limits. No anomalies.")
        
    return forecast, audit_log, is_valid

# ─── ORCHESTRATOR ───
def run_agentic_forecast():
    """The LangGraph-style execution loop."""
    # 1. Data Agent
    df, signals = data_ingestion_node()
    
    # 2. Quant Agent
    raw_forecast, model_used = quant_modeling_node(df, signals)
    
    # 3. Critic Agent
    final_forecast, audit_log, passed = critic_audit_node(raw_forecast, signals)
    
    return {
        "historical_data": df,
        "signals": signals,
        "model_used": model_used,
        "raw_forecast": raw_forecast,
        "final_forecast": final_forecast,
        "audit_log": audit_log,
        "audit_passed": passed
    }
