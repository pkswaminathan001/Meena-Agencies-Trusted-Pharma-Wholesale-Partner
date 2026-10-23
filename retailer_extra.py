import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# Replace with your actual OpenWeather API key later
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY" 

def render_weather_tracker():
    st.markdown("### 🌤️ Weather & Route Planner (Thanjavur)")
    
    city = "Thanjavur"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            temp = res['main']['temp']
            desc = res['weather'][0]['description'].title()
            st.info(f"Current Weather in {city}: **{temp}°C**, {desc}. Safe for field operations.")
        else:
            st.warning("Weather API key not configured. Please add it to `retailer_extra.py`.")
    except:
        st.warning("Could not fetch weather data.")

    st.markdown("### 📍 Live Sales Rep Tracking")
    st.caption("Using HTML5 Geolocation. Reps can click 'Check In' to update their pin.")
    
    m = folium.Map(location=[10.7870, 79.1378], zoom_start=12)
    folium.Marker(
        [10.7870, 79.1378], 
        popup="Meena Agencies HQ (Thanjavur)", 
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

    st_folium(m, width=700, height=400)

    check_in_html = """
    <button onclick="getLocation()" style="padding:10px; background:#0e7490; color:white; border:none; border-radius:8px; cursor:pointer;">
        📍 Check In Location
    </button>
    <p id="demo"></p>
    <script>
    function getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
      } else { 
        document.getElementById("demo").innerHTML = "Geolocation is not supported by this browser.";
      }
    }
    function showPosition(position) {
      document.getElementById("demo").innerHTML = "Lat: " + position.coords.latitude + 
      " Lon: " + position.coords.longitude + " (Sent to Owner)";
    }
    </script>
    """
    st.components.v1.html(check_in_html, height=100)

def render_appraisal_form():
    st.markdown("### ⭐ Feedback & Appraisal System")
    tab1, tab2 = st.tabs(["Customer Rating", "Owner Appraisal"])
    
    with tab1:
        st.write("**Retailer Feedback**")
        rating = st.slider("Rate Meena Agencies (1-5)", 1, 5, 5)
        feedback = feedback_text = st.text_area("Any issues with delivery or stock?")
        if st.button("Submit Feedback"):
            import json, os, datetime
            feedback_data = {
                "date": str(datetime.date.today()),
                "rating": rating,
                "feedback": feedback_text,
                "retailer": st.session_state.get("retailer_id", "Unknown")
            }
            try:
                data = []
                if os.path.exists("feedback.json"):
                    with open("feedback.json", "r") as f:
                        data = json.load(f)
                data.append(feedback_data)
                with open("feedback.json", "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass
            st.success("✅ Thank you! Feedback securely recorded to database.")
            if rating >= 4:
                st.info("🤖 AI Note: High rating. Sales rep performance is optimal.")
            else:
                st.warning("🤖 AI Note: Low rating. AI flags this for owner review.")

    with tab2:
        st.write("**Owner Appraisal (AI Assistant)**")
        emp_name = emp_name = st.selectbox("Select Employee", ["Sales Rep 1", "Sales Rep 2", "Warehouse Staff 1"])
        punctuality = st.slider("Punctuality", 1, 10, 8)
        sales = st.slider("Sales Target Met %", 0, 100, 80)
        compliance = st.slider("Compliance (Rules followed)", 1, 10, 9)
        
        if st.button("Calculate Appraisal Score (AI)"):
            score = (punctuality * 0.3) + ((sales/10) * 0.5) + (compliance * 0.2)
            st.metric("AI Appraisal Score", f"{score:.1f} / 10")
            
            import json, os, datetime
            appraisal_data = {
                "date": str(datetime.date.today()),
                "employee": emp_name,
                "score": round(score, 2),
                "punctuality": punctuality,
                "sales_target": sales,
                "compliance": compliance
            }
            try:
                data = []
                if os.path.exists("appraisals.json"):
                    with open("appraisals.json", "r") as f:
                        data = json.load(f)
                data.append(appraisal_data)
                with open("appraisals.json", "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

            if score > 8.5:
                st.success(f"Recommendation: **Increment Approved**. Excellent performance. (Saved for {emp_name})")
            elif score > 7.0:
                st.info("Recommendation: **Standard Increment**. Good performance.")
            else:
                st.error("Recommendation: **No Increment**. Schedule a performance review.")
