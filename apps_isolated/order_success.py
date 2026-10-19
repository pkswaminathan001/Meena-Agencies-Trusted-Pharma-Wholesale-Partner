import streamlit as st
from datetime import datetime, time


def show_amazon_success_page(order):
    """Amazon-style success page with two big buttons."""
    st.balloons()
    order_id = order.get("order_id", "-")
    total = order.get("total", 0)
    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:5rem;line-height:1;">✅</div>
            <h1 style="color:#10b981;margin:1rem 0 .5rem;">Order Placed Successfully!</h1>
            <p style="color:#8892b0;font-size:1.1rem;">Thank you for your order from Meena Agencies.</p>
            <div style="background:#1a1f2e;border:1px solid #2a3142;border-radius:14px;
                        padding:1.5rem;max-width:400px;margin:2rem auto;text-align:left;">
                <div style="display:flex;justify-content:space-between;padding:.5rem 0;
                            border-bottom:1px solid #2a3142;">
                    <span style="color:#8892b0;">Order ID</span>
                    <span style="color:#00d4ff;font-weight:700;">{order_id}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:.5rem 0;">
                    <span style="color:#8892b0;">Total</span>
                    <span style="color:#10b981;font-weight:700;">₹{total:,.2f}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Continue Shopping", use_container_width=True, type="primary"):
            st.session_state.pop("success_order", None)
            st.session_state.page = "home"
            st.rerun()
    with c2:
        if st.button("📦 View My Orders", use_container_width=True):
            st.session_state.pop("success_order", None)
            st.session_state.page = "my_orders"
            st.rerun()


def show_shop_hours_banner():
    """Show a red banner if the shop is currently closed (after 21:00)."""
    now = datetime.now().time()
    if now >= time(21, 0) or now < time(8, 0):
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#7f1d1d,#991b1b);
                        border:1px solid #ef4444;border-radius:12px;
                        padding:1rem 1.5rem;margin-bottom:1rem;color:#fff;
                        font-size:.95rem;line-height:1.4;">
                🌙 <b>Shop is currently closed.</b> Orders placed now will be
                processed the next working morning.
            </div>
            """,
            unsafe_allow_html=True,
        )
