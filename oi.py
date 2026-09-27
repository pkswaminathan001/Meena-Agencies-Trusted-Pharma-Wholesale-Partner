"""Operational Intelligence features for Meena Agencies"""
import os, json, requests
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def calculate_health_score(retailer, orders):
    """Return health score 0-100 with breakdown."""
    ret_orders = [o for o in orders if o.get("retailer_id") == retailer["id"]]
    
    # Credit utilization (lower is better)
    util = retailer["outstanding"] / max(retailer["credit_limit"], 1)
    credit_score = max(0, 100 - int(util * 100))
    
    # Order frequency (more = healthier)
    freq = len(ret_orders)
    freq_score = min(100, freq * 10)
    
    # Order consistency (recent activity)
    if ret_orders:
        last = max(o.get("placed_at", "") for o in ret_orders)
        consistency = 80
    else:
        consistency = 20
    
    # Status penalty
    status_penalty = 30 if retailer["status"] == "Blocked" else 0
    
    overall = max(0, min(100, int(
        credit_score * 0.35 + freq_score * 0.35 + consistency * 0.30
    ) - status_penalty))
    
    return {
        "overall": overall,
        "credit": credit_score,
        "frequency": freq_score,
        "consistency": consistency,
        "grade": "🟢" if overall >= 75 else ("🟡" if overall >= 50 else "🔴"),
        "risk": "Low" if overall >= 75 else ("Medium" if overall >= 50 else "High")
    }


def detect_fraud(order, retailer, all_orders):
    """Return list of fraud flags for an order."""
    flags = []
    
    # Rule 1: Unusual order time (before 6 AM or after 10 PM)
    placed = order.get("placed_at", "")
    try:
        hour = int(placed.split(" ")[-1].split(":")[0]) if " " in placed else 12
        if hour < 6 or hour > 22:
            flags.append(f"⏰ Unusual order time: {hour}:00")
    except:
        pass
    
    # Rule 2: Order near credit limit
    util = retailer["outstanding"] / max(retailer["credit_limit"], 1)
    if util > 0.9:
        flags.append(f"💳 Credit utilization at {util*100:.0f}%")
    
    # Rule 3: Large order (total > 50000)
    if order["total"] > 50000:
        flags.append(f"💰 Large order: ₹{order['total']:,.0f}")
    
    # Rule 4: Retailer is Blocked
    if retailer["status"] == "Blocked":
        flags.append(f"🚫 Retailer is BLOCKED")
    
    # Rule 5: No prior orders (first-time)
    prior = [o for o in all_orders if o.get("retailer_id") == retailer["id"] and o["status"] != "Awaiting OTP"]
    if len(prior) == 0:
        flags.append("🆕 First-ever order from this retailer")
    
    return flags


def predict_demand(retailer, orders, inventory_df):
    """Use LLM to predict next 30 days demand for a retailer."""
    ret_orders = [o for o in orders if o.get("retailer_id") == retailer["id"]]
    if not ret_orders:
        return {"summary": "No order history. Cannot predict.", "items": []}
    
    # Aggregate medicine quantities
    med_totals = {}
    for o in ret_orders:
        for item in o["items"]:
            med_totals[item["medicine"]] = med_totals.get(item["medicine"], 0) + item["qty"]
    
    history_text = "\n".join([f"- {m}: {q} units total" for m, q in med_totals.items()])
    
    prompt = f"""You are a pharma demand forecaster.

Retailer: {retailer['shop']}
Order history ({len(ret_orders)} orders):
{history_text}

Predict next 30 days demand. For each medicine give expected qty and confidence (0-100%).
Respond in this exact format:
SUMMARY: <1 sentence>
ITEM: <medicine> | <qty> | <confidence>%
ITEM: <medicine> | <qty> | <confidence>%"""
    
    try:
        r = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3, max_tokens=600
        )
        text = r.choices[0].message.content
        summary = ""
        items = []
        for line in text.split("\n"):
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:","").strip()
            elif line.startswith("ITEM:"):
                parts = line.replace("ITEM:","").split("|")
                if len(parts) >= 3:
                    items.append({"medicine": parts[0].strip(), "qty": parts[1].strip(), "conf": parts[2].strip()})
        return {"summary": summary, "items": items}
    except Exception as e:
        return {"summary": f"Prediction failed: {e}", "items": []}


def generate_purchase_orders(inventory_df):
    """Suggest purchase orders for low-stock or near-expiry-safe items."""
    pos = []
    for _, row in inventory_df.iterrows():
        if row["quantity"] < 50 and row["status"] == "Healthy" and row["days_to_expiry"] > 120:
            pos.append({
                "supplier": row["supplier"],
                "medicine": row["medicine_name"],
                "current_qty": int(row["quantity"]),
                "recommended_qty": 500,
                "cost": float(row["cost_price"] * 500),
                "reason": f"Stock low ({row['quantity']} units). Healthy shelf life."
            })
    return pos[:10]


def answer_whatif(question, context):
    """Use LLM to answer hypothetical business questions."""
    prompt = f"""You are a pharma business advisor.

Current business context:
{context}

Owner's question: {question}

Answer in 3-4 sentences with specific, actionable advice. Include numbers if possible."""
    
    try:
        r = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role":"user","content":prompt}],
            temperature=0.4, max_tokens=500
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def build_daily_report(retailers, orders, inventory_df):
    """Build daily report text for Telegram."""
    today = datetime.now().strftime("%d-%b-%Y").upper()
    pending = [o for o in orders if o["status"] == "Pending"]
    approved = [o for o in orders if o["status"] == "Approved"]
    
    expiring = inventory_df[(inventory_df["days_to_expiry"] > 0) & (inventory_df["days_to_expiry"] < 30)]
    at_risk_value = expiring["inventory_value"].sum() if len(expiring) > 0 else 0
    
    high_util = [r for r in retailers if r["outstanding"] / max(r["credit_limit"],1) > 0.85]
    
    msg = f"""📊 <b>Meena Agencies Daily Report — {today}</b>

<b>Orders:</b>
• Pending approval: {len(pending)}
• Approved today: {len(approved)}
• Total pipeline: ₹{sum(o['total'] for o in pending):,.0f}

<b>Inventory:</b>
• Items expiring in 30 days: {len(expiring)}
• Value at risk: ₹{at_risk_value:,.0f}

<b>Retailers:</b>
• Active: {len([r for r in retailers if r['status']=='Active'])}
• Blocked: {len([r for r in retailers if r['status']=='Blocked'])}
• High credit utilization: {len(high_util)}

<b>Action needed:</b>"""
    
    if pending:
        msg += f"\n⚠️ {len(pending)} order(s) awaiting your approval"
    if len(expiring) > 0:
        msg += f"\n⚠️ {len(expiring)} medicine(s) expiring soon"
    if high_util:
        msg += f"\n⚠️ {len(high_util)} retailer(s) near credit limit"
    if not (pending or len(expiring) or high_util):
        msg += "\n✅ All good. No urgent action."
    
    return msg


# ========== PROBABILISTIC DECISION LAYER ==========

import json as _json   # local import to avoid conflicts


def decide_order_probabilistic(order, retailer, all_orders):
    """
    Return a structured decision about this order.
    Uses Groq LLM in JSON mode. Returns dict with route, risk, confidence, action.
    """
    if not retailer:
        return {
            "route": "manual_review",
            "action": "human_review",
            "reason": "Retailer record missing",
            "suspicious_probability": 1.0,
            "route_confidence": 0.0,
            "risk_score": "high",
            "risk_confidence": 0.0,
        }

    prior = [
        o for o in all_orders
        if o.get("retailer_id") == retailer["id"] and o.get("status") != "Awaiting OTP"
    ]

    prompt = f"""You are a pharma wholesale order routing classifier.
Return ONLY valid JSON. No explanation, no markdown, no code fences.

Order:
- Total: Rs {order['total']:,.0f}
- Item count: {len(order['items'])}
- Placed at: {order['placed_at']}
- Location: {order.get('location', 'unknown')}

Retailer:
- Credit limit: Rs {retailer['credit_limit']:,}
- Outstanding: Rs {retailer['outstanding']:,}
- Status: {retailer['status']}
- Prior orders: {len(prior)}

Return JSON with EXACTLY these keys:
{
  "route": "standard" | "cold_chain" | "controlled" | "manual_review",
  "risk_score": "low" | "medium" | "high",
  "suspicious_probability": <float 0-1>,
  "route_confidence": <float 0-1>,
  "risk_confidence": <float 0-1>,
  "reason": "<one short sentence>"
}

Rules:
- If retailer status is Blocked -> route "manual_review", suspicious_probability >= 0.8
- If order total > 200000 -> higher suspicion, risk_score at least "medium"
- If prior orders is 0 -> suspicious_probability at least 0.4
- If everything normal -> route "standard", risk_score "low", high confidence
"""

    try:
        resp = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=250,
            response_format={"type": "json_object"},
        )
        decision = _json.loads(resp.choices[0].message.content)

        # --- Confidence gating (policy layer) ---
        if decision.get("route") == "controlled":
            decision["action"] = "human_review"
        elif decision.get("route") == "manual_review":
            decision["action"] = "human_review"
        elif decision.get("suspicious_probability", 0) >= 0.5:
            decision["action"] = "human_review"
        elif decision.get("route_confidence", 0) < 0.75:
            decision["action"] = "human_review"
        else:
            decision["action"] = "auto_execute"

        return decision

    except Exception as e:
        # Fail-safe: on any error, escalate to human
        return {
            "route": "manual_review",
            "action": "human_review",
            "reason": f"Decision failed: {e}",
            "suspicious_probability": 1.0,
            "route_confidence": 0.0,
            "risk_score": "high",
            "risk_confidence": 0.0,
        }
