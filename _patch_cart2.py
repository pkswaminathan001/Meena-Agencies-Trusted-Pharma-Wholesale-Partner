from pathlib import Path
import py_compile
import re

APP = Path("app.py")
src = APP.read_text()
original = src

# Locate the block starting at "if st.session_state.cart:"
lines = src.split("\n")
target_i = None
for i, ln in enumerate(lines):
    if ln.strip() == "if st.session_state.cart:":
        target_i = i
        break

if target_i is None:
    print("❌ 'if st.session_state.cart:' not found")
    raise SystemExit(1)

# Determine indentation (4 spaces typically)
indent = lines[target_i][:len(lines[target_i]) - len(lines[target_i].lstrip())]
print(f"Found cart block at line {target_i+1}, indent={len(indent)}")

# Show context for user's knowledge
print(f"  line {target_i+1}: {lines[target_i]}")
for j in range(1, 4):
    if target_i + j < len(lines):
        print(f"  line {target_i+j+1}: {lines[target_i+j]}")

# Build the panel HTML/Streamlit block to insert right after "if st.session_state.cart:"
panel_lines = [
    f'{indent}    # ═══ CART REVIEW PANEL (bounce + rich details) ═══',
    f'{indent}    try:',
    f'{indent}        st.markdown(CART_CSS, unsafe_allow_html=True)',
    f'{indent}    except NameError:',
    f'{indent}        pass',
    f'{indent}    _cart_items = st.session_state.cart or []',
    f'{indent}    _cart_count = len(_cart_items)',
    f'{indent}    _subtotal = 0.0',
    f'{indent}    _row_html = ""',
    f'{indent}    for _it in _cart_items:',
    f'{indent}        _name = _it.get("name") or _it.get("product") or "Item"',
    f'{indent}        _qty  = _it.get("qty") or _it.get("quantity") or 1',
    f'{indent}        _rate = float(_it.get("price") or _it.get("rate") or _it.get("mrp") or 0)',
    f'{indent}        _line = _qty * _rate',
    f'{indent}        _subtotal += _line',
    f'{indent}        _row_html += (',
    f'{indent}            f\'<div class="cart-row">\'',
    f'{indent}            f\'<span><b>{_name}</b><br><small>Qty: {_qty} × ₹{_rate:,.2f}</small></span>\'',
    f'{indent}            f\'<span style="font-weight:600;">₹{_line:,.2f}</span>\'',
    f'{indent}            f\'</div>\'',
    f'{indent}        )',
    f'{indent}    st.markdown(',
    f'{indent}        \'<h3 style="margin-bottom:6px;">🛒 Your Cart \'',
    f'{indent}        f\'<span class="cart-badge">{_cart_count}</span></h3>\'',
    f'{indent}        \'<div class="cart-card">\'',
    f'{indent}        + _row_html',
    f'{indent}        + f\'<div class="cart-total">Subtotal (base price): ₹{_subtotal:,.2f}</div>\'',
    f'{indent}        + \'<div class="cart-pending">💡 Discount will be applied <b>after owner approval</b>. You will receive the final price on Telegram.</div>\'',
    f'{indent}        + \'</div>\',',
    f'{indent}        unsafe_allow_html=True,',
    f'{indent}    )',
    f'{indent}    # ═══ END PANEL ═══',
]

# Insert after the "if st.session_state.cart:" line
new_lines = lines[:target_i+1] + panel_lines + lines[target_i+1:]
src = "\n".join(new_lines)

APP.write_text(src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ cart panel inserted")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
