"""
notification_ui.py — Notifications bell + panel + welcome banner.
Uses notifications.py as data layer. Theme: #00d4aa cyan, #7b61ff purple.
"""
import streamlit as st
from datetime import datetime
import notifications


def _time_ago(iso_str):
    try:
        then = datetime.fromisoformat(iso_str)
        secs = int((datetime.now() - then).total_seconds())
        if secs < 60:      return "just now"
        if secs < 3600:    return str(secs // 60) + " min ago"
        if secs < 86400:   return str(secs // 3600) + " hr ago"
        if secs < 604800:  return str(secs // 86400) + "d ago"
        return then.strftime("%d %b")
    except Exception:
        return "-"


def _icon_for(n_type):
    return {
        "staff_login":    "\U0001F9D1\u200D\U0001F4BC",
        "staff_action":   "\U0001F9D1\u200D\U0001F4BC",
        "order_placed":   "\U0001F6D2",
        "order_approved": "\u2705",
        "order_rejected": "\u274C",
        "message":        "\U0001F4AC",
        "low_stock":      "\u26A0\uFE0F",
        "expired":        "\U0001F534",
        "backup":         "\U0001F4BE",
        "system":         "\u2699\uFE0F",
    }.get(n_type, "\U0001F514")


def _severity_color(sev):
    return {"info": "#00d4aa", "warning": "#ffb547", "critical": "#ff4d6d"}.get(sev, "#8892b0")


def inject_css():
    if st.session_state.get("_notif_css_done"):
        return
    st.markdown("""
    <style>
    .ma-bell {
        position: relative; display: inline-flex;
        align-items: center; justify-content: center;
        width: 44px; height: 44px; border-radius: 12px;
        background: linear-gradient(135deg, #00d4aa, #7b61ff);
        color: #fff; font-size: 1.3rem; cursor: pointer;
        transition: transform .15s ease, box-shadow .15s ease;
        box-shadow: 0 4px 14px rgba(0,212,170,0.35);
    }
    .ma-bell:hover { transform: scale(1.08); box-shadow: 0 8px 24px rgba(0,212,170,0.55); }
    .ma-bell-badge {
        position: absolute; top: -4px; right: -4px;
        min-width: 20px; height: 20px; padding: 0 5px;
        border-radius: 10px; background: #ff4d6d; color: #fff;
        font-size: 0.7rem; font-weight: 800;
        display: flex; align-items: center; justify-content: center;
        animation: ma-pulse-badge 2s ease-in-out infinite;
    }
    @keyframes ma-pulse-badge {
        0%,100% { box-shadow: 0 0 0 0 rgba(255,77,109,0.7); }
        50%     { box-shadow: 0 0 0 6px rgba(255,77,109,0); }
    }
    .ma-notif-panel {
        position: fixed; top: 0; right: 0; width: 400px; height: 100vh;
        background: linear-gradient(180deg, #0d1130, #0a0e27);
        border-left: 1px solid rgba(0,212,170,0.3);
        box-shadow: -12px 0 40px rgba(0,0,0,0.6);
        z-index: 999999; overflow-y: auto;
        animation: ma-slide-in .25s ease-out;
    }
    @keyframes ma-slide-in {
        from { transform: translateX(100%); }
        to   { transform: translateX(0); }
    }
    .ma-notif-header {
        padding: 20px 22px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        display: flex; justify-content: space-between; align-items: center;
    }
    .ma-notif-header h3 { margin: 0; font-size: 1.1rem; color: #e8eaf6; font-weight: 800; }
    .ma-notif-item {
        padding: 14px 22px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        display: flex; gap: 12px;
        transition: background .15s;
    }
    .ma-notif-item:hover { background: rgba(0,212,170,0.05); }
    .ma-notif-icon {
        width: 36px; height: 36px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; flex-shrink: 0;
        background: rgba(0,212,170,0.12);
        border: 1px solid rgba(0,212,170,0.25);
    }
    .ma-notif-body { flex: 1; min-width: 0; }
    .ma-notif-actor { color: #e8eaf6; font-weight: 700; font-size: 0.85rem; margin-bottom: 2px; }
    .ma-notif-msg   { color: #a8b2d1; font-size: 0.78rem; margin-bottom: 4px; }
    .ma-notif-meta  { color: #6b7490; font-size: 0.68rem; display: flex; gap: 10px; }
    .ma-notif-unread-dot { width: 8px; height: 8px; border-radius: 50%; background: #00d4aa; flex-shrink: 0; margin-top: 14px; }
    .ma-notif-empty { padding: 60px 22px; text-align: center; color: #8892b0; font-size: 0.85rem; }
    .ma-welcome {
        padding: 18px 22px; margin: 8px 0 18px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(0,212,170,0.10), rgba(123,97,255,0.08));
        border: 1px solid rgba(0,212,170,0.25);
    }
    .ma-welcome-title { font-size: 1.15rem; color: #e8eaf6; font-weight: 800; margin-bottom: 6px; }
    .ma-welcome-meta { font-size: 0.78rem; color: #8892b0; letter-spacing: 0.5px; }
    .ma-welcome-summary {
        margin-top: 10px; padding-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.06);
        font-size: 0.82rem; color: #a8b2d1;
    }
    </style>
    """, unsafe_allow_html=True)
    st.session_state["_notif_css_done"] = True


def render_welcome(user_name="Swaminathan"):
    now = datetime.now()
    hour = now.hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
    unread = notifications.unread_count()
    if unread == 0:
        summary = "No new events since your last visit."
    else:
        plural = "s" if unread != 1 else ""
        summary = "You have <b style='color:#00d4aa'>" + str(unread) + "</b> new event" + plural + " since your last visit."
    st.markdown(
        '<div class="ma-welcome">'
        '<div class="ma-welcome-title">\U0001F44B ' + greeting + ', ' + user_name + '</div>'
        '<div class="ma-welcome-meta">Today: ' + now.strftime('%A, %d %b %Y') + ' &middot; ' + now.strftime('%I:%M %p') + '</div>'
        '<div class="ma-welcome-summary">' + summary + '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def render_bell_strip(title_html, user_name="Swaminathan"):
    """
    Render header row: title | bell | user badge | sign out.
    Returns 'bell' if bell clicked, 'signout' if sign-out clicked, else None.
    """
    inject_css()
    unread = notifications.unread_count()
    badge = '<span class="ma-bell-badge">' + str(unread) + '</span>' if unread > 0 else ""

    c1, c2, c3, c4 = st.columns([6, 1, 1.5, 1])
    with c1:
        st.markdown(title_html, unsafe_allow_html=True)
    with c2:
        # Single bell — Streamlit popover (no duplicate)
        with st.popover("\U0001F514 " + (str(unread) if unread > 0 else ""), use_container_width=True):
            _render_notif_popover_content()
        clicked = False
    with c3:
        st.markdown(
            '<div style="padding:10px 14px;border-radius:10px;'
            'background:rgba(0,212,170,0.08);'
            'border:1px solid rgba(0,212,170,0.2);'
            'color:#00d4aa;font-weight:700;font-size:0.8rem;text-align:center;">'
            '\U0001F464 ' + user_name + '</div>',
            unsafe_allow_html=True
        )
    with c4:
        sign_out = st.button("\U0001F6AA Sign Out", key="ma_signout_v1", use_container_width=True)

    if sign_out:
        return "signout"
    if clicked:
        return "bell"
    return None


def render_panel():
    items = notifications.get_recent(limit=30)

    if not items:
        rows_html = '<div class="ma-notif-empty">\U0001F515<br><br>No notifications yet</div>'
    else:
        parts = []
        for n in items:
            icon = _icon_for(n.get("type", ""))
            sev_color = _severity_color(n.get("severity", "info"))
            ago = _time_ago(n.get("ts", ""))
            actor = n.get("actor_name") or n.get("actor_id") or "System"
            msg = n.get("message", "")
            unread_dot = '<div class="ma-notif-unread-dot"></div>' if not n.get("read") else '<div style="width:8px"></div>'
            parts.append(
                '<div class="ma-notif-item">'
                + unread_dot +
                '<div class="ma-notif-icon" style="border-color:' + sev_color + '44;background:' + sev_color + '15;">' + icon + '</div>'
                '<div class="ma-notif-body">'
                '<div class="ma-notif-actor">' + actor + '</div>'
                '<div class="ma-notif-msg">' + msg + '</div>'
                '<div class="ma-notif-meta">'
                '<span>' + ago + '</span>'
                '<span>&middot;</span>'
                '<span style="color:' + sev_color + ';">' + n.get("type", "").replace("_", " ") + '</span>'
                '</div></div></div>'
            )
        rows_html = "".join(parts)

    st.markdown(
        '<div class="ma-notif-panel">'
        '<div class="ma-notif-header">'
        '<h3>\U0001F514 Notifications</h3>'
        '<div style="color:#8892b0;font-size:1.2rem;">\u2715</div>'
        '</div>'
        + rows_html +
        '</div>',
        unsafe_allow_html=True
    )
