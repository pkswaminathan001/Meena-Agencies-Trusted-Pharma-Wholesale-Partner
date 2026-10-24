import streamlit as st
import urllib.parse

def render_upi_payment(order, retailer, record_payment=None, notify_pro=None, load_owner=None):
    UPI_ID = "meenaagencies@upi"  # ⚠️ CHANGE THIS TO YOUR DAD'S ACTUAL UPI ID
    PAYEE_NAME = "Meena Agencies"

    order_id = order.get('order_id', 'NEW')
    total = order.get('total', 0)

    upi_params = {
        "pa": UPI_ID, "pn": PAYEE_NAME, "am": str(total),
        "cu": "INR", "tn": f"Order {order_id}"
    }
    upi_url = f"upi://pay?{urllib.parse.urlencode(upi_params)}"
    encoded = urllib.parse.quote(upi_url, safe='')
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={encoded}"

    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.08);border:2px solid #00d4ff;
                border-radius:16px;padding:1.5rem;text-align:center;margin:1rem 0;">
        <h3 style="color:#00d4ff;margin:0 0 0.5rem 0;">💳 UPI Payment</h3>
        <p style="color:#a8b2d1;">Order: <b>{order_id}</b></p>
        <p style="color:#00d4ff;font-size:1.6rem;font-weight:800;margin:0.2rem 0;">
            ₹{total:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(qr_url, width=220)

    st.markdown(
        f'<a href="{upi_url}" style="display:block;text-align:center;'
        f'padding:16px 20px;margin:1rem 0;background:linear-gradient(135deg,#00d4ff,#7b61ff);'
        f'color:#fff;font-weight:700;border-radius:12px;text-decoration:none;">'
        f'📱 Pay ₹{total:,.2f} via UPI App</a>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    txn_id = st.text_input("Enter UPI Transaction ID (12-digit) after paying", key="upi_txn")
    if st.button("✅ I've Paid — Confirm Payment", key="upi_confirm"):
        if txn_id.strip():
            if record_payment:
                res = record_payment(retailer.get("id"), total, f"UPI: {txn_id}", mode="upi", reference=txn_id, bank="")
                if res and res.get("ok"):
                    st.success("✅ Payment recorded! Packaging will start now.")
                else:
                    st.error(res.get("msg", "Error recording payment."))
            else:
                st.success(f"✅ Payment of ₹{total:,.2f} recorded successfully! (Demo Mode)")
            st.balloons()
        else:
            st.error("Please enter the UPI Transaction ID")
