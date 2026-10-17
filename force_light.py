"""
force_light.py — Mankind Pharma-inspired corporate theme.
Deep royal blue primary · Warm orange accent · Clean white surfaces
Call force_light.inject() once, right after st.set_page_config().
"""
import streamlit as st


_CSS = """
<style>
/* ══════════════════════════════════════════════════════════
   MANKIND PHARMA PALETTE
   ══════════════════════════════════════════════════════════ */
:root {
    --brand:         #0B3B8C;
    --brand-2:       #1560BD;
    --brand-soft:    #E8EFFB;
    --brand-deep:    #072A66;
    --accent:        #F58220;
    --accent-2:      #FDB913;
    --accent-soft:   #FFF1E0;
    --success:       #0E9F6E;
    --success-soft:  #E6F7F1;
    --warn:          #D97706;
    --warn-soft:     #FEF3C7;
    --danger:        #C81E1E;
    --danger-soft:   #FDE8E8;
    --bg:            #F4F7FC;
    --surface:       #FFFFFF;
    --border:        #E2E8F0;
    --text:          #1A1A2E;
    --muted:         #64748B;
    --radius:        10px;
    --radius-lg:     14px;
    --shadow-sm:     0 1px 3px rgba(11,59,140,.06);
    --shadow-md:     0 4px 14px rgba(11,59,140,.08);
    --shadow-lg:     0 12px 32px rgba(11,59,140,.12);
}

/* ══════════════ GLOBAL — always light ══════════════ */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 system-ui, Roboto, "Helvetica Neue", sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.main, .block-container { background: transparent !important; }
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ══════════════ TYPOGRAPHY ══════════════ */
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    font-weight: 800 !important;
    letter-spacing: -.3px !important;
}
h1 { font-size: 28px !important; }
h2 { font-size: 23px !important; }
h3 { font-size: 19px !important; }
h4 { font-size: 16px !important; }
p, span, label, div, li, td, th { color: var(--text); }
small, .stCaption, [data-testid="stCaptionContainer"] * {
    color: var(--muted) !important;
}

/* ══════════════ BUTTONS ══════════════ */
.stButton > button,
.stDownloadButton > button {
    border-radius: var(--radius) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 11px 20px !important;
    background: var(--surface) !important;
    color: var(--brand) !important;
    border: 1.5px solid var(--brand) !important;
    transition: all .15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--brand-soft) !important;
    transform: translateY(-1px);
    box-shadow: var(--shadow-md) !important;
}
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--brand) 0%, var(--brand-2) 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(11,59,140,.28) !important;
}
.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--brand-deep) 0%, var(--brand) 100%) !important;
    box-shadow: 0 8px 22px rgba(11,59,140,.35) !important;
}

/* ══════════════ INPUTS ══════════════ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="select"] {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-size: 14px !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(11,59,140,.12) !important;
    outline: none !important;
}
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] { background: var(--surface) !important; }
li[role="option"] { color: var(--text) !important; background: var(--surface) !important; }
li[role="option"]:hover { background: var(--brand-soft) !important; }

/* ══════════════ METRIC TILES ══════════════ */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 18px 20px !important;
    box-shadow: var(--shadow-md) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
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
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .6px;
}
[data-testid="stMetricValue"] * {
    color: var(--brand) !important;
    font-weight: 800 !important;
}

/* ══════════════ TABS ══════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
    border-bottom: 2px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    padding: 0 18px !important;
    border-radius: 10px 10px 0 0 !important;
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--brand) !important;
    background: var(--brand-soft) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--brand) !important;
    background: var(--surface) !important;
    border-bottom: 3px solid var(--brand) !important;
}

/* ══════════════ EXPANDERS ══════════════ */
details, details > summary,
.streamlit-expanderHeader {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-left: 4px solid var(--brand) !important;
    border-radius: var(--radius) !important;
    padding: 10px 14px !important;
    box-shadow: var(--shadow-sm) !important;
    font-weight: 700 !important;
}
details[open], details > summary:hover {
    border-left-color: var(--accent) !important;
    box-shadow: var(--shadow-md) !important;
}

/* ══════════════ TABLES ══════════════ */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stDataFrame"] thead th {
    background: linear-gradient(180deg, #F8FAFC, #EEF4FB) !important;
    color: var(--brand) !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    text-transform: uppercase;
    letter-spacing: .4px;
    border-bottom: 2px solid var(--brand) !important;
    padding: 13px 10px !important;
}
[data-testid="stDataFrame"] tbody td {
    color: var(--text) !important;
    font-size: 13.5px !important;
    padding: 11px 10px !important;
    border-bottom: 1px solid #F1F5F9 !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: #FAFCFF !important;
}

/* ══════════════ DIALOG / POPUP ══════════════ */
div[data-testid="stDialog"] > div,
div[role="dialog"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-lg) !important;
    border: 1px solid var(--border) !important;
    position: relative;
    overflow: hidden;
}
div[data-testid="stDialog"] > div::before,
div[role="dialog"] > div::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, var(--brand) 0%, var(--brand-2) 60%, var(--accent) 100%);
}
div[data-testid="stDialog"] *,
div[role="dialog"] * { color: var(--text) !important; }
div[data-testid="stDialog"] h1,
div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] h3,
div[role="dialog"] h1,
div[role="dialog"] h2,
div[role="dialog"] h3 {
    color: var(--brand) !important;
}

/* ══════════════ ALERTS ══════════════ */
div[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border-left-width: 5px !important;
    box-shadow: var(--shadow-sm) !important;
    background: var(--surface) !important;
}

/* ══════════════ PROGRESS + SCROLLBAR ══════════════ */
.stProgress > div > div { background: #E2E8F0 !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--brand), var(--brand-2)) !important;
}
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: #EEF4FB; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #B8CDF0, #8FB1E6);
    border-radius: 6px;
}

/* ══════════════ KILL DARK LEFTOVERS ══════════════ */
div[style*="background:#0"],
div[style*="background: #0"],
div[style*="background-color:#0"],
div[style*="background-color: #0"],
div[style*="background:#1"],
div[style*="background: #1"],
div[style*="background-color:#1"],
div[style*="background-color: #1"],
div[style*="background:rgb(0"],
div[style*="background: rgb(0"],
div[style*="background:rgba(0"],
div[style*="background: rgba(0"] {
    background: var(--surface) !important;
    color: var(--text) !important;
}
.card, .metric-card, .stat-card, .header-card,
[class*="card"], [class*="Card"] {
    background: var(--surface) !important;
    color: var(--text) !important;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none !important; }

/* ══════════════ MANKIND-STYLE HELPERS ══════════════ */
.mk-eyebrow {
    color: var(--accent) !important;
    font-size: 12px !important;
    font-weight: 800 !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}
.mk-hero-title {
    color: var(--text) !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    line-height: 1.15 !important;
    letter-spacing: -.5px !important;
    margin-bottom: 8px !important;
}
.mk-hero-sub {
    color: var(--muted) !important;
    font-size: 15px !important;
    line-height: 1.55 !important;
}
.mk-pill-blue, .mk-pill-orange, .mk-pill-green {
    display:inline-block;
    font-size: 11px !important;
    font-weight: 800 !important;
    letter-spacing: .8px !important;
    text-transform: uppercase !important;
    padding: 5px 12px !important;
    border-radius: 999px !important;
}
.mk-pill-blue   { background: var(--brand-soft) !important;   color: var(--brand) !important; }
.mk-pill-orange { background: var(--accent-soft) !important;  color: var(--accent) !important; }
.mk-pill-green  { background: var(--success-soft) !important; color: var(--success) !important; }

.mk-hero-banner {
    background: linear-gradient(120deg, #0B3B8C 0%, #1560BD 55%, #F58220 130%) !important;
    color: #ffffff !important;
    border-radius: 16px !important;
    padding: 26px 28px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 12px 32px rgba(11,59,140,.25) !important;
}
.mk-hero-banner h1,
.mk-hero-banner h2,
.mk-hero-banner h3,
.mk-hero-banner p,
.mk-hero-banner span,
.mk-hero-banner div { color: #ffffff !important; }
.mk-hero-banner .eyebrow {
    color: #FDB913 !important;
    font-size: 12px; font-weight: 800;
    letter-spacing: 1.4px; text-transform: uppercase;
    margin-bottom: 6px;
}

/* ══════════════ RESPONSIVE ══════════════ */
@media (max-width: 768px) {
    .block-container { padding: 1rem .8rem !important; }
    h1 { font-size: 22px !important; }
    h2 { font-size: 19px !important; }
    .stButton > button { padding: 10px 14px !important; font-size: 13px !important; }
    [data-testid="stMetric"] { padding: 12px !important; }
    .mk-hero-title { font-size: 24px !important; }
    .mk-hero-banner { padding: 18px 16px !important; border-radius: 12px !important; }
}

/* ══════════ HIDE STREAMLIT'S DEFAULT SIDEBAR TOGGLE ══════════ */
button[data-testid="stBaseButton-headerNoPadding"],
button[kind="header"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Reserve the top area for our own UI, no default header bar */
[data-testid="stHeader"] {
    display: none !important;
}
</style>
"""


def inject():
    """Inject the Mankind-inspired theme."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# NUCLEAR RULE — injected LAST, so nothing else can override.
# Uses body > * to beat every other selector on the page.
# ══════════════════════════════════════════════════════════
_NUCLEAR_CSS = """
<style>
/* Kill every dark !important on the app shell */
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stHeader"], .main, .block-container,
section.main, div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"] {
    background: #F4F7FC !important;
    background-color: #F4F7FC !important;
    background-image: none !important;
    color: #1A1A2E !important;
}

/* Any element with an inline dark bg gets overridden */
[style*="background:#0"],
[style*="background: #0"],
[style*="background-color:#0"],
[style*="background-color: #0"],
[style*="background:#1a"],
[style*="background: #1a"],
[style*="background:#0f"],
[style*="background: #0f"] {
    background: #FFFFFF !important;
    background-image: none !important;
    color: #1A1A2E !important;
}

/* Metrics & cards on light */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    background-image: none !important;
    color: #1A1A2E !important;
}
[data-testid="stMetric"] * { color: #1A1A2E !important; }
[data-testid="stMetricValue"] * { color: #0B3B8C !important; }
[data-testid="stMetricLabel"] * { color: #64748B !important; }

/* Category tiles (custom .cat-* classes) */
.cat-card, .cat-tile, .cat-grid-item, .category-card,
[class*="cat-"], [class*="category-"] {
    background: #FFFFFF !important;
    background-image: none !important;
    color: #1A1A2E !important;
    border: 1px solid #E2E8F0 !important;
}
.cat-card *, .cat-tile *, .category-card *,
[class*="cat-"] *, [class*="category-"] * {
    color: #1A1A2E !important;
}

/* Buttons on light */
.stButton > button,
.stDownloadButton > button {
    background: #FFFFFF !important;
    background-image: none !important;
    color: #0B3B8C !important;
    border: 1.5px solid #0B3B8C !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #E8EFFB !important;
}
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0B3B8C, #1560BD) !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* Text overrides — catch-all for neon on dark */
p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6, a {
    color: #1A1A2E !important;
}
small, .stCaption { color: #64748B !important; }

/* The corp-section titles should be dark */
.corp-section-title { color: #1A1A2E !important; }
.corp-section-sub { color: #64748B !important; }

/* ══════════════════════════════════════════════════════════
   HERO READABILITY — white text on gradient, big & bold
   ══════════════════════════════════════════════════════════ */
.corp-hero,
.corp-hero-inner {
    color: #FFFFFF !important;
}

/* Every text node inside the hero is white */
.corp-hero h1,
.corp-hero h2,
.corp-hero h3,
.corp-hero p,
.corp-hero span,
.corp-hero div,
.corp-hero strong,
.corp-hero em,
.corp-hero-inner h1,
.corp-hero-inner h2,
.corp-hero-inner h3,
.corp-hero-inner p,
.corp-hero-inner span,
.corp-hero-inner div,
.corp-hero-inner strong {
    color: #FFFFFF !important;
}

/* ── Main hero title "Meena Agencies" ── */
.corp-title {
    color: #FFFFFF !important;
    font-size: 44px !important;
    font-weight: 900 !important;
    letter-spacing: -1px !important;
    line-height: 1.1 !important;
    text-shadow: 0 2px 12px rgba(0,0,0,.18) !important;
    margin: 6px 0 12px 0 !important;
}
/* Accent word "Agencies" — bright amber for contrast */
.corp-title-accent {
    color: #FDB913 !important;
    text-shadow: 0 2px 12px rgba(0,0,0,.25) !important;
}

/* ── Eyebrow pill "RETAILER PORTAL · RET001" ── */
.corp-eyebrow {
    display: inline-block !important;
    background: rgba(255,255,255,0.18) !important;
    color: #FFFFFF !important;
    font-size: 12px !important;
    font-weight: 800 !important;
    letter-spacing: 1.6px !important;
    text-transform: uppercase !important;
    padding: 6px 14px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(6px) !important;
}

/* ── Subtitle "Welcome back, Chitra..." ── */
.corp-subtitle {
    color: rgba(255,255,255,0.95) !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    line-height: 1.55 !important;
    max-width: 720px !important;
    margin-bottom: 20px !important;
    text-shadow: 0 1px 6px rgba(0,0,0,.15) !important;
}

/* ── Meta row: ₹200,000 Credit Limit etc. ── */
.corp-meta-row {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 28px !important;
    margin-top: 20px !important;
    padding-top: 20px !important;
    border-top: 1px solid rgba(255,255,255,0.2) !important;
}
.corp-meta-item {
    color: rgba(255,255,255,0.85) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    line-height: 1.5 !important;
}
.corp-meta-item strong {
    display: block !important;
    color: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    letter-spacing: -0.3px !important;
    text-transform: none !important;
    margin-bottom: 4px !important;
    text-shadow: 0 1px 6px rgba(0,0,0,.2) !important;
}

/* ── Sign Out button — match the hero, don't break it ── */
.topnav-signout button,
.topnav-signout .stButton > button {
    background: rgba(255,255,255,0.15) !important;
    color: #FFFFFF !important;
    border: 1.5px solid rgba(255,255,255,0.5) !important;
    backdrop-filter: blur(6px) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}
.topnav-signout button:hover,
.topnav-signout .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
    border-color: #FFFFFF !important;
}

/* ── Fallback: any button sitting on the hero should be white ── */
.corp-hero ~ * button,
div:has(.corp-hero) + div button {
    /* handled by .topnav-signout above */
}

/* ── Mobile: bigger text, still readable ── */
@media (max-width: 768px) {
    .corp-title {
        font-size: 34px !important;
        line-height: 1.15 !important;
    }
    .corp-subtitle {
        font-size: 15px !important;
    }
    .corp-meta-item strong {
        font-size: 18px !important;
    }
    .corp-meta-row {
        gap: 20px !important;
    }
}
</style>
"""


def inject_nuclear():
    """Injected AFTER everything else so it wins."""
    st.markdown(_NUCLEAR_CSS, unsafe_allow_html=True)
