import streamlit as st
import urllib.parse

def render_upi_payment(order, retailer, record_payment, on_success=None):
    UPI_ID = "meenaagencies@upi"  # Change this to Dad's UPI
    PAYEE_NAME = "Meena Agencies"
    total = float(order.get("total", 0))
    items = order.get("items", [])
    
    # Amazon-style calculations
    item_total = sum(i.get("qty", 1) * i.get("price", 0) for i in items)
    delivery_fee = 0.0 if item_total > 500 else 40.0
    marketplace_fee = 5.0
    savings = item_total * 0.05  # 5% coupon savings
    order_total = item_total + delivery_fee + marketplace_fee - savings
    
    params = {"pa": UPI_ID, "pn": PAYEE_NAME, "am": f"{order_total:.2f}", "cu": "INR", "tn": f"Order {order.get('order_id','')}"}
    upi_url = f"upi://pay?{urllib.parse.urlencode(params)}"
    encoded = urllib.parse.quote(upi_url, safe='')
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={encoded}"

    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.08);border:2px solid #00d4ff;border-radius:16px;padding:1.5rem;margin:1rem 0;">
        <h3 style="color:#00d4ff;margin:0 0 1rem 0; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.5rem;">Secure Checkout</h3>
        
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
            <span style="color:#a8b2d1;">Items ({len(items)}):</span>
            <span style="color:#e8eaf6; font-weight:600;">₹{item_total:,.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
            <span style="color:#a8b2d1;">Delivery:</span>
            <span style="color:#e8eaf6; font-weight:600;">₹{delivery_fee:,.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
            <span style="color:#a8b2d1;">Marketplace Fee:</span>
            <span style="color:#e8eaf6; font-weight:600;">₹{marketplace_fee:,.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; border-bottom:1px dashed rgba(255,255,255,0.1); padding-bottom:0.5rem;">
            <span style="color:#00d47a;">Savings (5% Coupon):</span>
            <span style="color:#00d47a; font-weight:600;">- ₹{savings:,.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:0.5rem; font-size:1.2rem;">
            <span style="color:#ffffff; font-weight:700;">Order Total:</span>
            <span style="color:#00d4ff; font-weight:800;">₹{order_total:,.2f}</span>
        </div>
    </div>
    
    <div style="background:rgba(26,31,58,0.7); border:1px solid rgba(123,97,255,0.3); border-radius:12px; padding:1rem; margin:1rem 0;">
        <div style="color:#8892b0; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem;">Delivering to:</div>
        <div style="color:#e8eaf6; font-weight:600;">{retailer.get('owner', '')}</div>
        <div style="color:#a8b2d1; font-size:0.9rem;">{retailer.get('shop', '')}, {order.get('location', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 💳 Payment Method")
    pay_method = st.radio("Choose a payment method", ["📱 UPI / QR Code", "💵 Cash on Delivery"], horizontal=True)
    
    if pay_method == "📱 UPI / QR Code":
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2: st.image(qr_url, width=220)
        st.markdown(f'<a href="{upi_url}" style="display:block;text-align:center;padding:16px;margin:1rem 0;background:linear-gradient(135deg,#00d4ff,#7b61ff);color:#fff;font-weight:700;border-radius:12px;text-decoration:none;">📱 Pay ₹{order_total:,.2f} via UPI App</a>', unsafe_allow_html=True)
        st.markdown("---")
        txn = st.text_input("Enter UPI Transaction ID (after paying)", key="upi_txn")
        if st.button("✅ I've Paid — Confirm", key="upi_confirm"):
            if txn.strip():
                res = record_payment(retailer["id"], order_total, f"UPI: {txn}", mode="upi", reference=txn.strip(), bank="")
                if res.get("ok"):
                    if on_success: on_success()
                else: st.error(res.get("msg", "Failed"))
            else: st.error("Enter the transaction ID first")
    else:
        st.info("Cash on Delivery selected. Please keep exact change ready.")
        if st.button("✅ Place Order (COD)", key="cod_confirm"):
            res = record_payment(retailer["id"], 0.0, "COD", mode="cod", reference="", bank="")
            if res.get("ok"):
                if on_success: on_success()
            else: st.error(res.get("msg", "Failed"))
