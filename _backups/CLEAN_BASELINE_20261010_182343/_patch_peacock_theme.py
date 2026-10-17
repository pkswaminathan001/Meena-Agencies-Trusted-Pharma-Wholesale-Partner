from pathlib import Path
import py_compile

APP = Path("app.py")
src = APP.read_text()
original = src

if "PEACOCK_THEME_V1" in src:
    print("⏭  Peacock theme already installed")
    raise SystemExit(0)

# Find the first "import streamlit as st" and inject right after the imports block
anchor = "import streamlit as st"
if anchor not in src:
    print("❌ 'import streamlit as st' not found")
    raise SystemExit(1)

idx = src.index(anchor)
# find end of that line
eol = src.index("\n", idx) + 1

THEME = r'''
# ═════════════════════════════════════════════════════════════════
# PEACOCK_THEME_V1 — soft gradient peacock palette + 3D cards
# Applied globally. To disable, remove this block and re-run.
# ═════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Base app background: peacock gradient ── */
.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, #0e3a4a 0%, transparent 55%),
    radial-gradient(1000px 700px at 95% 110%, #1a2a55 0%, transparent 55%),
    linear-gradient(160deg, #061421 0%, #0a1f2f 40%, #0a1830 100%) !important;
  background-attachment: fixed !important;
}

/* Slightly lifted main content area */
.main .block-container {
  padding-top: 1.6rem !important;
  padding-bottom: 3rem !important;
  max-width: 1500px !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
  color: #eaf6ff !important;
  letter-spacing: 0.2px;
}
h1 { text-shadow: 0 2px 24px rgba(0,212,170,0.25); }
h2 { text-shadow: 0 2px 18px rgba(123,97,255,0.22); }

/* ── Paragraph / text ── */
p, span, label, .stMarkdown, .stCaption { color: #c8d6e5 !important; }
small, .stCaption { color: #8fa5ba !important; }

/* ── Metric cards (the top row in your screenshot) ── */
[data-testid="stMetric"] {
  background:
    linear-gradient(160deg, rgba(0,212,170,0.10), rgba(123,97,255,0.08)) !important;
  border: 1px solid rgba(0,212,170,0.28) !important;
  border-radius: 16px !important;
  padding: 16px 18px !important;
  box-shadow:
    0 12px 28px -18px rgba(0,0,0,0.7),
    0 2px 0 rgba(255,255,255,0.04) inset,
    0 0 0 1px rgba(0,212,170,0.06) !important;
  transition: transform .35s cubic-bezier(.2,.85,.3,1.05), box-shadow .35s ease !important;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-3px) !important;
  box-shadow:
    0 22px 44px -20px rgba(0,212,170,0.45),
    0 4px 8px -4px rgba(0,0,0,0.4),
    0 0 0 1px rgba(0,212,170,0.20) !important;
}
[data-testid="stMetricLabel"] { color: #8fa5ba !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] {
  color: #eaf6ff !important;
  font-weight: 800 !important;
  text-shadow: 0 2px 14px rgba(0,212,170,0.25);
}

/* ── Expander (Your Spending, Change My PIN, etc.) ── */
[data-testid="stExpander"] {
  background: linear-gradient(160deg, rgba(123,97,255,0.06), rgba(0,212,170,0.03)) !important;
  border: 1px solid rgba(123,97,255,0.22) !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 24px -18px rgba(0,0,0,0.6) !important;
  overflow: hidden;
  transition: border-color .3s ease, box-shadow .3s ease;
}
[data-testid="stExpander"]:hover {
  border-color: rgba(0,212,170,0.45) !important;
  box-shadow: 0 16px 36px -18px rgba(0,212,170,0.35) !important;
}
[data-testid="stExpander"] summary {
  color: #eaf6ff !important; font-weight: 700 !important;
}

/* ── Buttons (global) ── */
.stButton > button {
  background: linear-gradient(120deg, #0e8f7a 0%, #1a5fb4 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  letter-spacing: 0.3px;
  box-shadow:
    0 10px 22px -12px rgba(26,95,180,0.65),
    0 1px 0 rgba(255,255,255,0.15) inset !important;
  transition: transform .25s ease, box-shadow .25s ease, filter .25s ease !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.08);
  box-shadow:
    0 18px 32px -14px rgba(0,212,170,0.65),
    0 1px 0 rgba(255,255,255,0.20) inset !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary buttons (Clear, etc.) */
.stButton > button[kind="secondary"] {
  background: linear-gradient(120deg, #2a2e50, #3b2a55) !important;
}

/* ── Text inputs / number inputs ── */
input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
  background: rgba(10,25,42,0.85) !important;
  border: 1px solid rgba(0,212,170,0.22) !important;
  border-radius: 10px !important;
  color: #eaf6ff !important;
  transition: border-color .25s ease, box-shadow .25s ease;
}
input:focus, textarea:focus, [data-baseweb="input"]:focus-within {
  border-color: rgba(0,212,170,0.75) !important;
  box-shadow: 0 0 0 3px rgba(0,212,170,0.18) !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
  background: rgba(10,25,42,0.85) !important;
  border: 1px solid rgba(0,212,170,0.22) !important;
  border-radius: 10px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(10,25,42,0.65) !important;
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
  box-shadow: 0 6px 14px -8px rgba(0,212,170,0.7) !important;
}

/* ── Containers with border (used by cart items) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 14px !important;
  border: 1px solid rgba(0,212,170,0.16) !important;
  background: linear-gradient(160deg, rgba(0,212,170,0.04), rgba(123,97,255,0.03)) !important;
  box-shadow: 0 8px 20px -16px rgba(0,0,0,0.75);
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(0,212,170,0.40) !important;
  box-shadow: 0 14px 32px -16px rgba(0,212,170,0.35);
}

/* ── Product cards (grid tiles) ── */
[data-testid="stCard"] {
  background: linear-gradient(160deg, rgba(0,212,170,0.06), rgba(123,97,255,0.05)) !important;
  border: 1px solid rgba(123,97,255,0.25) !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 30px -18px rgba(0,0,0,0.65);
  transition: transform .35s cubic-bezier(.2,.85,.3,1.05), box-shadow .35s ease;
}
[data-testid="stCard"]:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 44px -18px rgba(0,212,170,0.5);
}

/* ── Divider lines ── */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent, rgba(0,212,170,0.35), transparent) !important;
  margin: 14px 0 !important;
}

/* ── Dataframe / tables ── */
[data-testid="stDataFrame"] {
  border-radius: 12px !important;
  overflow: hidden;
  border: 1px solid rgba(0,212,170,0.18) !important;
  box-shadow: 0 10px 26px -18px rgba(0,0,0,0.65);
}

/* ── Alerts (success/warning/info) ── */
[data-testid="stAlert"] {
  border-radius: 12px !important;
  border-left-width: 4px !important;
  box-shadow: 0 8px 20px -16px rgba(0,0,0,0.6);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #071727 0%, #0a1d33 100%) !important;
  border-right: 1px solid rgba(0,212,170,0.15) !important;
}

/* ── Scrollbar (webkit) ── */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0e8f7a, #1a5fb4);
  border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #00d4aa, #2a7fdc); }

/* ── Page-level subtle 3D entry ── */
@keyframes pageRise {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0);    }
}
.main .block-container { animation: pageRise 0.6s cubic-bezier(.2,.85,.3,1.05) both; }
</style>
""", unsafe_allow_html=True)
# ═════════════════════════════════════════════════════════════════
'''

src = src[:eol] + THEME + src[eol:]
APP.write_text(src)

try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ Peacock theme installed")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
