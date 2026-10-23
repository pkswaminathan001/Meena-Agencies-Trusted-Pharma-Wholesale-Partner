import streamlit as st
import pandas as pd
import os

def render_forecast_hub():
    st.markdown("## 📈 AI Forecasting Hub")
    st.caption("AutoARIMA (Seasonal) & Croston (Erratic) predictions based on local data.")

    excel_file = "local_pharma_replenishment_plan.xlsx"

    if not os.path.exists(excel_file):
        st.warning(f"⚠️ Forecast file not found. Please run `python3 pharma_local_engine.py` in your terminal first.")
        if st.button("Run Forecast Now"):
            with st.spinner("Running AI engine... this takes 10-15 seconds..."):
                os.system("python3 pharma_local_engine.py")
            st.rerun()
        return

    # Load the data
    df = pd.read_excel(excel_file)
    
    # KPI Metrics
    total_items = len(df)
    fast_movers = len(df[df["unique_id"].str.contains("OTC")])
    erratic_movers = len(df[df["unique_id"].str.contains("ONCOLOGY")])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total SKUs Forecasted", total_items)
    c2.metric("Fast Movers (AutoARIMA)", fast_movers)
    c3.metric("Erratic Items (Croston)", erratic_movers)

    st.markdown("---")
    
    # Show the table
    st.markdown("### 📋 Suggested Procurement Plan")
    st.dataframe(
        df[["unique_id", "ds", "FINAL_SUGGESTED_ORDER_QUANTITY", "APPLIED_LOGIC_RULE"]],
        use_container_width=True,
        hide_index=True
    )

    # Show a chart
    st.markdown("### 📊 Visual Demand Projection")
    pivot_df = df.pivot(index="ds", columns="unique_id", values="FINAL_SUGGESTED_ORDER_QUANTITY")
    st.bar_chart(pivot_df)
