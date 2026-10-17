"""Run daily at 8 AM via cron"""
import json, os, sys
import pandas as pd
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oi import build_daily_report
from notify import send_notification, get_active_channel
from dotenv import load_dotenv

load_dotenv()
BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "retailers.json")) as f: retailers = json.load(f)
try:
    with open(os.path.join(BASE, "owner.json")) as f: owner = json.load(f)
except: owner = {"telegram_chat_id": ""}
try:
    with open(os.path.join(BASE, "orders.json")) as f: orders = json.load(f)
except: orders = []

df = pd.read_csv(os.path.join(BASE, "inventory.csv"))
df["expiry_date"] = pd.to_datetime(df["expiry_date"])
today = pd.Timestamp.now()
df["days_to_expiry"] = (df["expiry_date"] - today).dt.days
df["inventory_value"] = df["quantity"] * df["cost_price"]

report = build_daily_report(retailers, orders, df)
chat_id = owner.get("telegram_chat_id", "")
if chat_id:
    ok, resp = send_notification(get_active_channel(), chat_id, report)
    print(f"Sent: {ok}")
else:
    print("No owner telegram_chat_id set. Skipping.")
