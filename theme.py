"""
theme.py — Peacock gradient theme for Meena Agencies.

SAFE: This is a standalone file. It only injects CSS via st.markdown.
It does not modify any other code. To disable, remove the
`apply_theme()` call from app.py — nothing else breaks.
"""
import streamlit as st


PEACOCK_CSS = """
<style>
/* ── Deep peacock gradient background ── */
.stApp {
  background:
    radial-gradient(1400px 700px at 8% -10%, #0d4054 0%, transparent 55%),
    radial-gradient(1200px 800px at 95% 110%, #1a2a55 0%, transparent 60%),
    linear-gradient(160deg, #061421 0%, #0a1f2f 45%, #0a1830 100%) !important;
  background-attachment: fixed !important;
}

.main .block-container {
  padding-top: 1.6rem !important;
  padding-bottom: 3rem !important;
  max-width: 1500px !important;
  animation: pageRise 0.5s cubic-bezier(.2,.85,.3,1.05) both;
}

@keyframes pageRise {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0);    }
}

/* ── Typography ── */
h1, h2, h3, h4 { color: #eaf6ff !important; letter-spacing: 0.2px; }
h1 { text-shadow: 0 2px 20px rgba(0,212,170,0.28); }
h2 { text-shadow: 0 2px 16px rgba(123,97,255,0.22); }
h3 { color: #d6e5f5 !important; }
p, span, label, .stMarkdown { color: #c8d6e5 !important; }
small, .stCaption { color: #8fa5ba !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
  background: linear-gradient(155deg, rgba(0,212,170,0.12), rgba(123,97,255,0.08)) !important;
  border: 1px solid rgba(0,212,170,0.30) !important;
  border-radius: 16px !important;
  padding: 16px 18px !important;
  box-shadow:
    0 14px 30px -20px rgba(0,0,0,0.75),
    0 2px 0 rgba(255,255,255,0.05) inset,
    0 0 0 1px rgba(0,212,170,0.08) !important;
  transition: transform .35s cubic-bezier(.2,.85,.3,1.05),
              box-shadow .35s ease !important;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-4px) !important;
  box-shadow:
    0 24px 44px -22px rgba(0,212,170,0.5),
    0 4px 10px -5px rgba(0,0,0,0.5),
    0 0 0 1px rgba(0,212,170,0.28) !important;
}
[data-testid="stMetricLabel"] {
  color: #8fa5ba !important; font-weight: 600 !important;
  letter-spacing: 0.4px;
}
[data-testid="stMetricValue"] {
  color: #eaf6ff !important; font-weight: 800 !important;
  text-shadow: 0 2px 12px rgba(0,212,170,0.3);
}

/* ── Expanders ── */
[data-testid="stExpander"] {
  background: linear-gradient(155deg, rgba(123,97,255,0.07), rgba(0,212,170,0.04)) !important;
  border: 1px solid rgba(123,97,255,0.24) !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 24px -18px rgba(0,0,0,0.65) !important;
  overflow: hidden;
  transition: border-color .3s ease, box-shadow .3s ease;
}
[data-testid="stExpander"]:hover {
  border-color: rgba(0,212,170,0.5) !important;
  box-shadow: 0 16px 36px -18px rgba(0,212,170,0.4) !important;
}
[data-testid="stExpander"] summary {
  color: #eaf6ff !important; font-weight: 700 !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(120deg, #0e8f7a 0%, #1a5fb4 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  letter-spacing: 0.3px;
  box-shadow:
    0 10px 22px -12px rgba(26,95,180,0.7),
    0 1px 0 rgba(255,255,255,0.18) inset !important;
  transition: transform .25s ease, box-shadow .25s ease,
              filter .25s ease !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.1);
  box-shadow:
    0 18px 34px -14px rgba(0,212,170,0.7),
    0 1px 0 rgba(255,255,255,0.22) inset !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs ── */
input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: rgba(10,25,42,0.85) !important;
  border: 1px solid rgba(0,212,170,0.24) !important;
  border-radius: 10px !important;
  color: #eaf6ff !important;
}
input:focus, textarea:focus {
  border-color: rgba(0,212,170,0.8) !important;
  box-shadow: 0 0 0 3px rgba(0,212,170,0.2) !important;
}
[data-baseweb="select"] > div {
  background: rgba(10,25,42,0.85) !important;
  border: 1px solid rgba(0,212,170,0.24) !important;
  border-radius: 10px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(10,25,42,0.7) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 9px !important;
  color: #9fb4c9 !important;
  font-weight: 600 !important;
  padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(120deg, #0e8f7a, #1a5fb4) !important;
  color: #ffffff !important;
  box-shadow: 0 6px 14px -8px rgba(0,212,170,0.75) !important;
}

/* ── Bordered containers (cart items) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 14px !important;
  border: 1px solid rgba(0,212,170,0.20) !important;
  background: linear-gradient(155deg, rgba(0,212,170,0.05), rgba(123,97,255,0.04)) !important;
  box-shadow: 0 8px 20px -16px rgba(0,0,0,0.75);
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(0,212,170,0.45) !important;
  box-shadow: 0 14px 32px -16px rgba(0,212,170,0.4);
}

/* ── Dividers ── */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent,
    rgba(0,212,170,0.4), transparent) !important;
  margin: 14px 0 !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
  border-radius: 12px !important;
  overflow: hidden;
  border: 1px solid rgba(0,212,170,0.22) !important;
  box-shadow: 0 10px 26px -18px rgba(0,0,0,0.7);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #071727 0%, #0a1d33 100%) !important;
  border-right: 1px solid rgba(0,212,170,0.18) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.25); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0e8f7a, #1a5fb4);
  border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #00d4aa, #2a7fdc);
}

/* ── Alerts ── */
[data-testid="stAlert"] {
  border-radius: 12px !important;
  border-left-width: 4px !important;
  box-shadow: 0 8px 20px -16px rgba(0,0,0,0.65);
}
</style>
"""


def apply_theme():
    """Inject peacock theme. Safe to call once per app run."""
    st.markdown(PEACOCK_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# AUTO-FIT / RESPONSIVE LAYER  (appended — safe to remove)
# ═══════════════════════════════════════════════════════════
AUTOFIT_CSS = """
<style>
/* Cap width on huge monitors so content stays readable */
.main .block-container {
  max-width: min(96vw, 1480px) !important;
  margin: 0 auto !important;
  padding-left: clamp(1rem, 3vw, 3rem) !important;
  padding-right: clamp(1rem, 3vw, 3rem) !important;
}

/* Fluid type — text scales with viewport, floors at 14px */
html, body, .stApp {
  font-size: clamp(14px, 0.28vw + 12px, 17px) !important;
}

/* Headings scale smoothly */
h1 { font-size: clamp(1.5rem, 1.2vw + 1rem, 2.2rem) !important; }
h2 { font-size: clamp(1.25rem, 0.9vw + 0.9rem, 1.75rem) !important; }
h3 { font-size: clamp(1.05rem, 0.6vw + 0.85rem, 1.35rem) !important; }

/* Metric cards keep sensible width on ultrawide */
[data-testid="stMetric"] {
  min-width: 180px;
  max-width: 100%;
}

/* Columns never crush below readable width */
[data-testid="column"] {
  min-width: 220px;
}

/* Tables scroll horizontally instead of squashing */
[data-testid="stDataFrame"] { overflow-x: auto !important; }

/* Input fields stay comfortable */
input, textarea, [data-baseweb="input"], [data-baseweb="select"] {
  min-height: 38px;
}

/* Buttons — comfortable hit targets */
.stButton > button {
  min-height: 38px;
  padding: 6px 16px;
}

/* Image safety */
img { max-width: 100%; height: auto; }

/* Ultra-wide (>1800px) — even tighter cap */
@media (min-width: 1800px) {
  .main .block-container { max-width: 1560px !important; }
}

/* Tablet (768–1024) */
@media (max-width: 1024px) {
  .main .block-container { padding-left: 1.2rem !important; padding-right: 1.2rem !important; }
  h1 { font-size: 1.6rem !important; }
}

/* Mobile (<768) — stack-friendly */
@media (max-width: 768px) {
  .main .block-container { max-width: 100% !important; padding-left: 0.9rem !important; padding-right: 0.9rem !important; }
  [data-testid="column"] { min-width: 100% !important; }
  [data-testid="stMetric"] { min-width: 100% !important; }
  h1 { font-size: 1.4rem !important; }
  h2 { font-size: 1.15rem !important; }
}
</style>
"""

# Apply auto-fit alongside the peacock theme
try:
    st.markdown(AUTOFIT_CSS, unsafe_allow_html=True)
except Exception:
    pass
