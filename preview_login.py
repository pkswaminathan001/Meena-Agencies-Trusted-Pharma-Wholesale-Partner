import sys
sys.argv = ["preview"]
import streamlit as st
from auth_screen import render_login

st.set_page_config(page_title="Login Preview", layout="centered", page_icon="🦚")

result = render_login()
if result:
    st.success(f"✅ Would log in as: {result['role']} · {result['name']}")
    st.info("This is a preview only. Your real app uses the old login.")
    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()
