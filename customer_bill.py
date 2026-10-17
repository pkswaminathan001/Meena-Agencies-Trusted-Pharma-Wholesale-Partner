"""
customer_bill.py — Colourful, brand-aligned popup bills.
Deep blue primary, warm orange accent, clean white cards.
"""
import streamlit as st


# ─── Safe color helper (prevents "color: 0 / #function()" console errors) ───
def _safe_color(v, fallback="#00d4ff"):
    """Return a valid CSS color string. Never returns 0/None/function."""
    if v is None:
        return fallback
    if callable(v):
        try:
            v = v()
        except Exception:
            return fallback
    s = str(v).strip()
    if not s or s.lower() in ("none", "null", "undefined", "0", "#0"):
        return fallback
    # Valid: #hex, rgb(), rgba(), hsl(), hsla(), or named color
    if re.match(r'^#([0-9a-fA-F]{3,8})$', s):
        return s
    if re.match(r'^(rgb|rgba|hsl|hsla)\(', s):
        return s
    # Single word named colors (red, blue, etc.)
    if re.match(r'^[a-zA-Z]+$', s):
        return s
    return fallback

import re
import html as _html


_ANIM_CSS = """
<style>
@keyframes billPopIn {
    0%   { opacity: 0; transform: translateY(24px) scale(.96); }
    60%  { opacity: 1; transform: translateY(-4px) scale(1.01); }
    100% { opacity: 1; transform: translateY(0)    scale(1); }
}
@keyframes billFadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes rowPopIn {
    0%   { opacity: 0; transform: translateY(10px) scale(.99); }
    100% { opacity: 1; transform: translateY(0)    scale(1); }
}

/* ── Compact bill row ── */
.bill-row-card {
    animation: rowPopIn .45s cubic-bezier(.2,.9,.3,1.2) both;
    background: #ffffff !important;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 8px 0 12px 0;
    box-shadow: 0 4px 14px rgba(11,59,140,.08);
    color: #1A1A2E !important;
    font-family: system-ui, -apple-system, sans-serif;
    position: relative;
    overflow: hidden;
}
.bill-row-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 5px;
    background: #0B3B8C;
}
.bill-row-card.status-approved::before   { background: linear-gradient(180deg,#10B981,#0E9F6E); }
.bill-row-card.status-delivered::before  { background: linear-gradient(180deg,#1560BD,#0B3B8C); }
.bill-row-card.status-pending::before    { background: linear-gradient(180deg,#FDB913,#F58220); }
.bill-row-card.status-cancelled::before  { background: linear-gradient(180deg,#F87171,#C81E1E); }

.bill-row-card .head {
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom: 8px;
}
.bill-row-card .oid {
    font-weight: 800; font-size: 15px; color:#1A1A2E !important;
}
.bill-row-card .badge {
    font-size: 12px; font-weight: 800;
    padding: 4px 12px; border-radius: 999px;
    letter-spacing: .3px;
    text-transform: uppercase;
}
.bill-row-card .meta {
    display:flex; justify-content:space-between;
    font-size: 13px; color:#64748B !important;
    margin-bottom: 10px;
}
.bill-row-card .total {
    display:flex; justify-content:space-between;
    align-items: baseline;
    font-size: 20px; font-weight: 800;
    color:#1A1A2E !important;
    padding-top: 10px;
    border-top: 1px dashed #CBD5E1;
}
.bill-row-card .total .lbl {
    font-size: 12px; font-weight: 700;
    color:#64748B !important;
    text-transform: uppercase; letter-spacing: .8px;
}
.bill-row-card .total .amt {
    background: linear-gradient(135deg,#0B3B8C,#1560BD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 22px;
    font-weight: 900;
}

/* ── Popup body ── */
.bill-popup-body {
    animation: billPopIn .5s cubic-bezier(.2,.9,.3,1.2) both;
    background: #ffffff !important;
    border-radius: 14px;
    padding: 8px 4px;
    color: #1A1A2E !important;
    font-family: system-ui, -apple-system, sans-serif;
}
.bill-popup-body .row { animation: billFadeUp .4s ease both; }
.bill-popup-body .row:nth-child(2) { animation-delay: .08s; }
.bill-popup-body .row:nth-child(3) { animation-delay: .16s; }
.bill-popup-body .row:nth-child(4) { animation-delay: .24s; }
.bill-popup-body .row:nth-child(5) { animation-delay: .32s; }

.bill-popup-body .head {
    display:flex; justify-content:space-between; align-items:center;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 14px; margin-bottom: 16px;
}
.bill-popup-body .title {
    font-size: 22px; font-weight: 900;
    background: linear-gradient(135deg,#0B3B8C,#1560BD 60%,#F58220);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -.4px;
}
.bill-popup-body .badge {
    font-size: 13px; font-weight: 800;
    padding: 5px 14px; border-radius: 999px;
    letter-spacing: .3px;
    text-transform: uppercase;
}
.bill-popup-body .meta {
    display:flex; justify-content:space-between;
    font-size: 14px; color: #475569 !important;
    margin-bottom: 16px;
    padding: 12px 14px;
    background: linear-gradient(135deg,#F8FAFC,#E8EFFB);
    border-radius: 10px;
    border-left: 4px solid #0B3B8C;
}
.bill-popup-body .meta b { color: #1A1A2E !important; }
.bill-popup-body .line {
    display:flex; justify-content:space-between;
    font-size: 15px; color: #1E293B !important;
    padding: 11px 6px;
    border-bottom: 1px solid #EEF2F7;
}
.bill-popup-body .line span:last-child {
    font-variant-numeric: tabular-nums;
    font-weight: 700;
    color: #1A1A2E !important;
}
.bill-popup-body .line:last-of-type { border-bottom: none; }
.bill-popup-body .total {
    display:flex; justify-content:space-between;
    align-items: baseline;
    font-size: 22px; font-weight: 900;
    border-top: 3px solid transparent;
    border-image: linear-gradient(90deg,#0B3B8C,#1560BD,#F58220) 1;
    margin-top: 14px; padding-top: 16px;
}
.bill-popup-body .total span:first-child {
    color: #64748B !important;
    font-size: 14px; text-transform: uppercase; letter-spacing: 1px;
}
.bill-popup-body .total span:last-child {
    background: linear-gradient(135deg,#0B3B8C,#1560BD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 26px;
    font-weight: 900;
    font-variant-numeric: tabular-nums;
}

div[data-testid="stDialog"] > div {
    background: #ffffff !important;
    color: #1A1A2E !important;
}
</style>
"""


def _money(v):
    try:
        return f"₹{float(v):,.2f}"
    except Exception:
        return "₹0.00"


def _badge_colors(status):
    s = str(status).lower()
    if s == "approved":  return "#E6F7F1", "#0E9F6E"
    if s == "delivered": return "#E8EFFB", "#0B3B8C"
    if s in ("pending", "awaiting otp"): return "#FFF1E0", "#F58220"
    if s == "cancelled": return "#FDE8E8", "#C81E1E"
    return "#E8EFFB", "#1560BD"


def _status_class(status):
    s = str(status).lower()
    if s == "approved":  return "status-approved"
    if s == "delivered": return "status-delivered"
    if s in ("pending", "awaiting otp"): return "status-pending"
    if s == "cancelled": return "status-cancelled"
    return ""


def _esc(v):
    return _html.escape(str(v if v is not None else "—"))


@st.dialog("Bill", width="large")
def _show_bill_dialog(order, company=None):
    st.markdown(_ANIM_CSS, unsafe_allow_html=True)

    oid    = _esc(order.get("order_id", "—"))
    status = _esc(order.get("status", "—"))
    placed = _esc(order.get("placed_at", "—"))
    shop   = _esc(order.get("shop", ""))
    items  = order.get("items", []) or []
    total  = order.get("total", 0)

    badge_bg, badge_fg = _badge_colors(order.get("status", ""))

    rows = ""
    for it in items:
        name  = _esc(it.get("medicine") or it.get("name") or "Item")
        qty   = it.get("qty", it.get("quantity", 1))
        price = it.get("price", 0)
        try:
            line = float(price) * float(qty)
        except Exception:
            line = 0.0
        rows += (
            f'<div class="line row">'
            f'<span>{name} <span style="color:#94A3B8;">× {qty}</span></span>'
            f'<span>{_money(line)}</span>'
            f'</div>'
        )
    if not rows:
        rows = '<div class="line row"><span>No items</span><span>—</span></div>'

    html = f"""
    <div class="bill-popup-body">
      <div class="head row">
        <div class="title">Invoice · {oid}</div>
        <div class="badge" style="background:{_safe_color(badge_bg, '#8892b0')};color:{_safe_color(badge_fg, '#e8eaf6')};">{status}</div>
      </div>
      <div class="meta row">
        <span>📅 <b>{placed}</b></span>
        <span>🏪 <b>{shop}</b></span>
      </div>
      {rows}
      <div class="total row">
        <span>Total</span>
        <span>{_money(total)}</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("")
    st.download_button(
        "⬇️  Download bill",
        data=_build_txt(order, company),
        file_name=f"{order.get('order_id','bill')}.txt",
        mime="text/plain",
        use_container_width=True,
        key=f"dl_modal_{order.get('order_id','x')}",
    )


def _reorder_into_cart(order):
    """Load order items into the cart and switch to Cart page."""
    items = order.get("items") or []
    if not items:
        st.warning("This order has no items to reorder.")
        return
    cart = []
    for it in items:
        cart.append({
            "medicine": it.get("medicine") or it.get("name") or "",
            "batch":    it.get("batch") or "",
            "qty":      int(it.get("qty") or it.get("quantity") or 1),
            "price":    float(it.get("price") or it.get("unit_price") or it.get("rate") or it.get("selling_price") or 0),
        })
    st.session_state["cart"] = cart
    st.session_state["retailer_page"] = "cart"
    st.success(f"✅ {len(cart)} item(s) loaded into cart")
    st.rerun()


def render_bill_card(order, company=None, allow_download=True, key=None):
    st.markdown(_ANIM_CSS, unsafe_allow_html=True)

    oid    = _esc(order.get("order_id", "—"))
    status = _esc(order.get("status", "—"))
    placed = _esc(order.get("placed_at", "—"))
    shop   = _esc(order.get("shop", ""))
    total  = order.get("total", 0)

    badge_bg, badge_fg = _badge_colors(order.get("status", ""))
    status_class = _status_class(order.get("status", ""))

    st.markdown(
        f"""
        <div class="bill-row-card {status_class}">
          <div class="head">
            <div class="oid">🧾 {oid}</div>
            <div class="badge" style="background:{_safe_color(badge_bg, '#8892b0')};color:{_safe_color(badge_fg, '#e8eaf6')};">{status}</div>
          </div>
          <div class="meta">
            <span>📅 {placed}</span>
            <span>🏪 {shop}</span>
          </div>
          <div class="total">
            <span class="lbl">Total</span>
            <span class="amt">{_money(total)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _bc1, _bc2 = st.columns(2)
    with _bc1:
        if st.button(
            "👁  View bill",
            key=key or f"view_{order.get('order_id','x')}",
            use_container_width=True,
        ):
            _show_bill_dialog(order, company=company)
    with _bc2:
        if st.button(
            "🔁  Reorder",
            key=f"reorder_{order.get('order_id','x')}_{key or 'x'}",
            use_container_width=True,
        ):
            _reorder_into_cart(order)


def render_order_list(orders, company=None, limit=None):
    if not orders:
        st.info("No bills to show yet.")
        return
    shown = orders[-limit:] if limit else orders
    for i, o in enumerate(shown):
        render_bill_card(o, company=company, key=f"view_{i}_{o.get('order_id','x')}")


def _build_txt(order, company=None):
    lines = [
        f"INVOICE {order.get('order_id','—')}",
        f"Status : {order.get('status','—')}",
        f"Date   : {order.get('placed_at','—')}",
    ]
    if company:
        lines.append(f"From   : {company.get('name','')}")
    lines.append("-" * 40)
    for it in (order.get("items") or []):
        name = it.get("medicine") or it.get("name") or "Item"
        qty  = it.get("qty", it.get("quantity", 1))
        price = it.get("price", 0)
        try:
            line = float(price) * float(qty)
        except Exception:
            line = 0.0
        lines.append(f"{name}  x{qty}  ₹{line:,.2f}")
    lines.append("-" * 40)
    lines.append(f"TOTAL  ₹{float(order.get('total',0)):,.2f}")
    return "\n".join(lines)
