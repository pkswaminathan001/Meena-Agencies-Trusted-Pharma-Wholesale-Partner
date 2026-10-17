"""
dense_layout.py v2 — nuclear whitespace removal.
Targets every possible source of Streamlit gap.
"""
import streamlit as st


_CSS = """
<style>
/* ══════════════════════════════════════════════════════════
   GLOBAL — reset every margin Streamlit adds
   ══════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    margin-top: 0.2rem !important;
    margin-bottom: 0.15rem !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 1.2 !important;
}
p, .stMarkdown, [data-testid="stMarkdownContainer"] {
    margin-top: 0 !important;
    margin-bottom: 0.2rem !important;
}
[data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.2rem !important;
}

/* ══════════════════════════════════════════════════════════
   THE BIG ONE — vertical block gap
   ══════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stVerticalBlockBorderWrapper"] > div > div {
    gap: 0.2rem !important;
    row-gap: 0.2rem !important;
}

/* Element containers */
[data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* ══════════════════════════════════════════════════════════
   Horizontal block gaps — kill column spacing
   ══════════════════════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] {
    gap: 0.4rem !important;
    column-gap: 0.4rem !important;
}

/* ══════════════════════════════════════════════════════════
   Main content container
   ══════════════════════════════════════════════════════════ */
.block-container {
    padding-top: 0.05rem !important;
    padding-bottom: 0.4rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    max-width: 100% !important;
}
.main, [data-testid="stAppViewContainer"] > .main {
    padding-top: 0 !important;
}

/* ══════════════════════════════════════════════════════════
   Metrics — compact
   ══════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    padding: 0.4rem 0.7rem !important;
    margin: 0 !important;
    min-height: 0 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.15rem !important;
    margin-bottom: 0 !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    margin: 0 !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.7rem !important;
}

/* ══════════════════════════════════════════════════════════
   Dividers — kill the giant <hr> gap
   ══════════════════════════════════════════════════════════ */
hr, [data-testid="stDivider"] {
    margin: 0.3rem 0 !important;
    padding: 0 !important;
}

/* ══════════════════════════════════════════════════════════
   Custom classes used by your app
   ══════════════════════════════════════════════════════════ */
.corp-section {
    margin: 0.4rem 0 0.3rem 0 !important;
    padding: 0 !important;
}
.corp-section-title {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}
.corp-section-sub {
    margin: 0.1rem 0 0.3rem 0 !important;
    padding: 0 !important;
    font-size: 0.8rem !important;
}

/* ══════════════════════════════════════════════════════════
   Alerts
   ══════════════════════════════════════════════════════════ */
.stAlert {
    padding: 0.5rem 0.8rem !important;
    margin: 0.2rem 0 !important;
    font-size: 0.85rem !important;
}
.stAlert p { margin: 0 !important; }

/* ══════════════════════════════════════════════════════════
   Buttons
   ══════════════════════════════════════════════════════════ */
.stButton > button {
    padding: 0.35rem 0.8rem !important;
    min-height: 34px !important;
    font-size: 0.85rem !important;
    margin: 0 !important;
}

/* ══════════════════════════════════════════════════════════
   Tabs, expanders
   ══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px !important;
    padding: 3px !important;
    margin-bottom: 0.3rem !important;
}
.stTabs [data-baseweb="tab"] {
    padding: 4px 12px !important;
    min-height: 30px !important;
    font-size: 0.82rem !important;
}
[data-testid="stExpander"] {
    margin: 0.15rem 0 !important;
}
[data-testid="stExpander"] summary {
    padding: 0.35rem 0.7rem !important;
    min-height: 36px !important;
    font-size: 0.85rem !important;
}

/* ══════════════════════════════════════════════════════════
   Columns — no internal padding on wrappers
   ══════════════════════════════════════════════════════════ */
[data-testid="column"] {
    padding: 0 !important;
}

/* ══════════════════════════════════════════════════════════
   MOBILE — even tighter
   ══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        padding-top: 0.05rem !important;
        padding-bottom: 0.3rem !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;
        row-gap: 0.15rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.25rem !important;
    }
    [data-testid="stMetric"] {
        padding: 0.35rem 0.5rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 0.95rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.6rem !important;
    }
    h1 { font-size: 1.2rem !important; }
    h2 { font-size: 1.05rem !important; }
    h3 { font-size: 0.95rem !important; }
    hr { margin: 0.2rem 0 !important; }
    .corp-section { margin: 0.25rem 0 !important; }
    .corp-section-title { font-size: 1.05rem !important; }
    .corp-section-sub { font-size: 0.75rem !important; }
    .stAlert { padding: 0.4rem 0.6rem !important; margin: 0.15rem 0 !important; }
    .stButton > button { min-height: 32px !important; padding: 0.3rem 0.6rem !important; }
}
</style>
"""


def apply():
    try:
        # st.html reaches the DOM directly in Streamlit 1.32+
        try:
            st.html(_CSS)
        except Exception:
            st.markdown(_CSS, unsafe_allow_html=True)
    except Exception as e:
        print("dense_layout v2 skipped:", e)


try:
    apply()
except Exception:
    pass
