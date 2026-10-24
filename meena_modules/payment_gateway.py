import streamlit as st
import urllib.parse

def render_upi_payment(order, retailer, record_payment, on_success=None):
    UPI_ID = "meenaagencies@upi"  # Change this to Dad's UPI
    PAYEE_NAME = "Meena Agencies"
    total = float(order.get("total", 0))
    params = {"pa": UPI_ID, "pn": PAYEE_NAME, "am": f"{total:.2f}", "cu": "INR", "tn": f"Order {order.get('order_id','')}"}
    upi_url = f"upi://pay?{urllib.parse.urlencode(params)}"
    encoded = urllib.parse.quote(upi_url, safe='')
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={encoded}"

    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.08);border:2px solid #00d4ff;border-radius:16px;padding:1.5rem;text-align:center;margin:1rem 0;">
        <h3 style="color:#00d4ff;margin:0 0 0.5rem 0;">💳 UPI Payment</h3>
        <p style="color:#a8b2d1;">Order <b>{order.get('order_id','')}</b></p>
        <p style="color:#00d4ff;font-size:1.6rem;font-weight:800;margin:0.2rem 0;">₹{total:,.2f}</p>
        <p style="color:#8892b0;font-size:0.85rem;">Scan with GPay / PhonePe / Paytm</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c2: st.image(qr_url, width=220)

    st.markdown(f'<a href="{upi_url}" style="display:block;text-align:center;padding:16px;margin:1rem 0;background:linear-gradient(135deg,#00d4ff,#7b61ff);color:#fff;font-weight:700;border-radius:12px;text-decoration:none;">📱 Pay ₹{total:,.2f} via UPI App</a>', unsafe_allow_html=True)

    st.markdown("---")
    txn = st.text_input("Enter UPI Transaction ID (after paying)", key="upi_txn")
    if st.button("✅ I've Paid — Confirm", key="upi_confirm"):
        if txn.strip():
            res = record_payment(retailer["id"], total, f"UPI: {txn}", mode="upi", reference=txn.strip(), bank="")
            if res.get("ok"):
                if on_success: on_success()
            else: st.error(res.get("msg", "Failed"))
        else: st.error("Enter the transaction ID first")
