"""
owner_spending_report.py — Confidential spending trend analytics.
Owner-only view. Never shown to customers or staff.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json


def _load_orders():
    try:
        return json.loads(Path("orders.json").read_text())
    except Exception:
        return []


def _load_retailers():
    try:
        return json.loads(Path("retailers.json").read_text())
    except Exception:
        return []


def render():
    """Render full spending analytics for owner."""
    st.markdown("### 📊 Business Intelligence — Spending & Trends")
    st.caption("🔒 Confidential · Owner-only view · Data never exposed to customers or staff")

    orders = _load_orders()
    retailers = _load_retailers()

    if not orders:
        st.info("No orders yet. Analytics will appear once orders are placed.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(orders)
    df["placed_at"] = pd.to_datetime(df["placed_at"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["placed_at"])
    df["total"] = pd.to_numeric(df.get("total", 0), errors="coerce").fillna(0)
    df["month"] = df["placed_at"].dt.strftime("%Y-%m")

    # ═══ KPI Cards ═══
    total_revenue = df[df["status"].isin(["Approved","Packed","Dispatched","Delivered"])]["total"].sum()
    this_month = df[df["placed_at"] >= datetime.now() - timedelta(days=30)]["total"].sum()
    pending = df[df["status"] == "Pending"]["total"].sum()
    avg_order = df["total"].mean() if len(df) > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    k2.metric("📅 Last 30 Days", f"₹{this_month:,.0f}")
    k3.metric("⏳ Pending Value", f"₹{pending:,.0f}")
    k4.metric("📈 Avg Order", f"₹{avg_order:,.0f}")

    st.markdown("---")

    # ═══ Tabs ═══
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Revenue Trend",
        "🏪 Top Retailers",
        "🎯 Segment Analysis",
        "⚠️ Churn Risk",
    ])

    # ── Tab 1: Revenue Trend ──
    with tab1:
        st.markdown("#### 📈 Monthly Revenue Trend")
        monthly = df.groupby("month").agg(
            revenue=("total", "sum"),
            orders=("order_id", "count"),
        ).reset_index()

        if len(monthly) > 0:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly["month"], y=monthly["revenue"],
                name="Revenue", marker_color="#00d4aa",
                text=monthly["revenue"].apply(lambda x: f"₹{x:,.0f}"),
                textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=monthly["month"], y=monthly["orders"],
                name="Orders", yaxis="y2",
                line=dict(color="#7b61ff", width=3),
                marker=dict(size=10),
            ))
            fig.update_layout(
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaf6"),
                yaxis=dict(title="Revenue (₹)", gridcolor="rgba(255,255,255,0.08)"),
                yaxis2=dict(title="Orders", overlaying="y", side="right",
                           showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Recent activity
        st.markdown("#### 🕐 Last 30 Days Activity")
        recent = df[df["placed_at"] >= datetime.now() - timedelta(days=30)]
        if len(recent) > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("Orders", len(recent))
            c2.metric("Revenue", f"₹{recent['total'].sum():,.0f}")
            c3.metric("Avg per Day", f"₹{recent['total'].sum() / 30:,.0f}")

    # ── Tab 2: Top Retailers ──
    with tab2:
        st.markdown("#### 🏪 Top Retailers by Revenue")
        by_ret = df[df["status"].isin(["Approved","Packed","Dispatched","Delivered"])].groupby("shop").agg(
            revenue=("total", "sum"),
            orders=("order_id", "count"),
        ).sort_values("revenue", ascending=False).head(15).reset_index()

        if len(by_ret) > 0:
            fig = px.bar(
                by_ret, x="revenue", y="shop", orientation="h",
                color="revenue", color_continuous_scale=["#0e8f7a", "#00d4aa", "#7b61ff"],
                text="revenue",
            )
            fig.update_traces(
                texttemplate="₹%{text:,.0f}",
                textposition="outside",
            )
            fig.update_layout(
                height=max(300, len(by_ret) * 40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaf6"),
                xaxis=dict(title="Revenue (₹)", gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(title="", autorange="reversed"),
                showlegend=False,
                margin=dict(l=10, r=40, t=20, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Table view
            with st.expander("📋 Detailed view"):
                by_ret["avg_order"] = by_ret["revenue"] / by_ret["orders"]
                st.dataframe(
                    by_ret.rename(columns={
                        "shop": "Retailer",
                        "revenue": "Revenue (₹)",
                        "orders": "Orders",
                        "avg_order": "Avg Order (₹)",
                    }),
                    use_container_width=True, hide_index=True,
                )

    # ── Tab 3: Segment Analysis ──
    with tab3:
        st.markdown("#### 🎯 Revenue by Order Status")
        status_breakdown = df.groupby("status")["total"].agg(["count", "sum"]).reset_index()
        status_breakdown.columns = ["Status", "Count", "Value"]

        fig = px.pie(
            status_breakdown, values="Value", names="Status",
            hole=0.5,
            color_discrete_sequence=["#00d4aa", "#7b61ff", "#ffb547", "#ff9900",
                                     "#ff4d6d", "#8892b0"],
        )
        fig.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf6"),
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📅 Day-of-Week Patterns")
        df["dow"] = df["placed_at"].dt.day_name()
        dow = df.groupby("dow")["total"].sum().reindex(
            ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        ).fillna(0)

        fig2 = px.bar(
            x=dow.index, y=dow.values,
            labels={"x": "Day", "y": "Revenue (₹)"},
            color=dow.values,
            color_continuous_scale=["#0e8f7a", "#00d4aa", "#7b61ff"],
        )
        fig2.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf6"),
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 4: Churn Risk ──
    with tab4:
        st.markdown("#### ⚠️ Retailers at Risk (No orders in 30+ days)")
        st.caption("Track who might stop ordering — reach out before they churn")

        if not retailers:
            st.info("No retailers loaded")
        else:
            today = datetime.now()
            risk_list = []
            for r in retailers:
                r_orders = df[df["retailer_id"] == r["id"]]
                if len(r_orders) == 0:
                    risk_list.append({
                        "Shop": r["shop"],
                        "Owner": r.get("owner", "—"),
                        "Last Order": "Never",
                        "Days Since": "—",
                        "Lifetime Value": 0,
                        "Risk": "🔴 New — no orders",
                    })
                    continue
                last = r_orders["placed_at"].max()
                days = (today - last).days
                ltv = r_orders[r_orders["status"].isin(["Approved","Packed","Dispatched","Delivered"])]["total"].sum()

                if days > 90:
                    risk = "🔴 HIGH RISK"
                elif days > 30:
                    risk = "🟡 Medium"
                else:
                    risk = "✅ Active"

                risk_list.append({
                    "Shop": r["shop"],
                    "Owner": r.get("owner", "—"),
                    "Last Order": last.strftime("%d-%b-%Y"),
                    "Days Since": days,
                    "Lifetime Value": f"₹{ltv:,.0f}",
                    "Risk": risk,
                })

            risk_df = pd.DataFrame(risk_list).sort_values("Days Since", ascending=False)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)

            # Summary
            high = len([x for x in risk_list if "HIGH" in x["Risk"]])
            med = len([x for x in risk_list if "Medium" in x["Risk"]])
            if high:
                st.error(f"⚠️ {high} retailer(s) at HIGH RISK of churning — no order in 90+ days")
            if med:
                st.warning(f"⏰ {med} retailer(s) quiet for 30-90 days — follow up")
