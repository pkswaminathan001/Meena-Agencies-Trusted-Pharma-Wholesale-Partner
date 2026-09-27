"""
_patch_cart.py — one-shot patch for cart UX in app.py.
Adds:
  1. Cart bounce animation on Add-to-Cart
  2. Rich cart review panel with product details + qty + price
  3. Discount hidden until owner approval
Safe: reverts on compile failure.
"""
from pathlib import Path
import py_compile

APP = Path("app.py")
src = APP.read_text()
original = src


# ═══════════════════════════════════════════════════════════
# FIX 1 — Inject CSS + bounce trigger CSS at top of file
# ═══════════════════════════════════════════════════════════
CSS_BLOCK = '''
# ═══════════════════════════════════════════════════════════
# CART UX — bounce animation + rich review panel CSS
# ═══════════════════════════════════════════════════════════
CART_CSS = """
<style>
@keyframes cartBounce {
  0%   { transform: scale(1);    }
  30%  { transform: scale(1.35); }
  60%  { transform: scale(0.95); }
  100% { transform: scale(1);    }
}
.cart-bounce { animation: cartBounce 0.55s ease-in-out; display:inline-block; }

@keyframes badgePulse {
  0%   { box-shadow: 0 0 0 0   rgba(255,82,82,0.7); }
  70%  { box-shadow: 0 0 0 12px rgba(255,82,82,0);   }
  100% { box-shadow: 0 0 0 0   rgba(255,82,82,0);   }
}
.cart-badge {
  display:inline-block; background:#ff5252; color:#fff;
  border-radius:50%; padding:1px 7px; font-size:0.75rem;
  font-weight:700; margin-left:6px;
  animation: badgePulse 1.2s ease-out 1;
}

.cart-card {
  border: 1.5px solid #7b61ff44;
  border-radius: 14px;
  padding: 14px 16px;
  background: linear-gradient(180deg, #ffffff08, #ffffff03);
  margin-bottom: 10px;
}
.cart-row {
  display: flex; justify-content: space-between;
  padding: 6px 0; border-bottom: 1px dashed #ffffff18;
  font-size: 0.92rem;
}
.cart-row:last-child { border-bottom: none; }
.cart-total {
  font-size: 1.15rem; font-weight: 700; color: #00d47a;
  padding-top: 10px; margin-top: 6px;
  border-top: 2px solid #ffffff22;
}
.cart-pending {
  font-size: 0.8rem; color: #8892b0; font-style: italic;
  background: #ffffff08; padding: 6px 10px; border-radius: 8px;
  margin-top: 8px;
}
</style>
"""
'''

# Insert right after the imports block — find "import notify_pro\nimport order_notifier"
anchor = "import order_notifier"
if anchor in src and "CART_CSS" not in src:
    idx = src.index(anchor) + len(anchor)
    eol = src.index("\n", idx) + 1
    src = src[:eol] + CSS_BLOCK + src[eol:]
    print("✅ CSS block injected")
else:
    print("⏭  CSS block already present or anchor missing")


# ═══════════════════════════════════════════════════════════
# FIX 2 — Cart bounce on Add-to-Cart button click (line 1542)
# ═══════════════════════════════════════════════════════════
OLD_ADD = '''                if st.button("🛒 Add to Cart", key="add_fifo_cart", use_container_width=True):
                    st.session_state.cart.append({'''
NEW_ADD = '''                if st.button("🛒 Add to Cart", key="add_fifo_cart", use_container_width=True):
                    st.session_state["cart_bounce_at"] = datetime.now().isoformat()
                    st.session_state.cart.append({'''

if OLD_ADD in src:
    src = src.replace(OLD_ADD, NEW_ADD, 1)
    print("✅ Add-to-Cart triggers bounce flag")
else:
    print("⏭  Add-to-Cart marker not found (may already be patched)")


# ═══════════════════════════════════════════════════════════
# FIX 3 — Rich cart review panel (replace block at 1649)
# ═══════════════════════════════════════════════════════════
OLD_CART_START = "    if st.session_state.cart:\n        cart_df = pd.DataFrame(st.session_state.cart)"

NEW_CART_PANEL = '''    if st.session_state.cart:
        # ═══ CART REVIEW PANEL (with bounce + rich details) ═══
        _bounce_at = st.session_state.get("cart_bounce_at")
        _now_iso = datetime.now().isoformat()
        _do_bounce = False
        if _bounce_at:
            try:
                from datetime import datetime as _d
                delta = (_d.fromisoformat(_now_iso) - _d.fromisoformat(_bounce_at)).total_seconds()
                if delta < 1.5:
                    _do_bounce = True
            except Exception:
                pass

        st.markdown(CART_CSS, unsafe_allow_html=True)

        _badge = f'<span class="cart-badge">{len(st.session_state.cart)}</span>'
        _bounce_cls = "cart-bounce" if _do_bounce else ""
        st.markdown(
            f'<h3 style="margin-bottom:4px;">'
            f'<span class="{_bounce_cls}">🛒</span> Your Cart{_badge}'
            f'</h3>',
            unsafe_allow_html=True,
        )

        # ── Per-item rows ──
        _subtotal = 0.0
        _rows_html = []
        for _i, _it in enumerate(st.session_state.cart):
            _name = _it.get("name") or _it.get("product") or "Item"
            _qty  = _it.get("qty") or _it.get("quantity") or 1
            _rate = float(_it.get("price") or _it.get("rate") or _it.get("mrp") or 0)
            _line = _qty * _rate
            _subtotal += _line
            _rows_html.append(
                f'<div class="cart-row">'
                f'<span><b>{_name}</b><br>'
                f'<small>Qty: {_qty} × ₹{_rate:,.2f}</small></span>'
                f'<span style="font-weight:600;">₹{_line:,.2f}</span>'
                f'</div>'
            )

        _subtotal_html = f'<div class="cart-total">Subtotal (base price): ₹{_subtotal:,.2f}</div>'
        _pending_html = (
            '<div class="cart-pending">'
            '💡 Discount will be applied <b>after owner approval</b>. '
            'You will receive the final price on Telegram.'
            '</div>'
        )

        st.markdown(
            '<div class="cart-card">'
            + "".join(_rows_html)
            + _subtotal_html
            + _pending_html
            + '</div>',
            unsafe_allow_html=True,
        )

        # ── Keep the existing checkout block below ──
        cart_df = pd.DataFrame(st.session_state.cart)'''

if OLD_CART_START in src:
    src = src.replace(OLD_CART_START, NEW_CART_PANEL, 1)
    print("✅ rich cart panel inserted")
else:
    print("⚠️  cart block marker not found — cart panel NOT inserted")


# ═══════════════════════════════════════════════════════════
# Write + compile guard
# ═══════════════════════════════════════════════════════════
APP.write_text(src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted to original app.py")
