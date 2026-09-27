"""
reports_visual.py — Visual dashboard rendering for PharmaMind.
Transforms plain AI reports into MBA-style visual dashboards.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


# ---------- Color palette ----------
COLORS = {
    "green":   "#00d47a",
    "amber":   "#ffb547",
    "red":     "#ff4d6d",
    "blue":    "#00d4ff",
    "purple":  "#7b61ff",
    "grey":    "#8892b0",
    "bg":      "rgba(26,31,58,0.7)",
    "border":  "rgba(123,97,255,0.3)",
}


def _rag(value, green_thresh, amber_thresh, higher_is_better=True):
    """Return RAG (Red/Amber/Green) status for a metric."""
    if higher_is_better:
        if value >= green_thresh: return "green", "🟢"
        if value >= amber_thresh: return "amber", "🟡"
        return "red", "🔴"
    else:
        if value <= green_thresh: return "green", "🟢"
        if value <= amber_thresh: return "amber", "🟡"
        return "red", "🔴"


# ---------- 1. KPI STRIP (headline cards) ----------
def render_kpi_strip(metrics: dict):
    """
    metrics = {
        "orders": {"value": 12, "delta": "+3", "rag": "green"},
        "revenue": {"value": "₹45,000", "delta": "-8%", "rag": "amber"},
        ...
    }
    """
    cols = st.columns(len(metrics))
    for col, (label, data) in zip(cols, metrics.items()):
        color = COLORS.get(data.get("rag", "grey"), COLORS["grey"])
        delta = data.get("delta", "")
        with col:
            st.markdown(f"""
            <div style="
                background: {COLORS['bg']};
                border: 2px solid {color};
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                height: 130px;
            ">
                <div style="color:{COLORS['grey']}; font-size:0.8rem;
                            text-transform:uppercase; letter-spacing:1px;">
                    {label}
                </div>
                <div style="color:{color}; font-size:2rem; font-weight:700;
                            margin:0.3rem 0;">
                    {data['value']}
                </div>
                <div style="color:{COLORS['grey']}; font-size:0.75rem;">
                    {delta}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ---------- 2. HEALTH BARS (BCG-style gauges) ----------
def render_health_bars(items: list):
    """Render health bars as HTML, with whitespace collapsed."""
    html = ""
    for it in items:
        pct = max(0, min(100, it["pct"]))
        color = COLORS.get(it["color"], COLORS["grey"])
        html += (
            f'<div style="margin-bottom:0.8rem;">'
            f'<div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:0.3rem;">'
            f'<span>{it["label"]}</span>'
            f'<span style="color:{color};font-weight:600;">{pct}%</span>'
            f'</div>'
            f'<div style="background:rgba(255,255,255,0.08);border-radius:6px;height:12px;overflow:hidden;">'
            f'<div style="background:{color};width:{pct}%;height:100%;border-radius:6px;"></div>'
            f'</div>'
            f'</div>'
        )
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


# ---------- 3. ACTION CARDS (Eisenhower-style) ----------
def render_action_cards(actions: list):
    """Render action cards with collapsed HTML."""
    cols = st.columns(len(actions))
    for col, a in zip(cols, actions):
        effort_color = COLORS["green"] if a["effort"] == "Low" else (
                       COLORS["amber"] if a["effort"] == "Medium" else COLORS["red"])
        impact_color = COLORS["green"] if a["impact"] == "High" else (
                       COLORS["amber"] if a["impact"] == "Medium" else COLORS["grey"])
        with col:
            html = (
                f'<div style="background:{COLORS["bg"]};border-left:4px solid {impact_color};'
                f'border-radius:10px;padding:1rem;height:200px;">'
                f'<div style="font-size:1.6rem;">{a["icon"]}</div>'
                f'<div style="font-weight:600;margin:0.3rem 0;">{a["title"]}</div>'
                f'<div style="font-size:0.8rem;color:{COLORS["grey"]};margin-bottom:0.6rem;">{a["desc"]}</div>'
                f'<div style="font-size:0.75rem;">'
                f'<span style="color:{effort_color};">⚡ Effort: {a["effort"]}</span><br>'
                f'<span style="color:{impact_color};">🎯 Impact: {a["impact"]}</span>'
                f'</div>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)


# ---------- 4. 5 WHYS ROOT CAUSE ----------
def render_root_cause(whys: list):
    """Render root cause as a numbered list with no leaking whitespace."""
    html = ""
    for i, why in enumerate(whys, 1):
        html += (
            f'<div style="display:flex;align-items:start;margin-bottom:0.5rem;">'
            f'<div style="background:#00d4ff;color:#000;width:26px;height:26px;'
            f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
            f'font-weight:700;font-size:0.8rem;flex-shrink:0;">{i}</div>'
            f'<div style="margin-left:0.8rem;padding-top:2px;">{why}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


# ---------- 5. INSIGHT BOX ----------
def render_insight(text: str, title: str = "🧠 SWAMI INSIGHT"):
    """Render insight box with collapsed HTML."""
    html = (
        f'<div style="background:linear-gradient(135deg, rgba(123,97,255,0.15), rgba(0,212,255,0.10));'
        f'border:1px solid {COLORS["purple"]};border-radius:12px;padding:1.2rem 1.4rem;margin:1rem 0;">'
        f'<div style="font-weight:700;color:{COLORS["purple"]};margin-bottom:0.5rem;font-size:0.95rem;">{title}</div>'
        f'<div style="line-height:1.6;">{text}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------- 6. GAUGE CHART (Plotly) ----------
def render_health_gauge(score: int, label: str = "Business Health"):
    color = COLORS["red"]
    if score >= 70: color = COLORS["green"]
    elif score >= 40: color = COLORS["amber"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": label, "font": {"color": "#e8eaf6", "size": 14}},
        number={"font": {"color": color, "size": 40}},
        gauge={
            "axis": {"range": [0, 100],
                     "tickcolor": "#8892b0"},
            "bar": {"color": color},
            "bgcolor": "rgba(255,255,255,0.05)",
            "steps": [
                {"range": [0, 40], "color": "rgba(255,77,109,0.15)"},
                {"range": [40, 70], "color": "rgba(255,181,71,0.15)"},
                {"range": [70, 100], "color": "rgba(0,212,122,0.15)"},
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e8eaf6"},
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- 7. TREND LINE (Plotly) ----------
def render_trend_line(x, y, title="Trend"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines+markers",
        line=dict(color=COLORS["blue"], width=3),
        marker=dict(size=8, color=COLORS["blue"]),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.10)",
    ))
    fig.update_layout(
        title={"text": title, "font": {"color": "#e8eaf6"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e8eaf6"},
        height=280,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- 8. RETAILER SCORECARD (BCG-style) ----------
def render_retailer_scorecard(retailers: list):
    """Render retailer scorecard with collapsed HTML."""
    html = ""
    for r in retailers:
        color = COLORS["green"]
        if r["utilization"] > 90: color = COLORS["red"]
        elif r["utilization"] > 70: color = COLORS["amber"]
        html += (
            f'<div style="background:{COLORS["bg"]};border-left:4px solid {color};'
            f'border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.6rem;'
            f'display:flex;justify-content:space-between;align-items:center;">'
            f'<div><div style="font-weight:600;">{r["shop"]}</div>'
            f'<div style="font-size:0.75rem;color:{COLORS["grey"]};">'
            f'Health: {r["health"]}/100 · Risk: {r["risk"]}</div></div>'
            f'<div style="text-align:right;">'
            f'<div style="font-weight:700;color:{color};">₹{r["outstanding"]:,}</div>'
            f'<div style="font-size:0.75rem;color:{COLORS["grey"]};">'
            f'{r["utilization"]}% credit used</div></div>'
            f'</div>'
        )
    st.markdown(html, unsafe_allow_html=True)
