"""
animations.py — Visual animation engine for PharmaMind.
Adds CSS animations, glow, pulse, fade-in, rolling counters, and micro-interactions.
"""
import streamlit as st

# ────────────────────────────────────────────────
# INJECT GLOBAL CSS — call once per page
# ────────────────────────────────────────────────
def inject_animations():
    """Inject all CSS animations. Call once at top of app."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    /* ─── Base ─── */
    * { font-family: 'Inter', sans-serif; }

    /* ─── Animated gradient background ─── */
    .stApp {
        background: linear-gradient(-45deg, #0a0e27, #1a1f3a, #0f1428, #151a35);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ─── Fade-in-up for cards ─── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.9); }
        to   { opacity: 1; transform: scale(1); }
    }

    /* ─── Pulse glow for important metrics ─── */
    @keyframes pulseGlow {
        0%   { box-shadow: 0 0 0 0 rgba(0,212,255,0.4); }
        70%  { box-shadow: 0 0 0 20px rgba(0,212,255,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,212,255,0); }
    }
    @keyframes pulseGreen {
        0%   { box-shadow: 0 0 0 0 rgba(0,212,122,0.5); }
        70%  { box-shadow: 0 0 0 15px rgba(0,212,122,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,212,122,0); }
    }
    @keyframes pulseRed {
        0%   { box-shadow: 0 0 0 0 rgba(255,77,109,0.5); }
        70%  { box-shadow: 0 0 0 15px rgba(255,77,109,0); }
        100% { box-shadow: 0 0 0 0 rgba(255,77,109,0); }
    }

    /* ─── Bounce ─── */
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-8px); }
    }

    /* ─── Spin ─── */
    @keyframes spin {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }

    /* ─── Shimmer for loading ─── */
    @keyframes shimmer {
        0%   { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    /* ─── Animated metric card ─── */
    .anim-card {
        background: rgba(26,31,58,0.75);
        border: 1px solid rgba(123,97,255,0.3);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        animation: fadeInUp 0.6s ease-out;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .anim-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0,212,255,0.6);
        box-shadow: 0 12px 30px rgba(0,212,255,0.15);
    }

    /* ─── Metric value with glow ─── */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b61ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeIn 0.8s ease-out;
    }

    /* ─── Status badges with pulse ─── */
    .badge-green {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(0,212,122,0.15);
        border: 1px solid #00d47a;
        border-radius: 20px;
        color: #00d47a;
        font-size: 0.75rem;
        font-weight: 600;
        animation: pulseGreen 2s infinite;
    }
    .badge-red {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(255,77,109,0.15);
        border: 1px solid #ff4d6d;
        border-radius: 20px;
        color: #ff4d6d;
        font-size: 0.75rem;
        font-weight: 600;
        animation: pulseRed 2s infinite;
    }
    .badge-blue {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(0,212,255,0.15);
        border: 1px solid #00d4ff;
        border-radius: 20px;
        color: #00d4ff;
        font-size: 0.75rem;
        font-weight: 600;
        animation: pulseGlow 2s infinite;
    }
    .badge-amber {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(255,181,71,0.15);
        border: 1px solid #ffb547;
        border-radius: 20px;
        color: #ffb547;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* ─── Animated buttons ─── */
    .stButton > button {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,212,255,0.25);
        border-color: #00d4ff !important;
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ─── Tabs with animated underline ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(26,31,58,0.4);
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0,212,255,0.08);
        transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,97,255,0.15)) !important;
        box-shadow: 0 4px 12px rgba(0,212,255,0.15);
    }

    /* ─── Metric tile (Streamlit native) ─── */
    [data-testid="stMetric"] {
        background: rgba(26,31,58,0.6);
        border: 1px solid rgba(123,97,255,0.25);
        border-radius: 12px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0,212,255,0.5);
        transform: translateY(-2px);
    }
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        background: linear-gradient(90deg, #00d4ff, #7b61ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ─── Progress bars ─── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #7b61ff);
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ─── Dataframe hover ─── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        animation: fadeIn 0.7s ease-out;
    }

    /* ─── Expander animation ─── */
    .streamlit-expanderHeader {
        transition: all 0.2s ease;
        border-radius: 10px;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(0,212,255,0.06);
    }

    /* ─── Alerts ─── */
    .stAlert {
        border-radius: 12px;
        animation: fadeInUp 0.4s ease-out;
    }

    /* ─── Hero title ─── */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff 0%, #7b61ff 50%, #00d47a 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s linear infinite;
        margin-bottom: 0.3rem;
    }

    /* ─── Success balloon effect ─── */
    .success-pulse {
        animation: pulseGreen 2s infinite;
        border-radius: 12px;
    }

    /* ─── Notification slide-in ─── */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(100px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    .notification {
        animation: slideInRight 0.5s ease-out;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #00d4ff;
        background: rgba(0,212,255,0.08);
    }

    /* ─── Heartbeat for live indicators ─── */
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.15); opacity: 0.8; }
    }
    .live-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00d47a;
        animation: heartbeat 1.5s infinite;
        margin-right: 6px;
        vertical-align: middle;
    }

    /* ─── Icon bounce ─── */
    .icon-bounce {
        display: inline-block;
        animation: bounce 2s infinite;
    }

    /* ─── Stagger delays for lists ─── */
    .stagger-1 { animation-delay: 0.1s; }
    .stagger-2 { animation-delay: 0.2s; }
    .stagger-3 { animation-delay: 0.3s; }
    .stagger-4 { animation-delay: 0.4s; }
    .stagger-5 { animation-delay: 0.5s; }
    </style>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# ANIMATED WIDGETS
# ────────────────────────────────────────────────
def animated_metric(label, value, delta="", color="blue", icon="📊"):
    """Return HTML for an animated KPI card."""
    color_map = {
        "blue":   ("#00d4ff", "rgba(0,212,255,0.15)"),
        "green":  ("#00d47a", "rgba(0,212,122,0.15)"),
        "red":    ("#ff4d6d", "rgba(255,77,109,0.15)"),
        "amber":  ("#ffb547", "rgba(255,181,71,0.15)"),
        "purple": ("#7b61ff", "rgba(123,97,255,0.15)"),
    }
    c, bg = color_map.get(color, color_map["blue"])
    return f'''
    <div class="anim-card" style="border-left: 4px solid {c}; text-align: center;">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{icon}</div>
        <div style="color:#8892b0; font-size:0.75rem; text-transform:uppercase; letter-spacing:1.5px;">{label}</div>
        <div style="font-size: 2rem; font-weight: 800; color: {c}; margin: 0.4rem 0;">{value}</div>
        {f'<div style="color:{c}; font-size:0.8rem;">{delta}</div>' if delta else ''}
    </div>
    '''


def live_badge(text):
    """Pulsing live indicator."""
    return f'<span class="live-dot"></span><span style="font-size:0.8rem; color:#00d47a; font-weight:600;">{text}</span>'


def status_badge(text, status="blue"):
    """Colored pulsing badge."""
    cls = {"green":"badge-green","red":"badge-red","blue":"badge-blue","amber":"badge-amber"}.get(status, "badge-blue")
    return f'<span class="{cls}">{text}</span>'


def hero(text, subtitle=""):
    """Animated hero title."""
    html = f'<div class="hero-title">{text}</div>'
    if subtitle:
        html += f'<div style="color:#8892b0; margin-bottom:1.5rem;">{subtitle}</div>'
    return html


def animated_card(content, delay=0, accent="blue"):
    """Wrap content in an animated card."""
    color_map = {"blue":"#00d4ff","green":"#00d47a","red":"#ff4d6d","amber":"#ffb547","purple":"#7b61ff"}
    c = color_map.get(accent, "#00d4ff")
    return f'<div class="anim-card stagger-{delay+1}" style="border-left: 4px solid {c};">{content}</div>'
