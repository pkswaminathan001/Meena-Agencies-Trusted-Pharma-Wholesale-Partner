import streamlit as st
import json
import os

RULES_FILE = "pricing_rules.json"

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    # Default rules
    return {"tier1_amount": 10000, "tier1_discount_pct": 2.0, "tier2_amount": 50000, "tier2_discount_pct": 5.0}

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2)

def calculate_bulk_discount(cart_total):
    """Used by the Checkout Engine to apply discounts."""
    rules = load_rules()
    if cart_total >= rules["tier2_amount"]:
        return rules["tier2_discount_pct"], f"Bulk Tier 2 (>{rules['tier2_amount']}): {rules['tier2_discount_pct']}% OFF"
    elif cart_total >= rules["tier1_amount"]:
        return rules["tier1_discount_pct"], f"Bulk Tier 1 (>{rules['tier1_amount']}): {rules['tier1_discount_pct']}% OFF"
    return 0.0, "No bulk discount applied."

def render_b2b_pricing():
    st.markdown("## 🏷️ B2B Pricing & Schemes")
    st.caption("Configure automated bulk discounts for your retailers (Page 57 & 95).")

    rules = load_rules()

    with st.form("pricing_form"):
        st.markdown("### Set Discount Tiers")
        c1, c2 = st.columns(2)
        t1_amt = c1.number_input("Tier 1 Minimum Amount (₹)", value=float(rules["tier1_amount"]), step=1000.0)
        t1_pct = c2.number_input("Tier 1 Discount (%)", value=float(rules["tier1_discount_pct"]), step=0.5)
        
        c3, c4 = st.columns(2)
        t2_amt = c3.number_input("Tier 2 Minimum Amount (₹)", value=float(rules["tier2_amount"]), step=5000.0)
        t2_pct = c4.number_input("Tier 2 Discount (%)", value=float(rules["tier2_discount_pct"]), step=0.5)

        if st.form_submit_button("💾 Save Pricing Rules", type="primary"):
            new_rules = {
                "tier1_amount": t1_amt,
                "tier1_discount_pct": t1_pct,
                "tier2_amount": t2_amt,
                "tier2_discount_pct": t2_pct
            }
            save_rules(new_rules)
            st.success("✅ Pricing rules updated! Checkout will apply these automatically.")

    st.markdown("---")
    st.markdown("### 🧪 Test the Pricing Engine")
    test_amt = st.number_input("Test Cart Total (₹)", value=12000.0, step=1000.0)
    disc_pct, msg = calculate_bulk_discount(test_amt)
    discount_val = test_amt * (disc_pct / 100)
    
    st.write(f"**Status:** {msg}")
    st.write(f"**Discount Applied:** ₹{discount_val:,.2f}")
    st.write(f"**Final Payable:** ₹{test_amt - discount_val:,.2f}")
