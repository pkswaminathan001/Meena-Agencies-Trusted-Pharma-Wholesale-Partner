"""brand_logo.py — ONE shared logo component for every screen.
Use anywhere: login, owner, staff, retailer.
Consistent size, style, and behavior.
"""
import streamlit as st
from pathlib import Path
import base64

_LOGO_CACHE = {"b64": None, "size": None}


def _get_logo_b64():
    if _LOGO_CACHE["b64"]:
        return _LOGO_CACHE["b64"]
    p = Path("logo_brand_small.png")
    if not p.exists():
        return ""
    _LOGO_CACHE["b64"] = base64.b64encode(p.read_bytes()).decode()
    return _LOGO_CACHE["b64"]


def _get_logo_size():
    try:
        from PIL import Image
        img = Image.open("logo_brand_small.png")
        return img.size
    except Exception:
        return (256, 256)


def render(size=64, centered=False, glow=True, subtitle=None):
    """
    Render the Meena Agencies logo.
    - size: pixel width/height (square)
    - centered: center horizontally
    - glow: add cyan glow
    - subtitle: optional text below
    """
    b64 = _get_logo_b64()
    if not b64:
        st.markdown(f"<div style='font-size:{size}px;'>💊</div>", unsafe_allow_html=True)
        return

    align = "text-align:center;" if centered else ""
    glow_css = f"box-shadow: 0 8px 32px rgba(0,212,170,0.35);" if glow else ""

    html = f"""
    <div style="{align}">
        <div style="display:inline-block;
                    width:{size}px; height:{size}px;
                    border-radius:50%;
                    background:linear-gradient(135deg, #00d4aa, #7b61ff);
                    padding:3px;
                    {glow_css}
                    overflow:hidden;">
            <img src="data:image/png;base64,{b64}"
                 alt="Meena Agencies"
                 style="width:100%; height:100%; object-fit:contain;
                        border-radius:50%; background:#fff; display:block;" />
        </div>
        {f'<div style="margin-top:8px;font-size:0.85rem;color:#8892b0;letter-spacing:1px;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
