import streamlit as st
import json
import datetime
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def render_rep_checkin(user):
    st.title("📍 Sales Rep Check-In")
    st.caption("Click below to mark your attendance and share your live location with the Owner.")
    
    # Ask for browser location
    loc = get_geolocation()
    
    if loc:
        try:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            st.success(f"✅ Location captured: {lat:.4f}, {lon:.4f}")
            
            if st.button("Confirm Check-In", type="primary", use_container_width=True):
                file_path = BASE_DIR / "rep_locations.json"
                data = {}
                if file_path.exists():
                    with open(file_path, "r") as f:
                        data = json.load(f)
                
                data[user["id"]] = {
                    "name": user["shop"],
                    "lat": lat,
                    "lon": lon,
                    "time": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                }
                
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                
                st.balloons()
                st.success("🎉 Check-In Successful! The Owner can now see you on the map.")
        except:
            st.warning("Could not read GPS. Please allow location access.")
    else:
        st.info("⏳ Waiting for GPS permission. Please click 'Allow' on your browser.")

def render_owner_map():
    st.title("🦅 Owner Eagle-Eye View")
    st.caption("Live location of all Sales Representatives. Use this to track work and defend against false claims.")
    
    file_path = BASE_DIR / "rep_locations.json"
    if not file_path.exists():
        st.warning("No reps have checked in yet.")
        return
        
    with open(file_path, "r") as f:
        data = json.load(f)
        
    if not data:
        st.warning("No reps have checked in yet.")
        return

    # Center map on Thanjavur
    m = folium.Map(location=[10.7870, 79.1378], zoom_start=11)
    
    for rep_id, info in data.items():
        folium.Marker(
            [info["lat"], info["lon"]],
            popup=f"<b>{info['name']}</b><br>Time: {info['time']}",
            tooltip=f"{info['name']} (Last seen: {info['time'].split(' ')[1]})",
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(m)
        
    st_folium(m, width=700, height=500)
    
    st.divider()
    st.markdown("### 📋 Check-In Log")
    for rep_id, info in data.items():
        st.write(f"**{info['name']}** checked in at `{info['time']}` (Lat: {info['lat']:.4f}, Lon: {info['lon']:.4f})")
