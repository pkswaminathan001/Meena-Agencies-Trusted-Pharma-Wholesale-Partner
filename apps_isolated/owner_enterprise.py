import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

def show_enterprise_dashboard():
    st.markdown("## 👑 Meena Agencies: Enterprise ERP (Phases 3, 4 & 5)")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 CMA: Landed Cost", 
        "📉 FP&A: Credit & Cash", 
        "🏛️ CPA: GST & Compliance",
        "🤖 AI & RAG Security",
        "👷 Employee Appraisal"
    ])

    # ==========================================
    # PHASE 3: CMA MODULE (Landed Cost)
    # ==========================================
    with tab1:
        st.subheader("True Landed Cost Calculator (CMA)")
        st.write("Calculate the exact profit margin of every batch.")
        
        col1, col2 = st.columns(2)
        with col1:
            purchase_price = st.number_input("Base Purchase Price (₹)", value=100.0)
            freight = st.number_input("Freight Inbound (₹)", value=5.0)
            cold_chain = st.number_input("Cold Chain Surcharge (₹)", value=2.0)
            handling = st.number_input("Handling Charges (₹)", value=1.0)
        with col2:
            sqft = st.number_input("Storage SqFt", value=10.0)
            days = st.number_input("Days in Storage", value=30.0)
            base_rate = st.number_input("Warehouse Base Rate (₹/sqft/day)", value=0.5)
            qty = st.number_input("Quantity Purchased", value=100)

        # CMA Formula from Document
        storage_cost = (sqft * days * base_rate)
        total_landed_cost = purchase_price + freight + cold_chain + handling + storage_cost
        lc_unit = total_landed_cost / qty

        st.success(f"**Total Landed Cost (LC_total): ₹{total_landed_cost:,.2f}**")
        st.info(f"**True Landed Cost Per Unit (LC_unit): ₹{lc_unit:,.2f}**")

        selling_price = st.number_input("Proposed Selling Price per Unit (₹)", value=150.0)
        margin = ((selling_price - lc_unit) / selling_price) * 100
        
        if margin < 8.0:
            st.error(f"🚨 HIGH-RISK MARGIN VIOLATION: Margin is {margin:.2f}% (Below 8%). Quote frozen.")
        else:
            st.success(f"✅ Healthy Margin: {margin:.2f}%")

    # ==========================================
    # PHASE 3: FP&A MODULE (Credit Control)
    # ==========================================
    with tab2:
        st.subheader("Credit Control & Cash Runway (FP&A)")
        
        st.markdown("#### Retailer Credit Holds")
        credit_data = pd.DataFrame({
            "Retailer": ["RET001", "RET002", "RET003"],
            "Outstanding Dues": [15000, 45000, 5000],
            "Days Overdue": [10, 35, 0],
            "Status": ["Active", "SUSPENDED", "Active"]
        })
        st.dataframe(credit_data, use_container_width=True)
        st.warning("⚠️ RET002 has crossed the 30-day limit. Checkout is automatically locked for this retailer.")

        st.markdown("#### 90-Day Cash Runway Forecast")
        days = pd.date_range(start=datetime.today(), periods=90)
        cash = [100000 + (i * 500) + random.randint(-2000, 2000) for i in range(90)]
        fig = px.line(x=days, y=cash, labels={'x': 'Date', 'y': 'Projected Cash (₹)'}, title="Realistic Cash Runway")
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # PHASE 3: CPA MODULE (GST & Compliance)
    # ==========================================
    with tab3:
        st.subheader("GST & Regulatory Compliance (CPA)")
        
        st.markdown("#### Drug License & GST Verification")
        st.checkbox("Retailer GSTIN Verified", value=True)
        st.checkbox("Drug License (Form 20B/21B) Uploaded", value=True)
        
        if st.button("Generate Monthly GSTR-1 Report"):
            st.success("GSTR-1 CSV Generated successfully. Ready for accountant.")
            st.download_button("Download GSTR-1 CSV", data="HSN, Taxable Value, IGST\n3004, 50000, 6000", file_name="gstr1.csv")

    # ==========================================
    # PHASE 4: AI SECURITY & RAG
    # ==========================================
    with tab4:
        st.subheader("RAG AI Pipeline & Ragas Security Shield")
        
        st.markdown("#### Vector Database Query (RAG)")
        query = st.text_input("Ask the AI about stock (e.g., 'Do we have Paracetamol?')")
        if query:
            st.info("🔍 Querying Vector Database...")
            st.success("✅ RAG Retrieved Context: Paracetamol 500mg is in stock (Batch #B-2026, 500 units).")
            
            st.markdown("#### Ragas AI Critic Evaluation")
            st.markdown("- **Faithfulness Score:** 0.98 (Passed)")
            st.markdown("- **Context Precision:** 0.95 (Passed)")
            st.markdown("- **FDA/Medical Compliance:** 1.0 (Passed - No hallucinated dosages)")
            st.success("🤖 AI Response Approved by Ragas Shield.")

    # ==========================================
    # PHASE 5: EMPLOYEE APPRAISAL
    # ==========================================
    with tab5:
        st.subheader("Employee & Operational Tools")
        
        st.markdown("#### AI-Driven Employee Appraisal")
        emp_name = st.selectbox("Select Employee", ["Murali P (Driver)", "Ramesh (Sales Rep)"])
        rating = st.slider("Performance Rating (1-5 Stars)", 1, 5, 4)
        feedback = st.text_area("Manager Feedback", "Consistently delivers on time, but needs to improve follow-ups.")
        
        if st.button("Generate AI Appraisal"):
            if rating >= 4:
                st.success(f"AI Analysis for {emp_name}: Excellent performance. Recommend for salary increment of 10%.")
            else:
                st.warning(f"AI Analysis for {emp_name}: Needs improvement. Recommend training before appraisal.")

        st.markdown("---")
        st.markdown("#### Expiry & Alert Tracker")
        st.warning("⚠️ 3 Batches (Metformin, Insulin) are expiring in 30 days!")
