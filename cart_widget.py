"""
cart_widget.py — Floating cart button + contents popover.
Appears on every retailer page. Shows live count + total.
Click → opens popover with full item list and actions.
"""
import streamlit as st


_CSS = """
<style>
/* ── Fixed bottom-right floating position ── */
div[data-testid="stPopover"] {
    
    bottom: 24px !important;
    right: 24px !important;
    left: auto !important;
    top: auto !important;
    z-index: 2147483640 !important;
    width: 76px !important;
    height: 76px !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Big bold circular button ── */
div[data-testid="stPopover"] > button {
    width: 76px !important;
    height: 76px !important;
    min-width: 76px !important;
    min-height: 76px !important;
    max-width: 76px !important;
    max-height: 76px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #4f46e5, #7b61ff) !important;
    color: #ffffff !important;
    border: 3px solid #ffffff !important;
    font-size: 1.4rem !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    letter-spacing: -1px !important;
    box-shadow:
        0 10px 28px rgba(79,70,229,0.7),
        0 4px 14px rgba(0,0,0,0.5) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    overflow: visible !important;
    position: relative !important;
}
div[data-testid="stPopover"] > button:hover {
    transform: scale(1.08) !important;
    box-shadow: 0 14px 36px rgba(79,70,229,0.9), 0 6px 18px rgba(0,0,0,0.6) !important;
}
div[data-testid="stPopover"] > button:active {
    transform: scale(0.96) !important;
}

/* Hide the default dropdown arrow */
div[data-testid="stPopover"] > button svg,
div[data-testid="stPopover"] > button [data-testid="stIconMaterial"] {
    display: none !important;
}

/* Empty cart — muted gray */
div[data-testid="stPopover"] > button.ma-empty {
    background: rgba(80,85,110,0.9) !important;
    box-shadow: 0 8px 22px rgba(0,0,0,0.45) !important;
}

/* Popover body */
div[data-testid="stPopoverBody"] {
    min-width: 300px !important;
    max-width: 400px !important;
    max-height: 70vh !important;
    overflow-y: auto !important;
    margin-right: 20px !important;
    margin-bottom: 12px !important;
}

/* Small screens — keep proportion */
@media (max-width: 480px) {
    div[data-testid="stPopover"],
    div[data-testid="stPopover"] > button {
        width: 68px !important;
        height: 68px !important;
        min-width: 68px !important;
        min-height: 68px !important;
    }
    div[data-testid="stPopover"] {
        bottom: 18px !important;
        right: 18px !important;
    }
    div[data-testid="stPopover"] > button {
        font-size: 1.25rem !important;
    }
}
</style>
"""


def _cart():
    return st.session_state.get("cart", []) or []


def _totals():
    items = _cart()
    qty = sum(int(i.get("qty", 1) or 1) for i in items)
    total = sum(
        float(i.get("price", 0) or 0) * int(i.get("qty", 1) or 1)
        for i in items
    )
    return len(items), qty, total


def render():
    """Render the floating circular cart button. Call once per page load."""
    st.markdown(_CSS, unsafe_allow_html=True)

    items = _cart()
    n_items, n_qty, total = _totals()

    # ── Label: just the digit when items exist, cart emoji when empty ──
    if n_qty > 0:
        label = str(n_qty)
    else:
        label = "🛒"

    with st.popover(label, use_container_width=False):
        if not items:
            st.markdown(
                "<div style='text-align:center;padding:16px;color:#8892b0;'>"
                "🛒<br><br>Your cart is empty.<br>"
                "<span style='font-size:0.8rem;'>Add items from Stock Check or Place Order.</span>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='font-size:1.05rem;font-weight:900;color:#e8eaf6;"
                f"margin-bottom:8px;'>🛒 Your Cart &nbsp;"
                f"<span style='color:#8892b0;font-size:0.8rem;font-weight:500;'>"
                f"({n_items} item{'s' if n_items>1 else ''}, {n_qty} units)</span></div>",
                unsafe_allow_html=True,
            )

            for idx, it in enumerate(items):
                name = it.get("medicine") or it.get("name") or "Item"
                qty = int(it.get("qty", 1) or 1)
                price = float(it.get("price", 0) or 0)
                line = qty * price

                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    st.markdown(
                        f"<div style='font-weight:600;color:#e8eaf6;font-size:0.9rem;'>"
                        f"{name[:38]}</div>"
                        f"<div style='font-size:0.7rem;color:#8892b0;'>"
                        f"₹{price:,.2f} × {qty}</div>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f"<div style='color:#00d4aa;font-weight:800;font-size:0.9rem;"
                        f"text-align:right;padding-top:4px;'>₹{line:,.0f}</div>",
                        unsafe_allow_html=True,
                    )
                with c3:
                    if st.button("✕", key=f"cw_rm_{idx}"):
                        st.session_state["cart"].pop(idx)
                        st.rerun()

            st.markdown("---")
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;"
                f"font-size:1.05rem;font-weight:900;color:#e8eaf6;padding:6px 0;'>"
                f"<span>Total</span>"
                f"<span style='color:#00d4aa;'>₹{total:,.2f}</span></div>",
                unsafe_allow_html=True,
            )

            st.markdown("")

            _b1, _b2 = st.columns(2)
            with _b1:
                if st.button("🗑 Clear", key="cw_clear", use_container_width=True):
                    st.session_state["cart"] = []
                    st.rerun()
            with _b2:
                if st.button("✅ Checkout", key="cw_checkout",
                             use_container_width=True, type="primary"):
                    st.session_state["retailer_page"] = "cart"
                    st.rerun()
