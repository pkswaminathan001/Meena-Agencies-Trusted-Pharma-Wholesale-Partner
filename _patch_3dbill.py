from pathlib import Path
import py_compile

APP = Path("app.py")
src = APP.read_text()
original = src
lines = src.split("\n")

# Find where the styled bill block starts (our previous patch)
start_i = None
end_i = None
for i, ln in enumerate(lines):
    if "# ═══ STYLED BILL" in ln or "cart_df = pd.DataFrame" in ln:
        start_i = i
        break

if start_i is None:
    print("❌ Can't find bill block")
    raise SystemExit(1)

# Scan forward to find where the block ends (next section at same indent or less)
base_indent = len(lines[start_i]) - len(lines[start_i].lstrip())
end_i = start_i + 1
while end_i < len(lines):
    ln = lines[end_i]
    if ln.strip() and (len(ln) - len(ln.lstrip())) <= base_indent:
        # check if it's a new section marker
        if not ln.strip().startswith("#"):
            break
    end_i += 1

indent = " " * base_indent
print(f"Replacing lines {start_i+1} .. {end_i}")

NEW = [
    f'{indent}# ═══ 3D ANIMATED BILL ═══',
    f'{indent}st.markdown("""',
    f'{indent}<style>',
    f'{indent}@keyframes billSlideIn {{',
    f'{indent}  0%   {{ opacity: 0; transform: translateY(30px) rotateX(-15deg) scale(0.94); }}',
    f'{indent}  60%  {{ opacity: 1; transform: translateY(-4px) rotateX(3deg) scale(1.01); }}',
    f'{indent}  100% {{ opacity: 1; transform: translateY(0) rotateX(0deg) scale(1); }}',
    f'{indent}}}',
    f'{indent}@keyframes rowFade {{',
    f'{indent}  from {{ opacity: 0; transform: translateX(-12px); }}',
    f'{indent}  to   {{ opacity: 1; transform: translateX(0);    }}',
    f'{indent}}}',
    f'{indent}@keyframes pulseTotal {{',
    f'{indent}  0%,100% {{ text-shadow: 0 0 0 rgba(0,212,122,0); }}',
    f'{indent}  50%     {{ text-shadow: 0 0 18px rgba(0,212,122,0.85); }}',
    f'{indent}}}',
    f'{indent}@keyframes shimmer {{',
    f'{indent}  0%   {{ background-position: -300% 0; }}',
    f'{indent}  100% {{ background-position:  300% 0; }}',
    f'{indent}}}',
    f'{indent}',
    f'{indent}.bill3d-scene {{',
    f'{indent}  perspective: 1400px;',
    f'{indent}  margin: 20px 0 26px;',
    f'{indent}}}',
    f'{indent}',
    f'{indent}.bill3d {{',
    f'{indent}  transform-style: preserve-3d;',
    f'{indent}  animation: billSlideIn 0.7s cubic-bezier(.2,.85,.3,1.05) both;',
    f'{indent}  border-radius: 18px;',
    f'{indent}  background: linear-gradient(160deg, #1a1d2e 0%, #14172a 100%);',
    f'{indent}  border: 1px solid rgba(123,97,255,0.35);',
    f'{indent}  box-shadow:',
    f'{indent}     0 30px 60px -20px rgba(0,0,0,0.75),',
    f'{indent}     0 18px 36px -18px rgba(123,97,255,0.45),',
    f'{indent}     0 2px 0 rgba(255,255,255,0.06) inset,',
    f'{indent}     0 -1px 0 rgba(0,0,0,0.4) inset;',
    f'{indent}  overflow: hidden;',
    f'{indent}  transition: transform .45s cubic-bezier(.2,.85,.3,1.05);',
    f'{indent}}}',
    f'{indent}.bill3d:hover {{',
    f'{indent}  transform: translateY(-4px) rotateX(1.5deg);',
    f'{indent}  box-shadow:',
    f'{indent}     0 40px 80px -24px rgba(0,0,0,0.85),',
    f'{indent}     0 22px 44px -20px rgba(123,97,255,0.65);',
    f'{indent}}}',
    f'{indent}',
    f'{indent}.bill3d-header {{',
    f'{indent}  position: relative;',
    f'{indent}  padding: 18px 24px;',
    f'{indent}  background: linear-gradient(120deg, #7b61ff 0%, #00d47a 55%, #7b61ff 100%);',
    f'{indent}  background-size: 300% 100%;',
    f'{indent}  animation: shimmer 6s linear infinite;',
    f'{indent}  color: #fff;',
    f'{indent}  display: flex; justify-content: space-between; align-items: center;',
    f'{indent}  font-weight: 700; font-size: 1.08rem;',
    f'{indent}  letter-spacing: 0.3px;',
    f'{indent}  text-shadow: 0 1px 2px rgba(0,0,0,0.35);',
    f'{indent}}}',
    f'{indent}.bill3d-header small {{',
    f'{indent}  font-weight: 500; opacity: 0.9; font-size: 0.8rem;',
    f'{indent}  background: rgba(0,0,0,0.25); padding: 3px 10px; border-radius: 12px;',
    f'{indent}}}',
    f'{indent}',
    f'{indent}.bill3d-body {{ padding: 8px 22px 14px; }}',
    f'{indent}',
    f'{indent}.bill3d-cols {{',
    f'{indent}  display: grid;',
    f'{indent}  grid-template-columns: 2.4fr 0.6fr 0.9fr 1fr;',
    f'{indent}  gap: 10px;',
    f'{indent}  padding: 12px 0 10px;',
    f'{indent}  border-bottom: 1px dashed rgba(255,255,255,0.14);',
    f'{indent}  font-size: 0.72rem;',
    f'{indent}  text-transform: uppercase;',
    f'{indent}  letter-spacing: 0.8px;',
    f'{indent}  color: #8892b0;',
    f'{indent}}}',
    f'{indent}',
    f'{indent}.bill3d-row {{',
    f'{indent}  display: grid;',
    f'{indent}  grid-template-columns: 2.4fr 0.6fr 0.9fr 1fr;',
    f'{indent}  gap: 10px;',
    f'{indent}  padding: 14px 0;',
    f'{indent}  border-bottom: 1px solid rgba(255,255,255,0.06);',
    f'{indent}  align-items: center;',
    f'{indent}  animation: rowFade 0.5s ease-out both;',
    f'{indent}}}',
    f'{indent}.bill3d-row:nth-child(1) {{ animation-delay: 0.10s; }}',
    f'{indent}.bill3d-row:nth-child(2) {{ animation-delay: 0.20s; }}',
    f'{indent}.bill3d-row:nth-child(3) {{ animation-delay: 0.30s; }}',
    f'{indent}.bill3d-row:nth-child(4) {{ animation-delay: 0.40s; }}',
    f'{indent}.bill3d-row:last-child {{ border-bottom: none; }}',
    f'{indent}',
    f'{indent}.bill3d-name {{ color: #e8ecf5; font-weight: 600; font-size: 0.95rem; }}',
    f'{indent}.bill3d-name small {{',
    f'{indent}  display: block; color: #6f7a99; font-weight: 400;',
    f'{indent}  font-size: 0.7rem; margin-top: 3px; letter-spacing: 0.4px;',
    f'{indent}}}',
    f'{indent}.bill3d-qty   {{ text-align: center; color: #b8c0d8; font-weight: 600; }}',
    f'{indent}.bill3d-rate  {{ text-align: right; color: #8892b0; }}',
    f'{indent}.bill3d-amt   {{ text-align: right; color: #e8ecf5; font-weight: 700; }}',
    f'{indent}',
    f'{indent}.bill3d-summary {{',
    f'{indent}  padding: 16px 24px 20px;',
    f'{indent}  background: linear-gradient(180deg, rgba(123,97,255,0.08), rgba(0,212,122,0.04));',
    f'{indent}  border-top: 2px solid rgba(123,97,255,0.35);',
    f'{indent}}}',
    f'{indent}.bill3d-sum-row {{',
    f'{indent}  display: flex; justify-content: space-between;',
    f'{indent}  padding: 6px 0; font-size: 0.92rem; color: #b8c0d8;',
    f'{indent}}}',
    f'{indent}.bill3d-total {{',
    f'{indent}  display: flex; justify-content: space-between; align-items: baseline;',
    f'{indent}  margin-top: 12px; padding-top: 14px;',
    f'{indent}  border-top: 2px solid rgba(0,212,122,0.45);',
    f'{indent}}}',
    f'{indent}.bill3d-total .label {{',
    f'{indent}  font-size: 1rem; color: #b8c0d8; font-weight: 600;',
    f'{indent}  letter-spacing: 0.5px; text-transform: uppercase;',
    f'{indent}}}',
    f'{indent}.bill3d-total .value {{',
    f'{indent}  font-size: 1.9rem; font-weight: 800; color: #00d47a;',
    f'{indent}  animation: pulseTotal 2.4s ease-in-out infinite;',
    f'{indent}  letter-spacing: -0.5px;',
    f'{indent}}}',
    f'{indent}.bill3d-pending {{',
    f'{indent}  margin-top: 14px; padding: 10px 14px;',
    f'{indent}  background: rgba(255,193,7,0.10);',
    f'{indent}  border-left: 3px solid #ffc107;',
    f'{indent}  border-radius: 8px;',
    f'{indent}  font-size: 0.78rem; color: #ffc107;',
    f'{indent}}}',
    f'{indent}</style>',
    f'{indent}""", unsafe_allow_html=True)',
    f'{indent}',
    f'{indent}_items = st.session_state.cart or []',
    f'{indent}_sub = 0.0',
    f'{indent}_rows = ""',
    f'{indent}for _i, _it in enumerate(_items):',
    f'{indent}    _n = _it.get("medicine") or _it.get("name") or _it.get("product") or "Item"',
    f'{indent}    _b = _it.get("batch") or ""',
    f'{indent}    _q = _it.get("qty") or _it.get("quantity") or 1',
    f'{indent}    _r = float(_it.get("price") or _it.get("rate") or _it.get("mrp") or 0)',
    f'{indent}    _amt = _q * _r',
    f'{indent}    _sub += _amt',
    f'{indent}    _batch = f"Batch {_b}" if _b else ""',
    f'{indent}    _rows += (',
    f'{indent}        f\'<div class="bill3d-row">\'',
    f'{indent}        f\'<div class="bill3d-name">{_n}<small>{_batch}</small></div>\'',
    f'{indent}        f\'<div class="bill3d-qty">{_q}</div>\'',
    f'{indent}        f\'<div class="bill3d-rate">₹{_r:,.2f}</div>\'',
    f'{indent}        f\'<div class="bill3d-amt">₹{_amt:,.2f}</div>\'',
    f'{indent}        f\'</div>\'',
    f'{indent}    )',
    f'{indent}',
    f'{indent}st.markdown(f"""',
    f'{indent}<div class="bill3d-scene">',
    f'{indent}  <div class="bill3d">',
    f'{indent}    <div class="bill3d-header">',
    f'{indent}      <span>🧾 Order Summary</span>',
    f'{indent}      <small>{len(_items)} item{"s" if len(_items)!=1 else ""}</small>',
    f'{indent}    </div>',
    f'{indent}    <div class="bill3d-body">',
    f'{indent}      <div class="bill3d-cols">',
    f'{indent}        <div>Item</div>',
    f'{indent}        <div style="text-align:center;">Qty</div>',
    f'{indent}        <div style="text-align:right;">Rate</div>',
    f'{indent}        <div style="text-align:right;">Amount</div>',
    f'{indent}      </div>',
    f'{indent}      {_rows}',
    f'{indent}    </div>',
    f'{indent}    <div class="bill3d-summary">',
    f'{indent}      <div class="bill3d-sum-row"><span>Subtotal (base)</span><span>₹{_sub:,.2f}</span></div>',
    f'{indent}      <div class="bill3d-sum-row"><span>Discount</span><span style="color:#ffc107;">Pending owner approval</span></div>',
    f'{indent}      <div class="bill3d-total">',
    f'{indent}        <span class="label">Payable</span>',
    f'{indent}        <span class="value">₹{_sub:,.2f}</span>',
    f'{indent}      </div>',
    f'{indent}      <div class="bill3d-pending">💡 Final amount with discount will be confirmed on Telegram after owner approves.</div>',
    f'{indent}    </div>',
    f'{indent}  </div>',
    f'{indent}</div>',
    f'{indent}""", unsafe_allow_html=True)',
    f'{indent}# ═══ END 3D BILL ═══',
]

src = "\n".join(lines[:start_i] + NEW + lines[end_i:])

APP.write_text(src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ 3D animated bill installed")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
