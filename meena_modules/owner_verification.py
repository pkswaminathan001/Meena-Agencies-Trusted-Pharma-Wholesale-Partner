import streamlit as st
import json
import os
from pathlib import Path
import datetime
from meena_modules.invoice_generator import generate_invoice_pdf, send_invoice_to_telegram

def render_owner_verification():
    st.markdown("## 💳 Payment Verification Center")
    st.caption("Verify UTR numbers against your bank statement before approving orders.")
    
    orders_file = Path("orders.json")
    if not orders_file.exists():
        st.info("No orders found.")
        return
        
    try:
        with open(orders_file, "r") as f:
            orders = json.load(f)
    except:
        st.error("Could not read orders file.")
        return
        
    pending_orders = [o for o in orders if o.get("status") == "Pending Verification"]
    
    if not pending_orders:
        st.success("✅ All orders are verified! No pending payments.")
        return
        
    st.warning(f"⚠️ You have **{len(pending_orders)}** orders waiting for payment verification.")
    
    for idx, order in enumerate(pending_orders):
        is_test = "TEST" in str(order.get("utr", ""))
        tag = "🧪 [TEST ORDER] " if is_test else ""
        with st.expander(f"{tag}Order {order.get('order_id')} - ₹{order.get('total'):,.2f} - {order.get('shop')}"):
            st.write(f"**Retailer:** {order.get('shop')} ({order.get('retailer_id')})")
            st.write(f"**Date:** {order.get('timestamp')}")
            st.write(f"**UTR / Transaction ID:** `{order.get('utr')}`")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Approve (Money Received)", key=f"app_{idx}", type="primary"):
                    # Update status
                    for o in orders:
                        if o.get("order_id") == order.get("order_id"):
                            o["status"] = "Approved"
                    with open(orders_file, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.success("Order Approved & Invoice Sent!")
                    st.rerun()
            with c2:
                if st.button("❌ Reject (Invalid UTR)", key=f"rej_{idx}"):
                    for o in orders:
                        if o.get("order_id") == order.get("order_id"):
                            o["status"] = "Rejected"
                    with open(orders_file, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.error("Order Rejected!")
                    st.rerun()
