"""ux_flow.py - UX Flow helpers for Meena Agencies.
Welcome screens, keyboard shortcuts, undo toasts, onboarding.
Nothing replaced - only new helpers."""
import streamlit as st
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════
# WELCOME FLOW
# ═══════════════════════════════════════════════

def is_first_visit(key: str) -> bool:
    """Check if this is the first visit for a feature."""
    flag = f"_seen_{key}"
    if st.session_state.get(flag):
        return False
    st.session_state[flag] = True
    return True


def welcome_card(name: str, role: str = "owner"):
    """Show a friendly welcome card on first login."""
    if not is_first_visit(f"welcome_{role}"):
        return

    greeting = "Good morning" if datetime.now().hour < 12 else (
               "Good afternoon" if datetime.now().hour < 17 else "Good evening")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,97,255,0.15));
                border:1px solid rgba(0,212,255,0.4);
                border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;">
        <h2 style="color:#00d4ff;margin:0;">👋 {greeting}, {name}!</h2>
        <p style="color:#e8eaf6;margin:0.5rem 0 0 0;font-size:1.05rem;">
            Here's what you can do today:
        </p>
    </div>
    """, unsafe_allow_html=True)


def welcome_actions(actions: list):
    """
    Show 3 welcome action buttons.
    actions = [{"icon": "📦", "label": "View Orders", "key": "orders"}]
    """
    if not actions:
        return None

    st.markdown("### 🎯 Quick Actions")
    cols = st.columns(len(actions))
    clicked = None
    for col, action in zip(cols, actions):
        with col:
            if st.button(
                f"{action['icon']}  {action['label']}",
                key=f"welcome_{action['key']}",
                use_container_width=True,
                type=action.get("type", "secondary")
            ):
                clicked = action["key"]
    return clicked


# ═══════════════════════════════════════════════
# CONTINUE WHERE YOU LEFT OFF
# ═══════════════════════════════════════════════

def remember_tab(tab_name: str):
    """Save the current tab so we can restore it next visit."""
    st.session_state["_last_tab"] = tab_name


def get_last_tab() -> str:
    """Get the last visited tab."""
    return st.session_state.get("_last_tab", "")


def continue_banner(user_name: str = ""):
    """Show 'continue where you left off' banner."""
    last_tab = get_last_tab()
    if not last_tab:
        return None

    st.markdown(f"""
    <div style="background:rgba(123,97,255,0.10);border-left:3px solid #7b61ff;
                padding:0.7rem 1rem;border-radius:8px;margin-bottom:1rem;font-size:0.9rem;">
        👋 Welcome back{", " + user_name if user_name else ""}. You were last viewing:
        <b style="color:#7b61ff;">{last_tab}</b>
    </div>
    """, unsafe_allow_html=True)
    return last_tab


# ═══════════════════════════════════════════════
# KEYBOARD SHORTCUTS
# ═══════════════════════════════════════════════

def inject_shortcuts():
    """Inject JavaScript for keyboard shortcuts."""
    st.markdown("""
    <script>
    (function() {
        // Ctrl+K = focus first text input (search)
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                var inputs = document.querySelectorAll('input[type="text"], input[type="search"]');
                if (inputs.length > 0) {
                    inputs[0].focus();
                    inputs[0].select();
                }
            }
        });

        // Escape = blur focus (close dropdown)
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.activeElement.blur();
            }
        });
    })();
    </script>
    """, unsafe_allow_html=True)


def shortcut_hint(keys: str, action: str):
    """Show a small hint about keyboard shortcuts."""
    st.caption(f"⌨️ Press **{keys}** to {action}")


# ═══════════════════════════════════════════════
# UNDO SYSTEM (30 sec)
# ═══════════════════════════════════════════════

def register_undo(action_id: str, description: str, undo_data: dict):
    """Register an action that can be undone for 30 seconds."""
    st.session_state.setdefault("_undo_stack", {})
    st.session_state["_undo_stack"][action_id] = {
        "description": description,
        "data": undo_data,
        "expires_at": (datetime.now() + timedelta(seconds=30)).isoformat(),
    }


def show_undo_prompt(action_id: str, undo_callback):
    """Show undo button if action is still reversible."""
    stack = st.session_state.get("_undo_stack", {})
    if action_id not in stack:
        return False

    item = stack[action_id]
    try:
        expires = datetime.fromisoformat(item["expires_at"])
    except Exception:
        del stack[action_id]
        return False

    if datetime.now() > expires:
        del stack[action_id]
        return False

    secs_left = int((expires - datetime.now()).total_seconds())

    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption(f"↩️ {item['description']}")
    with col2:
        if st.button(f"Undo ({secs_left}s)", key=f"undo_{action_id}"):
            undo_callback(item["data"])
            del stack[action_id]
            st.rerun()
    return True


# ═══════════════════════════════════════════════
# ONBOARDING HINTS
# ═══════════════════════════════════════════════

def hint(tab_key: str, title: str, message: str):
    """Show a one-time onboarding hint for a tab."""
    flag = f"_hint_seen_{tab_key}"
    if st.session_state.get(flag):
        return

    st.info(f"💡 **{title}** — {message}")
    if st.button("Got it", key=f"hint_dismiss_{tab_key}"):
        st.session_state[flag] = True
        st.rerun()
