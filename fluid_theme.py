"""
fluid_theme.py — Water-flow responsive theme for Meena Agencies.

Every element scales smoothly with viewport. No fixed sizes.
Fits: phone, tablet, laptop, ultrawide, 4K, split-screen.
"""
import streamlit as st


FLUID_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════
   FLUID ROOT — everything scales with viewport width (vw)
   ═══════════════════════════════════════════════════════════ */
:root {
  --fluid-pad:   clamp(0.6rem, 2.2vw, 2.2rem);
  --fluid-gap:   clamp(0.5rem, 1.4vw, 1.4rem);
  --fluid-radius: clamp(10px, 1.1vw, 18px);
  --fluid-font:  clamp(13.5px, 0.32vw + 12px, 16.5px);
  --fluid-h1:    clamp(1.35rem, 1.6vw + 0.7rem, 2rem);
  --fluid-h2:    clamp(1.15rem, 1.1vw + 0.7rem, 1.6rem);
  --fluid-h3:    clamp(1rem,    0.7vw + 0.7rem, 1.3rem);
  --max-content: min(97vw, 1500px);
}

/* ── Body & app shell ── */
html, body, .stApp { font-size: var(--fluid-font) !important; }

.stApp {
  background:
    radial-gradient(1400px 700px at 6% -8%, #0d4054 0%, transparent 55%),
    radial-gradient(1200px 800px at 96% 108%, #1a2a55 0%, transparent 60%),
    linear-gradient(165deg, #061421 0%, #0a1f2f 45%, #0a1830 100%) !important;
  background-attachment: fixed !important;
}

/* ── Main container — flows like water ── */
.main .block-container {
  max-width: var(--max-content) !important;
  width: 100% !important;
  margin: 0 auto !important;
  padding-left:  var(--fluid-pad) !important;
  padding-right: var(--fluid-pad) !important;
  padding-top:   clamp(0.9rem, 2vw, 2rem) !important;
  padding-bottom: clamp(2rem, 5vw, 4rem) !important;
  transition: all .35s cubic-bezier(.2,.85,.3,1.05);
}

/* ── Headings — fluid ── */
h1 { font-size: var(--fluid-h1) !important; line-height: 1.22 !important;
     color: #eaf6ff !important; text-shadow: 0 2px 20px rgba(0,212,170,0.25); margin-bottom: .35em !important; }
h2 { font-size: var(--fluid-h2) !important; line-height: 1.28 !important;
     color: #eaf6ff !important; text-shadow: 0 2px 16px rgba(123,97,255,0.20); margin-bottom: .3em !important; }
h3 { font-size: var(--fluid-h3) !important; line-height: 1.32 !important;
     color: #d6e5f5 !important; margin-bottom: .28em !important; }
p, span, label, .stMarkdown, .stText { color: #c8d6e5 !important; line-height: 1.55 !important; }
small, .stCaption, [data-testid="stCaptionContainer"] { color: #8fa5ba !important; font-size: 0.85em !important; }

/* ── Columns — always wrap, never crush ── */
[data-testid="stHorizontalBlock"] {
  gap: var(--fluid-gap) !important;
  flex-wrap: wrap !important;
}
[data-testid="column"] {
  min-width: min(240px, 100%) !important;
  flex: 1 1 auto !important;
  transition: flex-basis .35s ease, min-width .35s ease;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
  background: linear-gradient(155deg, rgba(0,212,170,0.11), rgba(123,97,255,0.08)) !important;
  border: 1px solid rgba(0,212,170,0.28) !important;
  border-radius: var(--fluid-radius) !important;
  padding: clamp(10px, 1.1vw, 18px) !important;
  box-shadow: 0 12px 28px -20px rgba(0,0,0,0.7), 0 2px 0 rgba(255,255,255,0.05) inset !important;
  transition: transform .35s cubic-bezier(.2,.85,.3,1.05), box-shadow .35s ease;
  min-width: 0 !important;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-4px) !important;
  box-shadow: 0 22px 44px -22px rgba(0,212,170,0.5) !important;
}
[data-testid="stMetricValue"] {
  font-size: clamp(1.1rem, 1.2vw + 0.6rem, 1.55rem) !important;
  color: #eaf6ff !important; font-weight: 800 !important;
  text-shadow: 0 2px 12px rgba(0,212,170,0.28); white-space: nowrap;
}
[data-testid="stMetricLabel"] { color: #8fa5ba !important; font-weight: 600 !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
  background: linear-gradient(155deg, rgba(123,97,255,0.06), rgba(0,212,170,0.03)) !important;
  border: 1px solid rgba(123,97,255,0.22) !important;
  border-radius: var(--fluid-radius) !important;
  box-shadow: 0 10px 24px -18px rgba(0,0,0,0.6) !important;
  overflow: hidden;
  transition: border-color .3s ease, box-shadow .3s ease;
}
[data-testid="stExpander"]:hover {
  border-color: rgba(0,212,170,0.45) !important;
  box-shadow: 0 16px 36px -18px rgba(0,212,170,0.35) !important;
}

/* ── Buttons ── */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  background: linear-gradient(120deg, #0e8f7a 0%, #1a5fb4 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: clamp(8px, 0.7vw, 12px) !important;
  font-weight: 700 !important;
  font-size: clamp(0.85rem, 0.3vw + 0.75rem, 1rem) !important;
  padding: clamp(6px, 0.5vw, 10px) clamp(12px, 1vw, 20px) !important;
  min-height: clamp(36px, 3.2vw, 44px);
  white-space: nowrap;
  box-shadow: 0 10px 22px -12px rgba(26,95,180,0.65), 0 1px 0 rgba(255,255,255,0.15) inset !important;
  transition: transform .25s ease, box-shadow .25s ease, filter .25s ease !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.08);
  box-shadow: 0 18px 32px -14px rgba(0,212,170,0.65) !important;
}

/* ── Inputs ── */
input, textarea, [data-baseweb="input"], [data-baseweb="textarea"],
[data-baseweb="select"] > div {
  background: rgba(10,25,42,0.85) !important;
  border: 1px solid rgba(0,212,170,0.22) !important;
  border-radius: clamp(8px, 0.6vw, 10px) !important;
  color: #eaf6ff !important;
  font-size: clamp(0.85rem, 0.3vw + 0.75rem, 1rem) !important;
  min-height: clamp(36px, 3.2vw, 44px);
}
input:focus, textarea:focus {
  border-color: rgba(0,212,170,0.8) !important;
  box-shadow: 0 0 0 3px rgba(0,212,170,0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(10,25,42,0.7) !important;
  border-radius: clamp(8px, 0.7vw, 12px) !important;
  padding: 4px !important;
  gap: 4px !important;
  flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: clamp(6px, 0.5vw, 9px) !important;
  color: #9fb4c9 !important;
  font-weight: 600 !important;
  padding: clamp(5px, 0.5vw, 9px) clamp(10px, 0.9vw, 16px) !important;
  font-size: clamp(0.8rem, 0.25vw + 0.72rem, 0.95rem) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(120deg, #0e8f7a, #1a5fb4) !important;
  color: #ffffff !important;
}

/* ── Bordered containers (cart items) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: var(--fluid-radius) !important;
  border: 1px solid rgba(0,212,170,0.18) !important;
  background: linear-gradient(155deg, rgba(0,212,170,0.04), rgba(123,97,255,0.03)) !important;
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(0,212,170,0.42) !important;
  box-shadow: 0 14px 32px -16px rgba(0,212,170,0.36);
}

/* ── Tables — scroll gracefully, never squash ── */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border-radius: clamp(8px, 0.7vw, 12px) !important;
  overflow-x: auto !important;
  border: 1px solid rgba(0,212,170,0.20) !important;
  max-width: 100%;
}
[data-testid="stDataFrame"] > div { max-width: 100%; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #071727 0%, #0a1d33 100%) !important;
  border-right: 1px solid rgba(0,212,170,0.15) !important;
  width: clamp(220px, 22vw, 320px) !important;
  min-width: 220px !important;
}

/* ── Images — never overflow ── */
img, svg { max-width: 100%; height: auto; }

/* ── Horizontal rules ── */
hr {
  border: none !important; height: 1px !important;
  background: linear-gradient(90deg, transparent, rgba(0,212,170,0.35), transparent) !important;
  margin: clamp(8px, 1vw, 16px) 0 !important;
}

/* ═══════════════════════════════════════════════════════════
   BREAKPOINT: NARROW MOBILE (< 640px) — full stack
   ═══════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  [data-testid="column"] { min-width: 100% !important; flex-basis: 100% !important; }
  [data-testid="stMetric"] { min-width: 100% !important; }
  h1 { font-size: 1.3rem !important; }
  h2 { font-size: 1.1rem !important; }
  .main .block-container { padding-left: .8rem !important; padding-right: .8rem !important; }
  [data-testid="stSidebar"] { width: 240px !important; min-width: 240px !important; }
}

/* ═══════════════════════════════════════════════════════════
   BREAKPOINT: TABLET (640 - 1024px)
   ═══════════════════════════════════════════════════════════ */
@media (min-width: 641px) and (max-width: 1024px) {
  [data-testid="column"] { min-width: min(200px, 45%) !important; }
  .main .block-container { padding-left: 1.2rem !important; padding-right: 1.2rem !important; }
}

/* ═══════════════════════════════════════════════════════════
   BREAKPOINT: ULTRAWIDE (> 1800px)
   ═══════════════════════════════════════════════════════════ */
@media (min-width: 1800px) {
  :root { --max-content: 1560px; }
}

/* ═══════════════════════════════════════════════════════════
   FLOWING WATER — subtle entrance for every page
   ═══════════════════════════════════════════════════════════ */
@keyframes flowIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.main .block-container > div > div > div {
  animation: flowIn 0.35s cubic-bezier(.2,.85,.3,1.05) both;
}

/* ── Smooth scrollbar ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0e8f7a, #1a5fb4);
  border-radius: 8px;
}
</style>
"""


def apply():
    """Safe to call any time. Wrapped in try/except by caller."""
    st.markdown(FLUID_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FIX-UP: remove box-inside-box, spread metrics, tighten chrome
# ═══════════════════════════════════════════════════════════
FIXUP_CSS = """
<style>
/* Kill ALL nested container borders/backgrounds — content flows freely */
[data-testid="stVerticalBlockBorderWrapper"] {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* Hero card — one clean surface, no inner box */
.main .block-container > div > div > div > div > [data-testid="stVerticalBlockBorderWrapper"] {
  border: none !important;
  background: transparent !important;
}

/* Metrics row — spread and breathe */
[data-testid="stHorizontalBlock"] [data-testid="stMetric"] {
  min-width: 0 !important;
  flex: 1 1 0 !important;
  padding: clamp(12px, 1.2vw, 20px) !important;
}
[data-testid="stHorizontalBlock"] {
  gap: clamp(8px, 1vw, 18px) !important;
}

/* Hero section — full width, no wasted sides */
.main .block-container [data-testid="stVerticalBlock"] {
  max-width: 100% !important;
}

/* Reduce outer chrome */
.main .block-container {
  padding-top: clamp(0.5rem, 1.2vw, 1.2rem) !important;
}

/* Back / Home bar — tighter, thinner */
.stButton > button {
  padding: clamp(4px, 0.4vw, 8px) clamp(10px, 0.9vw, 16px) !important;
  min-height: clamp(32px, 2.8vw, 40px) !important;
  font-size: clamp(0.82rem, 0.28vw + 0.72rem, 0.95rem) !important;
}

/* Welcome banner — no shadow layer behind */
.welcome-banner, .welcome-title, .welcome-om, .welcome-subtitle, .welcome-tamil {
  background: transparent !important;
  box-shadow: none !important;
}
</style>
"""

try:
    import streamlit as st
    st.markdown(FIXUP_CSS, unsafe_allow_html=True)
except Exception:
    pass


# ═══════════════════════════════════════════════════════════
# HERO-FIX: force hero to full width, remove all box constraints
# ═══════════════════════════════════════════════════════════
HERO_FIX_CSS = """
<style>
/* ── Kill every wrapper that could box the hero ── */
.main .block-container,
.main .block-container > div,
.main .block-container > div > div,
.main .block-container > div > div > div {
  max-width: 100% !important;
  width: 100% !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

/* ── Hero card — full-bleed, no side padding, symmetric ── */
.welcome-banner,
div.welcome-banner {
  max-width: 100% !important;
  width: 100% !important;
  margin: 0 !important;
  padding: clamp(18px, 2.2vw, 36px) clamp(16px, 2.4vw, 44px) !important;
  border-radius: clamp(10px, 1vw, 16px) !important;
  box-sizing: border-box !important;
}

/* ── Inner hero text — align left, no wasted space ── */
.welcome-title,
div.welcome-title {
  margin: 0 0 .3em 0 !important;
  padding: 0 !important;
  text-align: left !important;
  font-size: clamp(1.6rem, 2.4vw + 0.8rem, 2.6rem) !important;
  line-height: 1.15 !important;
}
.welcome-subtitle,
div.welcome-subtitle {
  margin: 0 0 .6em 0 !important;
  padding: 0 !important;
  text-align: left !important;
  max-width: 100% !important;
  font-size: clamp(0.9rem, 0.4vw + 0.75rem, 1.1rem) !important;
}
.welcome-om, .welcome-tamil {
  margin: 0 !important;
  padding: 0 !important;
}

/* ── Kill background/border on the wrapper Streamlit puts around custom HTML ── */
.main .block-container [data-testid="stVerticalBlockBorderWrapper"] {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
  width: 100% !important;
}

/* ── Metrics row under hero — spread evenly edge to edge ── */
.welcome-banner ~ div [data-testid="stMetric"],
[data-testid="stMetric"] {
  flex: 1 1 0 !important;
  min-width: 0 !important;
}

/* ── Top nav buttons (Back / Home) — keep tight, no growing ── */
.topnav-signout, .topnav-signout + div {
  max-width: max-content !important;
}
.main .block-container > div > div > div > div > div[data-testid="stHorizontalBlock"] {
  max-width: 100% !important;
}

/* ── Sign Out buttons — quiet, small, right-aligned ── */
button[kind="secondary"][data-testid*="signout"],
button[data-testid*="hero_signout"] {
  min-height: 34px !important;
  padding: 4px 12px !important;
  font-size: 0.85rem !important;
}

/* ── Remove the mysterious dark rectangle behind hero ── */
.main .block-container > div > div > div > div:has(> div > .welcome-banner) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
</style>
"""

try:
    import streamlit as st
    st.markdown(HERO_FIX_CSS, unsafe_allow_html=True)
except Exception:
    pass


# ═══════════════════════════════════════════════════════════
# CORP-HERO OVERRIDE — force full width, kill inner box
# ═══════════════════════════════════════════════════════════
CORP_HERO_FIX = """
<style>
.corp-hero,
div.corp-hero {
  max-width: 100% !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  box-sizing: border-box !important;
}
.corp-hero-inner,
div.corp-hero-inner {
  max-width: 100% !important;
  width: 100% !important;
  margin: 0 !important;
  padding: clamp(20px, 2.4vw, 44px) clamp(20px, 3vw, 56px) !important;
  box-sizing: border-box !important;
  border-radius: clamp(12px, 1.2vw, 20px) !important;
}
.corp-meta-row,
div.corp-meta-row {
  display: flex !important;
  justify-content: space-between !important;
  gap: clamp(8px, 1.5vw, 24px) !important;
  flex-wrap: wrap !important;
  margin-top: clamp(14px, 1.6vw, 26px) !important;
  width: 100% !important;
}
.corp-meta-item {
  flex: 1 1 0 !important;
  min-width: 90px !important;
}
/* Hide the second Sign Out when both exist */
[data-testid="stHorizontalBlock"] button[key*="hero_signout_ret"] + * { display: none !important; }
</style>
"""

try:
    import streamlit as st
    st.markdown(CORP_HERO_FIX, unsafe_allow_html=True)
except Exception:
    pass


# ═══════════════════════════════════════════════════════════
# LOGIN WELCOME ANIMATION — gradual, elegant, plays on page load
# ═══════════════════════════════════════════════════════════
WELCOME_ANIMATION_CSS = """
<style>
@keyframes welcomeFadeUp {
  0%   { opacity: 0; transform: translateY(40px) scale(0.96); filter: blur(6px); }
  60%  { opacity: 1; transform: translateY(-4px) scale(1.01); filter: blur(0);   }
  100% { opacity: 1; transform: translateY(0)    scale(1);    filter: blur(0);   }
}
@keyframes welcomeTitleGlow {
  0%   { text-shadow: 0 0 0 rgba(0,212,170,0); }
  50%  { text-shadow: 0 0 30px rgba(0,212,170,0.85); }
  100% { text-shadow: 0 0 0 rgba(0,212,170,0); }
}
@keyframes welcomeSlideIn {
  from { opacity: 0; transform: translateX(-20px); }
  to   { opacity: 1; transform: translateX(0);     }
}
@keyframes welcomeMetricPop {
  0%   { opacity: 0; transform: translateY(14px) scale(0.9); }
  70%  { opacity: 1; transform: translateY(-2px) scale(1.03); }
  100% { opacity: 1; transform: translateY(0)    scale(1);   }
}
@keyframes welcomeShimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

/* Whole hero card rises from below with 3D depth */
.corp-hero {
  animation: welcomeFadeUp 1.1s cubic-bezier(.2,.85,.3,1.05) both !important;
  transform-origin: center top;
  will-change: transform, opacity, filter;
}

/* Eyebrow pill slides in from the left */
.corp-eyebrow {
  animation: welcomeSlideIn 0.7s ease-out 0.35s both !important;
}

/* Main title — fades up + glow pulse */
.corp-title {
  animation: welcomeFadeUp 0.9s cubic-bezier(.2,.85,.3,1.05) 0.5s both,
             welcomeTitleGlow 2.2s ease-in-out 1.4s 1 !important;
}

/* Subtitle — delayed fade */
.corp-subtitle {
  animation: welcomeFadeUp 0.8s cubic-bezier(.2,.85,.3,1.05) 0.75s both !important;
}

/* Each metric pops in with a slight stagger */
.corp-meta-item {
  animation: welcomeMetricPop 0.65s cubic-bezier(.2,.85,.3,1.05) both !important;
}
.corp-meta-item:nth-child(1) { animation-delay: 0.95s !important; }
.corp-meta-item:nth-child(2) { animation-delay: 1.05s !important; }
.corp-meta-item:nth-child(3) { animation-delay: 1.15s !important; }
.corp-meta-item:nth-child(4) { animation-delay: 1.25s !important; }
.corp-meta-item:nth-child(5) { animation-delay: 1.35s !important; }

/* Intel card slides in from the right */
.corp-intel-card {
  animation: welcomeSlideIn 0.85s cubic-bezier(.2,.85,.3,1.05) 0.6s both !important;
}

/* Optional shimmer sweep across the hero backdrop */
.corp-hero::before {
  animation: welcomeShimmer 3.5s linear 0.4s 1 !important;
  background-size: 200% 100% !important;
}

/* Reduce motion — accessibility */
@media (prefers-reduced-motion: reduce) {
  .corp-hero, .corp-eyebrow, .corp-title, .corp-subtitle,
  .corp-meta-item, .corp-intel-card {
    animation: none !important;
  }
}
</style>
"""

try:
    import streamlit as st
    st.markdown(WELCOME_ANIMATION_CSS, unsafe_allow_html=True)
except Exception:
    pass


# ═══════════════════════════════════════════════════════════
# FINAL UNBOX — force full width, hide duplicate sign out
# ═══════════════════════════════════════════════════════════
FINAL_UNBOX_CSS = """
<style>
/* Force hero to fill container — attack from every angle */
.corp-hero {
    max-width: 100% !important;
    width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}
.corp-hero-inner {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    display: grid !important;
    grid-template-columns: 1.6fr 1fr !important;
    gap: 40px !important;
    align-items: start !important;
}
.corp-hero-left { min-width: 0 !important; }
.corp-hero-right { min-width: 0 !important; padding-top: 8px !important; }

/* Kill any outer padding on block container that boxes the hero */
.main .block-container {
    padding-left: clamp(0.8rem, 2vw, 2rem) !important;
    padding-right: clamp(0.8rem, 2vw, 2rem) !important;
}

/* Hide SECOND sign out (any button after the first one in retailer view) */
.stButton > button[key*="hero_signout_ret"]:nth-of-type(2) { display: none !important; }

/* Tablet/mobile */
@media (max-width: 900px) {
    .corp-hero-inner {
        grid-template-columns: 1fr !important;
        gap: 20px !important;
    }
}
</style>
"""

try:
    import streamlit as st
    st.markdown(FINAL_UNBOX_CSS, unsafe_allow_html=True)
except Exception:
    pass
