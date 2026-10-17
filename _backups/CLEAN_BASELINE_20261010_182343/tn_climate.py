"""
tn_climate.py — Tamil Nadu climate intelligence with 3D animation.
Live weather + climate zones + disease risk per region.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os
import json
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# TAMIL NADU CITIES — 12 major hubs with coordinates
# ═══════════════════════════════════════════════════════════
TN_CITIES = [
    # name, lat, lon, zone, alt_meters
    {"name": "Chennai",       "lat": 13.0827, "lon": 80.2707, "zone": "Coastal Plains", "alt": 6},
    {"name": "Thanjavur",     "lat": 10.7867, "lon": 79.1378, "zone": "Cauvery Delta", "alt": 60},
    {"name": "Coimbatore",    "lat": 11.0168, "lon": 76.9558, "zone": "Western Plains", "alt": 411},
    {"name": "Madurai",       "lat": 9.9252,  "lon": 78.1198, "zone": "Southern Plains", "alt": 101},
    {"name": "Trichy",        "lat": 10.7905, "lon": 78.7047, "zone": "Central Plains", "alt": 88},
    {"name": "Salem",         "lat": 11.6643, "lon": 78.1460, "zone": "Central Plains", "alt": 278},
    {"name": "Vellore",       "lat": 12.9165, "lon": 79.1325, "zone": "Northern Plains", "alt": 215},
    {"name": "Erode",         "lat": 11.3410, "lon": 77.7172, "zone": "Western Plains", "alt": 172},
    {"name": "Tirunelveli",   "lat": 8.7139,  "lon": 77.7567, "zone": "Southern Plains", "alt": 47},
    {"name": "Kanyakumari",   "lat": 8.0883,  "lon": 77.5385, "zone": "Coastal Tip", "alt": 30},
    {"name": "Ooty",          "lat": 11.4064, "lon": 76.6932, "zone": "Hills (Nilgiris)", "alt": 2240},
    {"name": "Kodaikanal",    "lat": 10.2381, "lon": 77.4892, "zone": "Hills (Palani)", "alt": 2133},
]

# Zone colors for visualization
ZONE_COLORS = {
    "Coastal Plains":  "#00d4ff",
    "Cauvery Delta":   "#00d47a",
    "Western Plains":  "#ffb547",
    "Central Plains":  "#ff8c42",
    "Northern Plains": "#e91e63",
    "Southern Plains": "#7b61ff",
    "Coastal Tip":     "#c41e3a",
    "Hills (Nilgiris)":"#4a90d9",
    "Hills (Palani)":  "#9b59b6",
}


# ═══════════════════════════════════════════════════════════
# WEATHER — OpenWeatherMap if key set, else realistic mock
# ═══════════════════════════════════════════════════════════
def get_weather(city_name, lat, lon):
    """Fetch weather. Uses OpenWeather if API key set. Otherwise seasonal mock."""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
        if api_key:
            import requests
            r = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
                timeout=8,
            )
            if r.status_code == 200:
                d = r.json()
                return {
                    "temp": round(d["main"]["temp"], 1),
                    "humidity": d["main"]["humidity"],
                    "condition": d["weather"][0]["main"],
                    "description": d["weather"][0]["description"],
                    "source": "live",
                }
    except Exception:
        pass

    # Seasonal mock — accurate for TN by month
    month = datetime.now().month
    # TN seasons: Winter (Nov-Feb), Summer (Mar-May), SW Monsoon (Jun-Aug), NE Monsoon (Oct-Dec)
    if month in (11, 12, 1, 2):
        temp, hum, cond, desc = 27.0, 75, "Clouds", "pleasant with NE monsoon"
    elif month in (3, 4, 5):
        temp, hum, cond, desc = 36.0, 55, "Clear", "hot and dry"
    elif month in (6, 7, 8):
        temp, hum, cond, desc = 31.0, 70, "Clouds", "SW monsoon breeze"
    else:  # Sep, Oct
        temp, hum, cond, desc = 29.0, 85, "Rain", "NE monsoon active"
    return {"temp": temp, "humidity": hum, "condition": cond,
            "description": desc, "source": "mock"}


# ═══════════════════════════════════════════════════════════
# CLIMATE ZONE → DISEASE RISK
# ═══════════════════════════════════════════════════════════
ZONE_DISEASE_MAP = {
    "Coastal Plains":  ["Dengue", "Chikungunya", "Typhoid", "Gastroenteritis"],
    "Cauvery Delta":   ["Dengue", "Cholera", "Typhoid", "Malaria"],
    "Western Plains":  ["Heatstroke", "Dehydration", "Dengue"],
    "Central Plains":  ["Dengue", "Malaria", "Typhoid"],
    "Northern Plains": ["Dengue", "Chikungunya", "Typhoid"],
    "Southern Plains": ["Dengue", "Malaria", "Diarrhea"],
    "Coastal Tip":     ["Dengue", "Tsunami-humidity effects", "Typhoid"],
    "Hills (Nilgiris)":["Respiratory infections", "Pneumonia", "Asthma", "Cold/Flu"],
    "Hills (Palani)":  ["Respiratory infections", "Asthma", "Cold/Flu"],
}


def disease_risk(zone, temp, humidity, condition):
    """Return risk score 0-100 for the zone given weather."""
    base = 50
    # High humidity → mosquito breeding
    if humidity > 80:
        base += 25
    elif humidity > 70:
        base += 15
    # Rain → waterborne
    if "Rain" in condition or "Drizzle" in condition:
        base += 20
    # Hills → respiratory
    if "Hills" in zone:
        if temp < 18:
            base += 15
        else:
            base -= 10
    # Hot plains → dehydration
    if temp > 35 and "Hills" not in zone:
        base += 10
    return max(0, min(100, base))


def risk_label(score):
    if score >= 75: return "🔴 HIGH", "#ff4d6d"
    if score >= 55: return "🟠 MODERATE", "#ffb547"
    if score >= 35: return "🟡 LOW", "#ffeaa7"
    return "🟢 MINIMAL", "#00d47a"


# ═══════════════════════════════════════════════════════════
# 3D ANIMATED MAP
# ═══════════════════════════════════════════════════════════
def build_3d_climate_map(weather_data):
    """
    Plotly 3D scatter map of TN cities.
    Height = temperature + humidity + risk.
    """
    fig = go.Figure()

    # Group by zone for legend
    zones = {}
    for i, city in enumerate(weather_data):
        zones.setdefault(city["zone"], []).append(city)

    for zone, cities in zones.items():
        color = ZONE_COLORS.get(zone, "#ffffff")
        lats = [c["lat"] for c in cities]
        lons = [c["lon"] for c in cities]
        # Z = altitude + temp elevation for 3D effect
        zs = [c["alt"] / 50 + c["temp"] / 2 + c["risk"] / 10 for c in cities]
        names = [c["name"] for c in cities]
        temps = [f"{c['temp']}°C" for c in cities]
        hums = [f"{c['humidity']}%" for c in cities]
        risks = [risk_label(c["risk"])[0] + f" ({c['risk']})" for c in cities]
        colors = [risk_label(c["risk"])[1] for c in cities]

        fig.add_trace(go.Scatter3d(
            x=lons, y=lats, z=zs,
            mode="markers+text",
            marker=dict(
                size=[14 + c["risk"] / 5 for c in cities],
                color=colors,
                opacity=0.85,
                line=dict(color="#ffffff", width=1.5),
                symbol="circle",
            ),
            text=names,
            textposition="top center",
            textfont=dict(color="#ffffff", size=11, family="Arial Black"),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Zone: " + zone + "<br>"
                "Temp: %{customdata[0]}<br>"
                "Humidity: %{customdata[1]}<br>"
                "Disease Risk: %{customdata[2]}<br>"
                "<extra></extra>"
            ),
            customdata=list(zip(temps, hums, risks)),
            name=zone,
        ))

    # Styling
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Longitude", showgrid=True,
                       gridcolor="rgba(0,212,255,0.15)",
                       backgroundcolor="rgba(10,14,39,0.9)",
                       color="#8892b0"),
            yaxis=dict(title="Latitude", showgrid=True,
                       gridcolor="rgba(0,212,255,0.15)",
                       backgroundcolor="rgba(10,14,39,0.9)",
                       color="#8892b0"),
            zaxis=dict(title="Elevation + Risk", showgrid=True,
                       gridcolor="rgba(123,97,255,0.15)",
                       backgroundcolor="rgba(10,14,39,0.9)",
                       color="#8892b0"),
            bgcolor="rgba(10,14,39,1)",
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.2),
                up=dict(x=0, y=0, z=1),
            ),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1.3, z=0.7),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf6"),
        height=650,
        margin=dict(l=0, r=0, t=30, b=0),
        title=dict(
            text="🗺️ Tamil Nadu — 3D Climate & Disease Risk Map",
            font=dict(color="#00d4ff", size=18, family="Georgia"),
            x=0.5,
        ),
        legend=dict(
            bgcolor="rgba(26,31,58,0.85)",
            bordercolor="#00d4ff",
            borderwidth=1,
            font=dict(color="#e8eaf6", size=10),
        ),
    )
    return fig


# ═══════════════════════════════════════════════════════════
# CLIMATE ZONE SUMMARY CARDS
# ═══════════════════════════════════════════════════════════
def render_zone_cards(weather_data):
    """Show climate zone cards with weather + disease risk."""
    zones_seen = {}
    for c in weather_data:
        zones_seen.setdefault(c["zone"], []).append(c)

    for zone, cities in zones_seen.items():
        color = ZONE_COLORS.get(zone, "#ffffff")
        # Zone avg
        avg_temp = sum(c["temp"] for c in cities) / len(cities)
        avg_hum = sum(c["humidity"] for c in cities) / len(cities)
        max_risk = max(c["risk"] for c in cities)
        risk_txt, risk_col = risk_label(max_risk)
        diseases = ZONE_DISEASE_MAP.get(zone, ["—"])

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(26,31,58,0.9),rgba(15,20,40,0.9));
                    border-left:5px solid {color};border-radius:12px;
                    padding:14px 18px;margin:8px 0;
                    box-shadow:0 6px 20px rgba(0,0,0,0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:1.1rem;font-weight:800;color:{color};">
                        {zone}
                    </div>
                    <div style="font-size:0.75rem;color:#8892b0;margin-top:2px;">
                        {', '.join(c['name'] for c in cities)}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.4rem;font-weight:800;color:{color};">
                        {avg_temp:.0f}°C
                    </div>
                    <div style="font-size:0.7rem;color:#8892b0;">
                        {avg_hum:.0f}% humidity
                    </div>
                </div>
            </div>
            <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:0.8rem;color:#e8eaf6;">
                    <b>Disease risk:</b> <span style="color:{risk_col};">{risk_txt}</span>
                </div>
                <div style="font-size:0.75rem;color:#8892b0;">
                    💊 {', '.join(diseases[:3])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# MAIN RENDER
# ═══════════════════════════════════════════════════════════
def render_climate_tab():
    """Main entry point — call from app.py."""
    st.markdown("### 🌦️ Tamil Nadu Climate Intelligence")
    st.caption("Live weather · Climate zones · Disease risk · 3D visualization")

    # ─── Fetch weather for all cities ───
    with st.spinner("Fetching weather for 12 TN cities..."):
        weather_data = []
        for city in TN_CITIES:
            w = get_weather(city["name"], city["lat"], city["lon"])
            risk = disease_risk(city["zone"], w["temp"], w["humidity"], w["condition"])
            weather_data.append({
                **city,
                **w,
                "risk": risk,
            })

    # ─── Top metrics ───
    hottest = max(weather_data, key=lambda c: c["temp"])
    coolest = min(weather_data, key=lambda c: c["temp"])
    riskiest = max(weather_data, key=lambda c: c["risk"])
    avg_risk = sum(c["risk"] for c in weather_data) / len(weather_data)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#ff4d6d22,#ff4d6d11);
                    border-left:4px solid #ff4d6d;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;letter-spacing:1px;">🔥 HOTTEST</div>
            <div style="color:#ff4d6d;font-size:1.5rem;font-weight:800;">{hottest['temp']}°C</div>
            <div style="color:#e8eaf6;font-size:0.8rem;">{hottest['name']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#00d4ff22,#00d4ff11);
                    border-left:4px solid #00d4ff;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;letter-spacing:1px;">❄️ COOLEST</div>
            <div style="color:#00d4ff;font-size:1.5rem;font-weight:800;">{coolest['temp']}°C</div>
            <div style="color:#e8eaf6;font-size:0.8rem;">{coolest['name']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#ffb54722,#ffb54711);
                    border-left:4px solid #ffb547;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;letter-spacing:1px;">⚠️ RISKIEST</div>
            <div style="color:#ffb547;font-size:1.5rem;font-weight:800;">{riskiest['risk']}/100</div>
            <div style="color:#e8eaf6;font-size:0.8rem;">{riskiest['name']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        _rc = risk_label(int(avg_risk))[1]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(123,97,255,0.13),rgba(123,97,255,0.05));
                    border-left:4px solid {_rc};border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;letter-spacing:1px;">📊 TN AVG RISK</div>
            <div style="color:{_rc};font-size:1.5rem;font-weight:800;">{int(avg_risk)}/100</div>
            <div style="color:#e8eaf6;font-size:0.8rem;">State-wide</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ─── Tabs ───
    ct1, ct2, ct3, ct4 = st.tabs([
        "🗺️ 3D Map", "📊 Zones", "🌡️ All Cities", "💊 Medicine Demand"
    ])

    # ═══ CT1 — 3D MAP ═══
    with ct1:
        st.caption("🖱️ Drag to rotate · Scroll to zoom · Hover for details")
        fig = build_3d_climate_map(weather_data)
        st.plotly_chart(fig, use_container_width=True, key="tn_climate_3d")

    # ═══ CT2 — ZONES ═══
    with ct2:
        st.markdown("#### Climate Zones of Tamil Nadu")
        render_zone_cards(weather_data)

    # ═══ CT3 — ALL CITIES ═══
    with ct3:
        st.markdown("#### All Cities — Live Weather")
        df = pd.DataFrame([{
            "City": c["name"],
            "Zone": c["zone"],
            "Temp (°C)": c["temp"],
            "Humidity (%)": c["humidity"],
            "Condition": c["condition"],
            "Altitude (m)": c["alt"],
            "Disease Risk": c["risk"],
        } for c in weather_data])
        df = df.sort_values("Disease Risk", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True, height=460)

    # ═══ CT4 — MEDICINE DEMAND ═══
    with ct4:
        st.markdown("#### 💊 Medicine Demand Forecast from Climate")
        st.caption("Based on temperature, humidity, and disease risk in each zone")

        recommendations = []
        for city in weather_data:
            zone = city["zone"]
            diseases = ZONE_DISEASE_MAP.get(zone, [])
            if city["risk"] >= 60:
                # High risk → push medicines
                meds = {
                    "Dengue": ["Paracetamol", "ORS", "Zinc"],
                    "Malaria": ["Doxycycline", "Paracetamol"],
                    "Typhoid": ["Azithromycin", "Ciprofloxacin"],
                    "Cholera": ["ORS", "Doxycycline"],
                    "Heatstroke": ["ORS", "Electrolytes"],
                    "Dehydration": ["ORS", "Electrolytes"],
                    "Respiratory infections": ["Cough Syrup", "Cetirizine", "Antibiotics"],
                    "Cold/Flu": ["Cetirizine", "Paracetamol", "Vitamin C"],
                    "Asthma": ["Salbutamol Inhaler"],
                }
                all_meds = set()
                for d in diseases:
                    all_meds.update(meds.get(d, []))
                recommendations.append({
                    "City": city["name"],
                    "Zone": zone,
                    "Risk": city["risk"],
                    "Top Diseases": ", ".join(diseases[:3]),
                    "Push Medicines": ", ".join(list(all_meds)[:5]),
                })

        if recommendations:
            df2 = pd.DataFrame(recommendations).sort_values("Risk", ascending=False)
            st.dataframe(df2, use_container_width=True, hide_index=True, height=400)
            st.markdown("##### 📌 Action")
            st.info("Retailers in high-risk zones should be encouraged to stock these medicines. "
                    "Send targeted promotion messages via Telegram/WhatsApp.")
        else:
            st.success("✅ No high-risk zones today. Standard stock levels apply.")

    # ─── Refresh + footer ───
    st.markdown("---")
    c_ref, c_src = st.columns([1, 3])
    with c_ref:
        if st.button("🔄 Refresh Weather", use_container_width=True):
            st.rerun()
    with c_src:
        _src = weather_data[0].get("source", "mock")
        _src_msg = "Live from OpenWeatherMap" if _src == "live" else "Using seasonal mock data (set OPENWEATHER_API_KEY in .env for live)"
        st.caption(f"📡 Source: {_src_msg}")


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Testing weather fetch...")
    weather_data = []
    for city in TN_CITIES:
        w = get_weather(city["name"], city["lat"], city["lon"])
        risk = disease_risk(city["zone"], w["temp"], w["humidity"], w["condition"])
        weather_data.append({**city, **w, "risk": risk})

    print(f"\n{'City':<15} {'Zone':<22} {'Temp':>6} {'Hum':>5} {'Risk':>5}")
    print("─" * 65)
    for c in weather_data:
        print(f"{c['name']:<15} {c['zone']:<22} {c['temp']:>5}°C {c['humidity']:>4}% {c['risk']:>4}/100")
