import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def render_expiry_engine():
    st.markdown("## ⚠️ Expiry Risk Dashboard")
    st.caption("A visual command center to prevent dead stock and financial losses.")

    # 1. Load Data securely from the Enterprise DB
    db_path = BASE_DIR / "meena_enterprise.db"
    if not db_path.exists():
        st.error("Database not found. Please run the cloud bootstrap script.")
        return

    @st.cache_data(ttl=300) # Caches data for 5 minutes
    def load_db():
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT sku as SKU, batch as Batch, qty as Qty, expiry as Expiry FROM products", conn)
        conn.close()
        return df

    try:
        df = load_db()
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return

    if df.empty:
        st.info("No inventory found in the database.")
        return

    # 2. Calculate Risk
    df["Expiry_Date"] = pd.to_datetime(df["Expiry"])
    today = datetime.today()
    df["Days_Left"] = (df["Expiry_Date"] - today).dt.days

    # 3. Categorize into buckets
    critical = df[df["Days_Left"] <= 30].sort_values("Days_Left")
    warning = df[(df["Days_Left"] > 30) & (df["Days_Left"] <= 90)].sort_values("Days_Left")
    safe = df[df["Days_Left"] > 90]

    # 4. Top-Level KPI Metrics
    st.markdown("### 📊 Inventory Health Summary")
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Total SKUs", f"{len(df):,}")
    c2.metric("🚨 Critical (<30 Days)", f"{len(critical):,}", delta="Needs Action", delta_color="inverse")
    c3.metric("⚠️ Warning (30-90 Days)", f"{len(warning):,}", delta="Review Soon", delta_color="off")
    c4.metric("✅ Safe (>90 Days)", f"{len(safe):,}", delta="Healthy", delta_color="normal")

    st.markdown("---")

    # 5. Visual UI for Critical Items
    st.markdown("### 🚨 Critical Action Required (Expiring < 30 Days)")
    if critical.empty:
        st.success("✅ No critical items expiring in the next 30 days!")
    else:
        for _, row in critical.head(10).iterrows(): # Show top 10 to keep it clean
            with st.container():
                st.markdown(f"""
                <div style="background-color: #FADBD8; border-left: 5px solid #C0392B; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #922B21;">{row['SKU']}</h4>
                    <p style="margin: 5px 0 0 0; color: #1C2833;">
                        <b>Batch:</b> {row['Batch']} | <b>Qty:</b> {row['Qty']} | <b>Expires in:</b> {row['Days_Left']} days ({row['Expiry']})
                    </p>
                </div>
                """, unsafe_allow_html=True)
        if len(critical) > 10:
            st.warning(f"... and {len(critical) - 10} more critical items. Please use the Data tab below to download the full list.")

    # 6. Visual UI for Warning Items
    st.markdown("### ⚠️ Warning Zone (Expiring in 30-90 Days)")
    if warning.empty:
        st.success("✅ No warning items in this range.")
    else:
        for _, row in warning.head(5).iterrows(): # Show top 5
            with st.container():
                st.markdown(f"""
                <div style="background-color: #FDEBD0; border-left: 5px solid #D35400; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #A04000;">{row['SKU']}</h4>
                    <p style="margin: 5px 0 0 0; color: #1C2833;">
                        <b>Batch:</b> {row['Batch']} | <b>Qty:</b> {row['Qty']} | <b>Expires in:</b> {row['Days_Left']} days
                    </p>
                </div>
                """, unsafe_allow_html=True)
        if len(warning) > 5:
            st.info(f"Showing top 5 of {len(warning)} warning items.")

    st.markdown("---")

    # 7. Safe Inventory & Download Option
    with st.expander("✅ View Safe Inventory (>90 Days) & Download Full Report"):
        st.dataframe(safe, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Inventory Risk Report (CSV)",
            data=csv,
            file_name=f"expiry_risk_report_{today.date()}.csv",
            mime="text/csv",
            type="primary"
        )
