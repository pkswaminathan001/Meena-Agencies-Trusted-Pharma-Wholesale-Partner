"""discounts_ui.py — Discount dashboard with 3D animations."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import discounts as dc


def _fmt(v):
    try:
        return f"₹{float(v):,.0f}"
    except:
        return "₹0"


def _pct(v):
    try:
        return f"{float(v):.1f}%"
    except:
        return "0.0%"


# ═══════════════════════════════════════════════════════════
# 3D TIER PYRAMID
# ═══════════════════════════════════════════════════════════
def render_3d_tier_pyramid(summary):
    tiers = ["Apex Partner", "Prime Partner", "Preferred Partner", "Standard Partner", "New Partner"]
    counts = [summary["tier_distribution"].get(t, 0) for t in tiers]
    colors = ["#00d4ff", "#7b61ff", "#00d47a", "#ffb547", "#8892b0"]
    sizes = [max(8, c * 4 + 8) for c in counts]

    fig = go.Figure(data=[go.Scatter3d(
        x=[0]*len(tiers),
        y=list(range(len(tiers))),
        z=counts,
        mode="markers+text",
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.9,
            line=dict(color="#ffffff", width=1),
        ),
        text=[f"{t}<br>{c} customer(s)" for t, c in zip(tiers, counts)],
        textposition="top center",
        textfont=dict(color="#e8eaf6", size=11),
        hovertemplate="<b>%{text}</b><br>Customers: %{z}<extra></extra>",
    )])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(len(tiers))),
                ticktext=tiers,
                showbackground=False,
                color="#8892b0",
                gridcolor="rgba(0,212,255,0.15)",
            ),
            zaxis=dict(
                title="Customers",
                showbackground=False,
                color="#8892b0",
                gridcolor="rgba(0,212,255,0.15)",
            ),
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=0.1, y=2.2, z=0.7)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf6"),
        height=380,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="tier_pyramid_3d")


# ═══════════════════════════════════════════════════════════
# 3D PRODUCT DISCOUNT CHART
# ═══════════════════════════════════════════════════════════
def render_3d_product_chart(products):
    if not products:
        st.caption("No product discount data yet.")
        return

    top = products[:12]
    fig = go.Figure(data=[go.Scatter3d(
        x=[p["discount_events"] for p in top],
        y=[p["avg_extra_pct"] for p in top],
        z=[p["customers_affected"] for p in top],
        mode="markers+text",
        marker=dict(
            size=[max(10, p["discount_events"] * 4) for p in top],
            color=[p["avg_extra_pct"] for p in top],
            colorscale=[
                [0, "#0066cc"], [0.5, "#7b61ff"], [1, "#ffb547"]
            ],
            opacity=0.85,
            line=dict(color="#ffffff", width=1),
            colorbar=dict(title="Avg %", x=1.0),
        ),
        text=[p["medicine"][:15] for p in top],
        textposition="top center",
        textfont=dict(color="#e8eaf6", size=9),
        hovertemplate="<b>%{text}</b><br>Events: %{x}<br>Avg Extra: %{y}%<br>Customers: %{z}<extra></extra>",
    )])
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Discount Events", showbackground=False,
                       color="#8892b0", gridcolor="rgba(0,212,255,0.15)"),
            yaxis=dict(title="Avg Extra %", showbackground=False,
                       color="#8892b0", gridcolor="rgba(0,212,255,0.15)"),
            zaxis=dict(title="Customers", showbackground=False,
                       color="#8892b0", gridcolor="rgba(0,212,255,0.15)"),
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf6"),
        height=440,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig, use_container_width=True, key="product_3d")


# ═══════════════════════════════════════════════════════════
# TIER BADGE (animated CSS)
# ═══════════════════════════════════════════════════════════
def tier_badge_html(tier_name, pct, color):
    return f"""
    <span style="display:inline-block;
                 background:linear-gradient(135deg, {color}33, {color}11);
                 border:1.5px solid {color};
                 border-radius:14px;padding:4px 12px;
                 color:{color};font-weight:700;font-size:0.75rem;
                 letter-spacing:1px;
                 animation:badgePulse 2s ease-in-out infinite;">
        ⭐ {tier_name} · {pct:.1f}%
    </span>
    """


def _inject_badge_css():
    st.markdown("""
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-6px); }
    }
    </style>
    """, unsafe_allow_html=True)
def _unused_badge_css():
    st.markdown("""
    <style>
    @keyframes badgePulse {
        0%,100% { box-shadow: 0 0 0 0 currentColor; }
        50%      { box-shadow: 0 0 12px 2px currentColor; }
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# OWNER DISCOUNT DASHBOARD
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
# VISUAL TIER CARDS — Human-psychology optimized
# ═══════════════════════════════════════════════════════════
TIER_ICONS = {
    "Apex Partner":      "👑",
    "Prime Partner":     "⭐",
    "Preferred Partner": "🏅",
    "Standard Partner":  "🎖️",
    "New Partner":       "🌱",
}


def render_visual_tier_cards(summary, retailers=None, orders=None):
    """Rich tier cards with revenue, avg, top customers, upgrade progress."""
    import discounts as _dc
    from datetime import datetime as _dt

    rules = _dc.load_rules()
    tiers = rules["tiers"]
    total_customers = max(1, summary["total_customers"])

    # ─── Build per-tier data ───
    tier_data = {}
    for tname in tiers:
        tier_data[tname] = {
            "customers": [], "orders": 0, "revenue": 0.0,
            "last_order_days": [], "customers_list": []
        }

    if retailers and orders:
        for r in retailers:
            try:
                cur_tier, _ = _dc.get_customer_tier(r["id"])
            except Exception:
                cur_tier = "New Partner"
            if cur_tier not in tier_data:
                continue
            my_orders = [o for o in orders
                         if o.get("retailer_id") == r["id"]
                         and o.get("status") == "Approved"]
            rev = sum(o.get("total", 0) for o in my_orders)
            tier_data[cur_tier]["customers"].append(r["id"])
            tier_data[cur_tier]["customers_list"].append({
                "id": r["id"], "shop": r["shop"],
                "orders": len(my_orders), "revenue": rev,
                "status": r.get("status", "Active")
            })
            tier_data[cur_tier]["orders"] += len(my_orders)
            tier_data[cur_tier]["revenue"] += rev
            if my_orders:
                last_dt = my_orders[-1].get("placed_at", "")
                try:
                    d = _dt.strptime(str(last_dt)[:11], "%d-%b-%Y")
                    tier_data[cur_tier]["last_order_days"].append(
                        (_dt.now() - d).days
                    )
                except Exception:
                    pass

    # ─── Header ───
    st.markdown(
        '<div style="text-align:center;margin-bottom:20px;">'
        '<div style="font-size:0.75rem;color:#8892b0;letter-spacing:2px;">CUSTOMER SEGMENTATION</div>'
        f'<div style="font-size:1.8rem;font-weight:800;background:linear-gradient(90deg,#00d4ff,#7b61ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:4px;">{total_customers} Retail Partners</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    sorted_tiers = sorted(tiers.items(), key=lambda x: -x[1]["discount_pct"])
    next_tier_for = {}
    for i, (tname, _) in enumerate(sorted_tiers):
        next_tier_for[tname] = sorted_tiers[i-1] if i > 0 else None

    for tier_name, data in sorted_tiers:
        count = summary["tier_distribution"].get(tier_name, 0)
        pct_of_total = (count / total_customers * 100)
        bar_width = max(2, pct_of_total)
        color = data["color"]
        icon = TIER_ICONS.get(tier_name, "⭐")
        td = tier_data.get(tier_name, {})
        rev = td.get("revenue", 0)
        n_orders = td.get("orders", 0)
        avg_order = (rev / n_orders) if n_orders else 0
        last_days_list = td.get("last_order_days", [])
        avg_last_days = int(sum(last_days_list) / len(last_days_list)) if last_days_list else 0

        # Upgrade progress
        next_t = next_tier_for.get(tier_name)
        upgrade_txt = ""
        if next_t:
            need = next_t[1]["min_orders"]
            closest = max((c["orders"] for c in td.get("customers_list", [])), default=0)
            gap = max(0, need - closest)
            upgrade_txt = f"Next: {next_t[0]} needs {gap} more orders"

        # Top customers
        cust_list = sorted(td.get("customers_list", []),
                          key=lambda x: -x["revenue"])[:3]
        cust_html = ""
        if cust_list:
            names = " · ".join(f"{c['shop'][:18]}" for c in cust_list)
            cust_html = f'<div style="font-size:0.75rem;color:#8892b0;margin-top:6px;">👥 {names}</div>'

        html = (
            f'<div style="background:linear-gradient(135deg,{color}18,{color}05);'
            f'border-left:6px solid {color};border-radius:14px;'
            f'padding:16px 20px;margin:10px 0;position:relative;overflow:hidden;">'
            f'<div style="position:absolute;top:-50%;right:-10%;width:250px;height:250px;'
            f'background:radial-gradient(circle,{color}22,transparent 70%);pointer-events:none;"></div>'
            f'<div style="display:flex;align-items:center;gap:20px;position:relative;">'
            f'<div style="font-size:2.8rem;filter:drop-shadow(0 4px 12px {color}99);">{icon}</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:1.25rem;font-weight:800;color:{color};letter-spacing:0.5px;">{tier_name.upper()}</div>'
            f'<div style="font-size:0.8rem;color:#e8eaf6;margin-top:2px;">'
            f'<b style="color:{color};">{data["discount_pct"]:.0f}%</b> discount · min <b>{data["min_orders"]}</b> orders'
            f'</div>'
            f'<div style="background:rgba(255,255,255,0.08);border-radius:8px;height:8px;margin-top:10px;overflow:hidden;">'
            f'<div style="background:linear-gradient(90deg,{color},{color}aa);width:{bar_width}%;height:100%;border-radius:8px;box-shadow:0 0 12px {color}99;"></div>'
            f'</div>'
            f'<div style="display:flex;gap:16px;margin-top:8px;font-size:0.7rem;color:#8892b0;">'
            f'<span>📦 {n_orders} orders</span>'
            f'<span>💰 ₹{rev:,.0f}</span>'
            f'<span>📊 avg ₹{avg_order:,.0f}</span>'
            f'<span>⏱ {avg_last_days}d since last</span>'
            f'</div>'
            + cust_html +
            f'</div>'
            f'<div style="text-align:right;min-width:90px;">'
            f'<div style="font-size:2.4rem;font-weight:900;color:{color};line-height:1;text-shadow:0 0 20px {color}66;">{count}</div>'
            f'<div style="font-size:0.65rem;color:#8892b0;letter-spacing:1px;">CUSTOMERS</div>'
            f'<div style="font-size:0.8rem;color:{color};font-weight:600;margin-top:2px;">{pct_of_total:.0f}%</div>'
            f'</div>'
            f'</div>'
            + (f'<div style="font-size:0.7rem;color:{color};margin-top:6px;font-style:italic;">🎯 {upgrade_txt}</div>' if upgrade_txt else "") +
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    # Insight
    top_tier = sorted_tiers[0]
    top_count = summary["tier_distribution"].get(top_tier[0], 0)
    if top_count > 0:
        st.markdown(
            '<div style="background:linear-gradient(135deg,rgba(123,97,255,0.15),rgba(0,212,255,0.10));'
            'border:1px solid #7b61ff;border-radius:12px;padding:14px 18px;margin-top:16px;">'
            '<div style="font-size:0.7rem;color:#7b61ff;letter-spacing:1.5px;">💡 INSIGHT</div>'
            f'<div style="color:#e8eaf6;margin-top:6px;font-size:0.9rem;">'
            f'Your <b style="color:{top_tier[1]["color"]};">{top_count} {top_tier[0]}(s)</b> generate the highest loyalty. '
            f'Consider exclusive offers to grow this group.</div></div>',
            unsafe_allow_html=True,
        )





def render_owner_discounts(orders, retailers):
    _inject_badge_css()
    st.markdown("### 💰 Discount Command Center")
    st.caption("Owner: approve staff proposals, set tiers, monitor patterns")

    summary = dc.discount_stage_summary(orders, retailers)

    # ─── KPI cards ───
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05));
                    border-left:4px solid #00d4ff;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">TOTAL CUSTOMERS</div>
            <div style="color:#00d4ff;font-size:1.6rem;font-weight:800;">{summary['total_customers']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(255,181,71,0.15),rgba(255,181,71,0.05));
                    border-left:4px solid #ffb547;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">DISCOUNT VALUE</div>
            <div style="color:#ffb547;font-size:1.6rem;font-weight:800;">{_fmt(summary['total_discount_value'])}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,212,122,0.15),rgba(0,212,122,0.05));
                    border-left:4px solid #00d47a;border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">DISCOUNT EVENTS</div>
            <div style="color:#00d47a;font-size:1.6rem;font-weight:800;">{summary['total_discount_events']}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        _col = "#ff4d6d" if summary['pending_approval'] else "#7b61ff"
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(123,97,255,0.15),rgba(123,97,255,0.05));
                    border-left:4px solid {_col};border-radius:10px;padding:12px;">
            <div style="color:#8892b0;font-size:0.7rem;">PENDING APPROVAL</div>
            <div style="color:{_col};font-size:1.6rem;font-weight:800;">{summary['pending_approval']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ─── Sub-tabs ───
    d1, d2, d3, d4, d5 = st.tabs([
        "🎯 Tier Pyramid", "👥 Customers", "📦 Products",
        "👨‍💼 Staff Leaderboard", "✅ Approvals"
    ])

    # ═══ D1: 3D Pyramid ═══
    with d1:
        st.markdown("#### 🎯 Customer Tiers")
        st.caption("Visual partner segments — icons + progress + counts")
        render_visual_tier_cards(summary, retailers=retailers, orders=orders)

        st.markdown("---")
        st.markdown("##### Tier Legend")
        rules = dc.load_rules()
        cols = st.columns(len(rules["tiers"]))
        for col, (tier, data) in zip(cols, rules["tiers"].items()):
            with col:
                st.markdown(f"""
                <div style="background:rgba(26,31,58,0.7);border-left:4px solid {data['color']};
                            border-radius:8px;padding:10px;text-align:center;">
                    <div style="color:{data['color']};font-weight:800;font-size:1.1rem;">{tier}</div>
                    <div style="color:#e8eaf6;font-size:1.2rem;font-weight:700;">{data['discount_pct']:.0f}%</div>
                    <div style="color:#8892b0;font-size:0.65rem;">min {data['min_orders']} orders</div>
                </div>
                """, unsafe_allow_html=True)

    # ═══ D2: Customer table ═══
    with d2:
        st.markdown("#### 👥 Customer Discount Status")
        rows = dc.customer_discount_analysis(orders, retailers)
        if rows:
            df = pd.DataFrame([{
                "ID": r["retailer_id"],
                "Shop": r["shop"],
                "Tier": r["current_tier"],
                "Base %": r["base_discount_pct"],
                "Orders": r["orders"],
                "Avg Extra %": r["avg_extra_discount_pct"],
                "Events": r["total_discount_events"],
                "Pending": r["pending_requests"],
                "Suggested": r["suggested_tier"] if r["should_upgrade"] else "—",
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)

            # Tier assignment
            st.markdown("---")
            st.markdown("##### 🎯 Assign Tier to Customer")
            _rc1, _rc2, _rc3 = st.columns([2, 2, 1])
            with _rc1:
                _ret_pick = st.selectbox("Customer",
                    [f"{r['id']} — {r['shop']}" for r in retailers],
                    key="tier_ret")
            with _rc2:
                _tier_pick = st.selectbox("New Tier",
                    list(dc.load_rules()["tiers"].keys()), key="tier_pick")
            with _rc3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Assign", use_container_width=True, type="primary"):
                    _rid = _ret_pick.split(" — ")[0]
                    ok, msg = dc.set_customer_tier(_rid, _tier_pick)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("No customers yet.")

    # ═══ D3: Products ═══
    with d3:
        st.markdown("#### 📦 Product Discount Intelligence")
        st.caption("Every medicine with its discount cap, category, and stock")

        rules = dc.load_rules()
        caps = rules["product_limits"]

        # Load inventory
        try:
            import pandas as _pd2
            import sqlite3 as _sq
            _conn = _sq.connect("inventory.db")
            inv = _pd2.read_sql("SELECT * FROM inventory", _conn)
            _conn.close()
        except Exception:
            inv = None

        # KPI row
        if inv is not None and len(inv) > 0:
            total_meds = inv["medicine_name"].nunique()
            total_stock = int(inv["quantity"].sum())
            total_value = float((inv["quantity"] * inv["cost_price"]).sum())

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div style="background:linear-gradient(135deg,rgba(0,212,255,0.12),rgba(0,212,255,0.04));border-left:4px solid #00d4ff;border-radius:10px;padding:12px;"><div style="color:#8892b0;font-size:0.7rem;">UNIQUE MEDICINES</div><div style="color:#00d4ff;font-size:1.6rem;font-weight:800;">{total_meds}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="background:linear-gradient(135deg,rgba(0,212,122,0.12),rgba(0,212,122,0.04));border-left:4px solid #00d47a;border-radius:10px;padding:12px;"><div style="color:#8892b0;font-size:0.7rem;">TOTAL STOCK</div><div style="color:#00d47a;font-size:1.6rem;font-weight:800;">{total_stock:,}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div style="background:linear-gradient(135deg,rgba(255,181,71,0.12),rgba(255,181,71,0.04));border-left:4px solid #ffb547;border-radius:10px;padding:12px;"><div style="color:#8892b0;font-size:0.7rem;">INVENTORY VALUE</div><div style="color:#ffb547;font-size:1.6rem;font-weight:800;">₹{total_value:,.0f}</div></div>', unsafe_allow_html=True)
            with c4:
                _discount_events = len(dc.load_history())
                st.markdown(f'<div style="background:linear-gradient(135deg,rgba(123,97,255,0.12),rgba(123,97,255,0.04));border-left:4px solid #7b61ff;border-radius:10px;padding:12px;"><div style="color:#8892b0;font-size:0.7rem;">DISCOUNT EVENTS</div><div style="color:#7b61ff;font-size:1.6rem;font-weight:800;">{_discount_events}</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            # Category summary
            st.markdown("##### 🚦 Discount Caps by Category")
            cat_icons = {"vaccine": "💉", "insulin": "🩸", "controlled": "🚫", "default": "💊"}
            cat_labels = {"vaccine": "Vaccines", "insulin": "Insulin", "controlled": "Controlled Substances", "default": "Standard Medicines"}
            for cat, cap in caps.items():
                _icon = cat_icons.get(cat, "💊")
                _label = cat_labels.get(cat, cat.title())
                _c = "#ff4d6d" if cap == 0 else ("#ffb547" if cap < 10 else "#00d47a")
                st.markdown(f'<div style="background:rgba(26,31,58,0.7);border-left:5px solid {_c};border-radius:10px;padding:10px 16px;margin:6px 0;display:flex;justify-content:space-between;align-items:center;"><div>{_icon} <b style="color:#e8eaf6;">{_label}</b></div><div style="color:{_c};font-weight:800;font-size:1.1rem;">max {cap:.1f}%</div></div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📋 Full Product Catalog with Discount Eligibility")

            # Classify each medicine
            def classify(name):
                n = str(name).lower()
                if "vaccine" in n: return "vaccine", caps.get("vaccine", 8.0)
                if "insulin" in n: return "insulin", caps.get("insulin", 10.0)
                if "morphine" in n or "schedule" in n or "narcotic" in n:
                    return "controlled", caps.get("controlled", 0.0)
                return "standard", caps.get("default", 15.0)

            # Aggregate by medicine name
            if inv is not None:
                agg = inv.groupby("medicine_name").agg({
                    "quantity": "sum",
                    "cost_price": "mean",
                    "selling_price": "mean" if "selling_price" in inv.columns else "mean",
                }).reset_index()
                agg["category"], agg["cap"] = zip(*agg["medicine_name"].apply(classify))
                agg = agg.sort_values("quantity", ascending=False)

                # Show top 20
                for _, row in agg.head(20).iterrows():
                    cat = row["category"]
                    cap = row["cap"]
                    icon = cat_icons.get(cat, "💊")
                    _c = "#ff4d6d" if cap == 0 else ("#ffb547" if cap < 10 else "#00d47a")
                    eligible = "🚫 Not discountable" if cap == 0 else f"✅ Discount up to {cap:.0f}%"
                    st.markdown(
                        f'<div style="background:rgba(26,31,58,0.6);border-radius:8px;padding:8px 14px;margin:4px 0;display:flex;justify-content:space-between;align-items:center;">'
                        f'<div style="flex:1;"><div style="color:#e8eaf6;font-weight:600;">{icon} {row["medicine_name"][:40]}</div>'
                        f'<div style="font-size:0.7rem;color:#8892b0;">Stock: {int(row["quantity"]):,} units · Cost ₹{row["cost_price"]:.2f}</div></div>'
                        f'<div style="text-align:right;"><div style="color:{_c};font-weight:700;font-size:0.85rem;">{eligible}</div>'
                        f'<div style="font-size:0.65rem;color:#8892b0;">{cat.title()}</div></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                if len(agg) > 20:
                    st.caption(f"... and {len(agg) - 20} more products")

                # Download CSV
                csv = agg[["medicine_name", "category", "quantity", "cost_price", "cap"]].to_csv(index=False)
                st.download_button("📥 Download Full List (CSV)", csv,
                                   file_name="product_discount_caps.csv",
                                   mime="text/csv", use_container_width=True)
        else:
            st.info("No inventory data. Add stock first via 💼 Ops → 📦 Add Stock.")

    # ═══ D4: Staff leaderboard ═══
    with d4:
        st.markdown("#### 👨‍💼 Staff Discount Leaderboard")
        st.caption("Who gives the most discounts — sorted by value given away")
        staff_stats = dc.staff_discount_analysis()
        if staff_stats:
            staff_stats.sort(key=lambda x: -x["total_value"])
            for i, s in enumerate(staff_stats, 1):
                _medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"#{i}")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(26,31,58,0.9),rgba(15,20,40,0.9));
                            border-left:4px solid {'#ffb547' if i==1 else '#7b61ff'};
                            border-radius:10px;padding:12px 16px;margin:6px 0;">
                    <div style="display:flex;justify-content:space-between;">
                        <div>
                            <div style="font-size:1.1rem;">{_medal} <b>{s['staff_name']}</b></div>
                            <div style="color:#8892b0;font-size:0.75rem;">ID: {s['staff_id']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#ff4d6d;font-weight:700;font-size:1.2rem;">{_fmt(s['total_value'])}</div>
                            <div style="color:#8892b0;font-size:0.7rem;">total discount value</div>
                        </div>
                    </div>
                    <div style="margin-top:8px;font-size:0.75rem;color:#8892b0;">
                        ✅ Approved: {s['approved']} · ❌ Rejected: {s['rejected']} · ⏳ Pending: {s['pending']} · Avg extra: {s['avg_extra_pct']}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No staff discount activity yet.")

    # ═══ D5: Approvals queue ═══
    with d5:
        st.markdown("#### ✅ Pending Staff Discount Proposals")
        pending = dc.pending_requests()
        if not pending:
            st.success("🎉 No pending requests. All clear.")
        else:
            for req in pending:
                st.markdown(f"""
                <div style="background:rgba(255,181,71,0.10);border-left:4px solid #ffb547;
                            border-radius:10px;padding:12px 16px;margin:8px 0;">
                    <div style="display:flex;justify-content:space-between;">
                        <div>
                            <div style="font-weight:700;color:#ffb547;font-size:1rem;">
                                ⏳ {req['staff_name']} → {req['retailer_shop']}
                            </div>
                            <div style="color:#8892b0;font-size:0.75rem;">
                                Order {req['order_id']} · {_fmt(req['order_amount'])} · {req['created_at']}
                            </div>
                            <div style="color:#e8eaf6;font-size:0.85rem;margin-top:6px;">
                                💬 {req['reason']}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#ff4d6d;font-size:1.5rem;font-weight:800;">
                                +{_pct(req['extra_pct'])}
                            </div>
                            <div style="color:#8892b0;font-size:0.7rem;">extra discount</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                _a1, _a2 = st.columns(2)
                with _a1:
                    if st.button(f"✅ Approve {req['request_id']}",
                                 key=f"app_{req['request_id']}",
                                 use_container_width=True, type="primary"):
                        ok, msg = dc.owner_decide(req["request_id"], "approve")
                        st.success(msg)
                        st.rerun()
                with _a2:
                    if st.button(f"❌ Reject {req['request_id']}",
                                 key=f"rej_{req['request_id']}",
                                 use_container_width=True):
                        ok, msg = dc.owner_decide(req["request_id"], "reject")
                        st.warning(msg)
                        st.rerun()


# ═══════════════════════════════════════════════════════════
# CUSTOMER — SHOW THEIR TIER + DISCOUNT
# ═══════════════════════════════════════════════════════════
def render_customer_discount_badge(retailer):
    tier, pct = dc.get_customer_tier(retailer["id"])
    rules = dc.load_rules()
    color = rules["tiers"].get(tier, {}).get("color", "#8892b0")
    _inject_badge_css()
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color}22,{color}08);
                border:1.5px solid {color};border-radius:12px;
                padding:10px 14px;margin:8px 0;
                animation:badgePulse 3s ease-in-out infinite;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="color:#8892b0;font-size:0.7rem;letter-spacing:1px;">YOUR DISCOUNT TIER</div>
                <div style="color:{color};font-weight:800;font-size:1.4rem;">⭐ {tier}</div>
            </div>
            <div style="text-align:right;">
                <div style="color:{color};font-size:2rem;font-weight:800;">{pct:.0f}%</div>
                <div style="color:#8892b0;font-size:0.7rem;">on every order</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# STAFF — PROPOSE DISCOUNT
# ═══════════════════════════════════════════════════════════
def render_staff_discount_propose(staff, retailer, order):
    st.markdown("##### 💰 Propose Extra Discount")
    st.caption("Maximum auto-approve: 8% — above that, owner must approve")

    with st.form(f"propose_{order.get('order_id','X')}"):
        _extra = st.slider("Extra discount %", 0.0, 20.0, 5.0, 0.5)
        _reason = st.text_area("Reason for this discount",
                               placeholder="e.g. bulk order, loyalty, festival")
        if st.form_submit_button("📩 Submit Proposal", use_container_width=True, type="primary"):
            if not _reason.strip():
                st.error("Please give a reason")
            else:
                sid = staff.get("id", "STAFF")
                sname = staff.get("name", "Staff")
                ok, msg, _ = dc.staff_propose_discount(sid, sname, retailer,
                                                        order, _extra, _reason)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
