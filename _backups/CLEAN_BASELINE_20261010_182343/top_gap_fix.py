import streamlit as st

_CSS = """
<style>
@media (max-width: 768px) {
  html body .stApp [data-testid="stMainBlockContainer"],
  html body .stApp .block-container,
  html body .stApp section.main > div.block-container {
      --water-pad-y: 3.5rem !important;
      padding-top: 0.05rem !important;
      padding-left: 0.75rem !important;
      padding-right: 0.75rem !important;
  }
  html body .stApp [data-testid="stMain"],
  html body .stApp [data-testid="stAppViewContainer"] > .main {
      padding-top: 0 !important;
  }
  html body .stApp .corp-hero { margin-top: 0 !important; }
}
</style>
"""

def apply():
    st.markdown(_CSS, unsafe_allow_html=True)


# ── READABILITY BOOST — bigger fonts for medicine cards ──
_READABLE_CSS = """
<style>
/* Medicine card — name */
.med-name, .ma-med-name, [class*="med-name"] {
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    line-height: 1.25 !important;
}

/* Medicine card — price */
.med-price, .ma-med-price, [class*="med-price"] {
    font-size: 1.5rem !important;
    font-weight: 900 !important;
}

/* Medicine card — meta (Exp, units, batches) */
.med-meta, .ma-med-meta, [class*="med-meta"] {
    font-size: 0.92rem !important;
    color: #c8d1e8 !important;
    font-weight: 600 !important;
    line-height: 1.35 !important;
}

/* Medicine card — stock line */
.med-stock, .ma-med-stock, [class*="med-stock"] {
    font-size: 0.92rem !important;
    font-weight: 700 !important;
}

/* Exp/units inline helpers used in some cards */
.med-card div, .ma-med-card div {
    font-size: 0.92rem !important;
    line-height: 1.35 !important;
}

/* Emoji icon on cards — slightly larger */
.med-emoji, .ma-med-emoji, [class*="med-emoji"] {
    font-size: 2.6rem !important;
}

/* Make card have a bit more internal padding to fit larger text */
.med-card, .ma-med-card {
    padding: 18px 14px 14px 14px !important;
    border-radius: 14px !important;
}

/* Select button — more prominent */
.stButton > button[kind="secondary"] {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    min-height: 44px !important;
}

/* Category pills — larger label */
.stButton > button {
    font-size: 0.92rem !important;
}

/* Caption — small text like 'Exp: Sep-2026' */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 0.85rem !important;
    color: #b0b8d0 !important;
}

/* Mobile — even bigger relative to screen */
@media (max-width: 480px) {
    .med-name, .ma-med-name {
        font-size: 1.2rem !important;
    }
    .med-price, .ma-med-price {
        font-size: 1.6rem !important;
    }
    .med-meta, .med-stock {
        font-size: 0.98rem !important;
    }
}
</style>
"""

try:
    import streamlit as _st_readable
    _st_readable.markdown(_READABLE_CSS, unsafe_allow_html=True)
except Exception:
    pass


# ── BILLS PAGE TOP GAP KILLER ──
_BILLS_TIGHT = """
<style>
/* Kill ALL top padding on the bills/statement page */
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"] > .main > div:first-child,
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0.3rem !important;
    margin-top: 0 !important;
}

/* First vertical block on page has no top margin */
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child,
[data-testid="stVerticalBlock"]:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Tighten headings on bills page */
h3, h4 {
    margin-top: 0.3rem !important;
    margin-bottom: 0.3rem !important;
    padding-top: 0 !important;
}

/* Tighten caption under headings */
[data-testid="stCaptionContainer"] {
    margin-top: 0 !important;
    margin-bottom: 0.3rem !important;
    padding: 0 !important;
}

/* Tighten the first markdown block after the hero */
[data-testid="stMarkdownContainer"]:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Mobile — kill gap even harder */
@media (max-width: 768px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 0.15rem !important;
    }
    h3, h4 { margin-top: 0.15rem !important; }
}
</style>
"""

try:
    import streamlit as _st_bills
    _st_bills.markdown(_BILLS_TIGHT, unsafe_allow_html=True)
except Exception:
    pass


# ── COLLAPSE_INVISIBLE_TOP — zero out hidden widgets at top of page ──
_COLLAPSE_TOP = """
<style>
/* The first 4 element containers on the page are:
   1. mobile_sidebar button (position: fixed)
   2. top_gap_fix markdown (invisible)
   3. cart_widget popover (position: fixed)
   4. cart_widget badge markdown (invisible)
   They all reserve flow space. Collapse them. */

[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:nth-child(1),
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:nth-child(2),
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:nth-child(3),
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:nth-child(4) {
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}

/* Also collapse any stMarkdown that only contains CSS */
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdownContainer"] style) {
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Kill the block container padding entirely */
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
.block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Any horizontal block right after the collapsed ones — no margin */
[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child {
    margin-top: 0 !important;
}
</style>
"""

try:
    import streamlit as _st_ct
    _st_ct.markdown(_COLLAPSE_TOP, unsafe_allow_html=True)
except Exception:
    pass
