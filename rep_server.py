"""rep_server.py — Backend for rep location tracking. Port 8502."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sqlite3, hashlib, math

DB = "reps.db"
app = FastAPI(title="Meena Agencies Rep Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS reps (
        rep_id TEXT PRIMARY KEY, name TEXT, phone TEXT,
        pin_hash TEXT, zone_lat REAL, zone_lng REAL, zone_radius_km REAL,
        active INTEGER DEFAULT 1, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rep_id TEXT, shop_name TEXT, order_id TEXT, amount REAL,
        lat REAL, lng REAL, accuracy_m REAL,
        created_at TEXT, synced_at TEXT, photo_b64 TEXT, visit_type TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS pings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rep_id TEXT, lat REAL, lng REAL, accuracy_m REAL,
        battery INTEGER, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rep_id TEXT, alert_type TEXT, details TEXT,
        created_at TEXT, seen INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()


init_db()


def hash_pin(pin):
    return hashlib.sha256(f"meena:{pin}".encode()).hexdigest()


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


class LoginReq(BaseModel):
    rep_id: str
    pin: str


class PingReq(BaseModel):
    rep_id: str
    lat: float
    lng: float
    accuracy_m: Optional[float] = 0
    battery: Optional[int] = -1


class VisitReq(BaseModel):
    rep_id: str
    shop_name: str
    order_id: Optional[str] = ""
    amount: Optional[float] = 0
    lat: float
    lng: float
    accuracy_m: Optional[float] = 0
    photo_b64: Optional[str] = ""
    visit_type: Optional[str] = "order"
    created_at: Optional[str] = ""


@app.get("/health")
def health():
    return {"ok": True, "server_time": datetime.now().isoformat()}


@app.post("/api/rep/login")
def rep_login(req: LoginReq):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT rep_id, name, pin_hash, zone_lat, zone_lng, zone_radius_km, active FROM reps WHERE rep_id=?", (req.rep_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Rep not found")
    if not row[6]:
        raise HTTPException(403, "Rep is inactive")
    if row[2] != hash_pin(req.pin):
        raise HTTPException(401, "Wrong PIN")
    return {"ok": True, "rep_id": row[0], "name": row[1],
            "zone": {"lat": row[3], "lng": row[4], "radius_km": row[5]}}


@app.post("/api/rep/ping")
def rep_ping(req: PingReq):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("SELECT zone_lat, zone_lng, zone_radius_km FROM reps WHERE rep_id=?", (req.rep_id,))
    rep = c.fetchone()
    if not rep:
        conn.close()
        raise HTTPException(404, "Rep not found")
    c.execute("INSERT INTO pings (rep_id, lat, lng, accuracy_m, battery, created_at) VALUES (?,?,?,?,?,?)",
              (req.rep_id, req.lat, req.lng, req.accuracy_m, req.battery, now))
    distance = haversine_km(req.lat, req.lng, rep[0], rep[1])
    outside = distance > rep[2]
    if outside:
        c.execute("INSERT INTO alerts (rep_id, alert_type, details, created_at) VALUES (?,?,?,?)",
                  (req.rep_id, "OUT_OF_ZONE", f"{distance:.1f}km from zone center (max {rep[2]}km)", now))
    conn.commit()
    conn.close()
    return {"ok": True, "outside_zone": outside, "distance_km": round(distance, 2)}


@app.post("/api/rep/visit")
def rep_visit(req: VisitReq):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    now = req.created_at or datetime.now().isoformat()
    c.execute("INSERT INTO visits (rep_id, shop_name, order_id, amount, lat, lng, accuracy_m, created_at, synced_at, photo_b64, visit_type) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
              (req.rep_id, req.shop_name, req.order_id, req.amount, req.lat, req.lng,
               req.accuracy_m, now, datetime.now().isoformat(), (req.photo_b64 or "")[:2000], req.visit_type))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/api/rep/today/{rep_id}")
def rep_today(rep_id: str):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), COALESCE(SUM(amount),0) FROM visits WHERE rep_id=? AND created_at LIKE ?",
              (rep_id, f"{today}%"))
    row = c.fetchone()
    conn.close()
    return {"visits": row[0], "total_amount": row[1], "date": today}


@app.get("/api/owner/live")
def owner_live():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT rep_id, name, phone FROM reps WHERE active=1")
    reps = c.fetchall()
    out = []
    for rep_id, name, phone in reps:
        c.execute("SELECT lat, lng, accuracy_m, battery, created_at FROM pings WHERE rep_id=? ORDER BY id DESC LIMIT 1", (rep_id,))
        last_ping = c.fetchone()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*), COALESCE(SUM(amount),0) FROM visits WHERE rep_id=? AND created_at LIKE ?", (rep_id, f"{today}%"))
        visits = c.fetchone()
        status = "offline"
        seconds_ago = None
        if last_ping:
            try:
                seconds_ago = int((datetime.now() - datetime.fromisoformat(last_ping[4])).total_seconds())
                if seconds_ago < 180:
                    status = "active"
                elif seconds_ago < 900:
                    status = "idle"
            except Exception:
                pass
        out.append({"rep_id": rep_id, "name": name, "phone": phone, "status": status,
                    "last_lat": last_ping[0] if last_ping else None,
                    "last_lng": last_ping[1] if last_ping else None,
                    "seconds_since_ping": seconds_ago,
                    "today_visits": visits[0], "today_amount": visits[1]})
    conn.close()
    return {"reps": out, "server_time": datetime.now().isoformat()}


@app.get("/api/owner/alerts")
def owner_alerts(limit: int = 50):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT rep_id, alert_type, details, created_at FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = [{"rep_id": r[0], "type": r[1], "details": r[2], "t": r[3]} for r in c.fetchall()]
    conn.close()
    return {"alerts": rows}


@app.post("/api/owner/add_rep")
def add_rep(rep_id: str, name: str, phone: str, pin: str,
            zone_lat: float, zone_lng: float, zone_radius_km: float):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO reps (rep_id, name, phone, pin_hash, zone_lat, zone_lng, zone_radius_km, active, created_at) VALUES (?,?,?,?,?,?,?,1,?)",
                  (rep_id, name, phone, hash_pin(pin), zone_lat, zone_lng, zone_radius_km, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "Rep ID already exists")
    conn.close()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Rep tracking server on http://localhost:8502")
    uvicorn.run(app, host="0.0.0.0", port=8502)
