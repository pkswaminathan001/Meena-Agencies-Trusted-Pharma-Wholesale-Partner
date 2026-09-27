"""
peacock_anim.py — Peacock feather animations for login & logout.
Pure CSS + SVG. No external images. Fast.
"""
import streamlit as st
import time


# ═══════════════════════════════════════════════════════════
# PEACOCK FEATHER SVG (inline, iridescent colors)
# ═══════════════════════════════════════════════════════════
FEATHER_SVG = '''
<svg viewBox="0 0 60 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="eye1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#7b61ff"/>
      <stop offset="35%" stop-color="#00d4ff"/>
      <stop offset="65%" stop-color="#00a86b"/>
      <stop offset="100%" stop-color="#ffb547"/>
    </radialGradient>
    <linearGradient id="stem1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00a86b"/>
      <stop offset="100%" stop-color="#006644"/>
    </linearGradient>
  </defs>
  <!-- Stem -->
  <path d="M30 60 Q32 120 30 195" stroke="url(#stem1)" stroke-width="3" fill="none"/>
  <!-- Barbs -->
  <path d="M30 100 Q15 115 10 140" stroke="#00a86b" stroke-width="1.5" fill="none" opacity="0.7"/>
  <path d="M30 100 Q45 115 50 140" stroke="#00a86b" stroke-width="1.5" fill="none" opacity="0.7"/>
  <path d="M30 130 Q18 145 15 170" stroke="#00a86b" stroke-width="1.5" fill="none" opacity="0.6"/>
  <path d="M30 130 Q42 145 45 170" stroke="#00a86b" stroke-width="1.5" fill="none" opacity="0.6"/>
  <!-- Eye (ocellus) -->
  <ellipse cx="30" cy="45" rx="22" ry="28" fill="url(#eye1)" opacity="0.95"/>
  <ellipse cx="30" cy="45" rx="16" ry="20" fill="#0047ab" opacity="0.85"/>
  <ellipse cx="30" cy="45" rx="9" ry="12" fill="#ffb547" opacity="0.95"/>
  <ellipse cx="30" cy="45" rx="4" ry="5" fill="#1a1a2e"/>
  <!-- Shine -->
  <ellipse cx="25" cy="38" rx="3" ry="4" fill="#ffffff" opacity="0.7"/>
</svg>
'''


# ═══════════════════════════════════════════════════════════
# LOGIN — Feathers unfurl + fall
# ═══════════════════════════════════════════════════════════
def inject_login_animation():
    """Call at top of login page. Adds falling peacock feathers."""
    st.markdown(f"""
    <style>
    .peacock-login-layer {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }}
    .peacock-feather {{
        position: absolute;
        opacity: 0;
        animation: featherFall 12s linear infinite;
        filter: drop-shadow(0 0 12px rgba(0,212,255,0.5));
    }}
    .peacock-feather svg {{
        width: 60px;
        height: 200px;
    }}
    @keyframes featherFall {{
        0%   {{ transform: translateY(-250px) rotate(-15deg) scale(0.8); opacity: 0; }}
        8%   {{ opacity: 0.9; }}
        85%  {{ opacity: 0.9; }}
        100% {{ transform: translateY(105vh) rotate(15deg) scale(1); opacity: 0; }}
    }}
    /* Stagger delays for natural look */
    .pf-1  {{ left: 4%;  animation-delay: 0s;   animation-duration: 14s; }}
    .pf-2  {{ left: 18%; animation-delay: 3s;   animation-duration: 16s; }}
    .pf-3  {{ left: 32%; animation-delay: 6s;   animation-duration: 13s; }}
    .pf-4  {{ left: 52%; animation-delay: 2s;   animation-duration: 15s; }}
    .pf-5  {{ left: 68%; animation-delay: 8s;   animation-duration: 14s; }}
    .pf-6  {{ left: 82%; animation-delay: 4s;   animation-duration: 17s; }}
    .pf-7  {{ left: 92%; animation-delay: 10s;  animation-duration: 12s; }}
    
    /* Radial glow at top of page */
    .peacock-glow {{
        position: fixed;
        top: -20%; left: 50%;
        transform: translateX(-50%);
        width: 900px; height: 900px;
        background: radial-gradient(circle,
                    rgba(0,212,255,0.10) 0%,
                    rgba(123,97,255,0.06) 40%,
                    transparent 70%);
        animation: peacockPulse 7s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }}
    @keyframes peacockPulse {{
        0%, 100% {{ transform: translateX(-50%) scale(1);   opacity: 0.7; }}
        50%      {{ transform: translateX(-50%) scale(1.15); opacity: 1;   }}
    }}
    </style>
    <div class="peacock-glow"></div>
    <div class="peacock-login-layer">
        <div class="peacock-feather pf-1">{FEATHER_SVG}</div>
        <div class="peacock-feather pf-2">{FEATHER_SVG}</div>
        <div class="peacock-feather pf-3">{FEATHER_SVG}</div>
        <div class="peacock-feather pf-4">{FEATHER_SVG}</div>
        <div class="peacock-feather pf-5">{FEATHER_SVG}</div>
        <div class="peacock-feather pf-6">{FEATHER_SVG}</div>
        <div class="peacock-feather pf-7">{FEATHER_SVG}</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# LOGOUT — Feathers fly up + farewell message
# ═══════════════════════════════════════════════════════════
def show_logout_animation(user_name="User"):
    """Show farewell animation for ~2 seconds, then return."""
    st.markdown(f"""
    <style>
    .peacock-logout-overlay {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        animation: overlayIn 0.4s ease-out;
    }}
    @keyframes overlayIn {{
        from {{ opacity: 0; }}
        to   {{ opacity: 1; }}
    }}
    .peacock-flyaway {{
        position: absolute;
        bottom: -200px;
        animation: flyUp 2s ease-out forwards;
    }}
    @keyframes flyUp {{
        0%   {{ transform: translateY(0) rotate(-30deg); opacity: 0; }}
        20%  {{ opacity: 1; }}
        100% {{ transform: translateY(-120vh) rotate(30deg); opacity: 0; }}
    }}
    .peacock-flyaway svg {{
        width: 60px; height: 200px;
        filter: drop-shadow(0 0 20px rgba(0,212,255,0.8));
    }}
    .pf-f1 {{ left: 15%; animation-delay: 0s;    animation-duration: 2.2s; }}
    .pf-f2 {{ left: 35%; animation-delay: 0.3s;  animation-duration: 2.0s; }}
    .pf-f3 {{ left: 55%; animation-delay: 0.15s; animation-duration: 2.1s; }}
    .pf-f4 {{ left: 75%; animation-delay: 0.4s;  animation-duration: 2.3s; }}
    
    .farewell-text {{
        position: relative;
        z-index: 2;
        text-align: center;
        animation: farewellFade 2s ease-out;
    }}
    @keyframes farewellFade {{
        0%   {{ opacity: 0; transform: translateY(20px); }}
        30%  {{ opacity: 1; transform: translateY(0); }}
        80%  {{ opacity: 1; }}
        100% {{ opacity: 0.9; }}
    }}
    .farewell-title {{
        font-family: Georgia, serif;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b61ff, #00a86b, #ffb547, #00d4ff);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: farewellShimmer 3s linear infinite;
        margin-bottom: 8px;
    }}
    @keyframes farewellShimmer {{
        0%   {{ background-position: 0% center; }}
        100% {{ background-position: 300% center; }}
    }}
    .farewell-sub {{
        color: #8892b0;
        font-size: 1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 10px;
    }}
    .farewell-tamil {{
        color: #ffb547;
        font-size: 1.2rem;
        margin-top: 20px;
        letter-spacing: 1px;
    }}
    </style>
    <div class="peacock-logout-overlay">
        <div class="peacock-flyaway pf-f1">{FEATHER_SVG}</div>
        <div class="peacock-flyaway pf-f2">{FEATHER_SVG}</div>
        <div class="peacock-flyaway pf-f3">{FEATHER_SVG}</div>
        <div class="peacock-flyaway pf-f4">{FEATHER_SVG}</div>
        <div class="farewell-text">
            <div class="farewell-title">தேங்க்ஸ் {user_name}!</div>
            <div class="farewell-sub">See You Soon</div>
            <div class="farewell-tamil">🦚 மீண்டும் வருக · Come Back Soon 🦚</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.0)


# ═══════════════════════════════════════════════════════════
# SESSION LOGOUT WITH ANIMATION
# ═══════════════════════════════════════════════════════════
def logout_with_animation():
    """
    Full logout — shows farewell animation, clears state, returns to login.
    Call this from your logout button.
    """
    # Get user name
    name = "User"
    try:
        if st.session_state.get("role") == "owner":
            name = "Boss"
        elif st.session_state.get("role") == "staff":
            name = st.session_state.get("staff", {}).get("name", "Staff").split()[0]
        elif st.session_state.get("role") == "customer":
            name = st.session_state.get("retailer", {}).get("owner", "Customer").split()[0]
    except Exception:
        pass

    # Show farewell animation
    show_logout_animation(name)

    # Log before clearing
    try:
        from security import log_action
        role = st.session_state.get("role", "unknown")
        uid = "UNKNOWN"
        if role == "owner": uid = "OWNER"
        elif role == "staff": uid = st.session_state.get("staff", {}).get("id", "UNKNOWN")
        elif role == "customer": uid = st.session_state.get("retailer", {}).get("id", "UNKNOWN")
        log_action(uid, "LOGOUT", f"role={role}")
    except Exception:
        pass

    # Clear all session state
    for k in list(st.session_state.keys()):
        try:
            del st.session_state[k]
        except Exception:
            pass

    st.rerun()
