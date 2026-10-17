"""
mobile_sidebar.py — Mobile sidebar toggle using session_state.
No JS, no iframes. Just Python + CSS.
"""
import streamlit as st


def render():
    """Render the ☰ toggle button. Call in main content area."""
    if "_mob_sb_open" not in st.session_state:
        st.session_state._mob_sb_open = True

    is_open = st.session_state._mob_sb_open
    transform = "translateX(0)" if is_open else "translateX(-110%)"

    st.markdown(f"""
    <style>
    /* Hide the anchor marker */
    .mob-toggle-anchor {{ display: none !important; }}

    /* Position the Streamlit button that comes right after the anchor */
    div[data-testid="stElementContainer"]:has(.mob-toggle-anchor)
    + div[data-testid="stElementContainer"] {{
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 2147483647 !important;
        width: auto !important;
    }}

    /* Style the button as a purple square */
    div[data-testid="stElementContainer"]:has(.mob-toggle-anchor)
    + div[data-testid="stElementContainer"] button {{
        background: #4f46e5 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        width: 46px !important;
        height: 46px !important;
        min-height: 46px !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        box-shadow: 0 6px 18px rgba(79,70,229,0.5) !important;
        padding: 0 !important;
        line-height: 1 !important;
    }}

    /* Mobile: sidebar becomes sliding overlay */
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            width: 82vw !important;
            max-width: 320px !important;
            min-width: 0 !important;
            z-index: 999999 !important;
            box-shadow: 6px 0 32px rgba(0,0,0,0.35) !important;
            transform: {transform} !important;
            transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        .main, [data-testid="stAppViewContainer"] > .main {{
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }}
    }}

    /* Desktop: no toggle button */
    @media (min-width: 769px) {{
        div[data-testid="stElementContainer"]:has(.mob-toggle-anchor)
        + div[data-testid="stElementContainer"] {{
            display: none !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # Anchor for CSS to find the button
    st.markdown('<span class="mob-toggle-anchor"></span>', unsafe_allow_html=True)

    # The real button
    icon = "✕" if is_open else "☰"
    if st.button(icon, key="mob_sb_toggle_btn", help="Toggle menu"):
        st.session_state._mob_sb_open = not is_open
        st.rerun()
