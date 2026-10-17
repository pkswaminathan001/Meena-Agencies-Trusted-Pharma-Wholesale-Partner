"""
theme.py — the ONLY place CSS lives in this app.
- No :has()
- No position:absolute on interactive elements
- Uses st.html() so it lands in the real DOM
- Scoped selectors only
"""
import streamlit as st

_CSS = """
<style>
/* ── Base ───────────────────────────────────────────── */
html, body, .stApp {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, "Helvetica Neue", Arial, sans-serif;
}
.stApp { background: #f7f8fa; }

/* ── Main content column: centered, never clipped ───── */
[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 1100px;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    margin-left: auto;
    margin-right: auto;
}

/* ── Sidebar ────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #1e2430;
}
[data-testid="stSidebar"] * {
    color: #e8ecf1;
}
[data-testid="stSidebar"] .stButton > button {
    color: #e8ecf1;
    background: transparent;
    border: 1px solid rgba(255,255,255,0.12);
    justify-content: flex-start;
    text-align: left;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.08);
}

/* ── Buttons (main area) ───────────────────────────── */
.main .stButton > button {
    border-radius: 8px;
    font-weight: 500;
    border: 1px solid #d5d9e0;
}
.main .stButton > button:hover {
    border-color: #b8bfc9;
}

/* ── Bill history cards ─────────────────────────────── */
.pk-range-card {
    background: #fff;
    border: 1px solid #e5e8ed;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.pk-range-title     { font-size: 1.1rem; font-weight: 600; color: #1e2430; }
.pk-range-heading   { font-size: 0.95rem; color: #4b5563; margin-top: 0.25rem; }
.pk-range-sub       { font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem; }
.pk-section-label {
    font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; color: #6b7280; margin: 1rem 0 0.5rem 0;
}
.pk-range-summary {
    display: flex; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;
}
.pk-stat {
    flex: 1; min-width: 140px;
    background: #fff; border: 1px solid #e5e8ed; border-radius: 10px;
    padding: 0.75rem 1rem;
}
.pk-stat-label {
    font-size: 0.75rem; text-transform: uppercase;
    color: #6b7280; letter-spacing: 0.04em;
}
.pk-stat-value {
    font-size: 1.4rem; font-weight: 700; color: #1e2430; margin-top: 0.25rem;
}

/* ── Login page ─────────────────────────────────────── */
.login-logo {
    display: block;
    margin: 0 auto 1rem auto;
    max-width: 120px;
}

/* ── Mobile ─────────────────────────────────────────── */
@media (max-width: 640px) {
    [data-testid="stAppViewContainer"] > .main > .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    .pk-range-summary { flex-direction: column; }
    .pk-stat { min-width: 100%; }
}
</style>
"""

def apply():
    st.html(_CSS)
