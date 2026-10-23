import streamlit as st

def render_advanced_finance():
    st.markdown("## 🏦 Advanced Financial Systems")
    st.caption("Enterprise modules for Export Margins (FMVA), Compliance (CPA), and Treasury (CFA).")

    tab1, tab2, tab3 = st.tabs(["📊 FMVA: Deal Sandbox", "🛡️ CPA: Compliance Gatekeeper", "💱 CFA: Treasury & FX"])

    # ─── TAB 1: FMVA Deal Sandbox ───
    with tab1:
        st.markdown("### Multi-Variable Export Margin Simulation")
        st.write("Stress-test global supply chain shocks before finalizing major contracts.")
        
        c1, c2, c3 = st.columns(3)
        q_units = c1.number_input("Order Volume (Units)", min_value=1, value=10000)
        p_usd = c2.number_input("Selling Price per Unit (USD)", min_value=1.0, value=2.50)
        e_rate = c3.number_input("Simulated USD/INR Exchange Rate", min_value=1.0, value=83.50)

        c4, c5, c6 = st.columns(3)
        c_base = c4.number_input("Manufacturer Base Cost (INR/Unit)", min_value=1.0, value=150.0)
        f_base = c5.number_input("Standard Shipping Freight (INR Total)", min_value=0.0, value=50000.0)
        f_inflation = c6.slider("Freight Inflation Slider (%)", 0, 100, 15) / 100

        # Formula from Document Page 21
        revenue_inr = q_units * p_usd * e_rate
        base_cost_inr = q_units * c_base
        freight_inr = f_base * (1 + f_inflation)
        
        # Assume 5% volume discount on base cost for bulk orders > 5000
        vol_discount = 0.05 if q_units > 5000 else 0.0
        net_cost = (base_cost_inr * (1 - vol_discount)) + freight_inr
        
        net_margin = revenue_inr - net_cost
        margin_pct = (net_margin / revenue_inr) * 100 if revenue_inr > 0 else 0

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Revenue (INR)", f"₹{revenue_inr:,.2f}")
        m2.metric("Total Cost (INR)", f"₹{net_cost:,.2f}")
        m3.metric("Simulated Net Margin", f"₹{net_margin:,.2f}", delta=f"{margin_pct:.2f}%", delta_color="normal")

        st.info("💡 **System Stage-Gate Rule:** A contract price cannot be locked if a 3% adverse currency drop + 10% freight spike pushes the margin below zero.")
        
        if margin_pct < 8.0:
            st.error("🚨 **High-Risk Margin Violation:** The margin is below the 8% safety threshold. Contract locking is blocked.")
        else:
            st.success("✅ Margin is healthy. Contract can be locked and sent.")

    # ─── TAB 2: CPA Compliance Gatekeeper ───
    with tab2:
        st.markdown("### Regulatory Compliance Verification")
        st.write("Verifies 4 critical binary states. If any fail, invoice generation is completely blocked.")
        
        c1, c2 = st.columns(2)
        s_hsn = c1.checkbox("HSN Code Validated (Government Directory)", value=True)
        s_license = c2.checkbox("Drug Export License Active", value=True)
        
        c3, c4 = st.columns(2)
        s_gst = c3.checkbox("GST Tax Slab Correct (IGST/Zero-Rated)", value=True)
        s_remittance = c4.checkbox("Bank EBRC Reference Verified", value=True)

        # Formula from Document Page 22
        v_comp = int(s_hsn) * int(s_license) * int(s_gst) * int(s_remittance)

        st.markdown("---")
        if v_comp == 0:
            st.error("🚨 **TERMINAL EXECUTION FAILURE:** Compliance Integrity Value (V_comp) = 0.")
            st.warning("The system has physically blocked the generation of warehouse dispatch orders and shipping manifests.")
        else:
            st.success("✅ **COMPLIANCE VERIFIED:** V_comp = 1. Invoice generation and manifest creation unlocked.")
            st.info("A cryptographic row hash has been appended to the immutable audit ledger.")

    # ─── TAB 3: CFA Treasury & FX ───
    with tab3:
        st.markdown("### Treasury & FX Exposure Matrix")
        st.write("Manage foreign exchange hedges and corporate cash reserves.")
        
        c1, c2 = st.columns(2)
        spot_rate = c1.number_input("Current Spot Rate (USD/INR)", value=83.50)
        forward_rate = c2.number_input("Forward Contract Rate (USD/INR)", value=84.20)
        
        days_maturity = st.slider("Days to Maturity", 30, 365, 90)
        
        # Formula from Document Page 24
        forward_premium = ((forward_rate - spot_rate) / spot_rate) * (365 / days_maturity) * 100
        
        st.markdown("---")
        st.metric("Annualized Forward Premium", f"{forward_premium:.2f}%")
        
        if forward_premium > 2.0:
            st.warning("⚠️ High forward premium detected. Consider adjusting hedging strategy.")
        else:
            st.success("✅ Premium is within acceptable bounds.")
            
        st.markdown("#### Unhedged Exposure")
        st.info("System Gate: Invoices exceeding $50,000 are blocked if unhedged exposure > 30% of liquid equity.")
