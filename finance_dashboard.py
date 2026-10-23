import streamlit as st
import pandas as pd
import numpy as np
import json
import os

def render_finance_hub():
    st.markdown("## 💰 Finance & Credit Hub")
    st.caption("Enterprise Financial Management: CMA Landed Cost & FP&A Cash Runway.")

    tab1, tab2 = st.tabs(["📦 True Landed Cost (CMA)", "📈 90-Day Cash Runway (FP&A)"])

    # ─── TAB 1: True Landed Cost ───
    with tab1:
        st.markdown("### Calculate True Batch Cost")
        st.write("Determine the actual cost of a batch to prevent hidden margin leaks.")
        
        c1, c2, c3 = st.columns(3)
        base_price = c1.number_input("Base Purchase Price (₹)", min_value=0.0, value=50000.0, step=1000.0)
        quantity = c2.number_input("Total Batch Units", min_value=1, value=1000)
        freight = c3.number_input("Inbound Freight (₹)", min_value=0.0, value=2500.0)

        c4, c5 = st.columns(2)
        cold_chain = c4.number_input("Cold Chain Surcharge (₹)", min_value=0.0, value=1500.0)
        handling = c5.number_input("Handling Charges (₹)", min_value=0.0, value=500.0)

        total_landed_cost = base_price + freight + cold_chain + handling
        cost_per_unit = total_landed_cost / quantity

        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("Total Landed Cost", f"₹{total_landed_cost:,.2f}")
        m2.metric("True Cost Per Unit", f"₹{cost_per_unit:,.2f}")
        
        st.info("💡 **System Stage-Gate Rule:** If you sell this unit for less than ₹" + f"{cost_per_unit * 1.08:,.2f} (8% margin), the system will block invoice generation.")

    # ─── TAB 2: 90-Day Cash Runway ───
    with tab2:
        st.markdown("### 90-Day Cash Flow Projection")
        st.write("Predicts liquidity by matching receivables against operational burn.")

        # Load outstanding from retailers.json
        receivables = 0.0
        if os.path.exists("retailers.json"):
            with open("retailers.json", "r") as f:
                retailers = json.load(f)
                receivables = sum(r.get("outstanding", 0) for r in retailers)

        # Mock Payables & Burn
        c1, c2 = st.columns(2)
        payables = c1.number_input("Total Payables to Manufacturers (₹)", min_value=0.0, value=150000.0, step=10000.0)
        monthly_burn = c2.number_input("Monthly Operational Burn (₹)", min_value=0.0, value=80000.0, step=5000.0)

        daily_burn = monthly_burn / 30
        starting_cash = 500000.0 # Mock starting cash balance

        # Projection Loop (90 days)
        days = np.arange(90)
        cash_balances = []
        current_cash = starting_cash

        for day in days:
            # Assume receivables come in evenly over 45 days
            inflow = (receivables / 45) if day < 45 else 0
            # Assume payables go out evenly over 60 days
            outflow = (payables / 60) if day < 60 else 0
            
            current_cash = current_cash + inflow - outflow - daily_burn
            cash_balances.append(current_cash)

        # Create Chart Data
        chart_data = pd.DataFrame({"Day": days, "Projected Cash Balance": cash_balances})
        chart_data.set_index("Day", inplace=True)

        st.markdown("---")
        st.line_chart(chart_data, color="#0e7490")

        # Stage-Gate Warning
        min_cash = min(cash_balances)
        if min_cash < 100000:
            st.error(f"🚨 **Stage-Gate Alert:** Projected cash drops below ₹1,00,000 on Day {cash_balances.index(min_cash)}. Outbound purchase orders will be disabled.")
        else:
            st.success(f"✅ Cash runway is healthy. Lowest projected balance is ₹{min_cash:,.2f}.")
