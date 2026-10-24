import streamlit as st

def render_pricing_sandbox(*args, **kwargs):
    """Fallback for pricing sandbox to prevent app crash."""
    st.info("Pricing Sandbox is currently under maintenance.")
    return None
