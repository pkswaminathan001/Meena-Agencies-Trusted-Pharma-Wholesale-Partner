import streamlit as st
import pandas as pd

def render_checkout():
    st.title("💳 Secure B2B Checkout")
    st.caption("Review your order and complete payment via UPI or Credit Line.")
    st.divider()

    cart = st.session_state.get("cart", [])
    if not cart:
        st.warning("Your cart is empty. Please add items before checking out.")
        if st.button("Return to Catalog", type="primary"):
            st.session_state.page = "order"
            st.rerun()
        return

    # ─── ORDER SUMMARY ───
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🧾 Order Details")
        df = pd.DataFrame(cart)
        df["Total"] = df["price"] * df["qty"]
        
        # Format the dataframe for display
        display_df = df[["name", "qty", "price", "Total"]].rename(columns={
            "name": "Medicine", "qty": "Qty", "price": "Unit Price", "Total": "Total Price"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    with col2:
        st.subheader("💰 Bill Summary")
        subtotal = sum(item["price"] * item["qty"] for item in cart)
        
        # GST Logic (12% for Pharma formulations)
        gst = subtotal * 0.12
        delivery = 150.00 if subtotal < 10000 else 0.00
        grand_total = subtotal + gst + delivery
        
        st.write(f"**Subtotal:** ₹ {subtotal:,.2f}")
        st.write(f"**GST (12%):** ₹ {gst:,.2f}")
        st.write(f"**Delivery:** ₹ {delivery:,.2f}")
        st.divider()
        st.subheader(f"Total Payable: ₹ {grand_total:,.2f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ─── PAYMENT GATEWAY ───
        st.subheader("🔒 Select Payment Method")
        payment_method = st.radio("Choose method:", ["UPI (GPay / PhonePe)", "Credit Line (Net 30)", "NEFT / RTGS"])
        
        if payment_method == "UPI (GPay / PhonePe)":
            st.info("Scan the QR code or enter your UPI ID to complete the payment.")
            upi_id = st.text_input("Enter UPI ID", placeholder="yourname@okhdfcbank")
            
            if st.button(f"Pay ₹ {grand_total:,.2f} Securely", type="primary", use_container_width=True):
                if not upi_id:
                    st.error("Please enter a valid UPI ID.")
                else:
                    with st.spinner("Connecting to Payment Gateway..."):
                        import time
                        time.sleep(2) # Simulating Razorpay/Stripe delay
                        st.success("🎉 Payment Successful! Order Confirmed.")
                        st.balloons()
                        st.session_state.cart = []
                        st.session_state.page = "home"
                        st.rerun()
                        
        elif payment_method == "Credit Line (Net 30)":
            st.warning("⚠️ Placing this order will add to your outstanding balance.")
            if st.button("Confirm Order on Credit", type="primary", use_container_width=True):
                st.success("✅ Order Confirmed! Invoice sent to your email.")
                st.session_state.cart = []
                st.session_state.page = "home"
                st.rerun()
