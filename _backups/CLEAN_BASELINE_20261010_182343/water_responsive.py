"""
water_responsive.py — ONE module. Works on every device. Flows like water.

Rule: the page adapts to CONTAINER WIDTH, not device name.
Works today, tomorrow, and on devices that don't exist yet.
"""
import streamlit as st


def inject():
    """Call once, right after set_page_config. Handles everything."""
    if st.session_state.get("_water_responsive_done"):
        return

    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════
       1. RESET — kill all Streamlit default width limits
       ═══════════════════════════════════════════════════════════ */
    :root {
        --water-max: min(100vw, 1800px);
        --water-pad-x: clamp(0.5rem, 2vw, 3rem);
        --water-pad-y: clamp(0.5rem, 1.5vh, 2rem);
        --water-gap: clamp(0.4rem, 1vw, 1rem);
    }

    /* Every possible container name Streamlit uses */
    .main .block-container,
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMainBlockContainer"],
    section.main > div.block-container,
    [data-testid="stAppViewContainer"] > .main > .block-container,
    section[data-testid="stMain"] > div > div > div {
        width: 100% !important;
        max-width: var(--water-max) !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: var(--water-pad-x) !important;
        padding-right: var(--water-pad-x) !important;
        padding-top: var(--water-pad-y) !important;
    }

    /* Kill any fixed-height containers that block flow */
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="column"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }

    /* ═══════════════════════════════════════════════════════════
       2. FLUID TYPOGRAPHY — scales with viewport
       ═══════════════════════════════════════════════════════════ */
    html, body, [class*="css"] {
        font-size: clamp(14px, 0.95vw + 10px, 17px) !important;
    }
    h1 { font-size: clamp(1.3rem, 1.5vw + 1rem, 2.4rem) !important; }
    h2 { font-size: clamp(1.1rem, 1.2vw + 0.9rem, 1.9rem) !important; }
    h3 { font-size: clamp(1rem, 1vw + 0.8rem, 1.5rem) !important; }
    p, li, span, .stMarkdown {
        font-size: clamp(0.85rem, 0.6vw + 0.7rem, 1rem) !important;
        line-height: 1.5 !important;
    }
    code, pre {
        font-size: clamp(0.72rem, 0.5vw + 0.6rem, 0.88rem) !important;
        overflow-x: auto !important;
        max-width: 100% !important;
    }

    /* ═══════════════════════════════════════════════════════════
       3. FLUID COLUMNS — wrap naturally
       ═══════════════════════════════════════════════════════════ */
    [data-testid="column"] {
        padding-left: calc(var(--water-gap) / 2) !important;
        padding-right: calc(var(--water-gap) / 2) !important;
    }

    /* ═══════════════════════════════════════════════════════════
       4. FLUID METRICS
       ═══════════════════════════════════════════════════════════ */
    [data-testid="stMetric"] {
        padding: clamp(0.5rem, 1vw, 1.2rem) !important;
        min-height: 0 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.1rem, 1.5vw + 0.6rem, 2rem) !important;
        line-height: 1.1 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.6rem, 0.5vw + 0.5rem, 0.85rem) !important;
    }

    /* ═══════════════════════════════════════════════════════════
       5. FLUID BUTTONS — touch-friendly everywhere
       ═══════════════════════════════════════════════════════════ */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        padding: clamp(0.5rem, 0.8vw, 0.8rem) clamp(0.8rem, 1.5vw, 1.5rem) !important;
        font-size: clamp(0.8rem, 0.6vw + 0.6rem, 1rem) !important;
        min-height: clamp(40px, 5vh, 48px) !important;
        white-space: nowrap !important;
    }

    /* ═══════════════════════════════════════════════════════════
       6. FLUID TABS — wrap to multiple rows if needed
       ═══════════════════════════════════════════════════════════ */
    [data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: 0.25rem !important;
        overflow-x: auto !important;
    }
    [data-baseweb="tab"] {
        font-size: clamp(0.72rem, 0.5vw + 0.55rem, 0.9rem) !important;
        padding: clamp(0.4rem, 0.8vw, 0.75rem) clamp(0.6rem, 1vw, 1.1rem) !important;
        white-space: nowrap !important;
    }

    /* ═══════════════════════════════════════════════════════════
       7. FLUID TABLES & CHARTS
       ═══════════════════════════════════════════════════════════ */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }
    .js-plotly-plot, [data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* ═══════════════════════════════════════════════════════════
       8. FLUID IMAGES
       ═══════════════════════════════════════════════════════════ */
    img {
        max-width: 100% !important;
        height: auto !important;
        object-fit: contain !important;
    }
    [data-testid="stImage"] img {
        max-width: 100% !important;
    }

    /* ═══════════════════════════════════════════════════════════
       9. FLUID SIDEBAR
       ═══════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        width: clamp(220px, 22vw, 340px) !important;
        min-width: 200px !important;
    }

    /* ═══════════════════════════════════════════════════════════
       10. KILL HORIZONTAL SCROLL — the #1 mobile bug
       ═══════════════════════════════════════════════════════════ */
    html, body, .stApp, .main, section.main, [data-testid="stAppViewContainer"] {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* ═══════════════════════════════════════════════════════════
       11. NARROW PHONES (< 480px) — force 1 column
       ═══════════════════════════════════════════════════════════ */
    @media (max-width: 480px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="column"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 100% !important;
            margin-bottom: 0.4rem !important;
        }
        [data-baseweb="tab"] {
            font-size: 0.7rem !important;
            padding: 0.35rem 0.6rem !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       12. PHONES LANDSCAPE & SMALL TABLETS (480-768px) — 2 cols max
       ═══════════════════════════════════════════════════════════ */
    @media (min-width: 481px) and (max-width: 768px) {
        [data-testid="column"] {
            min-width: calc(50% - var(--water-gap)) !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       13. TABLETS (768-1024px)
       ═══════════════════════════════════════════════════════════ */
    @media (min-width: 769px) and (max-width: 1024px) {
        :root { --water-pad-x: 1.5rem; }
    }

    /* ═══════════════════════════════════════════════════════════
       14. LARGE SCREENS (1920px+)
       ═══════════════════════════════════════════════════════════ */
    @media (min-width: 1920px) {
        :root { --water-max: 1800px; --water-pad-x: 3rem; }
    }
    @media (min-width: 2560px) {
        :root { --water-max: 2200px; --water-pad-x: 4rem; }
    }

    /* ═══════════════════════════════════════════════════════════
       15. TOUCH DEVICES — bigger hit targets
       ═══════════════════════════════════════════════════════════ */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
            min-height: 44px !important;
            min-width: 44px !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       16. HIDE STREAMLIT CHROME
       ═══════════════════════════════════════════════════════════ */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* ═══════════════════════════════════════════════════════════
       17. FLEXIBLE TEXT — never overflow
       ═══════════════════════════════════════════════════════════ */
    .stMarkdown, .stText {
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        hyphens: auto !important;
    }

    /* ═══════════════════════════════════════════════════════════
       18. PRESERVE DARK THEME
       ═══════════════════════════════════════════════════════════ */
    .stApp { background: #0a0e27 !important; }

    /* ═══════════════════════════════════════════════════════════
       19. SMOOTH SCROLLING
       ═══════════════════════════════════════════════════════════ */
    html { scroll-behavior: smooth; }
    body { -webkit-overflow-scrolling: touch; }

    /* ═══════════════════════════════════════════════════════════
       20. REDUCED MOTION RESPECT
       ═══════════════════════════════════════════════════════════ */
    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    st.session_state["_water_responsive_done"] = True
