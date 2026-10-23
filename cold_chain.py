import streamlit as st
import random
import time
import datetime

def render_cold_chain():
    st.markdown("## ❄️ Warehouse Cold-Chain Monitor")
    st.caption("Live IoT telemetry for temperature-sensitive medicines (2°C to 8°C).")

    # Initialize session state for the sensor
    if "temp_breach_start" not in st.session_state:
        st.session_state.temp_breach_start = None
    if "zone_locked" not in st.session_state:
        st.session_state.zone_locked = False

    st.markdown("### 🏢 Zone A: Vaccine & Biologics Storage")
    
    # We use a Streamlit fragment to auto-refresh the sensor every 3 seconds
    @st.fragment(run_every=3)
    def sensor_widget():
        # Simulate a temperature reading (mostly around 4°C, sometimes spiking)
        base_temp = 4.0
        if random.random() > 0.85: # 15% chance of a spike
            current_temp = round(random.uniform(8.1, 12.0), 1) 
        else:
            current_temp = round(random.uniform(2.0, 7.9), 1)

        # Display the metric
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Temp", f"{current_temp} °C", delta=f"{current_temp - 4.0:.1f} °C", delta_color="inverse")
        c2.metric("Target Range", "2.0 - 8.0 °C")
        
        # Status logic
        if 2.0 <= current_temp <= 8.0:
            c3.success("✅ OPTIMAL")
            st.session_state.temp_breach_start = None
        else:
            c3.error("🚨 BREACH DETECTED")
            
            # Track breach duration
            if st.session_state.temp_breach_start is None:
                st.session_state.temp_breach_start = time.time()
            
            # Calculate duration
            duration = time.time() - st.session_state.temp_breach_start
            
            if duration > 15: # Note: For demo, we will treat 15 seconds as 15 minutes
                st.session_state.zone_locked = True
                st.error(f"🔒 **ZONE LOCKED - BATCH QUARANTINE PENDING** (Breach duration: {int(duration)}s)")
                st.warning("All stock movement assigned to Zone A has been frozen. QA Manager override required.")
            else:
                st.warning(f"⚠️ Breach active for {int(duration)} seconds. If it exceeds 15 minutes (15s in demo), the zone will lock.")

        if st.session_state.zone_locked:
            st.error("❌ System requires QA Dual-Authorization to unlock this zone.")
            if st.button("🔓 Simulate QA Override & Unlock"):
                st.session_state.zone_locked = False
                st.session_state.temp_breach_start = None
                st.success("Zone unlocked by QA. Temperature must stabilize.")
                time.sleep(1)
                st.rerun()

    sensor_widget()

    st.markdown("---")
    st.markdown("### 📋 IoT Sensor Log")
    log_data = [
        {"Time": str(datetime.datetime.now() - datetime.timedelta(minutes=i)), "Zone": "Zone A", "Temp": f"{random.uniform(2, 8):.1f} °C", "Status": "Optimal"}
        for i in range(1, 6)
    ]
    st.table(log_data)
