import streamlit as st
import pandas as pd
import io

def render_order_intake():
    st.markdown("## 📥 Smart Order Intake")
    st.caption("Upload a retailer order (Excel/CSV). The system will parse it and create a draft.")

    uploaded_file = st.file_uploader("Upload Order File (Excel or CSV)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("✅ File parsed successfully!")
            st.markdown("### Extracted Order Data")
            st.dataframe(df, use_container_width=True)

            # Simulate AI Matching
            st.markdown("### 🤖 AI Matching & Draft Generation")
            if st.button("✨ Generate Draft Order", type="primary"):
                with st.spinner("Matching SKUs and checking credit limits..."):
                    # Simulate a match process
                    st.info("✅ All items matched to internal SKUs.")
                    st.warning("⚠️ 1 item is low in stock (replenishment suggested).")
                    st.success("📝 Draft Order created successfully! Ready for owner approval.")
                    
        except Exception as e:
            st.error(f"Error parsing file: {e}")
    else:
        st.info("Please upload a file to begin. (Tip: Create a CSV with columns 'Medicine Name' and 'Quantity')")
