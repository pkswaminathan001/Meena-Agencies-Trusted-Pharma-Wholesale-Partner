"""
forecast_pro.py — Smart demand forecast using order history + season + disease patterns.
No LLM guessing. Real math + real medical knowledge.
"""
from datetime import datetime, timedelta
from collections import defaultdict
import math
import json
import os


# ────────────────────────────────────────────────
# DISEASE → MEDICINE KNOWLEDGE BASE (India-specific)
# ────────────────────────────────────────────────
SEASON_MAP = {
    "winter":  {"months": [11, 12, 1, 2],   "name": "Winter",  "emoji": "❄️"},
    "summer":  {"months": [3, 4, 5],         "name": "Summer",  "emoji": "☀️"},
    "monsoon": {"months": [6, 7, 8, 9],      "name": "Monsoon", "emoji": "🌧️"},
    "post_m":  {"months": [10],              "name": "Post-Monsoon", "emoji": "🍂"},
}

DISEASE_MEDICINES = {
    # Monsoon diseases
    "dengue":      ["paracetamol", "ors", "zinc", "cetirizine"],
    "malaria":     ["doxycycline", "paracetamol", "ciprofloxacin"],
    "typhoid":     ["azithromycin", "ciprofloxacin", "paracetamol"],
    "diarrhea":    ["ors", "zinc", "metronidazole", "ciprofloxacin"],
    "cholera":     ["ors", "doxycycline", "zinc"],
    # Winter diseases
    "cold_flu":    ["cetirizine", "paracetamol", "cough_syrup", "vitamin"],
    "cough":       ["cough_syrup", "salbutamol", "cetirizine"],
    "asthma":      ["salbutamol", "inhaler"],
    "pneumonia":   ["amoxicillin", "azithromycin", "paracetamol"],
    # Summer diseases
    "heatstroke":  ["ors", "electrolytes", "paracetamol"],
    "dehydration": ["ors", "electrolytes"],
    "food_poison": ["ors", "antacid", "ciprofloxacin"],
    # Chronic (always)
    "diabetes":    ["insulin", "metformin", "glimepiride"],
    "hypertension":["amlodipine", "telmisartan", "metoprolol"],
    "cardiac":     ["atorvastatin", "aspirin", "clopidogrel"],
    "thyroid":     ["levothyroxine"],
}

# Season → likely diseases
SEASON_DISEASES = {
    "monsoon": ["dengue", "malaria", "typhoid", "diarrhea", "cholera"],
    "winter":  ["cold_flu", "cough", "asthma", "pneumonia"],
    "summer":  ["heatstroke", "dehydration", "food_poison"],
    "post_m":  ["dengue", "cold_flu"],
}

# Keywords in medicine names → matched to disease medicines
MED_KEYWORDS = {
    "paracetamol":  ["paracetamol", "dolo", "crocin", "calpol"],
    "ors":          ["ors", "oral rehydration"],
    "zinc":         ["zinc"],
    "cetirizine":   ["cetirizine", "zyrtec", "alerid"],
    "doxycycline":  ["doxycycline"],
    "ciprofloxacin":["ciprofloxacin", "ciplox"],
    "azithromycin": ["azithromycin", "azee", "zithromax"],
    "amoxicillin":  ["amoxicillin", "mox", "novamox"],
    "metronidazole":["metronidazole", "flagyl"],
    "cough_syrup":  ["cough", "syrup", "benadryl", "ascoril"],
    "salbutamol":   ["salbutamol", "asthalin", "ventorlin", "inhaler"],
    "inhaler":      ["inhaler", "inhal"],
    "vitamin":      ["vitamin", "vit c", "multivitamin"],
    "electrolytes": ["electrolyte", "electral", "gatorade"],
    "antacid":      ["antacid", "gelusil", "digene", "pan", "omeprazole", "pantoprazole"],
    "insulin":      ["insulin"],
    "metformin":    ["metformin", "glycomet"],
    "glimepiride":  ["glimepiride", "amaryl"],
    "amlodipine":   ["amlodipine", "amlopres"],
    "telmisartan":  ["telmisartan", "telma"],
    "metoprolol":   ["metoprolol"],
    "atorvastatin": ["atorvastatin", "atorva", "storvas"],
    "aspirin":      ["aspirin", "ecosprin"],
    "clopidogrel":  ["clopidogrel", "clopilet"],
    "levothyroxine":["levothyroxine", "thyronorm", "eltroxin"],
}


def current_season():
    m = datetime.now().month
    for s, info in SEASON_MAP.items():
        if m in info["months"]:
            return s, info
    return "summer", SEASON_MAP["summer"]


def match_medicine(med_name: str):
    """Return the keyword key(s) a medicine matches."""
    n = med_name.lower()
    matches = []
    for key, keywords in MED_KEYWORDS.items():
        for kw in keywords:
            if kw in n:
                matches.append(key)
                break
    return matches


def seasonal_demand_score(med_name: str):
    """
    Return 0-100: how likely this medicine is needed right now
    based on season + disease patterns.
    """
    season, _ = current_season()
    seasonal_diseases = SEASON_DISEASES.get(season, [])
    recommended_meds = set()
    for d in seasonal_diseases:
        for m in DISEASE_MEDICINES.get(d, []):
            recommended_meds.add(m)

    matches = match_medicine(med_name)
    if not matches:
        return 30  # baseline — chronic meds still sell

    # Check if any match is in the seasonal recommended set
    for m in matches:
        if m in recommended_meds:
            return 90

    # Chronic medicines always sell
    chronic = ["insulin", "metformin", "amlodipine", "telmisartan",
               "atorvastatin", "aspirin", "levothyroxine"]
    for m in matches:
        if m in chronic:
            return 60

    return 30  # off-season


# ────────────────────────────────────────────────
# ORDER HISTORY ANALYSIS
# ────────────────────────────────────────────────
def retailer_order_history(retailer_id: str, orders: list):
    """Return dict: {medicine: [(date, qty), ...]} for this retailer."""
    history = defaultdict(list)
    for o in orders:
        if o.get("retailer_id") != retailer_id:
            continue
        if o.get("status") not in ("Approved", "Pending"):
            continue
        try:
            placed = datetime.strptime(o.get("placed_at", "")[:11], "%d-%b-%Y")
        except Exception:
            continue
        for item in o.get("items", []):
            history[item["medicine"]].append((placed, item["qty"]))
    return dict(history)


def moving_average_forecast(history, window=3):
    """Simple moving average of last N orders."""
    if not history:
        return None, 0, "no data"
    recent = sorted(history, key=lambda x: x[0])[-window:]
    if len(recent) < 2:
        return recent[-1][1] if recent else 0, 20, "minimal data"
    qtys = [h[1] for h in recent]
    avg = sum(qtys) / len(qtys)
    variance = sum((q - avg) ** 2 for q in qtys) / len(qtys)
    std = math.sqrt(variance)
    # Confidence: higher if low variance relative to average
    cv = std / avg if avg > 0 else 1
    confidence = max(20, min(90, int(100 - cv * 40)))
    return avg, confidence, f"moving avg of {len(recent)}"


def trend_forecast(history):
    """Detect trend (increasing, decreasing, stable) via linear regression."""
    if not history or len(history) < 3:
        return "insufficient", 0, 0
    sorted_h = sorted(history, key=lambda x: x[0])
    n = len(sorted_h)
    xs = list(range(n))
    ys = [h[1] for h in sorted_h]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((x - mean_x) ** 2 for x in xs) or 1
    slope = num / den
    if slope > mean_y * 0.1:
        return "rising", slope, mean_y
    elif slope < -mean_y * 0.1:
        return "falling", slope, mean_y
    return "stable", slope, mean_y


# ────────────────────────────────────────────────
# THE MAIN FORECASTER
# ────────────────────────────────────────────────
def forecast_retailer(retailer: dict, orders: list, inventory_df=None,
                       days_ahead: int = 30):
    """
    Return a forecast + promotion recommendations for one retailer.
    Uses: order history + season + disease patterns.
    """
    season_key, season_info = current_season()
    history = retailer_order_history(retailer["id"], orders)

    result = {
        "retailer_id": retailer["id"],
        "retailer_shop": retailer["shop"],
        "season": season_info["name"],
        "season_emoji": season_info["emoji"],
        "forecasts": [],
        "promotions": [],
        "summary_lines": [],
    }

    # 1. Forecast from history
    for med, hist in history.items():
        avg, conf, method = moving_average_forecast(hist)
        trend, slope, _ = trend_forecast(hist)
        seasonal_score = seasonal_demand_score(med)

        # Blend: 60% history + 40% seasonal
        history_qty = avg or 0
        seasonal_boost = 1 + (seasonal_score - 30) / 200.0  # 1.0 to 1.3
        blended = history_qty * seasonal_boost

        # Apply trend
        if trend == "rising":
            blended *= 1.15
        elif trend == "falling":
            blended *= 0.85

        final_qty = max(1, int(round(blended)))
        # Confidence blends historical + seasonal
        final_conf = min(95, int(conf * 0.6 + seasonal_score * 0.4))

        result["forecasts"].append({
            "medicine": med,
            "predicted_qty": final_qty,
            "confidence": final_conf,
            "seasonal_score": seasonal_score,
            "trend": trend,
            "method": method,
            "history_samples": len(hist),
        })

    # 2. Season-based promotion recommendations
    # (even for medicines never ordered — new opportunity)
    seasonal_diseases = SEASON_DISEASES.get(season_key, [])
    recommended_meds = set()
    for d in seasonal_diseases:
        for m in DISEASE_MEDICINES.get(d, []):
            recommended_meds.add(m)

    # Match against inventory
    if inventory_df is not None:
        for _, row in inventory_df.iterrows():
            med_name = row["medicine_name"]
            matches = match_medicine(med_name)
            for m in matches:
                if m in recommended_meds:
                    # This medicine is seasonally relevant
                    result["promotions"].append({
                        "medicine": med_name,
                        "reason": f"High demand in {season_info['name']}",
                        "score": 90,
                        "stock": int(row.get("quantity", 0)),
                    })
                    break

    # Deduplicate promotions
    seen = set()
    unique_promos = []
    for p in sorted(result["promotions"], key=lambda x: -x["score"]):
        if p["medicine"] not in seen:
            seen.add(p["medicine"])
            unique_promos.append(p)
    result["promotions"] = unique_promos[:10]

    # 3. Build human-readable summary
    s = season_info
    result["summary_lines"].append(
        f"{s['emoji']} Currently in <b>{s['name']}</b> season"
    )
    if seasonal_diseases:
        result["summary_lines"].append(
            f"🦠 Watch for: {', '.join(seasonal_diseases[:4])}"
        )
    if result["promotions"]:
        result["summary_lines"].append(
            f"📢 Promote: {', '.join(p['medicine'] for p in result['promotions'][:3])}"
        )
    if history:
        result["summary_lines"].append(
            f"📦 Forecast from {len(history)} medicines in history"
        )
    else:
        result["summary_lines"].append(
            "ℹ️ No order history — showing season-based recommendations only"
        )

    return result


# ────────────────────────────────────────────────
# WEATHER INTEGRATION (optional, mock by default)
# ────────────────────────────────────────────────
def get_weather(city: str = "Chennai"):
    """
    Return weather dict. Uses OpenWeatherMap if API key is set,
    otherwise returns a season-appropriate mock.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if api_key:
        try:
            import requests
            r = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": api_key, "units": "metric"},
                timeout=10,
            )
            if r.status_code == 200:
                d = r.json()
                return {
                    "city": city,
                    "temp": round(d["main"]["temp"], 1),
                    "humidity": d["main"]["humidity"],
                    "condition": d["weather"][0]["main"],
                    "description": d["weather"][0]["description"],
                    "source": "live",
                }
        except Exception:
            pass

    # Mock — season-appropriate
    season_key, _ = current_season()
    mocks = {
        "winter":  {"temp": 22.0, "humidity": 65, "condition": "Clear",      "description": "cool and dry"},
        "summer":  {"temp": 38.0, "humidity": 40, "condition": "Hot",        "description": "very hot"},
        "monsoon": {"temp": 28.0, "humidity": 85, "condition": "Rain",       "description": "heavy rain"},
        "post_m":  {"temp": 30.0, "humidity": 75, "condition": "Clouds",     "description": "partly cloudy"},
    }
    m = mocks.get(season_key, mocks["summer"])
    return {"city": city, **m, "source": "mock"}
