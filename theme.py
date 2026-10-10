"""theme.py - GUI Foundation for Meena Agencies.
One source of truth for colors, fonts, spacing, icons.
Nothing replaced - only added."""
import streamlit as st

# ═══════════════════════════════════════════════
# DESIGN TOKENS
# ═══════════════════════════════════════════════
COLORS = {
    "primary":    "#00d4ff",
    "secondary":  "#7b61ff",
    "success":    "#00d47a",
    "warning":    "#ffb547",
    "danger":     "#ff4d6d",
    "bg_dark":    "#0a0e27",
    "bg_mid":     "#0f1a3a",
    "text":       "#e8eaf6",
    "text_muted": "#8892b0",
}

FONTS = {
    "h1":   "2.5rem",
    "h2":   "2rem",
    "h3":   "1.5rem",
    "h4":   "1.15rem",
    "body": "1rem",
    "small": "0.85rem",
    "tiny": "0.7rem",
}

SPACING = {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
    "xxl": "3rem",
}

ICONS = {
    "orders":      "📦",
    "retailers":   "🏪",
    "inventory":   "💊",
    "money":       "💰",
    "reps":        "🚗",
    "analytics":   "📊",
    "alerts":      "⚠️",
    "success":     "✅",
    "error":       "❌",
    "pending":     "⏳",
    "approved":    "✅",
    "cancelled":   "❌",
}


def apply_theme():
    """Apply global GUI theme. Call once at top of app."""
    st.markdown("""
    <style>
    /* ─── Font scale ─── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    h1 { font-size: 2.5rem !important; font-weight: 800 !important; color: #e8eaf6 !important; }
    h2 { font-size: 2rem !important; font-weight: 700 !important; color: #e8eaf6 !important; }
    h3 { font-size: 1.5rem !important; font-weight: 700 !important; color: #e8eaf6 !important; }
    h4 { font-size: 1.15rem !important; font-weight: 600 !important; color: #00d4ff !important; }

    /* ─── Cards ─── */
    .ma-card {
        background: linear-gradient(145deg, #0f1a3a 0%, #0a0e27 100%);
        border: 1px solid rgba(0,212,255,0.18);
        border-radius: 14px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    /* ─── Buttons ─── */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,212,255,0.3);
    }

    /* ─── Metric cards ─── */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #0f1a3a, #0a0e27) !important;
        border: 1px solid rgba(0,212,255,0.15) !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8892b0 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(15,26,58,0.5);
        padding: 4px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(123,97,255,0.2));
        color: #00d4ff !important;
        font-weight: 700;
    }

    /* ─── Alerts ─── */
    .stAlert {
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)


def title(text, icon="", subtitle=""):
    """Render a consistent page title."""
    html = f'<h1>{icon} {text}</h1>'
    if subtitle:
        html += f'<p style="color:#8892b0;font-size:0.9rem;margin-top:-0.5rem;">{subtitle}</p>'
    st.markdown(html, unsafe_allow_html=True)


def card(content, accent="primary"):
    """Wrap content in a themed card."""
    color = COLORS.get(accent, COLORS["primary"])
    st.markdown(
        f'<div class="ma-card" style="border-left:4px solid {color};">{content}</div>',
        unsafe_allow_html=True,
    )


def empty_state(icon, title, message, action_label=None):
    """Show a friendly empty state."""
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;color:#8892b0;">
        <div style="font-size:3rem;">{icon}</div>
        <h3 style="color:#e8eaf6;margin-top:1rem;">{title}</h3>
        <p style="margin:0.5rem 0 1rem 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    if action_label:
        return st.button(action_label, type="primary")
    return None


def loading_state(text="Loading..."):
    """Friendly loading indicator."""
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;color:#8892b0;">
        <span style="display:inline-block;animation:spin 1s linear infinite;">⏳</span>
        {" "} {text}
    </div>
    <style>@keyframes spin {{ to {{ transform: rotate(360deg); }} }}</style>
    """, unsafe_allow_html=True)


def error_state(title, message, retry_label="Try Again"):
    """Friendly error with retry."""
    st.markdown(f"""
    <div style="background:rgba(255,77,109,0.1);border-left:4px solid #ff4d6d;
                padding:1rem;border-radius:10px;margin:0.5rem 0;">
        <b style="color:#ff4d6d;">{title}</b>
        <p style="color:#e8eaf6;margin:0.3rem 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(retry_label)


def success_state(title, message=""):
    """Friendly success."""
    st.markdown(f"""
    <div style="background:rgba(0,212,122,0.1);border-left:4px solid #00d47a;
                padding:1rem;border-radius:10px;margin:0.5rem 0;">
        <b style="color:#00d47a;">✅ {title}</b>
        {f'<p style="color:#e8eaf6;margin:0.3rem 0;">{message}</p>' if message else ''}
    </div>
    """, unsafe_allow_html=True)


def kpi_row(items):
    """Render a row of KPI metrics."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.metric(item["label"], item["value"], item.get("delta", ""))
