"""
theme.py — A single, calm design system for the whole app.
Forces light theme even when Streamlit tries to go dark.
Call inject() once at the very top of app.py (after set_page_config).
"""
import streamlit as st


_CSS = """
<style>
/* ══════════════════════════════════════════════════════════
   GLOBAL RESET + TYPOGRAPHY
   ══════════════════════════════════════════════════════════ */
:root {
    --bg:        #f5f7fb;
    --surface:   #ffffff;
    --border:    #e5e7eb;
    --text:      #111827;
    --muted:     #6b7280;
    --accent:    #4f46e5;
    --accent-2:  #4338ca;
    --success:   #15803d;
    --success-bg:#dcfce7;
    --warn:      #b45309;
    --warn-bg:   #fef3c7;
    --danger:    #b91c1c;
    --danger-bg: #fee2e2;
    --radius:    12px;
    --shadow:    0 4px 14px rgba(15,23,42,.06);
}

/* Force light background on the whole app */
html, body, [data-testid="stAppViewContainer"], .main, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 system-ui, Roboto, sans-serif !important;
}

/* Kill any residual dark-mode leftovers */
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ══════════════════════════════════════════════════════════
   HEADINGS
   ══════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: -.2px !important;
}
h1 { font-size: 26px !important; }
h2 { font-size: 22px !important; }
h3 { font-size: 18px !important; }
h4 { font-size: 16px !important; }

p, span, label, div {
    color: var(--text);
}

/* ══════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════ */
.stButton > button,
.stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 18px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    transition: transform .12s ease, background .15s ease,
                box-shadow .15s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.04) !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #f9fafb !important;
    border-color: #cbd5e1 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15,23,42,.08) !important;
}

/* Primary buttons — accent color */
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    border-color: var(--accent) !important;
}
.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    background: var(--accent-2) !important;
    border-color: var(--accent-2) !important;
}

/* Kill the ugly default red download button */
.stDownloadButton > button {
    background: var(--surface) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
}
.stDownloadButton > button:hover {
    background: #eef2ff !important;
}

/* ══════════════════════════════════════════════════════════
   INPUTS
   ══════════════════════════════════════════════════════════ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-size: 14px !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,.12) !important;
    outline: none !important;
}

/* ══════════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    height: 42px !important;
    padding: 0 16px !important;
    border-radius: 8px 8px 0 0 !important;
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    background: transparent !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ══════════════════════════════════════════════════════════
   METRICS
   ══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 14px 16px !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: .5px;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-weight: 800 !important;
}

/* ══════════════════════════════════════════════════════════
   EXPANDERS
   ══════════════════════════════════════════════════════════ */
.streamlit-expanderHeader,
details summary {
    background: var(--surface) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════════════
   TABLES
   ══════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stDataFrame"] thead th {
    background: #f8fafc !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] tbody td {
    color: var(--text) !important;
    border-bottom: 1px solid #f3f4f6 !important;
}

/* ══════════════════════════════════════════════════════════
   DIALOG / MODAL — force LIGHT inside st.dialog
   ══════════════════════════════════════════════════════════ */
div[data-testid="stDialog"] > div,
div[role="dialog"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-radius: 16px !important;
    box-shadow: 0 24px 60px rgba(15,23,42,.22) !important;
    border: 1px solid var(--border) !important;
}
div[data-testid="stDialog"] h1,
div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] h3,
div[data-testid="stDialog"] p,
div[data-testid="stDialog"] span,
div[data-testid="stDialog"] label,
div[data-testid="stDialog"] div {
    color: var(--text) !important;
}
/* Modal close X */
div[data-testid="stDialog"] button[kind="header"] {
    color: var(--text) !important;
}

/* ══════════════════════════════════════════════════════════
   ALERTS — calmer colors
   ══════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow) !important;
}

/* ══════════════════════════════════════════════════════════
   HIDE STREAMLIT CHROME
   ══════════════════════════════════════════════════════════ */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { background: transparent !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ══════════════════════════════════════════════════════════
   RESPONSIVE — mobile-friendly
   ══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding: 1rem .8rem !important; }
    h1 { font-size: 22px !important; }
    h2 { font-size: 19px !important; }
    .stButton > button { padding: 10px 14px !important; font-size: 13px !important; }
    div[data-testid="stDialog"] > div { border-radius: 12px !important; }
}
</style>
"""


def inject():
    """Call once, at the top of app.py (after set_page_config)."""
    st.markdown(_CSS, unsafe_allow_html=True)
