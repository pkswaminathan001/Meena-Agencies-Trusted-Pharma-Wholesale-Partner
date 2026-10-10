"""rich_header.py — Beautiful owner header with logo, KPIs, live activity, mood."""
import streamlit as st
from datetime import datetime
import json
from pathlib import Path


def _read_notifs(limit=5):
    try:
        items = json.loads(Path("notifications.json").read_text())
        items.sort(key=lambda x: x.get("ts", ""), reverse=True)
        return items[:limit]
    except Exception:
        return []


def _time_ago(iso_str):
    try:
        then = datetime.fromisoformat(iso_str)
        secs = int((datetime.now() - then).total_seconds())
        if secs < 60:      return "just now"
        if secs < 3600:    return f"{secs//60} min ago"
        if secs < 86400:   return f"{secs//3600} hr ago"
        return then.strftime("%d %b")
    except Exception:
        return "—"


def _mood(pending_count, notif_count):
    if pending_count > 5:
        return ("🟡", "Busy day — several approvals waiting", "#ffb547")
    if pending_count > 0:
        return ("🟢", "All systems normal", "#00d4aa")
    return ("🔵", "Quiet — nothing pending", "#7b61ff")


def inject_css():
    if st.session_state.get("_rich_header_done"):
        return
    st.markdown("""
    <style>
    @keyframes rhFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes rhPulse {
        0%,100% { opacity: 1; }
        50%     { opacity: .55; }
    }
    @keyframes rhShimmer {
        0%   { background-position: -300px 0; }
        100% { background-position: 300px 0; }
    }
    .rh-hero {
        position: relative;
        padding: 22px 28px 26px;
        margin: 0 0 20px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(0,212,170,0.14), rgba(123,97,255,0.12));
        border: 1px solid rgba(0,212,170,0.3);
        overflow: hidden;
        animation: rhFadeIn .5s ease-out;
    }
    .rh-hero::before {
        content: "";
        position: absolute; inset: 0;
        background: radial-gradient(600px 200px at 10% 0%, rgba(0,212,170,0.15), transparent 60%);
        pointer-events: none;
    }
    .rh-hero-row { display: flex; align-items: center; gap: 18px; position: relative; z-index: 1; }
    .rh-logo {
        width: 64px; height: 64px;
        border-radius: 16px;
        background: linear-gradient(135deg, #00d4aa, #7b61ff);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.8rem; font-weight: 800; color: #fff;
        box-shadow: 0 8px 26px rgba(0,212,170,0.35);
        flex-shrink: 0;
    }
    .rh-title {
        font-size: 1.65rem;
        font-weight: 800;
        color: #e8eaf6;
        letter-spacing: 0.3px;
        line-height: 1.1;
    }
    .rh-sub {
        margin-top: 4px;
        font-size: 0.82rem;
        color: #8892b0;
        letter-spacing: 0.6px;
    }
    .rh-mood {
        margin-left: auto;
        display: flex; align-items: center; gap: 8px;
        font-size: 0.85rem; font-weight: 700;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(0,212,170,0.12);
        border: 1px solid rgba(0,212,170,0.35);
        white-space: nowrap;
    }
    .rh-mood-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #00d4aa;
        animation: rhPulse 2s ease-in-out infinite;
    }
    .rh-kpis {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-top: 18px;
        position: relative; z-index: 1;
    }
    .rh-kpi {
        padding: 14px 16px;
        border-radius: 12px;
        background: rgba(10,14,39,0.65);
        border: 1px solid rgba(0,212,170,0.18);
        animation: rhFadeIn .5s ease-out;
        transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }
    .rh-kpi:hover {
        transform: translateY(-3px);
        border-color: rgba(0,212,170,0.5);
        box-shadow: 0 10px 26px rgba(0,212,170,0.22);
    }
    .rh-kpi-label {
        font-size: 0.68rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 700;
    }
    .rh-kpi-value {
        margin-top: 4px;
        font-size: 1.5rem;
        font-weight: 800;
        color: #00d4aa;
        line-height: 1.1;
    }
    .rh-kpi-note {
        margin-top: 2px;
        font-size: 0.7rem;
        color: #6b7490;
    }
    .rh-activity {
        margin-top: 18px;
        padding: 16px 20px;
        border-radius: 14px;
        background: rgba(10,14,39,0.55);
        border: 1px solid rgba(123,97,255,0.22);
        position: relative; z-index: 1;
    }
    .rh-activity-title {
        font-size: 0.78rem;
        font-weight: 800;
        color: #e8eaf6;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .rh-act-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 6px 0;
        border-bottom: 1px dashed rgba(255,255,255,0.05);
        font-size: 0.82rem;
    }
    .rh-act-item:last-child { border-bottom: none; }
    .rh-act-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #7b61ff;
        margin-right: 10px;
        display: inline-block;
    }
    .rh-act-actor { color: #e8eaf6; font-weight: 700; }
    .rh-act-msg { color: #a8b2d1; margin-left: 8px; }
    .rh-act-when { color: #6b7490; font-size: 0.72rem; }
    .rh-empty {
        color: #8892b0;
        font-size: 0.8rem;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)
    st.session_state["_rich_header_done"] = True


def render(owner_name="Swaminathan", pending=0, total_orders=0, approved=0, pending_value=0, unread=0):
    inject_css()

    mood_icon, mood_text, mood_color = _mood(pending, unread)
    now = datetime.now()
    greeting = "Good morning" if now.hour < 12 else ("Good afternoon" if now.hour < 17 else "Good evening")
    notifs = _read_notifs(5)

    activity_rows = []
    if not notifs:
        activity_rows.append('<div class="rh-empty">No recent activity</div>')
    else:
        for n in notifs:
            actor = n.get("actor_name") or n.get("actor_id") or "System"
            msg = n.get("message", "")
            ago = _time_ago(n.get("ts", ""))
            activity_rows.append(
                f'<div class="rh-act-item">'
                f'<div><span class="rh-act-dot"></span>'
                f'<span class="rh-act-actor">{actor}</span>'
                f'<span class="rh-act-msg">{msg}</span></div>'
                f'<div class="rh-act-when">{ago}</div>'
                f'</div>'
            )

    hero_html = (
        '<div class="rh-hero">'
        '<div class="rh-hero-row">'
        '<div class="rh-logo">💊</div>'
        '<div>'
        f'<div class="rh-title">👋 {greeting}, {owner_name}</div>'
        f'<div class="rh-sub">Owner Dashboard · {now.strftime("%A, %d %b %Y · %I:%M %p")}</div>'
        '</div>'
        f'<div class="rh-mood"><span class="rh-mood-dot"></span>{mood_icon} {mood_text}</div>'
        '</div>'

        '<div class="rh-kpis">'
        f'<div class="rh-kpi"><div class="rh-kpi-label">Pending Orders</div>'
        f'<div class="rh-kpi-value">{pending}</div>'
        f'<div class="rh-kpi-note">awaiting action</div></div>'

        f'<div class="rh-kpi"><div class="rh-kpi-label">Total Orders</div>'
        f'<div class="rh-kpi-value">{total_orders}</div>'
        f'<div class="rh-kpi-note">all time</div></div>'

        f'<div class="rh-kpi"><div class="rh-kpi-label">Approved</div>'
        f'<div class="rh-kpi-value">{approved}</div>'
        f'<div class="rh-kpi-note">this period</div></div>'

        f'<div class="rh-kpi"><div class="rh-kpi-label">Pending Value</div>'
        f'<div class="rh-kpi-value">₹{pending_value:,.0f}</div>'
        f'<div class="rh-kpi-note">in queue</div></div>'
        '</div>'

        '<div class="rh-activity">'
        '<div class="rh-activity-title">🔔 Recent Activity</div>'
        + "".join(activity_rows) +
        '</div>'

        '</div>'
    )

    st.markdown(hero_html, unsafe_allow_html=True)
