from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import streamlit as st
import json
import os
import datetime
import random
from b2b_pricing import calculate_bulk_discount

def load_orders():
    if os.path.exists(str(BASE_DIR / "orders.json")):
        with open(str(BASE_DIR / "orders.json"), "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(str(BASE_DIR / "orders.json"), "w") as f:
        json.dump(orders, f, indent=2)

def render_checkout():
    st.markdown("## 💳 Checkout & Payment")
    st.caption("Complete your order via UPI. Parcel charges are calculated from Thanjavur.")

    if "cart" not in st.session_state or not st.session_state.cart:
        st.info("🛒 Your cart is empty. Go to 'Place Order' to add items first.")
        return

    # Calculate totals
    total_amount = sum(item["price"] * item["qty"] for item in st.session_state.cart)
    
    # Mock Delivery Logic (Thanjavur to Chennai)
    destination = st.text_input("Delivery Destination (City/Town)", value="Chennai")
    if "chennai" in destination.lower():
        delivery_charge = 150.00  # Base rate to Chennai
    else:
        delivery_charge = 80.00   # Local Tamil Nadu rate

    # Apply B2B Discount
    disc_pct, disc_msg = calculate_bulk_discount(total_amount)
    discount_amount = total_amount * (disc_pct / 100)
    discounted_subtotal = total_amount - discount_amount
    
    grand_total = discounted_subtotal + delivery_charge

    st.markdown("### 🧾 Order Summary")
    for item in st.session_state.cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['price'] * item['qty']:.2f}")
    
    st.write(f"**Subtotal:** ₹{total_amount:.2f}")
    if disc_pct > 0:
        st.success(f"🎉 **{disc_msg}** (-₹{discount_amount:.2f})")
    st.write(f"**Delivery Charge ({destination}):** ₹{delivery_charge:.2f}")
    st.markdown(f"### 💰 Grand Total: ₹{grand_total:.2f}")

    st.markdown("---")
    st.markdown("### 📱 Pay via UPI")
    st.info("Scan the QR code or click 'Simulate Payment' to complete.")
    
    # Mock UPI UI
    st.text_input("UPI ID", value="meena@upi", disabled=True)
    
    if st.button("✅ Simulate Successful Payment", type="primary", use_container_width=True):
        # Create the order
        new_order = {
            "order_id": f"ORD-{random.randint(10000, 99999)}",
            "date": str(datetime.datetime.now()),
            "retailer_id": st.session_state.get("retailer_id", "Unknown"),
            "items": st.session_state.cart,
            "delivery_charge": delivery_charge,
            "total": grand_total,
            "status": "Paid",
            "destination": destination
        }
        
        orders = load_orders()
        orders.append(new_order)
        save_orders(orders)
        
        # Clear cart
        st.session_state.cart = []
        
        st.success(f"🎉 Payment Successful! Order {new_order['order_id']} has been recorded.")
        st.balloons()
        st.info("📦 The warehouse has been notified. Packaging will start shortly.")
        
        # Auto-redirect to tracking after 2 seconds
        import time
        time.sleep(2)
        st.session_state.page = "track_orders"
        st.rerun()

def render_track_orders():
    st.markdown("## 🚚 Track Orders")
    st.caption("Live status updates for your shipments.")

    orders = load_orders()
    if not orders:
        st.info("No orders found yet.")
        return

    for order in reversed(orders):
        if order.get("retailer_id") == st.session_state.get("retailer_id", "Unknown"):
            with st.expander(f"Order {order['order_id']} - {order['date'][:10]} (₹{order['total']})"):
                st.write(f"**Destination:** {order['destination']}")
                st.write(f"**Status:** {order['status']}")
                
                # Show progress bar
                if order['status'] == "Paid":
                    st.progress(25, text="💳 Payment Received")
                    st.info("⏳ Awaiting warehouse packaging.")
                elif order['status'] == "Processing":
                    st.progress(60, text="📦 Packaging & Checking")
                    st.info("🏃‍♂️ Workers are counting and packing your items.")
                elif order['status'] == "Shipped":
                    st.progress(100, text="🚚 Dispatched")
                    st.success("Your order has left the Thanjavur facility.")
