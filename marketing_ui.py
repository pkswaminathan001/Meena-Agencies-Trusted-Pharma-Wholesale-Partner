"""marketing_ui.py — Marketing dashboard with 3D animations."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import marketing as mk


# ═══════════════════════════════════════════════════════════
# 3D PROMOTION UNIVERSE
# ═══════════════════════════════════════════════════════════
def render_3d_promo_universe(promos):
    if not promos:
        st.caption("No promotions yet — create one below.")
        return

    x, y, z, labels, colors, sizes = [], [], [], [], [], []
    type_colors = {
        "seasonal": "#00d4ff", "festival": "#ffb547",
        "clearance": "#ff4d6d", "new_stock": "#00d47a",
        "loyalty": "#7b61ff", "bulk": "#ff8c42", "custom": "#8892b0",
    }

    for i, p in enumerate(promos):
        # X: extra discount %, Y: days remaining, Z: sent count
        try:
            days_left = (datetime.strptime(p["valid_until"], "%Y-%m-%d") - datetime.now()).days
        except Exception:
            days_left = 0
        x.append(float(p.get("extra_discount_pct", 0)))
        y.append(max(0, days_left))
        z.append(len(p.get("sent_to", [])))
        labels.append(p["title"][:18])
        colors.append(type_colors.get(p["type"], "#8892b0"))
        sizes.append(max(10, len(p.get("sent_to", [])) * 4 + 12))

    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers+text",
        marker=dict(
            size=sizes, color=colors, opacity=0.85,
            line=dict(color="#ffffff", width=1),
        ),
        text=labels,
        textposition="top center",
        textfont=dict(color="#e8eaf6", size=10),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Discount: %{x}%<br>"
            "Days left: %{y}<br>"
            "Sent: %{z}<extra></extra>"
        ),
    )])

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Discount %", showbackground=False,
                       color="#8892b0", gridcolor="rgba(0,212,255,0.15)"),
            yaxis=dict(title="Days Left", showbackground=False,
                       color="#8892b0", gridcolor="rgba(0,212,255,0.15)"),
            zaxis=dict(title="Sent", showbackground=False,
                       color="#8892b0", gridcolor="rgba(0,212,255,0.15)"),
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf6"),
        height=460,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig, use_container_width=True, key="promo_universe_3d")


# ═══════════════════════════════════════════════════════════
# 3D CUSTOMER CLUSTERS
# ═══════════════════════════════════════════════════════════
def render_3d_customer_clusters(retailers, orders):
    if not retailers:
        return
    x, y, z, labels, colors, sizes = [], [], [], [], [], []
    for r in retailers:
        my_orders = [o for o in orders
                     if o.get("retailer_id") == r["id"] and o.get("status") == "Approved"]
        total_spent = sum(o.get("total", 0) for o in my_orders)
        outstanding = float(r.get("outstanding", 0))
        # X: orders count, Y: total spent (scaled), Z: outstanding
        x.append(len(my_orders))
        y.append(total_spent / 1000)
        z.append(outstanding / 1000)
        labels.append(r["shop"][:14])
        # Color by status
        colors.append("#00d47a" if r.get("status") == "Active" else "#ff4d6d")
        # Size by order count
        sizes.append(max(10, len(my_orders) * 3 + 12))

    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers+text",
        marker=dict(size=sizes, color=colors, opacity=0.85,
                    line=dict(color="#ffffff", width=1)),
        text=labels,
        textposition="top center",
        textfont=dict(color="#e8eaf6", size=10),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Orders: %{x}<br>"
            "Spent: ₹%{y}k<br>"
            "Outstanding: ₹%{z}k<extra></extra>"
        ),
    )])
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Orders", showbackground=False, color="#8892b0"),
            yaxis=dict(title="Spent (₹k)", showbackground=False, color="#8892b0"),
            zaxis=dict(title="Outstanding (₹k)", showbackground=False, color="#8892b0"),
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf6"),
        height=460,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig, use_container_width=True, key="cust_3d")


# ═══════════════════════════════════════════════════════════
# OWNER MARKETING DASHBOARD
# ═══════════════════════════════════════════════════════════
def render_owner_marketing(retailers, orders):
    st.markdown("### 📢 Marketing & Promotions")
    st.caption("Privacy-first: Public messages never show prices. Each customer sees only their price.")

    summary = mk.campaign_summary()

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05));
                    border-left:4px solid #00d4ff;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">TOTAL PROMOS</div>
            <div style="color:#00d4ff;font-size:1.6rem;font-weight:800;">{summary['total_promos']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,212,122,0.15),rgba(0,212,122,0.05));
                    border-left:4px solid #00d47a;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">ACTIVE</div>
            <div style="color:#00d47a;font-size:1.6rem;font-weight:800;">{summary['active']}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(255,181,71,0.15),rgba(255,181,71,0.05));
                    border-left:4px solid #ffb547;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">MESSAGES SENT</div>
            <div style="color:#ffb547;font-size:1.6rem;font-weight:800;">{summary['total_sent']}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(123,97,255,0.15),rgba(123,97,255,0.05));
                    border-left:4px solid #7b61ff;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">CUSTOMERS</div>
            <div style="color:#7b61ff;font-size:1.6rem;font-weight:800;">{len(retailers)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Sub-tabs
    m1, m2, m3, m4, m5 = st.tabs([
        "🚀 Create", "🌌 3D Universe", "👥 Customers 3D",
        "📋 Active", "📤 Send"
    ])

    # ═══ M1: CREATE ═══
    with m1:
        st.markdown("#### 🎯 New Promotion")
        st.caption("Public text is shown to everyone. Prices NEVER appear publicly.")

        with st.form("new_promo"):
            col_a, col_b = st.columns(2)
            with col_a:
                _title = st.text_input("Title *",
                    placeholder="Monsoon Health Drive")
                _ptype = st.selectbox("Type", list(mk.PROMO_TYPES.keys()),
                    format_func=lambda x: f"{mk.PROMO_TYPES[x]['emoji']} {mk.PROMO_TYPES[x]['label']}")
            with col_b:
                _extra = st.number_input("Hidden extra discount %",
                    min_value=0.0, max_value=20.0, value=3.0, step=0.5)
                _days = st.number_input("Valid for (days)",
                    min_value=1, max_value=180, value=30)

            _public = st.text_area("Public message * (NO PRICES)",
                placeholder="Stock up on seasonal medicines. Login to see your exclusive price.",
                height=100)

            _audience = st.selectbox("Send to",
                ["all", "specific"],
                format_func=lambda x: "🌍 All customers" if x == "all" else "🎯 Specific customers")

            _selected = []
            if _audience == "specific":
                _selected = st.multiselect("Choose retailers",
                    [f"{r['id']} — {r['shop']}" for r in retailers])

            if st.form_submit_button("✨ Create Promotion", use_container_width=True, type="primary"):
                if not _title.strip() or not _public.strip():
                    st.error("Title and public message required")
                else:
                    _target = [s.split(" — ")[0] for s in _selected] if _selected else []
                    promo = mk.create_promotion(
                        title=_title.strip(), promo_type=_ptype,
                        public_text=_public.strip(),
                        extra_discount_pct=float(_extra),
                        valid_days=int(_days),
                        audience=_audience,
                        target_retailers=_target,
                    )
                    st.success(f"✅ Created: {promo['id']}")
                    st.rerun()

    # ═══ M2: 3D UNIVERSE ═══
    with m2:
        st.markdown("#### 🌌 Promotion Universe (3D)")
        st.caption("Each sphere = 1 promotion. Rotate with mouse.")
        promos = mk.load_promos()
        render_3d_promo_universe(promos)

    # ═══ M3: 3D CUSTOMERS ═══
    with m3:
        st.markdown("#### 👥 Customer Cluster (3D)")
        st.caption("Size = order count · Color = status (green=active, red=blocked)")
        render_3d_customer_clusters(retailers, orders)

    # ═══ M4: ACTIVE ═══
    with m4:
        st.markdown("#### 📋 Active Promotions")
        promos = mk.load_promos()
        today = datetime.now().strftime("%Y-%m-%d")

        if not promos:
            st.info("No promotions yet.")
        else:
            for p in promos:
                status = "🟢 Active" if p.get("active") else "⚪ Inactive"
                expired = p["valid_until"] < today
                if expired:
                    status = "🔴 Expired"

                t = mk.PROMO_TYPES.get(p["type"], mk.PROMO_TYPES["custom"])
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(26,31,58,0.9),rgba(15,20,40,0.9));
                            border-left:4px solid #00d4ff;border-radius:12px;
                            padding:14px 18px;margin:8px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:start;">
                        <div>
                            <div style="font-size:1.1rem;font-weight:800;color:#e8eaf6;">
                                {t['emoji']} {p['title']}
                            </div>
                            <div style="color:#8892b0;font-size:0.75rem;margin-top:4px;">
                                {p['id']} · {status} · Valid {p['valid_from']} → {p['valid_until']}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#ff4d6d;font-weight:800;">+{p['extra_discount_pct']:.1f}%</div>
                            <div style="color:#8892b0;font-size:0.7rem;">hidden discount</div>
                        </div>
                    </div>
                    <div style="color:#e8eaf6;font-size:0.85rem;margin-top:8px;">
                        📝 {p['public_text'][:120]}{'...' if len(p['public_text'])>120 else ''}
                    </div>
                    <div style="color:#8892b0;font-size:0.75rem;margin-top:6px;">
                        👥 Audience: {p['audience']} · 📤 Sent: {len(p.get('sent_to', []))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if p.get("active") and not expired:
                    if st.button(f"⏹ Deactivate {p['id']}",
                                 key=f"deact_{p['id']}"):
                        mk.deactivate_promo(p["id"])
                        st.rerun()

    # ═══ M5: SEND ═══
    with m5:
        st.markdown("#### 📤 Send Promotion")
        st.caption("Public message sent to all. No prices visible to anyone.")
        promos = mk.load_promos()
        active_promos = [p for p in promos if p.get("active")]
        if not active_promos:
            st.info("No active promotions. Create one first.")
        else:
            _pick = st.selectbox("Choose promotion",
                [f"{p['id']} — {p['title']}" for p in active_promos])
            _pid = _pick.split(" — ")[0]

            # Preview
            _promo = next((p for p in active_promos if p["id"] == _pid), None)
            if _promo:
                st.markdown("##### 👁️ Preview — what customers will see")
                st.info(mk.build_public_message(_promo).replace("<b>", "**").replace("</b>", "**"))

                _c1, _c2 = st.columns(2)
                with _c1:
                    if st.button("📤 Send Now", use_container_width=True, type="primary"):
                        with st.spinner("Sending..."):
                            res = mk.send_promotion(_pid, retailers, orders)
                        if res.get("ok"):
                            st.success(f"✅ Sent: {res['sent']} · Failed: {res['failed']}")
                            st.rerun()
                        else:
                            st.error(res.get("msg", "Unknown error"))
                with _c2:
                    if st.button("🧪 Dry Run", use_container_width=True):
                        res = mk.send_promotion(_pid, retailers, orders, dry_run=True)
                        st.info(f"Would send to {res.get('recipients', 0)} customers")


# ═══════════════════════════════════════════════════════════
# CUSTOMER VIEW — what retailer sees
# ═══════════════════════════════════════════════════════════
def render_customer_promotions(retailer):
    st.markdown("### 🎁 Offers For You")
    promos = mk.active_promos_for_retailer(retailer["id"])
    if not promos:
        st.info("No active offers right now. Check back soon!")
        return
    for p in promos:
        t = mk.PROMO_TYPES.get(p["type"], mk.PROMO_TYPES["custom"])
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(0,212,255,0.12),rgba(123,97,255,0.08));
                    border-left:4px solid #00d4ff;border-radius:12px;
                    padding:14px 18px;margin:10px 0;
                    animation:shimmer 3s ease-in-out infinite;">
            <div style="font-size:1.15rem;font-weight:800;color:#00d4ff;">
                {t['emoji']} {p['title']}
            </div>
            <div style="color:#e8eaf6;margin-top:8px;font-size:0.9rem;">
                {p['public_text']}
            </div>
            <div style="color:#8892b0;font-size:0.75rem;margin-top:8px;">
                📅 Valid until {p['valid_until']} · 👤 Login to see your exclusive price
            </div>
        </div>
        """, unsafe_allow_html=True)
