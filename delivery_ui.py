"""
delivery_ui.py — Streamlit UI for delivery tracking.
Two views: owner (full control) and retailer (visible only after approval).
"""
import streamlit as st
from datetime import datetime
import delivery_tracker as dt


# ═══════════════════════════════════════════════════════════
# PROGRESS BAR (shared)
# ═══════════════════════════════════════════════════════════
def _render_progress(order):
    steps = dt.get_delivery_progress(order)
    html = '<div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0;gap:4px;">'
    for i, s in enumerate(steps):
        color = "#00d47a" if s["done"] else "#4a5568"
        bg = "rgba(0,212,122,0.15)" if s["done"] else "rgba(74,85,104,0.15)"
        html += f'''
        <div style="flex:1;text-align:center;">
            <div style="background:{bg};border:2px solid {color};border-radius:50%;
                        width:44px;height:44px;margin:0 auto;
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.2rem;">{s["icon"]}</div>
            <div style="font-size:0.7rem;color:{color};margin-top:4px;
                        font-weight:600;">{s["status"]}</div>
            <div style="font-size:0.6rem;color:#8892b0;">{s["timestamp"]}</div>
        </div>'''
        if i < len(steps) - 1:
            html += f'<div style="flex:0.3;height:2px;background:{color};margin-top:-25px;"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# OWNER VIEW — Full control
# ═══════════════════════════════════════════════════════════
def render_owner_delivery(order, retailer, save_orders, all_orders):
    """
    Owner sees delivery estimate + all controls.
    Call from Approvals tab for each order.
    """
    est = dt.estimate_delivery(retailer, order)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(0,212,255,0.10),rgba(123,97,255,0.10));
                border-left:4px solid #00d4ff;border-radius:10px;
                padding:12px 16px;margin:10px 0;">
        <div style="font-size:0.7rem;color:#8892b0;letter-spacing:1.5px;">🚚 DELIVERY ESTIMATE</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:8px;">
            <div>
                <div style="font-size:0.65rem;color:#8892b0;">DESTINATION</div>
                <div style="color:#00d4ff;font-weight:700;">{est['destination_city']}</div>
            </div>
            <div>
                <div style="font-size:0.65rem;color:#8892b0;">DISTANCE</div>
                <div style="color:#e8eaf6;font-weight:700;">{est['distance_km_road']} km</div>
            </div>
            <div>
                <div style="font-size:0.65rem;color:#8892b0;">CONFIDENCE</div>
                <div style="color:#00d47a;font-weight:700;">{est['confidence_label']}</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px;">
            <div>
                <div style="font-size:0.65rem;color:#8892b0;">DISPATCH</div>
                <div style="color:#ffb547;font-weight:700;">{est['estimated_dispatch']}</div>
            </div>
            <div>
                <div style="font-size:0.65rem;color:#8892b0;">EST. ARRIVAL</div>
                <div style="color:#00d47a;font-weight:700;">{est['estimated_arrival_full']}</div>
            </div>
        </div>
        <div style="font-size:0.65rem;color:#8892b0;margin-top:8px;">
            Season: {est['climate_season']} · Climate delay ×{est['climate_delay_multiplier']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Progress bar if already started ───
    if order.get("delivery_timeline"):
        st.markdown("**Delivery Progress:**")
        _render_progress(order)

    # ─── Status update buttons ───
    st.markdown("**Update Status:**")
    _cols = st.columns(4)
    _statuses = [("Packed", "📦 Packed"),
                 ("Dispatched", "🚚 Dispatched"),
                 ("Out for Delivery", "🛵 Out for Delivery"),
                 ("Delivered", "🎉 Delivered")]
    for _col, (_status, _label) in zip(_cols, _statuses):
        with _col:
            if st.button(_label, key=f"dlv_{order['order_id']}_{_status}",
                         use_container_width=True):
                dt.mark_delivery_status(order, _status)
                for _o in all_orders:
                    if _o["order_id"] == order["order_id"]:
                        _o.update(order)
                        break
                save_orders(all_orders)
                # Notify retailer on Telegram
                try:
                    import notify_pro
                    _msg = (f"📦 <b>Delivery Update — {_status}</b>\n\n"
                            f"Order: <b>{order['order_id']}</b>\n"
                            f"Status: {_status}\n"
                            f"Distance: {est['distance_km_road']} km\n"
                            f"ETA: {est['estimated_arrival_full']}")
                    notify_pro.notify_retailer(retailer, _msg)
                except Exception:
                    pass
                st.success(f"✅ Marked: {_status}")
                st.rerun()

    # (Courier/Driver inputs removed — external delivery)


# ═══════════════════════════════════════════════════════════
# RETAILER VIEW — Only after owner confirms
# ═══════════════════════════════════════════════════════════
def render_retailer_delivery(order, retailer):
    """
    Retailer sees delivery details only if approved.
    Before approval — sees a "waiting" message.
    """
    if not dt.can_retailer_see_delivery(order):
        st.markdown(f"""
        <div style="background:rgba(255,181,71,0.10);border-left:4px solid #ffb547;
                    border-radius:10px;padding:12px 16px;">
            <div style="font-size:0.9rem;color:#ffb547;font-weight:700;">
                ⏳ Awaiting Owner Approval
            </div>
            <div style="font-size:0.8rem;color:#8892b0;margin-top:4px;">
                Delivery details will appear here once owner confirms your order.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    est = dt.estimate_delivery(retailer, order)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(0,212,122,0.10),rgba(0,212,255,0.10));
                border-left:4px solid #00d47a;border-radius:10px;
                padding:14px 18px;margin:8px 0;">
        <div style="font-size:0.75rem;color:#8892b0;letter-spacing:1.5px;">🚚 YOUR DELIVERY</div>
        <div style="font-size:1.3rem;font-weight:800;color:#00d47a;margin-top:4px;">
            {est['estimated_arrival_full']}
        </div>
        <div style="font-size:0.85rem;color:#e8eaf6;margin-top:6px;">
            📍 {est['destination_city']} · {est['distance_km_road']} km from Thanjavur
        </div>
        <div style="font-size:0.75rem;color:#8892b0;margin-top:4px;">
            Dispatches: {est['estimated_dispatch']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    _render_progress(order)

    # (Courier display removed — external delivery service)


# ═══════════════════════════════════════════════════════════
# OWNER — DAILY DISPATCH SHEET
# ═══════════════════════════════════════════════════════════
def render_dispatch_sheet(orders, retailers):
    """Owner dashboard — today's dispatch list."""
    today = datetime.now().strftime("%d-%b-%Y").upper()
    today_dispatches = [
        o for o in orders
        if o.get("delivery_timeline", {}).get("Dispatched", "").startswith(today)
    ]
    if not today_dispatches:
        st.caption("No dispatches today yet.")
        return
    st.markdown(f"**📦 Today's Dispatch Sheet ({len(today_dispatches)} orders)**")
    rows = []
    for o in today_dispatches:
        r = next((x for x in retailers if x["id"] == o.get("retailer_id")), None)
        if r:
            est = dt.estimate_delivery(r, o)
            rows.append({
                "Order": o["order_id"],
                "Shop": r.get("shop", ""),
                "Phone": r.get("phone", ""),
                "Destination": est["destination_city"],
                "Distance": f"{est['distance_km_road']} km",
                "Driver": o.get("driver_name", "—"),
                "Vehicle": o.get("vehicle_no", "—"),
            })
    import pandas as pd
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
