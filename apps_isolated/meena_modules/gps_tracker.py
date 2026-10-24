import streamlit as st
import pandas as pd
import json, os, glob

def render_owner_rep_map():
    st.markdown("### 🗺️ Sales Rep Live Tracking")
    st.caption("Real-time GPS locations — Thanjavur region")
    
    rep_files = glob.glob("rep_locations_*.json")
    if not rep_files:
        st.info("No tracking data yet. Sales reps need to log in from the field.")
        return
        
    all_locations = []
    for f in rep_files:
        with open(f) as fh:
            try: all_locations.extend(json.load(fh))
            except: pass
            
    if not all_locations:
        st.info("No location data recorded yet.")
        return
        
    try:
        import plotly.express as px
        df = pd.DataFrame(all_locations)
        df['datetime'] = pd.to_datetime(df['timestamp'])
        latest = df.sort_values('datetime').groupby('rep_id').last().reset_index()
        
        fig = px.scatter_mapbox(latest, lat="lat", lon="lng", hover_name="rep_id",
            zoom=10, center={"lat": 10.7870, "lon": 79.1378},
            mapbox_style="carto-darkmatter", color_discrete_sequence=["#00d4ff"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8eaf6"), height=500)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.warning("Plotly not installed, cannot render map.")
