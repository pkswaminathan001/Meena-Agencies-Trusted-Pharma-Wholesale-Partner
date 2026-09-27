"""
brand.py — Meena Agencies brand identity system.
Used everywhere: headers, footers, emails, invoices, OTPs.
"""
import streamlit as st
from datetime import datetime

# ────────────────────────────────────────────────
# BRAND CONSTANTS
# ────────────────────────────────────────────────
BRAND = {
    "name": "Meena Agencies",
    "short": "Meena",
    "tagline": "Trusted Pharma Wholesale Partner",
    "sub_tagline": "Serving Pharmacies Since 2015",
    "emoji": "💊",
    "logo_letter": "M",
    "address": "2661, South Main Street, near Indian Bank",
    "address2": "Rajakrishnapuram, Thanjavur, Tamilnadu — 613009",
    "phone": "6382130536",
    "email": "meena.agencies@gmail.com",
    "gstin": "33AAIFM8119N1ZW",
    "website": "www.meenaagencies.in",
}

# ────────────────────────────────────────────────
# BRAND COLORS
# ────────────────────────────────────────────────
BRAND_COLORS = {
    "primary":   "#00d4ff",   # Cyan — trust, technology
    "secondary": "#7b61ff",   # Purple — premium, health
    "accent":    "#ffb547",   # Gold — warmth, care
    "success":   "#00d47a",   # Green — health, growth
    "danger":    "#ff4d6d",   # Red — urgency
    "bg_dark":   "#0a0e27",
    "bg_card":   "rgba(26,31,58,0.7)",
}


# ────────────────────────────────────────────────
# BRAND CSS
# ────────────────────────────────────────────────
def inject_brand_css():
    """Global brand styling. Call once at top of app."""
    st.markdown(f"""
    <style>
    /* Brand accent variables */
    :root {{
        --brand-primary: {BRAND_COLORS['primary']};
        --brand-secondary: {BRAND_COLORS['secondary']};
        --brand-accent: {BRAND_COLORS['accent']};
        --brand-success: {BRAND_COLORS['success']};
        --brand-danger: {BRAND_COLORS['danger']};
    }}

    /* Brand gradient utility */
    .brand-gradient {{
        background: linear-gradient(90deg, {BRAND_COLORS['primary']}, {BRAND_COLORS['secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* Brand header */
    .brand-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0;
        border-bottom: 2px solid rgba(0,212,255,0.2);
        margin-bottom: 1.5rem;
        animation: brand-fade-in 0.5s ease-out;
    }}
    @keyframes brand-fade-in {{
        from {{ opacity: 0; transform: translateY(-8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .brand-logo {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }}
    .brand-icon {{
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background: linear-gradient(135deg, {BRAND_COLORS['primary']}, {BRAND_COLORS['secondary']});
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        box-shadow: 0 6px 20px rgba(0,212,255,0.35);
        animation: brand-pulse-glow 3s ease-in-out infinite;
    }}
    @keyframes brand-pulse-glow {{
        0%, 100% {{ box-shadow: 0 6px 20px rgba(0,212,255,0.35); }}
        50%      {{ box-shadow: 0 6px 32px rgba(123,97,255,0.55); }}
    }}

    .brand-name {{
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, {BRAND_COLORS['primary']}, {BRAND_COLORS['secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.5px;
        line-height: 1.1;
    }}
    .brand-tagline {{
        font-size: 0.75rem;
        color: #8892b0;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }}

    .brand-meta {{
        text-align: right;
        font-size: 0.75rem;
        color: #8892b0;
        line-height: 1.5;
    }}
    .brand-meta strong {{ color: #e8eaf6; }}

    /* Brand footer */
    .brand-footer {{
        margin-top: 3rem;
        padding: 1.5rem 0;
        border-top: 1px solid rgba(0,212,255,0.15);
        text-align: center;
        color: #8892b0;
        font-size: 0.75rem;
        line-height: 1.7;
        animation: brand-fade-in 0.6s ease-out;
    }}
    .brand-footer a {{
        color: {BRAND_COLORS['primary']};
        text-decoration: none;
    }}
    .brand-footer-divider {{
        display: inline-block;
        width: 4px;
        height: 4px;
        background: #8892b0;
        border-radius: 50%;
        margin: 0 8px;
        vertical-align: middle;
    }}

    /* Brand hero for login page */
    .brand-hero {{
        text-align: center;
        padding: 2rem 0;
        animation: brand-fade-in 0.7s ease-out;
    }}
    .brand-hero-icon {{
        font-size: 4rem;
        display: inline-block;
        animation: brand-bounce 2.5s ease-in-out infinite;
    }}
    @keyframes brand-bounce {{
        0%, 100% {{ transform: translateY(0); }}
        50%      {{ transform: translateY(-10px); }}
    }}
    .brand-hero-title {{
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 50%, {BRAND_COLORS['success']} 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: brand-gradient-shift 5s linear infinite;
        margin: 0.5rem 0;
    }}
    @keyframes brand-gradient-shift {{
        0%   {{ background-position: 0% center; }}
        100% {{ background-position: 200% center; }}
    }}
    .brand-hero-sub {{
        color: #8892b0;
        font-size: 1rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    .brand-hero-tag {{
        display: inline-block;
        margin-top: 1rem;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        background: rgba(0,212,255,0.10);
        border: 1px solid rgba(0,212,255,0.35);
        color: {BRAND_COLORS['primary']};
        font-size: 0.8rem;
        font-weight: 600;
    }}

    /* Powered by strip */
    .powered-by {{
        text-align: center;
        color: #8892b0;
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 2rem;
    }}
    </style>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# HEADER (top of every page)
# ────────────────────────────────────────────────
def brand_header(user_label="", user_role=""):
    """Branded top header. Call at top of logged-in pages."""
    now = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
    user_html = ""
    if user_label:
        user_html = f"<strong>{user_label}</strong>"
        if user_role:
            user_html += f" · {user_role}"
        user_html += "<br>"

    import base64
    from pathlib import Path as _P2
    logo_icon = "💊"
    if _P2("logo.png").exists():
        try:
            _b64 = base64.b64encode(_P2("logo.png").read_bytes()).decode()
            logo_icon = f'<img src="data:image/png;base64,{_b64}" style="width:52px;height:52px;border-radius:50%;" />'
        except Exception:
            pass

    st.markdown(f"""
    <div class="brand-header">
        <div class="brand-logo">
            <div class="brand-icon">{logo_icon}</div>
            <div>
                <div class="brand-name">{BRAND['name']}</div>
                <div class="brand-tagline">{BRAND['tagline']}</div>
            </div>
        </div>
        <div class="brand-meta">
            {user_html}
            <strong>{now}</strong><br>
            📞 {BRAND['phone']}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# FOOTER (bottom of every page)
# ────────────────────────────────────────────────
def brand_footer():
    """Branded footer. Call at bottom of pages."""
    st.markdown(f"""
    <div class="brand-footer">
        <strong style="color:#e8eaf6;">{BRAND['name']}</strong> — {BRAND['tagline']}
        <span class="brand-footer-divider"></span>
        {BRAND['phone']}
        <span class="brand-footer-divider"></span>
        {BRAND['email']}
        <br>
        {BRAND['address']} · {BRAND['address2']}
        <br>
        <span style="opacity:0.7;">GSTIN: {BRAND['gstin']}</span>
        <span class="brand-footer-divider"></span>
        <span style="opacity:0.6;">© {datetime.now().year} {BRAND['name']}. All rights reserved.</span>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# LOGIN HERO (for login page)
# ────────────────────────────────────────────────
def brand_login_hero():
    """Animated hero for login screens with actual logo."""
    import base64
    from pathlib import Path as _P
    logo_html = "💊"
    if _P("logo.png").exists():
        try:
            _b64 = base64.b64encode(_P("logo.png").read_bytes()).decode()
            logo_html = f'<img src="data:image/png;base64,{_b64}" style="width:140px;height:140px;border-radius:50%;box-shadow:0 12px 40px rgba(0,212,255,0.4),0 0 0 3px rgba(0,212,255,0.3);animation:brand-bounce 2.5s ease-in-out infinite;" />'
        except Exception:
            pass
    st.markdown(f"""
    <div class="brand-hero">
        <div class="brand-hero-icon">{logo_html}</div>
        <div class="brand-hero-title">{BRAND['name']}</div>
        <div class="brand-hero-sub">{BRAND['tagline']}</div>
        <div class="brand-hero-tag">✨ {BRAND['sub_tagline']} ✨</div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# BRANDED MESSAGE WRAPPERS
# ────────────────────────────────────────────────
def brand_greeting(name=""):
    """Return a branded greeting string."""
    if name:
        return f"Welcome to {BRAND['name']}, {name}!"
    return f"Welcome to {BRAND['name']}"


def brand_signature():
    """Return branded signature for messages."""
    return f"— Team {BRAND['name']} · {BRAND['phone']}"
