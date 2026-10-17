"""
ui.py — Meena Agencies responsive design system.
One file. All devices. No more CSS wars.

Call ui.inject() once, right after st.set_page_config().
Call ui.brand_header() at the top of any page.
Call ui.hamburger(retailer=..., on_signout=...) for the menu.
"""
import streamlit as st
import sidebar_toggle


# ══════════════════════════════════════════════════════════
# DESIGN TOKENS — change colors here, they update everywhere
# ══════════════════════════════════════════════════════════
_TOKENS = """
:root {
    /* Brand */
    --brand:        #0B3B8C;
    --brand-2:      #1560BD;
    --brand-deep:   #072A66;
    --brand-soft:   #E8EFFB;

    /* Accent */
    --accent:       #F58220;
    --accent-2:     #FDB913;
    --accent-soft:  #FFF1E0;

    /* Semantic */
    --success:      #0E9F6E;
    --success-soft: #E6F7F1;
    --danger:       #C81E1E;
    --danger-soft:  #FDE8E8;
    --warn:         #D97706;
    --warn-soft:    #FEF3C7;

    /* Neutrals */
    --bg:           #F4F7FC;
    --surface:      #FFFFFF;
    --surface-alt:  #F8FAFC;
    --border:       #E2E8F0;
    --text:         #1A1A2E;
    --muted:        #64748B;

    /* Spacing (4px grid) */
    --s-1:  4px;
    --s-2:  8px;
    --s-3:  12px;
    --s-4:  16px;
    --s-5:  20px;
    --s-6:  24px;
    --s-8:  32px;
    --s-10: 40px;

    /* Radius */
    --r-sm: 8px;
    --r-md: 12px;
    --r-lg: 16px;

    /* Shadow */
    --sh-sm: 0 1px 3px rgba(11,59,140,.06);
    --sh-md: 0 4px 14px rgba(11,59,140,.08);
    --sh-lg: 0 12px 32px rgba(11,59,140,.12);
}
"""


_CSS = """
<style>
""" + _TOKENS + """
/* ══════════════════════════════════════════════════════════
   GLOBAL RESET
   ══════════════════════════════════════════════════════════ */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    background-image: none !important;
    color: var(--text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 system-ui, Roboto, "Helvetica Neue", sans-serif !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    -webkit-font-smoothing: antialiased !important;
}

/* The container width — fluid, capped at 1280px on desktop */
.block-container,
.main .block-container {
    max-width: 1280px !important;
    margin: 0 auto !important;
    padding: 1rem 1.25rem 2rem 1.25rem !important;
    background: transparent !important;
}
@media (max-width: 640px) {
    .block-container,
    .main .block-container {
        padding: .75rem .85rem 1.5rem .85rem !important;
    }
}
@media (min-width: 1600px) {
    .block-container {
        max-width: 1440px !important;
    }
}

[data-testid="stHeader"], [data-testid="stToolbar"] {
    display: none !important;
}
footer, #MainMenu { display: none !important; }

/* Kill Streamlit's own sidebar toggle */
button[data-testid="stBaseButton-headerNoPadding"],
button[kind="header"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ══════════════════════════════════════════════════════════
   TYPOGRAPHY — fluid scaling
   ══════════════════════════════════════════════════════════ */
h1 { font-size: clamp(22px, 4vw, 28px) !important; font-weight: 800 !important;
     color: var(--text) !important; letter-spacing: -.4px !important; margin: 0 0 4px 0 !important; }
h2 { font-size: clamp(19px, 3.4vw, 24px) !important; font-weight: 800 !important;
     color: var(--text) !important; letter-spacing: -.3px !important; }
h3 { font-size: clamp(16px, 2.8vw, 20px) !important; font-weight: 700 !important; color: var(--text) !important; }
h4 { font-size: 16px !important; font-weight: 700 !important; color: var(--text) !important; }

p, span, label, div, li, td, th { color: var(--text); font-size: 15px; }
small, .stCaption, [data-testid="stCaptionContainer"] * {
    color: var(--muted) !important;
    font-size: 13px !important;
}

/* ══════════════════════════════════════════════════════════
   BRAND HEADER — 56px, sticky, works on all screens
   ══════════════════════════════════════════════════════════ */
.mk-brand-header {
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 10px 18px !important;
    margin: -1rem -1.25rem 18px -1.25rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    box-shadow: 0 1px 3px rgba(11,59,140,.04) !important;
}
.mk-brand-header .logo {
    width: 34px; height: 34px;
    border-radius: 8px;
    background: linear-gradient(135deg, #0B3B8C, #1560BD);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 900; font-size: 16px;
    flex-shrink: 0;
}
.mk-brand-header .text { flex: 1; min-width: 0; }
.mk-brand-header .name {
    font-size: 15px; font-weight: 900;
    color: var(--text);
    letter-spacing: -.2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    line-height: 1.15;
}
.mk-brand-header .tagline {
    font-size: 11px; font-weight: 500;
    color: var(--muted);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    line-height: 1.2;
}
.mk-brand-header .actions {
    display: flex; gap: 6px; flex-shrink: 0;
}

@media (max-width: 640px) {
    .mk-brand-header {
        padding: 8px 12px !important;
        margin: -.75rem -.85rem 14px -.85rem !important;
    }
    .mk-brand-header .tagline { display: none; }
    .mk-brand-header .name { font-size: 14px; }
}

/* ══════════════════════════════════════════════════════════
   HERO — responsive gradient banner
   ══════════════════════════════════════════════════════════ */
.corp-hero {
    background: linear-gradient(120deg, #072A66 0%, #0B3B8C 40%, #1560BD 75%, #F58220 130%) !important;
    border-radius: var(--r-lg) !important;
    padding: clamp(20px, 4vw, 32px) clamp(18px, 4vw, 34px) !important;
    margin: 0 0 20px 0 !important;
    color: #FFFFFF !important;
    box-shadow: 0 12px 32px rgba(11,59,140,.20) !important;
    overflow: hidden !important;
    position: relative !important;
}
.corp-hero * { color: #FFFFFF !important; }
.corp-hero .corp-eyebrow {
    display: inline-block !important;
    background: rgba(255,255,255,0.18) !important;
    color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
    padding: 5px 12px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(6px) !important;
}
.corp-hero .corp-title {
    color: #FFFFFF !important;
    font-size: clamp(26px, 5vw, 40px) !important;
    font-weight: 900 !important;
    letter-spacing: -1px !important;
    line-height: 1.1 !important;
    margin: 4px 0 10px 0 !important;
    text-shadow: 0 2px 14px rgba(0,0,0,.18) !important;
}
.corp-hero .corp-title-accent {
    color: #FDB913 !important;
}
.corp-hero .corp-subtitle {
    color: rgba(255,255,255,0.94) !important;
    font-size: clamp(13px, 2.4vw, 15px) !important;
    line-height: 1.55 !important;
    max-width: 720px !important;
    margin: 0 0 12px 0 !important;
}
.corp-hero .corp-meta-row {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)) !important;
    gap: 14px 24px !important;
    margin-top: 16px !important;
    padding-top: 16px !important;
    border-top: 1px solid rgba(255,255,255,0.22) !important;
}
.corp-hero .corp-meta-item {
    color: rgba(255,255,255,0.82) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.corp-hero .corp-meta-item strong {
    display: block !important;
    color: #FFFFFF !important;
    font-size: clamp(15px, 2.8vw, 18px) !important;
    font-weight: 800 !important;
    letter-spacing: -.2px !important;
    text-transform: none !important;
    margin-bottom: 3px !important;
}

/* ══════════════════════════════════════════════════════════
   SECTIONS
   ══════════════════════════════════════════════════════════ */
.corp-section {
    margin: 24px 0 12px 0 !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid var(--border) !important;
}
.corp-section-title {
    color: var(--text) !important;
    font-size: clamp(16px, 2.8vw, 19px) !important;
    font-weight: 800 !important;
    letter-spacing: -.2px !important;
    margin-bottom: 3px !important;
}
.corp-section-sub {
    color: var(--muted) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ══════════════════════════════════════════════════════════
   METRICS — auto-fit grid, always at least 2 per row on mobile
   ══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    padding: clamp(12px, 2.4vw, 18px) clamp(12px, 2.4vw, 20px) !important;
    box-shadow: var(--sh-sm) !important;
    position: relative !important;
    overflow: hidden !important;
    min-height: 78px !important;
}
[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--brand), var(--brand-2));
}
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"]::before {
    background: linear-gradient(90deg, var(--accent), var(--accent-2));
}
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"]::before {
    background: linear-gradient(90deg, var(--success), #34D399);
}
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetric"]::before {
    background: linear-gradient(90deg, var(--brand-2), var(--brand));
}
[data-testid="stMetricLabel"] * {
    color: var(--muted) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
}
[data-testid="stMetricValue"] * {
    color: var(--brand) !important;
    font-weight: 800 !important;
    font-size: clamp(19px, 3.6vw, 26px) !important;
    letter-spacing: -.5px !important;
}

/* ══════════════════════════════════════════════════════════
   BUTTONS — touch-friendly, 44px min on mobile
   ══════════════════════════════════════════════════════════ */
.stButton > button,
.stDownloadButton > button {
    border-radius: var(--r-sm) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 10px 18px !important;
    min-height: 44px !important;
    background: var(--surface) !important;
    color: var(--brand) !important;
    border: 1.5px solid var(--brand) !important;
    box-shadow: none !important;
    transition: all .15s ease !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--brand-soft) !important;
}
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: var(--brand) !important;
    color: #FFFFFF !important;
    border-color: var(--brand) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--brand-deep) !important;
}

/* ══════════════════════════════════════════════════════════
   INPUTS — bigger on mobile for thumb taps
   ══════════════════════════════════════════════════════════ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input,
div[data-baseweb="input"],
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    font-size: 15px !important;
    min-height: 44px !important;
    padding: 10px 12px !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(11,59,140,.12) !important;
    outline: none !important;
}

/* ══════════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
    border-bottom: 2px solid var(--border) !important;
    overflow-x: auto !important;
}
.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    padding: 0 14px !important;
    border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
    color: var(--brand) !important;
    background: var(--surface) !important;
    border-bottom: 3px solid var(--brand) !important;
}

/* ══════════════════════════════════════════════════════════
   EXPANDERS
   ══════════════════════════════════════════════════════════ */
details, details > summary, .streamlit-expanderHeader {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-left: 4px solid var(--brand) !important;
    border-radius: var(--r-sm) !important;
    padding: 10px 14px !important;
    font-weight: 700 !important;
}

/* ══════════════════════════════════════════════════════════
   TABLES — horizontal scroll on mobile
   ══════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    overflow: hidden !important;
    box-shadow: var(--sh-sm) !important;
}
[data-testid="stDataFrame"] thead th {
    background: var(--brand-soft) !important;
    color: var(--brand) !important;
    font-weight: 800 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: .4px !important;
    padding: 10px 8px !important;
}
[data-testid="stDataFrame"] tbody td {
    color: var(--text) !important;
    font-size: 13.5px !important;
    padding: 10px 8px !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ══════════════════════════════════════════════════════════
   POPOVER PANEL (hamburger menu)
   ══════════════════════════════════════════════════════════ */
div[data-testid="stPopoverBody"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    box-shadow: 0 20px 50px rgba(11,59,140,.22) !important;
    padding: 14px !important;
    min-width: 260px !important;
    max-width: 300px !important;
}
div[data-testid="stPopoverBody"] * { color: var(--text) !important; }
div[data-testid="stPopoverBody"] .stButton > button {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    padding: 10px 12px !important;
    margin-bottom: 2px !important;
    min-height: 40px !important;
    font-weight: 600 !important;
}
div[data-testid="stPopoverBody"] .stButton > button:hover {
    background: var(--brand-soft) !important;
    color: var(--brand) !important;
}

/* ══════════════════════════════════════════════════════════
   FLOATING HAMBURGER — pinned to left edge
   ══════════════════════════════════════════════════════════ */
div[data-testid="stPopover"] {
    position: fixed !important;
    top: 50vh !important;
    left: 0 !important;
    transform: translateY(-50%) !important;
    z-index: 999998 !important;
}
div[data-testid="stPopover"] > button {
    background: var(--brand) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 12px 10px 12px 12px !important;
    font-size: 16px !important;
    font-weight: 900 !important;
    box-shadow: 3px 4px 14px rgba(11,59,140,.28) !important;
    opacity: .85 !important;
    min-width: 40px !important;
    min-height: 42px !important;
    transition: all .2s ease !important;
}
div[data-testid="stPopover"] > button:hover {
    opacity: 1 !important;
    background: var(--brand-deep) !important;
}

@media (max-width: 640px) {
    div[data-testid="stPopover"] {
        top: 55vh !important;
    }
}

/* ══════════════════════════════════════════════════════════
   SCROLLBAR
   ══════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--surface-alt); }
::-webkit-scrollbar-thumb { background: #B8CDF0; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #8FB1E6; }



</style>
"""


def inject():
    """Call once, right after st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def brand_header(company="Meena Agencies",
                 tagline="Trusted Pharma Wholesale Partner",
                 logo_text="M",
                 right_html=""):
    """Thin brand header, sticky at the top. 56px tall."""
    st.markdown(f"""
    <div class="mk-brand-header">
        <div class="logo">{logo_text}</div>
        <div class="text">
            <div class="name">{company}</div>
            <div class="tagline">{tagline}</div>
        </div>
        <div class="actions">{right_html}</div>
    </div>
    """, unsafe_allow_html=True)


def hero(title, accent, subtitle, eyebrow="", meta=None):
    """Responsive gradient hero."""
    meta = meta or []
    meta_html = ""
    if meta:
        meta_html = '<div class="corp-meta-row">'
        for item in meta:
            meta_html += f'<div class="corp-meta-item"><strong>{item["value"]}</strong>{item["label"]}</div>'
        meta_html += '</div>'

    st.markdown(f"""
    <div class="corp-hero">
        <div class="corp-hero-inner">
            {f'<div class="corp-eyebrow">{eyebrow}</div>' if eyebrow else ''}
            <h1 class="corp-title">{title} <span class="corp-title-accent">{accent}</span></h1>
            <p class="corp-subtitle">{subtitle}</p>
            {meta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section(title, subtitle=""):
    """Section header with underline."""
    st.markdown(f"""
    <div class="corp-section">
        <div class="corp-section-title">{title}</div>
        <div class="corp-section-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# NATIVE SIDEBAR — reliable on every device
# ══════════════════════════════════════════════════════════

_SIDEBAR_CSS = """
<style>
/* ══════════════════════════════════════════════════════════
   MINIMAL SIDEBAR STYLING — only what's needed.
   Do NOT touch layout or visibility of containers.
   ══════════════════════════════════════════════════════════ */

/* Sidebar background */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

/* Profile card */
.sb-profile {
    background: linear-gradient(120deg, #072A66 0%, #0B3B8C 40%, #1560BD 100%) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    margin: 0 0 16px 0 !important;
    color: #FFFFFF !important;
}
.sb-profile * { color: #FFFFFF !important; }
.sb-profile .tag {
    display: inline-block !important;
    background: rgba(255,255,255,.20) !important;
    font-size: 10px !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 3px 10px !important;
    border-radius: 999px !important;
    margin-bottom: 8px !important;
}
.sb-profile .who {
    font-size: 16px !important;
    font-weight: 900 !important;
    letter-spacing: -.2px !important;
    line-height: 1.15 !important;
    margin-bottom: 3px !important;
}
.sb-profile .what {
    font-size: 12px !important;
    font-weight: 500 !important;
    opacity: .92 !important;
}

/* Section labels */
.sb-label {
    color: #64748B !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    margin: 14px 0 6px 0 !important;
}

/* Buttons — light touch, no layout overrides */
section[data-testid="stSidebar"] .stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #E8EFFB !important;
    color: #0B3B8C !important;
    border-color: #0B3B8C !important;
}

/* Sign Out — red accent */
.sb-signout button,
section[data-testid="stSidebar"] .sb-signout .stButton > button {
    background: #FDE8E8 !important;
    color: #C81E1E !important;
    font-weight: 800 !important;
    border-color: #FDE8E8 !important;
}
section[data-testid="stSidebar"] .sb-signout .stButton > button:hover {
    background: #C81E1E !important;
    color: #FFFFFF !important;
    border-color: #C81E1E !important;
}
</style>

"""

# ── FORCE sidebar visible ──
_FORCE_SIDEBAR_CSS = """
<style>
/* Kill anything hiding the sidebar */
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    min-width: 240px !important;
    width: 240px !important;
    transform: none !important;
}
/* Show the collapse/expand control */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}
/* Sidebar buttons look clean */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    margin-bottom: 4px !important;
    background: transparent !important;
    border: 1px solid rgba(0,212,255,0.20) !important;
    border-radius: 8px !important;
    color: #e8eaf6 !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,0.10) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
}
</style>
"""


def enable_sidebar():
    """Turn on the native sidebar + style it."""
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)


def sidebar_menu(retailer=None, on_signout=None, selected_page=None):
    """Compact collapsible sidebar — no guard, always renders."""
    if not st.session_state.get("_sb_open", False):
        return
    with st.sidebar:
        st.markdown("### 💊 Meena")
        if retailer:
            st.caption(f"{retailer.get('shop','')}")
            st.caption(f"`{retailer.get('id','')}`")
        st.markdown("---")

        if retailer:
            if st.button("🏠  Home",       key="sb_home_v3",   use_container_width=True):
                st.session_state.pop("category", None); st.rerun()
            if st.button("📦  Categories", key="sb_cat_v3",    use_container_width=True):
                st.session_state["category"] = None; st.rerun()
            if st.button("🛒  Cart",       key="sb_cart_v3",   use_container_width=True):
                st.rerun()
            if st.button("📜  Orders",     key="sb_orders_v3", use_container_width=True):
                st.rerun()
            if st.button("👤  Account",    key="sb_acct_v3",   use_container_width=True):
                st.session_state["_show_account"] = True; st.rerun()

            st.markdown("---")
            if on_signout and st.button("🚪  Sign Out", key="sb_signout_v3", use_container_width=True):
                on_signout()
        else:
            if st.button("🏠  Dashboard", key="sb_owner_home_v3", use_container_width=True):
                st.rerun()


