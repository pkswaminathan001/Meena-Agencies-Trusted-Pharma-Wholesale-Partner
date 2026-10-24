import streamlit as st
import json
import datetime
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def init_rep_db():
    db_path = BASE_DIR / "meena_enterprise.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rep_locations (
        rep_id TEXT PRIMARY KEY,
        name TEXT,
        lat REAL,
        lon REAL,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def render_rep_checkin(user):
    st.title("📍 Sales Rep Check-In")
    st.warning("⚠️ **Note:** For exact GPS tracking, please open this on a mobile phone with Location turned ON. Laptops use IP/Wi-Fi, which can be off by several kilometers.")
    st.caption("Click below to mark your attendance and share your live location with the Owner.")
    
    loc = get_geolocation(expire_time=300)
    
    if loc:
        try:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            st.success(f"✅ Location captured: {lat:.4f}, {lon:.4f}")
            
            if st.button("Confirm Check-In", type="primary", use_container_width=True):
                init_rep_db()
                db_path = BASE_DIR / "meena_enterprise.db"
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # Insert or replace location
                c.execute("INSERT OR REPLACE INTO rep_locations (rep_id, name, lat, lon, timestamp) VALUES (?, ?, ?, ?, ?)",
                          (user["id"], user["shop"], lat, lon, now))
                conn.commit()
                conn.close()
                
                st.balloons()
                st.success("🎉 Check-In Successful! The Owner can now see you on the map.")
        except Exception as e:
            st.warning(f"Could not read GPS. Error: {e}")
    else:
        st.info("⏳ Waiting for GPS permission. Please click 'Allow' on your browser.")

def render_owner_map():
    st.title("🦅 Owner Eagle-Eye View")
    st.caption("Live location of all Sales Representatives.")
    
    init_rep_db()
    db_path = BASE_DIR / "meena_enterprise.db"
    
    try:
        conn = sqlite3.connect(db_path)
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM rep_locations", conn)
        conn.close()
    except:
        df = pd.DataFrame()

    if df.empty:
        st.warning("No reps have checked in yet. Ask a rep to log in and check in.")
        return

    m = folium.Map(location=[10.7870, 79.1378], zoom_start=11)
    
    for _, row in df.iterrows():
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"<b>{row['name']}</b><br>Time: {row['timestamp']}",
            tooltip=f"{row['name']}",
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(m)
        
    st_folium(m, width=700, height=500)
    
    st.divider()
    st.markdown("### 📋 Check-In Log")
    st.dataframe(df[['name', 'timestamp', 'lat', 'lon']], use_container_width=True)
