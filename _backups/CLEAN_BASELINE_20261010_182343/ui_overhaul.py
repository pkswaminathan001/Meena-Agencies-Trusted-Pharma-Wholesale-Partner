"""
ui_overhaul.py — Amazon-style sidebar + mobile-first layout + no waste.
"""
import streamlit as st


OVERHAUL_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════
   1. NO SCROLL for top-level content
   ═══════════════════════════════════════════════════════════ */
.main .block-container {
    padding: 0.8rem 1rem !important;
    max-width: 100% !important;
}

/* ═══════════════════════════════════════════════════════════
   2. KILL WASTE GAPS
   ═══════════════════════════════════════════════════════════ */
.main .block-container > div { margin-bottom: 0.3rem !important; }
.element-container { margin-bottom: 0.3rem !important; }
hr { margin: 8px 0 !important; }
h1, h2, h3 { margin-top: 0.2em !important; margin-bottom: 0.3em !important; }
.stMarkdown p { margin-bottom: 0.3em !important; }

/* ═══════════════════════════════════════════════════════════
   3. AMAZON-STYLE HAMBURGER SIDEBAR
   ═══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1420 0%, #0d1b2e 100%) !important;
    border-right: 1px solid rgba(0,212,170,0.2) !important;
    width: 240px !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #00d4aa !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #b8c0d8 !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    min-height: 44px !important;
    transition: all .2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(90deg, rgba(0,212,170,0.15), transparent) !important;
    color: #00d4aa !important;
    transform: translateX(4px) !important;
}

/* Sidebar collapse button (hamburger) — always visible, styled */
[data-testid="stSidebarCollapsedControl"] {
    top: 12px !important;
    left: 12px !important;
    z-index: 10000 !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    background: linear-gradient(135deg, rgba(0,212,170,0.9), rgba(123,97,255,0.9)) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 10px !important;
    width: 44px !important;
    height: 44px !important;
    box-shadow: 0 6px 20px rgba(0,212,170,0.4) !important;
    transition: all .2s ease !important;
}
[data-testid="stSidebarCollapsedControl"] button:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 28px rgba(0,212,170,0.6) !important;
}

/* ═══════════════════════════════════════════════════════════
   4. COMPACT METRICS (fit in less space)
   ═══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    padding: 12px 14px !important;
    min-height: 0 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
}

/* ═══════════════════════════════════════════════════════════
   5. MOBILE-FIRST: BIGGER TAP TARGETS
   ═══════════════════════════════════════════════════════════ */
.stButton > button {
    min-height: 44px !important;
    font-size: 0.92rem !important;
}
[data-baseweb="select"] > div {
    min-height: 44px !important;
}
input, textarea {
    min-height: 44px !important;
}

/* ═══════════════════════════════════════════════════════════
   6. FILL VIEWPORT — content flows to full height naturally
   ═══════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
[data-testid="stHorizontalBlock"] { gap: 0.6rem !important; }

/* ═══════════════════════════════════════════════════════════
   7. MOBILE BREAKPOINT — < 768px
   ═══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.6rem 0.7rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }
    [data-testid="stMetric"] {
        padding: 10px !important;
    }
    [data-testid="column"] {
        min-width: 100% !important;
    }
    [data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
    }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1rem !important; }
}

/* ═══════════════════════════════════════════════════════════
   8. HIDE STREAMLIT CHROME
   ═══════════════════════════════════════════════════════════ */
#MainMenu, footer, header [data-testid="stToolbar"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
}
</style>
"""


def apply_overhaul():
    """Inject the overhaul CSS. Safe to call once per render."""
    st.markdown(OVERHAUL_CSS, unsafe_allow_html=True)


def render_sidebar(role, name, menu_items):
    """
    Render the Amazon-style sidebar.
    menu_items = list of (icon, label, key) tuples.
    Returns the key of the chosen item, or None.
    """
    with st.sidebar:
        st.markdown(f"## 🏥 Meena Agencies")
        st.markdown(f"**{name}** · `{role.upper()}`")
        st.markdown("---")

        for icon, label, key in menu_items:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                return key

        st.markdown("---")
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
            return "logout"

    return None
