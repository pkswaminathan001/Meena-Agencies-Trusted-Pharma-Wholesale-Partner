"""unified_brand.py — Same big centered logo + brand block for every screen.
Used by: Owner dashboard, Staff dashboard, Retailer view, Login page.
"""
import streamlit as st
from pathlib import Path
import base64

_CACHE = {"b64": None}


def _b64():
    if _CACHE["b64"]:
        return _CACHE["b64"]
    for name in ("logo_brand_small.png", "logo_rich_small.png", "logo.png"):
        p = Path(name)
        if p.exists():
            _CACHE["b64"] = base64.b64encode(p.read_bytes()).decode()
            return _CACHE["b64"]
    return ""


def render(size=140, subtitle=None, show_buttons_row=False):
    """
    Big centered brand block — the same one used on the login page.
    size: logo pixel size (default 140, same as login)
    subtitle: text below the brand name (default: 'Trusted Pharma Wholesale Partner')
    show_buttons_row: if True, adds bell + user + sign out on the right
    """
    b64 = _b64()
    sub = subtitle if subtitle else "Trusted Pharma Wholesale Partner"

    html = f'''
    <div style="text-align:center; padding: 22px 0 12px 0;">
        <div style="display:inline-block;
                    width:{size}px; height:{size}px;
                    border-radius:50%;
                    background:linear-gradient(135deg, #00d4aa, #7b61ff);
                    padding:5px;
                    box-shadow: 0 20px 60px rgba(0,212,170,0.35);
                    margin-bottom:16px;">
            <img src="data:image/png;base64,{b64}"
                 alt="Meena Agencies"
                 style="width:100%; height:100%; object-fit:contain;
                        border-radius:50%; background:#fff; display:block;" />
        </div>
        <div style="font-size:1.7rem; font-weight:900; letter-spacing:4px;
                    background:linear-gradient(90deg, #00d4aa, #7b61ff);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    background-clip:text;
                    line-height:1.1;">
            MEENA AGENCIES
        </div>
        <div style="font-size:0.78rem; color:#8892b0; letter-spacing:3px;
                    margin-top:6px; text-transform:uppercase; font-weight:600;">
            {sub}
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
