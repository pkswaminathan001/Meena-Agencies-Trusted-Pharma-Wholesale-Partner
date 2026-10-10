"""
navigation.py — Universal back-button + navigation history.
Works across roles, tabs, and sub-views.
"""
import streamlit as st


HISTORY_KEY = "_nav_history"
MAX_HISTORY = 20


# ═══════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════
def init_nav():
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []


def _snapshot():
    """Capture current navigation state."""
    return {
        "role": st.session_state.get("role"),
        "retailer": st.session_state.get("retailer", {}).get("id") if st.session_state.get("retailer") else None,
        "staff": st.session_state.get("staff", {}).get("id") if st.session_state.get("staff") else None,
        "page": st.session_state.get("current_page", "dashboard"),
    }


def _restore(snap):
    """Restore a prior state."""
    st.session_state.role = snap.get("role")
    # Retailer: reload from file if needed
    rid = snap.get("retailer")
    if rid:
        try:
            import json
            from pathlib import Path
            retailers = json.loads(Path("retailers.json").read_text())
            r = next((x for x in retailers if x["id"] == rid), None)
            if r:
                st.session_state.retailer = r
        except Exception:
            pass
    st.session_state.current_page = snap.get("page", "dashboard")


# ═══════════════════════════════════════════════════════════
# PUSH / POP
# ═══════════════════════════════════════════════════════════
def push():
    """Call BEFORE changing navigation state."""
    init_nav()
    hist = st.session_state[HISTORY_KEY]
    hist.append(_snapshot())
    if len(hist) > MAX_HISTORY:
        hist.pop(0)


def go_back():
    """Pop previous state and apply."""
    init_nav()
    hist = st.session_state[HISTORY_KEY]
    if not hist:
        # Nothing to go back to — clear session and go to login
        _hard_reset()
        return
    prev = hist.pop()
    _restore(prev)
    st.rerun()


def can_go_back():
    init_nav()
    return len(st.session_state[HISTORY_KEY]) > 0


def clear_history():
    st.session_state[HISTORY_KEY] = []


def _hard_reset():
    """Fallback — clear everything, back to login."""
    for k in list(st.session_state.keys()):
        try:
            del st.session_state[k]
        except Exception:
            pass
    st.rerun()


# ═══════════════════════════════════════════════════════════
# UNIVERSAL BACK BUTTON UI
# ═══════════════════════════════════════════════════════════
def render_back_button(label="← Back", key_suffix="", compact=True):
    """
    Render a Back button. Auto-hides if no history.
    Call this at the top of every view (login, dashboards, sub-views).
    """
    if not can_go_back():
        return False
    _key = f"nav_back_{key_suffix or 'default'}"
    if st.button(label, key=_key, help="Go back to previous screen"):
        go_back()
        return True
    return False


def render_back_bar(key_suffix="", show_home=True):
    """
    Always-visible back bar.
    Back: disabled if no history. Home: always active.
    """
    _has_back = can_go_back()

    _cols = st.columns([1, 1, 6])
    with _cols[0]:
        if st.button("← Back", key=f"bb_{key_suffix or 'x'}",
                     use_container_width=True, disabled=not _has_back):
            go_back()
    with _cols[1]:
        if show_home:
            if st.button("🏠 Home", key=f"bh_{key_suffix or 'x'}",
                         use_container_width=True):
                clear_history()
                for _k in list(st.session_state.keys()):
                    try:
                        del st.session_state[_k]
                    except Exception:
                        pass
                st.rerun()
