"""
profile_pic.py — Round profile picture, centered, tight layout.
"""
import streamlit as st
from pathlib import Path
import json
import base64

PIC_DIR = Path("profile_pics")
PIC_DIR.mkdir(exist_ok=True)
RETAILERS_FILE = Path("retailers.json")


_DENSE_CSS = """
<style>
/* Kill top padding + all vertical gaps on profile page */
.block-container { padding-top: 3rem !important; padding-bottom: 1rem !important; }
[data-testid="stMainBlockContainer"] { padding-top: 3rem !important; padding-bottom: 1rem !important; }
[data-testid="stVerticalBlock"] { gap: 1rem !important; }
[data-testid="stElementContainer"] { margin: 0.3rem 0 !important; padding: 0 !important; }

/* Headings — no margin */
h1, h2, h3, h4 { margin: 0.4rem 0 !important; padding: 0 !important; line-height: 1.3 !important; }

/* Divider — thin */
hr { margin: 1rem 0 !important; }

/* Hide caption gap */
.stCaption, [data-testid="stCaptionContainer"] { margin: 0 !important; }

/* Tighten the file uploader */
[data-testid="stFileUploader"] { margin: 0 !important; padding: 0 !important; }
[data-testid="stFileUploader"] section { padding: 16px !important; min-height: 60px !important; }

/* Dataframe — compact */
[data-testid="stDataFrame"] { margin: 1rem 0 !important; }
</style>
"""


def _load_retailers():
    try:
        return json.loads(RETAILERS_FILE.read_text())
    except Exception:
        return []


def _save_retailers(data):
    try:
        RETAILERS_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        print("save_retailers failed:", e)


def _pic_path(retailer_id):
    for ext in (".png", ".jpg", ".jpeg"):
        p = PIC_DIR / f"{retailer_id}{ext}"
        if p.exists():
            return p
    return None


def _b64(p):
    try:
        return base64.b64encode(Path(p).read_bytes()).decode()
    except Exception:
        return ""


def render(retailer):
    if not retailer:
        return
    st.markdown(_DENSE_CSS, unsafe_allow_html=True)
    rid = retailer.get("id", "x")

    # Title — centered, tight
    st.markdown(
        '<div style="text-align:center; font-size:1.2rem; font-weight:800; '
        'margin:0 0 0.6rem 0;">👤 My Profile</div>'
        '<div style="text-align:center; font-size:0.8rem; color:#8892b0; '
        'margin:0 0 1rem 0;">Profile Picture (optional)</div>',
        unsafe_allow_html=True,
    )

    existing = _pic_path(rid)

    # Picture — centered, smaller
    if existing:
        b64 = _b64(existing)
        st.markdown(f"""
        <div style="text-align:center; margin:0 0 1rem 0;">
            <img src="data:image/png;base64,{b64}"
                 style="width:110px;height:110px;
                        border-radius:50%;
                        object-fit:cover;
                        border:3px solid #4f46e5;
                        box-shadow:0 4px 14px rgba(79,70,229,0.35);
                        display:inline-block;" />
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; margin:0 0 1rem 0;">
            <div style="width:110px;height:110px;
                        border-radius:50%;
                        background:linear-gradient(135deg,#4f46e5,#7b61ff);
                        display:inline-flex;
                        align-items:center;
                        justify-content:center;
                        color:#fff;
                        font-size:2.5rem;
                        font-weight:900;
                        border:3px solid #4f46e5;
                        box-shadow:0 4px 14px rgba(79,70,229,0.35);">?</div>
        </div>
        """, unsafe_allow_html=True)

    # Uploader — narrow, centered
    _l, mid, _r = st.columns([1, 3, 1])
    with mid:
        uploaded = st.file_uploader(
            "Choose a picture",
            type=["png", "jpg", "jpeg"],
            key=f"profpic_{rid}",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            try:
                target = PIC_DIR / f"{rid}.png"
                target.write_bytes(uploaded.getvalue())
                data = _load_retailers()
                for r in data:
                    if r.get("id") == rid:
                        r["profile_pic"] = str(target)
                        break
                _save_retailers(data)
                st.success("✅ Picture uploaded")
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")

        if existing:
            if st.button("🗑 Remove picture", key=f"rmpic_{rid}", use_container_width=True):
                try:
                    existing.unlink()
                    data = _load_retailers()
                    for r in data:
                        if r.get("id") == rid:
                            r.pop("profile_pic", None)
                            break
                    _save_retailers(data)
                    st.success("Removed")
                    st.rerun()
                except Exception as e:
                    st.error(f"Remove failed: {e}")

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:16px 0;"></div>', unsafe_allow_html=True)
