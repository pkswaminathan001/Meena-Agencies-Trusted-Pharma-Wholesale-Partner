from pathlib import Path
import py_compile

APP = Path("app.py")
src = APP.read_text()
original = src
lines = src.split("\n")

start_i = None
for i, ln in enumerate(lines):
    if i > 1400 and ln.strip() == "if st.session_state.cart:":
        start_i = i
        break

if start_i is None:
    print("❌ Could not find `if st.session_state.cart:` after line 1400")
    raise SystemExit(1)

end_i = None
for i in range(start_i + 1, min(start_i + 100, len(lines))):
    ln = lines[i]
    if ('Delivery location' in ln or 'location = st.text_input' in ln
        or 'location=st.text_input' in ln):
        end_i = i
        break

if end_i is None:
    for i in range(start_i + 1, min(start_i + 100, len(lines))):
        if 'Total:' in lines[i] and ('markdown' in lines[i] or '**' in lines[i]):
            end_i = i + 1
            break

if end_i is None:
    print(f"❌ Could not find end after line {start_i+1}")
    for j in range(start_i, min(start_i + 45, len(lines))):
        print(f"  {j+1}: {lines[j].rstrip()}")
    raise SystemExit(1)

print(f"Replacing lines {start_i+1} .. {end_i}")

# Use a template with escaped braces {{ }} so they survive generation
TEMPLATE = '''    if st.session_state.cart:
        # ═══ AMAZON-STYLE CART ═══
        _items = st.session_state.cart
        _subtotal = 0.0
        for _x in _items:
            _q = _x.get("qty") or _x.get("quantity") or 1
            _p = float(_x.get("price") or _x.get("rate") or _x.get("mrp") or 0)
            _subtotal += _q * _p

        _col_items, _col_summary = st.columns([2.2, 1], gap="medium")

        with _col_items:
            _count = len(_items)
            _plural = "item" if _count == 1 else "items"
            st.markdown(f"### 🛒 Shopping Cart · <span style='color:#8892b0;font-size:0.9rem;'>{_count} {_plural}</span>", unsafe_allow_html=True)
            _remove_idx = None
            for _i, _it in enumerate(_items):
                _name  = _it.get("medicine") or _it.get("name") or _it.get("product") or "Item"
                _batch = _it.get("batch") or "—"
                _iid   = _it.get("item_id") or _it.get("id") or ""
                _q     = _it.get("qty") or _it.get("quantity") or 1
                _r     = float(_it.get("price") or _it.get("rate") or _it.get("mrp") or 0)
                _amt   = _q * _r
                with st.container(border=True):
                    _c1, _c2, _c3, _c4, _c5 = st.columns([0.55, 3, 1.1, 1.3, 0.5])
                    with _c1:
                        st.markdown("<div style='font-size:2.2rem;text-align:center;line-height:1;'>💊</div>", unsafe_allow_html=True)
                    with _c2:
                        st.markdown(f"**{_name}**")
                        _sub = f"Batch {_batch}" + (f" · {_iid}" if _iid else "")
                        st.caption(_sub)
                    with _c3:
                        st.caption("Qty")
                        _new_q = st.number_input("Qty", min_value=1, value=int(_q), step=1, key=f"qty_{_i}", label_visibility="collapsed")
                        if _new_q != _q:
                            st.session_state.cart[_i]["qty"] = _new_q
                            st.rerun()
                    with _c4:
                        _html = f"<div style='text-align:right;'><b style='color:#e8ecf5;font-size:1.05rem;'>₹{_amt:,.2f}</b><br><small style='color:#8892b0;'>₹{_r:,.2f} × {_q}</small></div>"
                        st.markdown(_html, unsafe_allow_html=True)
                    with _c5:
                        if st.button("🗑️", key=f"rm_{_i}", help="Remove item"):
                            _remove_idx = _i
            if _remove_idx is not None:
                st.session_state.cart.pop(_remove_idx)
                st.rerun()

        with _col_summary:
            st.markdown("### 🧾 Order Summary")
            with st.container(border=True):
                _h1 = f"<div style='display:flex;justify-content:space-between;padding:6px 0;'><span style='color:#b8c0d8;'>Subtotal</span><b>₹{_subtotal:,.2f}</b></div>"
                st.markdown(_h1, unsafe_allow_html=True)
                _h2 = "<div style='display:flex;justify-content:space-between;padding:6px 0;'><span style='color:#b8c0d8;'>Discount</span><span style='color:#ffc107;font-size:0.82rem;font-style:italic;'>Pending owner approval</span></div>"
                st.markdown(_h2, unsafe_allow_html=True)
                st.markdown("<hr style='margin:10px 0;border:none;border-top:2px solid #00d47a55;'>", unsafe_allow_html=True)
                _h3 = f"<div style='display:flex;justify-content:space-between;align-items:baseline;'><span style='font-size:0.82rem;color:#b8c0d8;text-transform:uppercase;letter-spacing:0.6px;'>Payable</span><b style='color:#00d47a;font-size:1.6rem;font-weight:800;'>₹{_subtotal:,.2f}</b></div>"
                st.markdown(_h3, unsafe_allow_html=True)
            st.caption("💡 Discount will be confirmed on Telegram after owner approval.")
        # ═══ END AMAZON CART ═══'''

NEW = TEMPLATE.split("\n")

src = "\n".join(lines[:start_i] + NEW + lines[end_i:])
APP.write_text(src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ Amazon-style cart installed")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
