"""
compact_spacing.py — Intercepts Streamlit's divider calls and
replaces them with tight HTML lines. Works because we patch
the actual function, not CSS.
"""
import streamlit as st


# ── Preserve originals ──
_orig_markdown = st.markdown
_orig_write = st.write

_COMPACT_HR = (
    '<div style="height:1px;background:rgba(128,128,128,0.18);'
    'margin:6px 0;padding:0;"></div>'
)


def _patched_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        stripped = body.strip()
        # Replace bare divider with compact version
        if stripped == "---":
            return _orig_markdown(_COMPACT_HR, unsafe_allow_html=True)
        if stripped == "<hr>":
            return _orig_markdown(_COMPACT_HR, unsafe_allow_html=True)
        if stripped == "***":
            return _orig_markdown(_COMPACT_HR, unsafe_allow_html=True)
    return _orig_markdown(body, *args, **kwargs)


def _patched_write(body, *args, **kwargs):
    # Drop empty writes (used as spacers)
    if body == "" or body is None:
        return None
    return _orig_write(body, *args, **kwargs)


# ── Apply patches at import time ──
st.markdown = _patched_markdown
st.write = _patched_write


# ── Also patch st.divider if present ──
if hasattr(st, "divider"):
    _orig_divider = st.divider

    def _patched_divider(*args, **kwargs):
        return _orig_markdown(_COMPACT_HR, unsafe_allow_html=True)

    st.divider = _patched_divider


# ── And add a global tightener for section headings ──
_TOP_PAD_CSS = """
<style>
/* ══════════════════════════════════════════════════════════
   KILL THE TOP GAP — Streamlit's default block-container padding
   ══════════════════════════════════════════════════════════ */
.block-container {
    padding-top: 0.05rem !important;
    padding-bottom: 0.5rem !important;
}

/* Kill the top padding on Streamlit's main wrapper */
[data-testid="stAppViewContainer"] > .main > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0 !important;
}
[data-testid="stMain"] {
    padding-top: 0 !important;
}

/* Header toolbar — collapse */
[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    background: transparent !important;
}

/* First child of any vertical block — no top margin */
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Hero card used by app */
.corp-hero {
    margin-top: 0 !important;
    padding-top: 2rem !important;
}

/* Mobile — even tighter */
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.4rem !important;
    }
    .corp-hero {
        padding-top: 0.05rem !important;
    }
}
</style>
"""

_KILL_TOP_GAP = """
<style>
/* Aggressive: name every container Streamlit uses */
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
.stMain,
[data-testid="stMain"] > div,
[data-testid="stAppViewContainer"] > .main > div:first-child,
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0 !important;
    padding-bottom: 0.4rem !important;
    margin-top: 0 !important;
}

/* First vertical block on the page */
[data-testid="stVerticalBlock"]:first-child,
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child,
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Hero card — kill internal top padding */
.corp-hero {
    padding-top: 0.05rem !important;
    margin-top: 0 !important;
}
.corp-hero-inner {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Header toolbar */
[data-testid="stHeader"],
[data-testid="stToolbar"],
header[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Mobile — even tighter */
@media (max-width: 768px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 0 !important;
    }
    .corp-hero {
        padding-top: 0.05rem !important;
    }
}

/* ── Collapse the mobile ☰ button wrapper so it doesn't take flow space ── */
div[data-testid="stElementContainer"]:has(button[data-testid="stBaseButton-secondary"][kind="secondary"][aria-label="Toggle menu"]),
div[data-testid="stElementContainer"]:has(> div > button[kind="secondary"]),
div[data-testid="stElementContainer"]:has(.mob-toggle-anchor) + div[data-testid="stElementContainer"] {
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}

</style>
"""

def apply_css():
    try:
        st.markdown(_TOP_PAD_CSS, unsafe_allow_html=True)
        st.markdown(_KILL_TOP_GAP, unsafe_allow_html=True)
        st.markdown("""
        <style>
        hr { margin: 6px 0 !important; }
        [data-testid="stMarkdownContainer"] hr { margin: 6px 0 !important; }
        </style>
        """, unsafe_allow_html=True)
    except Exception:
        pass


try:
    apply_css()
except Exception:
    pass
