from pathlib import Path
import py_compile
import re

APP = Path("app.py")
src = APP.read_text()
original = src

# Find the cart_df line
lines = src.split("\n")
cart_df_i = None
for i, ln in enumerate(lines):
    if "cart_df = pd.DataFrame(st.session_state.cart)" in ln:
        cart_df_i = i
        break

if cart_df_i is None:
    print("❌ cart_df line not found")
    raise SystemExit(1)

print(f"Found cart_df at line {cart_df_i+1}")

# Determine indentation
indent = lines[cart_df_i][:len(lines[cart_df_i]) - len(lines[cart_df_i].lstrip())]

# Find the end of the display block. Look for lines after that reference cart_df
# Stop when we hit a line with lower indent (or an empty line then a lower-indent line)
end_i = cart_df_i + 1
while end_i < len(lines):
    ln = lines[end_i]
    if ln.strip() and not ln.startswith(indent):
        break
    end_i += 1

print(f"Replacing lines {cart_df_i+1} .. {end_i}")

bill_lines = [
    f'{indent}# ═══ STYLED BILL (replaces raw dataframe) ═══',
    f'{indent}st.markdown("""',
    f'{indent}<style>',
    f'{indent}.bill-wrap {{',
    f'{indent}  border: 1.5px solid #7b61ff55;',
    f'{indent}  border-radius: 16px;',
    f'{indent}  overflow: hidden;',
    f'{indent}  margin: 12px 0;',
    f'{indent}  background: linear-gradient(180deg, #ffffff08, #ffffff02);',
    f'{indent}  font-family: -apple-system, Segoe UI, Roboto, sans-serif;',
    f'{indent}}}',
    f'{indent}.bill-header {{',
    f'{indent}  background: linear-gradient(135deg, #7b61ff, #00d47a);',
    f'{indent}  color: #fff;',
    f'{indent}  padding: 14px 18px;',
    f'{indent}  font-weight: 700;',
    f'{indent}  font-size: 1.05rem;',
    f'{indent}  display: flex;',
    f'{indent}  justify-content: space-between;',
    f'{indent}}}',
    f'{indent}.bill-header small {{ opacity: 0.85; font-weight: 400; }}',
    f'{indent}.bill-body {{ padding: 14px 18px; }}',
    f'{indent}.bill-cols {{',
    f'{indent}  display: grid;',
    f'{indent}  grid-template-columns: 2.5fr 0.7fr 1fr 1fr;',
    f'{indent}  gap: 8px;',
    f'{indent}  padding: 8px 0;',
    f'{indent}  border-bottom: 1px dashed #ffffff22;',
    f'{indent}  font-size: 0.78rem;',
    f'{indent}  color: #8892b0;',
    f'{indent}  text-transform: uppercase;',
    f'{indent}  letter-spacing: 0.5px;',
    f'{indent}}}',
    f'{indent}.bill-row {{',
    f'{indent}  display: grid;',
    f'{indent}  grid-template-columns: 2.5fr 0.7fr 1fr 1fr;',
    f'{indent}  gap: 8px;',
    f'{indent}  padding: 12px 0;',
    f'{indent}  border-bottom: 1px solid #ffffff10;',
    f'{indent}  align-items: center;',
    f'{indent}}}',
    f'{indent}.bill-row:last-child {{ border-bottom: none; }}',
    f'{indent}.bill-name {{ font-weight: 600; color: #e8ecf5; }}',
    f'{indent}.bill-name small {{ display: block; color: #8892b0; font-weight: 400; font-size: 0.72rem; margin-top: 2px; }}',
    f'{indent}.bill-qty {{ text-align: center; color: #b8c0d8; }}',
    f'{indent}.bill-rate {{ text-align: right; color: #8892b0; }}',
    f'{indent}.bill-total {{ text-align: right; font-weight: 700; color: #e8ecf5; }}',
    f'{indent}.bill-summary {{',
    f'{indent}  padding: 14px 18px 18px;',
    f'{indent}  background: #ffffff05;',
    f'{indent}  border-top: 2px solid #7b61ff44;',
    f'{indent}}}',
    f'{indent}.bill-summary-row {{',
    f'{indent}  display: flex;',
    f'{indent}  justify-content: space-between;',
    f'{indent}  padding: 6px 0;',
    f'{indent}  font-size: 0.92rem;',
    f'{indent}  color: #b8c0d8;',
    f'{indent}}}',
    f'{indent}.bill-grand {{',
    f'{indent}  display: flex;',
    f'{indent}  justify-content: space-between;',
    f'{indent}  padding: 12px 0 4px;',
    f'{indent}  margin-top: 8px;',
    f'{indent}  border-top: 2px solid #00d47a55;',
    f'{indent}  font-size: 1.25rem;',
    f'{indent}  font-weight: 800;',
    f'{indent}  color: #00d47a;',
    f'{indent}}}',
    f'{indent}.bill-pending {{',
    f'{indent}  background: #ffc10712;',
    f'{indent}  border-left: 3px solid #ffc107;',
    f'{indent}  padding: 10px 14px;',
    f'{indent}  border-radius: 8px;',
    f'{indent}  font-size: 0.8rem;',
    f'{indent}  color: #ffc107;',
    f'{indent}  margin-top: 12px;',
    f'{indent}}}',
    f'{indent}</style>',
    f'{indent}""", unsafe_allow_html=True)',
    f'{indent}',
    f'{indent}_items = st.session_state.cart or []',
    f'{indent}_sub = 0.0',
    f'{indent}_rows = ""',
    f'{indent}for _it in _items:',
    f'{indent}    _n   = _it.get("medicine") or _it.get("name") or _it.get("product") or "Item"',
    f'{indent}    _b   = _it.get("batch") or ""',
    f'{indent}    _q   = _it.get("qty") or _it.get("quantity") or 1',
    f'{indent}    _r   = float(_it.get("price") or _it.get("rate") or _it.get("mrp") or 0)',
    f'{indent}    _amt = _q * _r',
    f'{indent}    _sub += _amt',
    f'{indent}    _sub_line = f"Batch: {_b}" if _b else ""',
    f'{indent}    _rows += (',
    f'{indent}        f\'<div class="bill-row">\'',
    f'{indent}        f\'<div class="bill-name">{_n}<small>{_sub_line}</small></div>\'',
    f'{indent}        f\'<div class="bill-qty">{_q}</div>\'',
    f'{indent}        f\'<div class="bill-rate">₹{_r:,.2f}</div>\'',
    f'{indent}        f\'<div class="bill-total">₹{_amt:,.2f}</div>\'',
    f'{indent}        f\'</div>\'',
    f'{indent}    )',
    f'{indent}',
    f'{indent}st.markdown(f"""',
    f'{indent}<div class="bill-wrap">',
    f'{indent}  <div class="bill-header">',
    f'{indent}    <span>🧾 Order Summary</span>',
    f'{indent}    <small>{len(_items)} item(s)</small>',
    f'{indent}  </div>',
    f'{indent}  <div class="bill-body">',
    f'{indent}    <div class="bill-cols">',
    f'{indent}      <div>Item</div><div style="text-align:center;">Qty</div>',
    f'{indent}      <div style="text-align:right;">Rate</div>',
    f'{indent}      <div style="text-align:right;">Amount</div>',
    f'{indent}    </div>',
    f'{indent}    {_rows}',
    f'{indent}  </div>',
    f'{indent}  <div class="bill-summary">',
    f'{indent}    <div class="bill-summary-row"><span>Subtotal (base)</span><span>₹{_sub:,.2f}</span></div>',
    f'{indent}    <div class="bill-summary-row"><span>Discount</span><span style="color:#ffc107;">Pending owner approval</span></div>',
    f'{indent}    <div class="bill-grand"><span>Payable</span><span>₹{_sub:,.2f}</span></div>',
    f'{indent}    <div class="bill-pending">💡 Final amount with discount will be confirmed on Telegram after owner approves.</div>',
    f'{indent}  </div>',
    f'{indent}</div>',
    f'{indent}""", unsafe_allow_html=True)',
    f'{indent}# ═══ END STYLED BILL ═══',
]

new_lines = lines[:cart_df_i] + bill_lines + lines[end_i:]
src = "\n".join(new_lines)

APP.write_text(src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ styled bill installed")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
