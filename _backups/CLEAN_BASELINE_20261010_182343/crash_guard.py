"""
crash_guard.py — Makes the app bulletproof.
Any error anywhere → friendly message, no crash, silent logging.
"""
import streamlit as st
import traceback
from datetime import datetime
from pathlib import Path


ERROR_LOG = Path("app_errors.log")


def log_error(e: Exception, context: str = ""):
    """Log error silently — never shown to user."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"TIME:    {datetime.now().isoformat()}\n")
            f.write(f"CONTEXT: {context}\n")
            f.write(f"ERROR:   {type(e).__name__}: {e}\n")
            f.write(traceback.format_exc())
    except Exception:
        pass  # never let logging itself crash


def safe_button(label, key=None, **kwargs):
    """
    A drop-in replacement for st.button that never crashes.
    Returns True if clicked, False otherwise.
    """
    try:
        return st.button(label, key=key, **kwargs)
    except Exception as e:
        log_error(e, f"button:{label}")
        return False


def safe_run(func, *args, **kwargs):
    """
    Wrap any function so it never crashes the app.
    Usage: safe_run(my_function, arg1, arg2)
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error(e, f"safe_run:{func.__name__}")
        st.error("⚠️ Something went wrong. Please try again.")
        return None


def install_guard():
    """
    Install global protections. Call this once at the top of app.py.
    """
    try:
        # Hide full tracebacks from users
        st.set_option("client.showErrorDetails", False)
    except Exception:
        pass

    # Ensure session state keys always exist
    defaults = {
        "role": None,
        "cart": [],
        "retailer": None,
        "pending_order": None,
        "login_attempts": 0,
        "password_correct": False,
        "cart_bounce_at": None,
        "_meena_reorder_flash": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            try:
                st.session_state[k] = v if not isinstance(v, list) else []
            except Exception:
                pass


def safe_section(name: str):
    """
    Context manager to wrap any section of code.
    Usage:
        with safe_section("my feature"):
            # risky code
    """
    class _SafeSection:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                log_error(exc_val, f"section:{name}")
                st.error(f"⚠️ {name} had an issue. The rest of the app continues working.")
                return True  # swallow the exception
            return False
    return _SafeSection()
