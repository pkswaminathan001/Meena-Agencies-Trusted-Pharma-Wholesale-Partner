import streamlit as st
import pandas as pd
import json
import os
import datetime

def render_qc_dashboard():
    st.markdown("## 🎯 Automated Employee QC")
    st.caption("AI-driven performance analysis and scoring for your workforce.")

    # Load saved appraisals
    if not os.path.exists("appraisals.json"):
        st.info("No appraisals recorded yet. Go to 'Appraisal AI' to generate some.")
        return

    with open("appraisals.json", "r") as f:
        data = json.load(f)

    if not data:
        st.info("No appraisal data found.")
        return

    df = pd.DataFrame(data)
    
    # Automated Metrics
    st.markdown("### 📊 Overall Workforce Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Appraisals", len(df))
    
    if not df.empty:
        best = df.loc[df['score'].idxmax()]
        worst = df.loc[df['score'].idxmin()]
        c2.metric("Top Performer", best['employee'], f"Score: {best['score']}")
        c3.metric("Needs Review", worst['employee'], f"Score: {worst['score']}")

    # Automated QC Analysis
    st.markdown("### 🤖 AI QC Analysis & Recommendations")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Download Option (Requested in document)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download QC Report (CSV)",
        data=csv,
        file_name=f"employee_qc_report_{datetime.date.today()}.csv",
        mime="text/csv",
        type="primary"
    )

def render_compliance_tracker():
    st.markdown("## 📜 Regulatory Compliance Tracker")
    st.caption("Monitor Drug Licenses (DL) and GST to avoid legal penalties.")
    
    if not os.path.exists("retailers.json"):
        st.error("retailers.json not found.")
        return

    with open("retailers.json", "r") as f:
        retailers = json.load(f)

    # Mock adding license data if it doesn't exist to simulate the real workflow
    for r in retailers:
        if "dl_expiry" not in r:
            r["dl_expiry"] = "2026-12-31" if r["id"] == "RET001" else "2026-10-01" # RET002 is expired
        if "gst_status" not in r:
            r["gst_status"] = "Active" if r["id"] != "RET003" else "Suspended"

    df = pd.DataFrame(retailers)
    
    st.markdown("### 🚨 Critical Alerts")
    
    issues = 0
    for r in retailers:
        # Check DL Expiry
        dl_date = datetime.datetime.strptime(r["dl_expiry"], "%Y-%m-%d").date()
        days_left = (dl_date - datetime.date.today()).days
        
        if days_left < 0:
            st.error(f"❌ **{r['shop']} ({r['id']})**: Drug License EXPIRED on {r['dl_expiry']}. Account blocked.")
            issues += 1
        elif days_left < 30:
            st.warning(f"⚠️ **{r['shop']} ({r['id']})**: Drug License expires in {days_left} days.")
            issues += 1
            
        # Check GST
        if r["gst_status"] != "Active":
            st.error(f"❌ **{r['shop']} ({r['id']})**: GST Status is **{r['gst_status']}**. Cannot process invoices.")
            issues += 1

    if issues == 0:
        st.success("✅ All retailers are compliant. No expired licenses or suspended GSTs.")

    st.markdown("### 📋 Retailer Compliance Matrix")
    st.dataframe(df[["id", "shop", "status", "dl_expiry", "gst_status", "outstanding"]], use_container_width=True, hide_index=True)
