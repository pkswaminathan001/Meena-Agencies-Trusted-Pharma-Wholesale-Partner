"""overflow_fix.py — stops horizontal overflow on every screen. Load last."""
import streamlit as st

_CSS = """
<style>
html, body, .stApp {
    max-width: 100vw !important;
    overflow-x: hidden !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
    max-width: 100vw !important;
    overflow-x: hidden !important;
}
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stElementContainer"],
[data-testid="column"] {
    max-width: 100% !important;
    min-width: 0 !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 1 1 0% !important;
    overflow: hidden !important;
}
[data-testid="column"] > div {
    min-width: 0 !important;
    overflow: hidden !important;
}
img, iframe, video, canvas, svg {
    max-width: 100% !important;
    height: auto !important;
}
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    max-width: 100% !important;
    overflow-x: auto !important;
}
[data-testid="stMetric"],
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
.stButton > button,
.stDownloadButton > button {
    max-width: 100% !important;
}
</style>
"""

try:
    st.html(_CSS)
except Exception:
    st.markdown(_CSS, unsafe_allow_html=True)


def apply():
    pass  # st.html runs on import

apply()
