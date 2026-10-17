"""
theme.py — the ONLY place CSS lives.
Light sidebar, dark readable text, visible buttons.
"""
import streamlit as st

_CSS = """
<style>
/* ══════════════════════════════════════════════════════════════
   1. FORCE LIGHT SIDEBAR — beats any earlier dark-theme CSS
   ══════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"],
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e8ed !important;
}

/* ══════════════════════════════════════════════════════════════
   2. DARK TEXT EVERYWHERE INSIDE THE SIDEBAR
   ══════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] *,
[data-testid="stSidebar"] *,
[data-testid="stSidebarContent"] * {
    color: #1e2430 !important;
}

/* Header info block (MEENA AGENCIES / Wholesale Partner / etc.) */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #1e2430 !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] div {
    color: #1e2430 !important;
}

/* "Menu" and other section headings — muted, but readable */
[data-testid="stSidebar"] .stMarkdown p {
    color: #4b5563 !important;
}

/* ══════════════════════════════════════════════════════════════
   3. SIDEBAR BUTTONS — full-width, tappable, readable
   ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    background: #f7f8fa !important;
    color: #1e2430 !important;
    border: 1px solid #e0e4eb !important;
    border-radius: 10px !important;
    padding: 0.65rem 0.9rem !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    line-height: 1.2 !important;
    margin: 0 0 0.35rem 0 !important;
    min-height: 44px !important;
    transition: background 0.15s, border-color 0.15s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color: #1e2430 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #eef1f6 !important;
    border-color: #c8d0db !important;
}
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    background: #e6ebf2 !important;
    border-color: #b8bfc9 !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.18) !important;
}

/* Primary button (e.g. "My Profile") keeps the purple accent */
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
    background: #4f46e5 !important;
    border-color: #4f46e5 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"]:hover {
    background: #4338ca !important;
    border-color: #4338ca !important;
}

/* ══════════════════════════════════════════════════════════════
   4. DIVIDERS & SPACING
   ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid #e5e8ed !important;
    margin: 0.75rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════
   5. SIDEBAR COLLAPSE ARROW (mobile)
   ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button,
button[kind="header"] {
    color: #1e2430 !important;
    background: #ffffff !important;
    border: 1px solid #e5e8ed !important;
}

/* ══════════════════════════════════════════════════════════════
   6. MAIN CONTENT COLUMN — centered, never clipped
   ══════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 1100px;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    margin-left: auto;
    margin-right: auto;
}

/* ══════════════════════════════════════════════════════════════
   7. MOBILE
   ══════════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
    [data-testid="stAppViewContainer"] > .main > .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
}
</style>
"""

def apply():
    st.html(_CSS)
