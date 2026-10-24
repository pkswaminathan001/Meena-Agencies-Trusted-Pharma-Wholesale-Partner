import streamlit as st
import pandas as pd
import os

def render_forecast_dashboard():
    st.markdown("### 📈 AI Demand Forecasting")
    st.caption("AutoARIMA & Croston predictions based on local data.")
    
    excel_file = "local_pharma_replenishment_plan.xlsx"
    if not os.path.exists(excel_file):
        st.warning("⚠️ Forecast file not found. Run `python3 pharma_local_engine.py` first.")
        return
        
    try:
        df = pd.read_excel(excel_file)
        
        # Show metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total SKUs Forecasted", len(df))
        c2.metric("Fast Movers (AutoARIMA)", len(df[df["unique_id"].str.contains("OTC")]))
        c3.metric("Erratic Items (Croston)", len(df[df["unique_id"].str.contains("ONCOLOGY")]))
        
        st.markdown("---")
        st.dataframe(
            df[["unique_id", "ds", "FINAL_SUGGESTED_ORDER_QUANTITY", "APPLIED_LOGIC_RULE"]],
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error loading forecast: {e}")
