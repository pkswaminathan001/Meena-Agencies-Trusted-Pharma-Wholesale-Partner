"""
auth_gate.py — Extra security layer before the app loads.
Requires a password to even reach the login screen.
"""
import streamlit as st
import hmac

def check_password():
    """Returns True if the user has entered the correct access password."""
    def password_entered():
        try:
            expected = st.secrets["ACCESS_PASSWORD"]
        except Exception:
            # No password set — allow (dev mode)
            st.session_state["password_correct"] = True
            return
        if hmac.compare_digest(st.session_state["password"], expected):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("""
    <div style="max-width:420px;margin:80px auto;padding:32px;
                background:linear-gradient(135deg,#0e1d4a,#1a2a55);
                border-radius:16px;border:1px solid #00d4ff33;">
        <h2 style="color:#eaf6ff;text-align:center;">🔒 Meena Agencies</h2>
        <p style="color:#8892b0;text-align:center;font-size:0.9rem;">
            Authorised access only
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.text_input("Access Password", type="password",
                  on_change=password_entered, key="password")
    if st.session_state.get("password_correct") is False:
        st.error("❌ Wrong password")
    return False
