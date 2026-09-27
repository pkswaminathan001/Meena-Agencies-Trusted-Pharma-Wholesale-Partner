"""
responsive.py — Full responsive design across mobile, tablet, desktop.
Detects device width and adapts layout automatically.
"""
import streamlit as st


def inject_responsive():
    """Call once at top of app. Handles all breakpoints."""
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════
       RESPONSIVE MASTER STYLESHEET
       Mobile first · Fluid typography · Auto-stacking layout
       ═══════════════════════════════════════════════════════════ */

    /* ─── Viewport meta (forces proper mobile scaling) ─── */
    @viewport {
        width: device-width;
        initial-scale: 1.0;
        maximum-scale: 5.0;
        user-scalable: yes;
    }

    /* ─── Fluid root font size ─── */
    html {
        font-size: clamp(14px, 1.4vw, 18px);
        -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
    }

    /* ─── Base layout fluid padding ─── */
    .block-container {
        max-width: 100% !important;
        padding: clamp(1rem, 3vw, 4rem) !important;
    }
    .stApp {
        min-height: 100vh;
        overflow-x: hidden;
    }

    /* ─── Fluid typography ─── */
    h1, .title, .hero-title, .corp-title {
        font-size: clamp(1.6rem, 5vw, 3.5rem) !important;
        line-height: 1.15 !important;
    }
    h2 {
        font-size: clamp(1.3rem, 3.5vw, 2.2rem) !important;
    }
    h3, .section-title, .corp-section-title {
        font-size: clamp(1.1rem, 2.5vw, 1.6rem) !important;
    }
    h4 { font-size: clamp(1rem, 2vw, 1.3rem) !important; }

    p, .stMarkdown, .stCaption {
        font-size: clamp(0.85rem, 1.2vw, 1rem);
    }

    /* ─── Button touch targets (mobile) ─── */
    .stButton > button {
        min-height: 44px;  /* Apple/Android recommended minimum */
        padding: clamp(0.5rem, 1.2vw, 0.9rem) clamp(0.8rem, 2vw, 1.5rem) !important;
        font-size: clamp(0.85rem, 1.1vw, 1rem) !important;
    }

    /* ─── Metrics fluid ─── */
    [data-testid="stMetric"] {
        padding: clamp(0.8rem, 1.8vw, 1.8rem) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.3rem, 3vw, 2.5rem) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.7rem, 1vw, 0.85rem) !important;
    }

    /* ─── Tables scroll horizontally on narrow screens ─── */
    [data-testid="stDataFrame"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    /* ═══════════════════════════════════════════════════════════
       MOBILE: up to 640px
       ═══════════════════════════════════════════════════════════ */
    @media (max-width: 640px) {
        /* Stack all horizontal columns vertically */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.6rem !important;
        }
        /* Full-width inputs */
        .stTextInput, .stNumberInput, .stSelectbox, .stTextArea,
        .stMultiSelect, .stDateInput, .stRadio, .stCheckbox {
            width: 100% !important;
        }
        /* Hero adjustments */
        .corp-hero, .login-bg {
            padding: 2rem 1rem 1.5rem 1rem !important;
            margin: 0 !important;
        }
        .corp-title, .welcome-title, .hero-title {
            font-size: clamp(1.6rem, 8vw, 2.2rem) !important;
            letter-spacing: -0.5px !important;
        }
        .corp-subtitle, .welcome-subtitle {
            font-size: 0.8rem !important;
            letter-spacing: 1px !important;
        }
        .welcome-tamil {
            font-size: 1rem !important;
        }
        /* Rotating logo smaller on mobile */
        .rotating-logo {
            width: 110px !important;
            height: 110px !important;
        }
        /* Login buttons full width */
        .stButton > button {
            width: 100% !important;
            min-height: 50px !important;
        }
        /* Tabs scroll horizontally */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
            flex-wrap: nowrap !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 0.9rem !important;
            font-size: 0.8rem !important;
            white-space: nowrap !important;
        }
        /* Hide empty spacer columns */
        div[data-testid="column"]:empty {
            display: none !important;
        }
        /* Reduce expander padding */
        .streamlit-expanderHeader {
            font-size: 0.85rem !important;
            padding: 0.5rem 0.8rem !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       TABLET: 641px to 1024px
       ═══════════════════════════════════════════════════════════ */
    @media (min-width: 641px) and (max-width: 1024px) {
        /* Keep columns but reduce gap */
        div[data-testid="stHorizontalBlock"] {
            gap: 0.8rem !important;
        }
        .corp-title, .welcome-title {
            font-size: clamp(2rem, 5vw, 2.6rem) !important;
        }
        .rotating-logo {
            width: 130px !important;
            height: 130px !important;
        }
        /* 2-column tables become narrower */
        [data-testid="stDataFrame"] {
            font-size: 0.85rem !important;
        }
        /* Modest padding */
        .block-container {
            padding: 1.5rem 2rem !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       DESKTOP: 1025px and up
       ═══════════════════════════════════════════════════════════ */
    @media (min-width: 1025px) {
        .block-container {
            max-width: 1400px !important;
            margin: 0 auto !important;
            padding: 2rem 3rem !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       LARGE DESKTOP: 1600px+
       ═══════════════════════════════════════════════════════════ */
    @media (min-width: 1600px) {
        .block-container {
            max-width: 1600px !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       LANDSCAPE MOBILE (phone rotated)
       ═══════════════════════════════════════════════════════════ */
    @media (max-height: 500px) and (orientation: landscape) {
        .corp-hero, .login-bg {
            padding: 1rem !important;
        }
        .rotating-logo {
            width: 80px !important;
            height: 80px !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       PRINT (A4 optimized)
       ═══════════════════════════════════════════════════════════ */
    @media print {
        .stApp { background: #fff !important; }
        .block-container { padding: 0.5cm !important; }
        .stButton, .stSidebar, [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stDataFrame"] { font-size: 10pt !important; }
    }

    /* ═══════════════════════════════════════════════════════════
       TOUCH DEVICE TWEAKS
       ═══════════════════════════════════════════════════════════ */
    @media (hover: none) and (pointer: coarse) {
        /* Larger tap targets on touch devices */
        .stButton > button {
            min-height: 48px !important;
        }
        /* No hover transforms on touch (they look janky) */
        .stButton > button:hover {
            transform: none !important;
        }
        [data-testid="stMetric"]:hover {
            transform: none !important;
        }
        /* Increase click area of radio/checkbox */
        .stRadio label, .stCheckbox label {
            padding: 0.6rem !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       ACCESSIBILITY — reduced motion preference
       ═══════════════════════════════════════════════════════════ */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       DARK MODE / LIGHT MODE adaptation
       ═══════════════════════════════════════════════════════════ */
    @media (prefers-color-scheme: light) {
        /* If user has light mode, we still force our dark theme for consistency */
        .stApp {
            color-scheme: dark;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def detect_device():
    """Optional: JS snippet to log device category (for analytics)."""
    st.markdown("""
    <script>
    (function() {
        const w = window.innerWidth;
        let device = 'desktop';
        if (w < 640) device = 'mobile';
        else if (w < 1024) device = 'tablet';
        else if (w < 1600) device = 'laptop';
        else device = 'large-desktop';
        console.log('📱 Device:', device, '· Width:', w + 'px');
    })();
    </script>
    """, unsafe_allow_html=True)
