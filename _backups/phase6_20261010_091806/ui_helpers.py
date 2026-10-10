"""ui_helpers.py - Reusable UI components for Meena Agencies.
Adds friendly empty states, loading indicators, success/error toasts.
Nothing replaced - only new helpers."""
import streamlit as st


def empty_orders(action_label="Place First Order"):
    """Empty state when there are no orders."""
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;">
        <div style="font-size:4rem;opacity:0.6;">📦</div>
        <h3 style="color:#e8eaf6;margin-top:1rem;">No orders yet</h3>
        <p style="color:#8892b0;margin:0.5rem 0 1.5rem 0;">
            When your first order arrives, you'll see it here.
        </p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(f"➕ {action_label}", type="primary", use_container_width=False)


def empty_retailers(action_label="Add Retailer"):
    """Empty state for retailers."""
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;">
        <div style="font-size:4rem;opacity:0.6;">🏪</div>
        <h3 style="color:#e8eaf6;margin-top:1rem;">No retailers yet</h3>
        <p style="color:#8892b0;margin:0.5rem 0 1.5rem 0;">
            Add your first retailer to start taking orders.
        </p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(f"➕ {action_label}", type="primary", use_container_width=False)


def empty_inventory(action_label="Add Stock"):
    """Empty state for inventory."""
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;">
        <div style="font-size:4rem;opacity:0.6;">💊</div>
        <h3 style="color:#e8eaf6;margin-top:1rem;">No inventory yet</h3>
        <p style="color:#8892b0;margin:0.5rem 0 1.5rem 0;">
            Add stock to start tracking batches and expiry.
        </p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(f"➕ {action_label}", type="primary", use_container_width=False)


def empty_generic(icon, title, message, action_label=None):
    """Generic empty state."""
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;">
        <div style="font-size:4rem;opacity:0.6;">{icon}</div>
        <h3 style="color:#e8eaf6;margin-top:1rem;">{title}</h3>
        <p style="color:#8892b0;margin:0.5rem 0 1.5rem 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    if action_label:
        return st.button(f"➕ {action_label}", type="primary")
    return None


def loading_box(text="Loading..."):
    """Friendly loading indicator."""
    placeholder = st.empty()
    placeholder.markdown(f"""
    <div style="text-align:center;padding:2rem;color:#8892b0;">
        <div style="font-size:2rem;animation:pulse 1.5s ease-in-out infinite;">⏳</div>
        <div style="margin-top:0.5rem;">{text}</div>
    </div>
    <style>
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}
    </style>
    """, unsafe_allow_html=True)
    return placeholder


def toast_success(title, message="", action_label=None):
    """Success toast with optional action button."""
    st.markdown(f"""
    <div style="background:rgba(0,212,122,0.12);border-left:4px solid #00d47a;
                padding:1rem;border-radius:10px;margin:0.5rem 0;">
        <b style="color:#00d47a;font-size:1.05rem;">✅ {title}</b>
        {f'<p style="color:#e8eaf6;margin:0.3rem 0 0 0;">{message}</p>' if message else ''}
    </div>
    """, unsafe_allow_html=True)
    if action_label:
        return st.button(action_label, type="primary")


def toast_error(title, message="", action_label="Retry"):
    """Error toast with retry button."""
    st.markdown(f"""
    <div style="background:rgba(255,77,109,0.12);border-left:4px solid #ff4d6d;
                padding:1rem;border-radius:10px;margin:0.5rem 0;">
        <b style="color:#ff4d6d;font-size:1.05rem;">❌ {title}</b>
        {f'<p style="color:#e8eaf6;margin:0.3rem 0 0 0;">{message}</p>' if message else ''}
    </div>
    """, unsafe_allow_html=True)
    if action_label:
        return st.button(action_label)


def toast_warning(title, message=""):
    """Warning toast."""
    st.markdown(f"""
    <div style="background:rgba(255,181,71,0.12);border-left:4px solid #ffb547;
                padding:1rem;border-radius:10px;margin:0.5rem 0;">
        <b style="color:#ffb547;font-size:1.05rem;">⚠️ {title}</b>
        {f'<p style="color:#e8eaf6;margin:0.3rem 0 0 0;">{message}</p>' if message else ''}
    </div>
    """, unsafe_allow_html=True)


def confirm_dialog(title, message, confirm_label="Yes, Continue", cancel_label="Cancel"):
    """Simple confirm dialog. Returns True if confirmed."""
    st.warning(f"**{title}**\n\n{message}")
    c1, c2 = st.columns(2)
    with c1:
        confirmed = st.button(f"✅ {confirm_label}", type="primary", use_container_width=True)
    with c2:
        cancelled = st.button(f"❌ {cancel_label}", use_container_width=True)
    if cancelled:
        st.info("Cancelled.")
        return False
    return confirmed


def section_header(title, subtitle=""):
    """Consistent section header."""
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
