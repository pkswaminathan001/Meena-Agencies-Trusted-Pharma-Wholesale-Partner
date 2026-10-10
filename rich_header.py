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
            # If message already starts with actor name, don't duplicate
            if msg.lower().startswith(actor.lower()):
                display = msg
            else:
                display = actor + " · " + msg
            activity_rows.append(
                f'<div class="rh-act-item">'
                f'<div><span class="rh-act-dot"></span>'
                f'<span class="rh-act-msg">{display}</span></div>'
                f'<div class="rh-act-when">{ago}</div>'
                f'</div>'
            )

    hero_html = (
        '<div class="rh-hero">'
        '<div class="rh-hero-row">'
        '<div class="rh-logo"><img src="data:image/png;base64,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" alt="Meena Agencies" style="width:100%;height:100%;object-fit:contain;border-radius:12px;" /></div>'
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
