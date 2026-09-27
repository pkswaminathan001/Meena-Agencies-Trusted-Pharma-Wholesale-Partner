"""
delivery_tracker.py — Smart delivery estimation + tracking.
Distance from Thanjavur, climate-aware ETA, owner-controlled visibility.
"""
import json
import math
from datetime import datetime, timedelta
from pathlib import Path


# ═══════════════════════════════════════════════════════════
# ORIGIN — Meena Agencies warehouse
# ═══════════════════════════════════════════════════════════
ORIGIN = {
    "name": "Meena Agencies Warehouse",
    "city": "Thanjavur",
    "lat": 10.7867,
    "lon": 79.1378,
    "dispatch_hours": "9:00 AM – 6:00 PM",
    "cutoff_time": 15,  # 3 PM — orders after this dispatch next day
}


# ═══════════════════════════════════════════════════════════
# TAMIL NADU CITIES / TOWNS — for distance lookup
# ═══════════════════════════════════════════════════════════
TN_LOCATIONS = {
    # Major cities
    "chennai":      {"lat": 13.0827, "lon": 80.2707, "tier": 1},
    "coimbatore":   {"lat": 11.0168, "lon": 76.9558, "tier": 1},
    "madurai":      {"lat": 9.9252,  "lon": 78.1198, "tier": 1},
    "trichy":       {"lat": 10.7905, "lon": 78.7047, "tier": 1},
    "tiruchirappalli": {"lat": 10.7905, "lon": 78.7047, "tier": 1},
    "salem":        {"lat": 11.6643, "lon": 78.1460, "tier": 1},
    "tirunelveli":  {"lat": 8.7139,  "lon": 77.7567, "tier": 1},
    "vellore":      {"lat": 12.9165, "lon": 79.1325, "tier": 1},
    "erode":        {"lat": 11.3410, "lon": 77.7172, "tier": 1},
    "tiruppur":     {"lat": 11.1085, "lon": 77.3411, "tier": 1},
    "kanyakumari":  {"lat": 8.0883,  "lon": 77.5385, "tier": 1},
    "thoothukudi":  {"lat": 8.7642,  "lon": 78.1348, "tier": 1},
    "dindigul":     {"lat": 10.3624, "lon": 77.9695, "tier": 1},
    "thanjavur":    {"lat": 10.7867, "lon": 79.1378, "tier": 1},
    "nagapattinam": {"lat": 10.7665, "lon": 79.8439, "tier": 1},
    "cuddalore":    {"lat": 11.7480, "lon": 79.7714, "tier": 1},
    "karur":        {"lat": 10.9601, "lon": 78.0766, "tier": 1},
    "namakkal":     {"lat": 11.2189, "lon": 78.1674, "tier": 1},
    "dharmapuri":   {"lat": 12.1211, "lon": 78.1581, "tier": 1},
    "krishnagiri":  {"lat": 12.5186, "lon": 78.2137, "tier": 1},
    "villupuram":   {"lat": 11.9401, "lon": 79.4861, "tier": 1},
    "kanchipuram":  {"lat": 12.8342, "lon": 79.7036, "tier": 1},
    "tiruvannamalai": {"lat": 12.2253, "lon": 79.0747, "tier": 1},
    "pudukkottai":  {"lat": 10.3833, "lon": 78.8001, "tier": 1},
    "ramanathapuram": {"lat": 9.3639, "lon": 78.8395, "tier": 1},
    "virudhunagar": {"lat": 9.5680,  "lon": 77.9624, "tier": 1},
    "theni":        {"lat": 10.0104, "lon": 77.4768, "tier": 1},
    "sivagangai":   {"lat": 9.8433,  "lon": 78.4809, "tier": 1},
    "ariyalur":     {"lat": 11.1401, "lon": 79.0756, "tier": 2},
    "perambalur":   {"lat": 11.2342, "lon": 78.8805, "tier": 2},
    "nilgiris":     {"lat": 11.4064, "lon": 76.6932, "tier": 2},
    "ooty":         {"lat": 11.4064, "lon": 76.6932, "tier": 2},
    "kodaikanal":   {"lat": 10.2381, "lon": 77.4892, "tier": 2},
}


# ═══════════════════════════════════════════════════════════
# DISTANCE — Haversine formula
# ═══════════════════════════════════════════════════════════
def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    return round(R * 2 * math.asin(math.sqrt(a)), 1)


def lookup_retailer_location(retailer):
    """
    Find retailer's coordinates.
    Tries: exact city in address, then state capital (default: Chennai).
    """
    address = (retailer.get("address", "") + " " + retailer.get("shop", "")).lower()
    for city, data in TN_LOCATIONS.items():
        if city in address:
            return {"matched_city": city.title(), **data}
    # Default: Chennai (worst case for ETA)
    return {"matched_city": "Chennai (default)", **TN_LOCATIONS["chennai"]}


# ═══════════════════════════════════════════════════════════
# CLIMATE — quick lookup (reuses logic from tn_climate)
# ═══════════════════════════════════════════════════════════
def current_season():
    m = datetime.now().month
    if m in (11, 12, 1, 2): return "Winter (NE Monsoon tail)"
    if m in (3, 4, 5):      return "Summer"
    if m in (6, 7, 8):      return "SW Monsoon"
    return "NE Monsoon"


def climate_delay_factor():
    """Return multiplier for delivery delay based on current season."""
    season = current_season()
    if "Monsoon" in season:
        return 1.35  # 35% longer
    if "Summer" in season:
        return 1.10  # minor delays due to heat
    return 1.0


# ═══════════════════════════════════════════════════════════
# ESTIMATE DELIVERY
# ═══════════════════════════════════════════════════════════
def estimate_delivery(retailer, order, dispatch_time=None):
    """
    Return dict with distance, base transit days, climate delay,
    estimated arrival, and confidence.
    """
    loc = lookup_retailer_location(retailer)
    distance = haversine_km(ORIGIN["lat"], ORIGIN["lon"], loc["lat"], loc["lon"])
    # Road distance ≈ straight-line × 1.35 (realistic for TN roads)
    road_km = round(distance * 1.35, 0)

    # Base transit days
    if road_km < 30:
        base_days = 0.5  # same-day
    elif road_km < 100:
        base_days = 1
    elif road_km < 250:
        base_days = 2
    elif road_km < 450:
        base_days = 3
    else:
        base_days = 4

    # Climate multiplier
    climate = climate_delay_factor()
    total_days = round(base_days * climate, 1)

    # Dispatch time — based on order placement
    placed_str = order.get("placed_at", "")
    try:
        placed = datetime.strptime(str(placed_str)[:17], "%d-%b-%Y %H:%M")
    except Exception:
        placed = datetime.now()

    # If placed after 3 PM cutoff, dispatch next business day
    dispatch = dispatch_time or placed
    if dispatch.hour >= ORIGIN["cutoff_time"]:
        dispatch = dispatch + timedelta(days=1)
    # Skip Sundays (no dispatch)
    if dispatch.weekday() == 6:
        dispatch = dispatch + timedelta(days=1)

    # Set dispatch to 10 AM
    dispatch = dispatch.replace(hour=10, minute=0, second=0, microsecond=0)

    # Estimated arrival
    arrival = dispatch + timedelta(days=total_days)

    # Confidence — higher for shorter distances
    if road_km < 50:
        confidence = 0.95
    elif road_km < 200:
        confidence = 0.85
    elif road_km < 400:
        confidence = 0.75
    else:
        confidence = 0.65

    return {
        "destination_city": loc["matched_city"],
        "distance_km_straight": distance,
        "distance_km_road": road_km,
        "base_transit_days": base_days,
        "climate_season": current_season(),
        "climate_delay_multiplier": climate,
        "estimated_transit_days": total_days,
        "estimated_dispatch": dispatch.strftime("%d-%b-%Y %H:%M").upper(),
        "estimated_arrival": arrival.strftime("%d-%b-%Y").upper(),
        "estimated_arrival_full": arrival.strftime("%A, %d %b %Y").upper(),
        "confidence": confidence,
        "confidence_label": f"{int(confidence*100)}%",
    }


# ═══════════════════════════════════════════════════════════
# VISIBILITY CONTROL — retailer sees only after owner confirms
# ═══════════════════════════════════════════════════════════
def can_retailer_see_delivery(order):
    """Retailer only sees delivery details after owner approves."""
    return order.get("status") in ("Approved", "Dispatched", "Delivered")


# ═══════════════════════════════════════════════════════════
# DELIVERY STATUS WORKFLOW (owner-controlled)
# ═══════════════════════════════════════════════════════════
DELIVERY_STATUSES = ["Pending", "Approved", "Packed", "Dispatched", "Out for Delivery", "Delivered", "Returned"]

DELIVERY_STATUS_ICONS = {
    "Pending":          "⏳",
    "Approved":         "✅",
    "Packed":           "📦",
    "Dispatched":       "🚚",
    "Out for Delivery": "🛵",
    "Delivered":        "🎉",
    "Returned":         "↩️",
}


def get_delivery_progress(order):
    """Return step-by-step progress with timestamps."""
    steps = []
    timeline = order.get("delivery_timeline", {})
    for status in DELIVERY_STATUSES[:6]:  # exclude Returned from normal flow
        ts = timeline.get(status, "")
        steps.append({
            "status": status,
            "icon": DELIVERY_STATUS_ICONS.get(status, "•"),
            "done": bool(ts),
            "timestamp": ts or "—",
        })
    return steps


def mark_delivery_status(order, new_status, note=""):
    """Update order status. Called by owner only."""
    if "delivery_timeline" not in order:
        order["delivery_timeline"] = {}
    order["delivery_timeline"][new_status] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
    order["status"] = new_status if new_status in ("Dispatched", "Delivered") else order.get("status", "Approved")
    if note:
        order.setdefault("delivery_notes", []).append({
            "ts": datetime.now().strftime("%d-%b-%Y %H:%M").upper(),
            "status": new_status,
            "note": note,
        })
    return order


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test with 3 different retailers
    tests = [
        {"id": "RET001", "shop": "Sri Balaji Medicals", "address": "Thanjavur, Tamil Nadu"},
        {"id": "RET002", "shop": "Annai Pharmacy",      "address": "Chennai, Tamil Nadu"},
        {"id": "RET003", "shop": "Vetri Medicals",      "address": "Coimbatore, Tamil Nadu"},
    ]
    order = {"order_id": "ORD-TEST", "placed_at": datetime.now().strftime("%d-%b-%Y %H:%M").upper()}

    print("═" * 80)
    print("  DELIVERY ESTIMATION — from Thanjavur Warehouse")
    print("═" * 80)
    for r in tests:
        est = estimate_delivery(r, order)
        print(f"\n{r['shop']} ({r['id']})")
        print(f"  Destination: {est['destination_city']}")
        print(f"  Distance: {est['distance_km_road']} km (road) / {est['distance_km_straight']} km (straight)")
        print(f"  Season: {est['climate_season']} × {est['climate_delay_multiplier']} delay")
        print(f"  Dispatch: {est['estimated_dispatch']}")
        print(f"  Arrival: {est['estimated_arrival_full']}")
        print(f"  Confidence: {est['confidence_label']}")
