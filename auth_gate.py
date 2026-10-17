"""
auth_gate.py — Smooth, cached, animated access gate.
"""
import streamlit as st
import hmac
from pathlib import Path


# ═══════════════════════════════════════════════════════════
# MODULE-LEVEL STATE — survives session_state.clear()
# ═══════════════════════════════════════════════════════════
_GATE_UNLOCKED = False
_LOGO_B64_CACHE = None  # computed once, reused forever


def _get_logo_b64() -> str:
    """Return the logo base64 — computed only once."""
    global _LOGO_B64_CACHE
    if _LOGO_B64_CACHE is not None:
        return _LOGO_B64_CACHE
    try:
        p = Path("logo.png")
        if p.exists():
            _LOGO_B64_CACHE = base64.b64encode(p.read_bytes()).decode()
        else:
            _LOGO_B64_CACHE = ""
    except Exception:
        _LOGO_B64_CACHE = ""
    return _LOGO_B64_CACHE


AUTH_CSS = """
<style>
@keyframes meshFlow {
  0%   { transform: translate(0, 0) rotate(0deg); }
  50%  { transform: translate(-3%, 2%) rotate(180deg); }
  100% { transform: translate(0, 0) rotate(360deg); }
}
@keyframes cardIn {
  0%   { opacity: 0; transform: translateY(28px) scale(0.96); filter: blur(6px); }
  100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}
@keyframes heroIn {
  0%   { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 40px rgba(0,212,170,0.25), 0 30px 60px rgba(0,0,0,0.6); }
  50%      { box-shadow: 0 0 60px rgba(0,212,170,0.45), 0 30px 70px rgba(0,0,0,0.65); }
}
@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-8px); }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}
/* Prevent any flash of unstyled content */
html, body, .stApp, [data-testid="stAppViewContainer"] {
  transition: opacity .25s ease-in-out;
}
.stApp { background: #050818 !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.block-container { padding: 3vh 1rem !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"]::before {
  content: '';
   inset: -20%; z-index: 0;
  background:
    radial-gradient(closest-side, rgba(0,212,170,0.28), transparent 70%) 15% 20% / 60% 60% no-repeat,
    radial-gradient(closest-side, rgba(123,97,255,0.32), transparent 70%) 85% 25% / 70% 70% no-repeat,
    radial-gradient(closest-side, rgba(255,180,71,0.18), transparent 70%) 50% 90% / 60% 60% no-repeat,
    linear-gradient(160deg, #050818 0%, #0a1f2f 45%, #0a1830 100%);
  animation: meshFlow 40s linear infinite;
  filter: blur(30px);
  pointer-events: none;
}
.main, .main .block-container, section.main { position: relative; z-index: 2; }
.ma-hero-wrap {
  max-width: 460px;
  margin: 6vh auto 24px;
  perspective: 1400px;
  animation: heroIn .55s cubic-bezier(.2,.85,.3,1.05) both;
}
.ma-hero {
  position: relative; padding: 40px 42px 34px;
  border-radius: 24px;
  background: linear-gradient(160deg, rgba(20,30,60,0.85) 0%, rgba(10,20,45,0.9) 100%);
  border: 1px solid rgba(0,212,170,0.22);
  backdrop-filter: blur(24px) saturate(140%);
  -webkit-backdrop-filter: blur(24px) saturate(140%);
  animation: cardIn .7s cubic-bezier(.2,.85,.3,1.05) both,
             glowPulse 4s ease-in-out 1s infinite;
  text-align: center; overflow: hidden;
}
.ma-hero::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, #7b61ff, #ffb547, transparent);
  background-size: 200% 100%;
  animation: shimmer 4s linear infinite;
}
.ma-logo {
  display: block; width: 120px; height: 120px;
  margin: 0 auto 18px; border-radius: 50%; object-fit: cover;
  background: #ffffff; padding: 6px;
  animation: logoFloat 4s ease-in-out infinite;
  box-shadow: 0 0 30px rgba(0,212,170,0.45), 0 0 60px rgba(123,97,255,0.25), 0 10px 30px rgba(0,0,0,0.45);
  border: 2px solid rgba(0,212,170,0.4);
  /* Prevents flicker while loading */
  will-change: transform;
}
.ma-brand {
  font-family: Georgia, serif; font-size: 2rem; font-weight: 800;
  letter-spacing: 1.6px; margin: 0 0 8px;
  background: linear-gradient(90deg, #00d4aa 0%, #7b61ff 45%, #ffb547 75%, #00d4aa 100%);
  background-size: 200% auto;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 6s linear infinite;
}
.ma-sub {
  font-size: 0.75rem; letter-spacing: 3px; text-transform: uppercase;
  color: #8892b0; margin: 0 0 6px;
}
.ma-underline {
  display: block; width: 60px; height: 3px; margin: 14px auto 0;
  background: linear-gradient(90deg, #00d4aa, #7b61ff); border-radius: 3px;
}
/* Login form fades in after card */
div[data-testid="stTextInput"] {
  animation: heroIn .5s cubic-bezier(.2,.85,.3,1.05) .15s both;
}
button[kind="primary"], button[kind="secondary"] {
  animation: heroIn .5s cubic-bezier(.2,.85,.3,1.05) .2s both;
}
[data-testid="stTextInput"] input {
  background: rgba(8,18,40,0.75) !important;
  border: 1.5px solid rgba(0,212,170,0.25) !important;
  border-radius: 12px !important;
  color: #eaf6ff !important;
  padding: 14px 18px !important;
  font-size: 1rem !important;
  transition: border-color .25s ease, box-shadow .25s ease !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: rgba(0,212,170,0.9) !important;
  box-shadow: 0 0 0 4px rgba(0,212,170,0.15) !important;
}
[data-testid="stTextInput"] label {
  color: #8892b0 !important; font-size: 0.72rem !important;
  letter-spacing: 2px !important; text-transform: uppercase !important;
}
/* Smooth buttons */
.stButton > button {
  transition: transform .2s ease, box-shadow .2s ease, filter .2s ease !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.08);
}
@media (max-width: 640px) {
  .ma-hero-wrap { margin: 4vh 12px 20px; }
  .ma-hero { padding: 30px 22px 26px; }
  .ma-brand { font-size: 1.5rem; }
  .ma-logo { width: 90px; height: 90px; }
}
</style>
"""


def _render_hero(logo_b64: str):
    html = (
        '<div class="ma-hero-wrap">'
        '<div class="ma-hero">'
        + (f'<img class="ma-logo" src="data:image/png;base64,{logo_b64}" alt="Meena Agencies" />' if logo_b64 else '')
        + '<div class="ma-brand">Meena Agencies</div>'
        '<div class="ma-sub">Authorised Access Only</div>'
        '<span class="ma-underline"></span>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def unlock_gate():
    global _GATE_UNLOCKED
    _GATE_UNLOCKED = True


def lock_gate():
    global _GATE_UNLOCKED
    _GATE_UNLOCKED = False


def is_unlocked() -> bool:
    return _GATE_UNLOCKED


def check_password():
    """Return True if already unlocked."""
    global _GATE_UNLOCKED

    if _GATE_UNLOCKED:
        return True
    if st.session_state.get("_ma_gate_unlocked") is True:
        _GATE_UNLOCKED = True
        return True

    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    def password_entered():
        global _GATE_UNLOCKED
        try:
            expected = st.secrets["ACCESS_PASSWORD"]
        except Exception:
            _GATE_UNLOCKED = True
            st.session_state["_ma_gate_unlocked"] = True
            return
        entered = st.session_state.get("password", "")
        if entered and hmac.compare_digest(entered, expected):
            _GATE_UNLOCKED = True
            st.session_state["_ma_gate_unlocked"] = True
            st.session_state["_ma_gate_error"] = False
        else:
            st.session_state["_ma_gate_error"] = True

    _render_hero(_get_logo_b64())

    _sp_l, _mid, _sp_r = st.columns([1, 1.6, 1])
    with _mid:
        st.text_input(
            "Access Password",
            type="password",
            key="password",
            on_change=password_entered,
            placeholder="Enter your passphrase",
        )
        if st.session_state.get("_ma_gate_error"):
            st.error("Wrong password — try again")

    return _GATE_UNLOCKED
