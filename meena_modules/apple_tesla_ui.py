import streamlit as st

def render_apple_tesla_view(r, _my_orders, inr):
    st.markdown("""
    <style>
    .ring-container { display: flex; justify-content: center; gap: 2rem; margin: 2rem 0; }
    .ring-item { text-align: center; }
    .ring-svg { transform: rotate(-90deg); }
    .ring-bg { stroke: rgba(255,255,255,0.1); }
    .ring-fg { stroke-linecap: round; transition: stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1); }
    .ring-label { color: #8892b0; font-size: 0.8rem; margin-top: 0.5rem; }
    .ring-value { color: #ffffff; font-size: 1.2rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

    used_pct = (r.get("outstanding", 0) / r.get("credit_limit", 1)) * 100 if r.get("credit_limit", 0) > 0 else 100
    health_pct = 100 - used_pct

    def render_ring(stroke_dashoffset, color, label, value):
        return f"""
        <div class="ring-item">
            <svg class="ring-svg" width="100" height="100" viewBox="0 0 100 100">
                <circle class="ring-bg" cx="50" cy="50" r="45" fill="none" stroke-width="8"/>
                <circle class="ring-fg" cx="50" cy="50" r="45" fill="none" stroke="{color}" stroke-width="8"
                        stroke-dasharray="282.6" stroke-dashoffset="{stroke_dashoffset}"/>
            </svg>
            <div class="ring-value">{value}</div>
            <div class="ring-label">{label}</div>
        </div>"""

    credit_offset = 282.6 * (1 - used_pct/100)
    health_offset = 282.6 * (1 - health_pct/100)

    st.markdown(f"""
    <div class="ring-container">
        {render_ring(credit_offset, "#ff4d6d", "Credit Used", f"{used_pct:.0f}%")}
        {render_ring(health_offset, "#00d47a", "Account Health", f"{health_pct:.0f}%")}
    </div>
    """, unsafe_allow_html=True)

    _my_last_order = _my_orders[-1] if _my_orders else None
    st.markdown("### ⚡ Tesla Autopilot Ordering")
    
    if _my_last_order and _my_last_order.get("items"):
        est_total = sum(i.get("qty", 1) * i.get("price", 0) for i in _my_last_order["items"])
        st.info(f"🤖 AI suggests reordering **{len(_my_last_order['items'])} items**. Estimated total: **{inr(est_total, 2)}**")
        if st.button("🚀 1-TAP APPROVE SMART CART", key="tesla_1tap"):
            st.session_state.cart = []
            for _it in _my_last_order["items"]:
                st.session_state.cart.append({
                    "item_id": _it.get("item_id", ""), "medicine": _it.get("medicine", ""),
                    "batch": _it.get("batch", ""), "qty": _it.get("qty", 1), "price": _it.get("price", 0),
                })
            st.success("✅ Smart Cart loaded!")
            st.rerun()
    else:
        st.info("Place your first order to unlock AI Autopilot.")
