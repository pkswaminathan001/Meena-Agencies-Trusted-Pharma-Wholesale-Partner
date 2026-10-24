"""
Amazon-style UI helpers for Meena Agencies.
  * get_icon           — bulletproof image resolver (local → category → placeholder)
  * inject_amazon_css  — Amazon-inspired stylesheet
  * render_product_card — one card, in a keyed container
  * render_product_grid — responsive 4-up grid
"""
import base64
import urllib.parse
from pathlib import Path
from typing import Callable, Iterable, Optional

import streamlit as st

# ---------- image resolution ----------
_THIS = Path(__file__).resolve().parent
_IMG  = _THIS / "images"
_MED  = _IMG / "medicines"          # put curated real photos here
_EXTS = (".jpg", ".jpeg", ".png", ".webp")

_CATEGORIES = [
    ("tablet",   ["tablet", "tab", "dolo", "paracetamol", "crocin", "aspirin",
                  "metformin", "atorvastatin", "amlodipine", "atorva"]),
    ("capsule",  ["capsule", "cap", "amoxicillin", "azithral", "augmentin",
                  "omeprazole", "pantoprazole", "pantop"]),
    ("syrup",    ["syrup", "syp", "suspension", "drops", "cough",
                  "benadryl", "ascoril", "solution"]),
    ("injection",["injection", "inj", "vial", "ampoule", "insulin", "vaccine"]),
    ("cream",    ["cream", "ointment", "gel", "lotion", "soap", "tube"]),
]

def _safe(name: str) -> str:
    out = str(name).lower().replace(" ", "_").replace("/", "_")
    for ch in "()%#&'\"\\":
        out = out.replace(ch, "")
    return out.strip("_")

@st.cache_data(show_spinner=False, max_entries=512)
def _data_uri(path_str: str) -> Optional[str]:
    p = Path(path_str)
    try:
        raw = p.read_bytes()
    except OSError:
        return None
    ext = p.suffix.lstrip(".").lower() or "jpeg"
    if ext == "jpg":
        ext = "jpeg"
    if ext not in {"jpeg", "png", "webp", "gif"}:
        ext = "jpeg"
    return f"data:image/{ext};base64," + base64.b64encode(raw).decode("ascii")

def _local_image(name: str) -> Optional[Path]:
    safe = _safe(name)
    # 1) exact medicine image in images/medicines/ or images/
    for base in (_MED, _IMG):
        if not base.is_dir():
            continue
        for ext in _EXTS:
            p = base / f"{safe}{ext}"
            if p.is_file():
                return p
    # 2) category image
    low = name.lower()
    for cat, kws in _CATEGORIES:
        if any(k in low for k in kws):
            for ext in _EXTS:
                p = _IMG / f"real_{cat}{ext}"
                if p.is_file():
                    return p
    # 3) generic default
    for ext in _EXTS:
        p = _IMG / f"real_default{ext}"
        if p.is_file():
            return p
    return None

def get_icon(name: str) -> str:
    import hashlib
    label = str(name).strip() or "Medicine"
    
    # 1. Try local images first (if you ever manually add them)
    local = _local_image(label)
    if local:
        uri = _data_uri(str(local))
        if uri:
            return uri
            
    # 2. Dynamic high-quality stock photos (Distinct per medicine!)
    # We use a hash "lock" so the image for "Insulin" stays the same forever.
    lock_id = int(hashlib.md5(label.encode()).hexdigest(), 16) % 1000
    
    low = label.lower()
    keywords = "medicine,pills"
    
    # Smart matching based on medicine name
    if any(k in low for k in ["syrup", "liquid", "susp"]):
        keywords = "syrup,bottle"
    elif any(k in low for k in ["injection", "insulin", "vial"]):
        keywords = "syringe,medicine"
    elif any(k in low for k in ["cream", "gel", "ointment"]):
        keywords = "cream,tube"
    elif any(k in low for k in ["capsule", "cap"]):
        keywords = "capsule,pills"
        
    return f"https://loremflickr.com/300/300/{keywords}?lock={lock_id}"


# ---------- Amazon CSS ----------
AMAZON_CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 1280px;}

/* Product card (matches st.container(key="pcard_*")) */
[class*="st-key-pcard_"] {
    background: #ffffff !important;
    border: 1px solid #e5e5e5 !important;
    border-radius: 8px !important;
    padding: 12px 12px 10px !important;
    height: 100%;
    transition: box-shadow .2s ease, transform .2s ease;
}
[class*="st-key-pcard_"]:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,.18);
    transform: translateY(-2px);
}
[class*="st-key-pcard_"] img {
    display: block; width: 100%; height: 170px;
    object-fit: contain; background: #fff; border-radius: 6px;
}

.amz-title {
    color:#0F1111; font-size:15px; font-weight:500; line-height:1.35;
    margin:10px 0 4px; min-height:40px;
    display:-webkit-box; -webkit-line-clamp:2;
    -webkit-box-orient:vertical; overflow:hidden;
}
.amz-rating  { color:#FFA41C; font-size:14px; letter-spacing:1px; }
.amz-reviews { color:#007185; font-size:13px; margin-left:4px; }
.amz-price   { color:#0F1111; font-size:22px; font-weight:600; line-height:1; margin:6px 0; }
.amz-decimal { font-size:13px; position:relative; top:3px; }
.amz-delivery{ color:#0F1111; font-size:13px; margin:4px 0 8px; }

[class*="st-key-pcard_"] button {
    background:#FFD814 !important; color:#0F1111 !important;
    border:1px solid #FCD200 !important; border-radius:20px !important;
    font-weight:600 !important; font-size:14px !important;
    padding:6px 12px !important; width:100% !important;
}
[class*="st-key-pcard_"] button:hover {
    background:#F7CA00 !important; border-color:#F2C200 !important;
}

div[data-testid="stTextInput"] input {
    border:2px solid #FFD814 !important; border-radius:6px !important;
    padding:10px 14px !important; font-size:15px !important;
}
div[data-testid="stTextInput"] input:focus {
    box-shadow: 0 0 0 2px rgba(255,216,20,.35) !important;
}
h1,h2,h3 { color:#0B3C5D; }
</style>
"""

def inject_amazon_css() -> None:
    st.markdown(AMAZON_CSS, unsafe_allow_html=True)

# ---------- card + grid ----------
def _rupee_block(paise: int) -> str:
    r, p = divmod(int(paise), 100)
    return (f'<div class="amz-price"><span class="amz-decimal">₹</span>{r}'
            f'<span class="amz-decimal">.{p:02d}</span></div>')

def render_product_card(*, name: str, price_paise: int, key: str,
                        on_add: Optional[Callable[[str, int], None]] = None,
                        rating: str = "★★★★☆", reviews: int = 1245,
                        delivery: str = "FREE delivery <b>Tomorrow</b>") -> None:
    with st.container(key=f"pcard_{key}"):
        st.markdown(f'<img src="{get_icon(name)}" alt="{name}">', unsafe_allow_html=True)
        st.markdown(f'<div class="amz-title">{name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="amz-rating">{rating}'
                    f'<span class="amz-reviews">({reviews:,})</span></div>',
                    unsafe_allow_html=True)
        st.markdown(_rupee_block(price_paise), unsafe_allow_html=True)
        st.markdown(f'<div class="amz-delivery">{delivery}</div>',
                    unsafe_allow_html=True)
        cart = st.session_state.setdefault("cart", [])
        item = next((x for x in cart if x["name"] == name), None)

        if item:
            def _update_qty(item_name, key, delta=None):
                for x in st.session_state.cart:
                    if x["name"] == item_name:
                        if delta is not None:
                            x["qty"] += delta
                        else:
                            x["qty"] = st.session_state[f"qty_in_{key}"]
                        
                        if x["qty"] <= 0:
                            st.session_state.cart.remove(x)
                        else:
                            st.session_state[f"qty_in_{key}"] = x["qty"]
                        break

            c1, c2, c3 = st.columns([1, 1.5, 1])
            
            c1.button("➖", key=f"minus_{key}", use_container_width=True, 
                      on_click=_update_qty, args=(name, key, -1))
            
            c2.number_input(
                "Qty", min_value=1, max_value=9999, 
                value=int(item["qty"]), 
                key=f"qty_in_{key}", 
                label_visibility="collapsed",
                on_change=_update_qty,
                args=(name, key, None)
            )
            
            c3.button("➕", key=f"plus_{key}", use_container_width=True, 
                      on_click=_update_qty, args=(name, key, 1))
        else:
            if st.button("Add to Cart", key=f"add_{key}", use_container_width=True):
                if on_add:
                    on_add(name, price_paise)
                else:
                    cart.append({"name": name, "price": price_paise / 100, "qty": 1})
                st.rerun()

def render_product_grid(items: Iterable[dict], *,
                        on_add: Optional[Callable[[str, int], None]] = None,
                        cols_per_row: int = 4) -> None:
    items = list(items)
    if not items:
        st.info("No products to show.")
        return
    for i in range(0, len(items), cols_per_row):
        chunk = items[i:i + cols_per_row]
        cols = st.columns(cols_per_row, gap="medium")
        for col, it in zip(cols, chunk):
            with col:
                render_product_card(
                    name=it["name"],
                    price_paise=int(it.get("price_paise", it.get("price", 0))),
                    key=it.get("key", f"{i}_{_safe(it['name'])}"),
                    on_add=on_add,
                    rating=it.get("rating", "★★★★☆"),
                    reviews=int(it.get("reviews", 1245)),
                    delivery=it.get("delivery", "FREE delivery <b>Tomorrow</b>"),
                )
