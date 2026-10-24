import streamlit as st
import urllib.parse
import json
import os
import datetime
from pathlib import Path

# Safely import the Telegram notifier we created earlier
try:
    from telegram_notify import send_message
except ImportError:
    send_message = None

def render_upi_payment(order, retailer):
    UPI_ID = "prswaminathan1@okicici"
    PAYEE_NAME = "Meena Agencies"
    total = order.get('total', 0)
    order_id = order.get('order_id', f"ORD-{datetime.datetime.now().strftime('%M%S')}")

    # 1. Generate the UPI Deep Link
    upi_params = {
        "pa": UPI_ID,
        "pn": PAYEE_NAME,
        "am": f"{total:.2f}",
        "cu": "INR",
        "tn": f"Order {order_id}"
    }
    upi_url = f"upi://pay?{urllib.parse.urlencode(upi_params)}"

    # 2. Generate QR Code
    encoded_upi = urllib.parse.quote(upi_url, safe='')
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={encoded_upi}"

    st.markdown("### 💳 Secure UPI Payment")
    st.info(f"Please pay **₹{total:,.2f}** to **{UPI_ID}**")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(qr_image_url, width=220)

    # 3. Direct "Pay" button
    st.markdown(
        f'<a href="{upi_url}" style="display:block;text-align:center;padding:16px;'
        f'margin:1rem 0;background:linear-gradient(135deg,#1D8348,#0B3C5D);color:#fff;'
        f'font-weight:700;border-radius:12px;text-decoration:none;">'
        f'📱 Open UPI App & Pay</a>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### ✅ Confirm Your Payment")
    st.caption("After paying, enter the 12-digit UTR/Transaction ID from your app.")
    
    txn_id = st.text_input("Enter UTR / Transaction ID", key=f"upi_utr_{order_id}")
    
    if st.button("I have paid, confirm my order", type="primary", use_container_width=True):
        if txn_id.strip():
            # --- SAVE ORDER TO DATABASE ---
            orders_file = Path("orders.json")
            orders = []
            if orders_file.exists():
                try:
                    with open(orders_file, "r") as f:
                        orders = json.load(f)
                except:
                    pass
            
            new_order = {
                "order_id": order_id,
                "retailer_id": retailer.get("id", "UNKNOWN"),
                "shop": retailer.get("shop", "Unknown"),
                "total": total,
                "items": order.get("items", []),
                "payment_method": "UPI Direct",
                "utr": txn_id.strip(),
                "status": "Pending Verification",
                "timestamp": str(datetime.datetime.now())
            }
            orders.append(new_order)
            
            with open(orders_file, "w") as f:
                json.dump(orders, f, indent=2)

            # --- NOTIFY OWNER VIA TELEGRAM ---
            if send_message:
                alert_text = (
                    f"💰 *NEW UPI PAYMENT RECEIVED*\n\n"
                    f"Order: {order_id}\n"
                    f"Shop: {retailer.get('shop', 'Unknown')}\n"
                    f"Amount: ₹{total:,.2f}\n"
                    f"UTR: {txn_id.strip()}\n\n"
                    f"⚠️ Please check your bank app to verify this UTR before packing."
                )
                send_message(alert_text)

            # --- SUCCESS UI ---
            st.success(f"✅ Order {order_id} recorded! Payment reference: {txn_id}")
            st.info("Your order is now pending verification. We will notify you once it is approved.")
            
            # Clear the cart safely
            if "cart" in st.session_state:
                st.session_state.cart = []
                
            st.balloons()
        else:
            st.error("Please enter the UTR/Transaction ID from your payment app.")
