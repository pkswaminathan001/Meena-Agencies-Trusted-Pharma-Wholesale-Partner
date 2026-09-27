from pathlib import Path
import py_compile

APP = Path("app.py")
src = APP.read_text()
original = src
lines = src.split("\n")

# Find start of Amazon cart block (search for "# ═══ AMAZON-STYLE CART ═══")
start_i = None
for i, ln in enumerate(lines):
    if "# ═══ AMAZON-STYLE CART" in ln:
        start_i = i - 1   # the "if st.session_state.cart:" line is just above
        break

if start_i is None:
    print("❌ AMAZON-STYLE CART marker not found")
    raise SystemExit(1)

# Find end marker
end_i = None
for i in range(start_i, min(start_i + 150, len(lines))):
    if "# ═══ END AMAZON CART" in lines[i]:
        end_i = i + 1
        break

if end_i is None:
    print("❌ END AMAZON CART marker not found")
    raise SystemExit(1)

print(f"Replacing lines {start_i+1} .. {end_i}")

TEMPLATE = '''    if st.session_state.cart:
        # ═══ 3D AMAZON CART ═══
        st.markdown("""
<style>
@keyframes cartEnter {
  0%   { opacity: 0; transform: perspective(1200px) rotateX(-18deg) translateY(40px) scale(0.92); }
  60%  { opacity: 1; transform: perspective(1200px) rotateX(4deg)   translateY(-6px) scale(1.01); }
  100% { opacity: 1; transform: perspective(1200px) rotateX(0deg)   translateY(0)    scale(1);    }
}
@keyframes itemSlide {
  from { opacity: 0; transform: translateX(-24px) scale(0.96); }
  to   { opacity: 1; transform: translateX(0)     scale(1);    }
}
@keyframes totalPulse {
  0%,100% { text-shadow: 0 0 0 rgba(0,212,122,0);   transform: scale(1);    }
  50%     { text-shadow: 0 0 22px rgba(0,212,122,0.9); transform: scale(1.04); }
}
@keyframes shimmerBg {
  0%   { background-position: -250% 0; }
  100% { background-position:  250% 0; }
}
@keyframes glowRing {
  0%,100% { box-shadow: 0 0 0 0   rgba(123,97,255,0.45); }
  50%     { box-shadow: 0 0 32px 4px rgba(123,97,255,0.65); }
}
@keyframes badgeBounce {
  0%   { transform: scale(1);    }
  40%  { transform: scale(1.5);  }
  70%  { transform: scale(0.9);  }
  100% { transform: scale(1);    }
}

.cart-hero {
  perspective: 1400px;
  margin-bottom: 18px;
  animation: cartEnter 0.85s cubic-bezier(.2,.85,.3,1.05) both;
}
.cart-hero-inner {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  padding: 14px 26px 14px 20px;
  border-radius: 16px;
  background: linear-gradient(120deg, #7b61ff 0%, #00d47a 55%, #7b61ff 100%);
  background-size: 300% 100%;
  animation: shimmerBg 7s linear infinite;
  color: #fff;
  font-weight: 800;
  font-size: 1.2rem;
  letter-spacing: 0.4px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.35);
  box-shadow:
    0 22px 40px -18px rgba(123,97,255,0.6),
    0 8px 16px -8px rgba(0,0,0,0.4),
    0 1px 0 rgba(255,255,255,0.25) inset;
  transform-style: preserve-3d;
  transition: transform 0.4s cubic-bezier(.2,.85,.3,1.05);
}
.cart-hero-inner:hover { transform: translateY(-3px) rotateX(2deg); }
.cart-hero-icon { font-size: 1.6rem; }
.cart-hero-badge {
  background: #fff;
  color: #7b61ff;
  border-radius: 999px;
  padding: 4px 14px;
  font-size: 0.85rem;
  font-weight: 800;
  animation: badgeBounce 1s ease-out 1;
}

.cart-item-3d {
  animation: itemSlide 0.55s cubic-bezier(.2,.85,.3,1.05) both;
  perspective: 1000px;
}
.cart-item-3d:nth-child(1) { animation-delay: 0.08s; }
.cart-item-3d:nth-child(2) { animation-delay: 0.16s; }
.cart-item-3d:nth-child(3) { animation-delay: 0.24s; }
.cart-item-3d:nth-child(4) { animation-delay: 0.32s; }
.cart-item-3d:nth-child(5) { animation-delay: 0.40s; }

.cart-item-3d > div {
  transition: transform 0.35s cubic-bezier(.2,.85,.3,1.05),
              box-shadow 0.35s ease;
}
.cart-item-3d > div:hover {
  transform: translateY(-4px) rotateX(1deg) scale(1.01);
  box-shadow:
    0 20px 40px -20px rgba(123,97,255,0.55),
    0 8px 16px -8px rgba(0,0,0,0.5);
  border-color: rgba(123,97,255,0.6) !important;
}

.summary-3d {
  animation: glowRing 3.5s ease-in-out infinite;
  border-radius: 16px;
  padding: 4px;
  background: linear-gradient(160deg, #7b61ff33, #00d47a33);
}
.summary-3d-inner {
  border-radius: 12px;
  background: linear-gradient(180deg, #0f1220, #0a0c18);
  padding: 18px 20px;
}
.summary-total-value {
  font-size: 2rem;
  font-weight: 900;
  color: #00d47a;
  animation: totalPulse 2.4s ease-in-out infinite;
  letter-spacing: -0.6px;
  display: inline-block;
}
.summary-row {
  display: flex; justify-content: space-between;
  padding: 8px 0;
  font-size: 0.94rem;
  color: #b8c0d8;
}
.summary-divider {
  margin: 12px 0;
  border: none;
  border-top: 2px dashed rgba(0,212,122,0.35);
}
.summary-pending {
  background: rgba(255,193,7,0.08);
  border-left: 3px solid #ffc107;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.78rem;
  color: #ffc107;
  margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

        _items = st.session_state.cart
        _subtotal = 0.0
        for _x in _items:
            _q = _x.get("qty") or _x.get("quantity") or 1
            _p = float(_x.get("price") or _x.get("rate") or _x.get("mrp") or 0)
            _subtotal += _q * _p

        _count = len(_items)
        _plural = "item" if _count == 1 else "items"
        st.markdown(f'''
<div class="cart-hero">
  <div class="cart-hero-inner">
    <span class="cart-hero-icon">🛒</span>
    <span>Shopping Cart</span>
    <span class="cart-hero-badge">{_count} {_plural}</span>
  </div>
</div>
''', unsafe_allow_html=True)

        _col_items, _col_summary = st.columns([2.2, 1], gap="medium")

        with _col_items:
            _remove_idx = None
            for _i, _it in enumerate(_items):
                _name  = _it.get("medicine") or _it.get("name") or _it.get("product") or "Item"
                _batch = _it.get("batch") or "—"
                _iid   = _it.get("item_id") or _it.get("id") or ""
                _q     = _it.get("qty") or _it.get("quantity") or 1
                _r     = float(_it.get("price") or _it.get("rate") or _it.get("mrp") or 0)
                _amt   = _q * _r
                st.markdown('<div class="cart-item-3d">', unsafe_allow_html=True)
                with st.container(border=True):
                    _c1, _c2, _c3, _c4, _c5 = st.columns([0.55, 3, 1.1, 1.3, 0.5])
                    with _c1:
                        st.markdown("<div style='font-size:2.4rem;text-align:center;line-height:1;filter:drop-shadow(0 4px 8px rgba(255,82,82,0.4));'>💊</div>", unsafe_allow_html=True)
                    with _c2:
                        st.markdown(f"<div style='font-size:1.02rem;font-weight:700;color:#e8ecf5;'>{_name}</div>", unsafe_allow_html=True)
                        _sub = f"Batch {_batch}" + (f" · {_iid}" if _iid else "")
                        st.caption(_sub)
                    with _c3:
                        st.caption("Qty")
                        _new_q = st.number_input("Qty", min_value=1, value=int(_q), step=1, key=f"qty_{_i}", label_visibility="collapsed")
                        if _new_q != _q:
                            st.session_state.cart[_i]["qty"] = _new_q
                            st.rerun()
                    with _c4:
                        _html = f"<div style='text-align:right;'><b style='color:#00d47a;font-size:1.15rem;'>₹{_amt:,.2f}</b><br><small style='color:#8892b0;'>₹{_r:,.2f} × {_q}</small></div>"
                        st.markdown(_html, unsafe_allow_html=True)
                    with _c5:
                        if st.button("🗑️", key=f"rm_{_i}", help="Remove item"):
                            _remove_idx = _i
                st.markdown('</div>', unsafe_allow_html=True)
            if _remove_idx is not None:
                st.session_state.cart.pop(_remove_idx)
                st.rerun()

        with _col_summary:
            st.markdown('<div class="summary-3d"><div class="summary-3d-inner">', unsafe_allow_html=True)
            st.markdown("<div style='font-size:1.05rem;font-weight:700;color:#e8ecf5;margin-bottom:8px;'>🧾 Order Summary</div>", unsafe_allow_html=True)
            _h1 = f"<div class='summary-row'><span>Subtotal</span><b style='color:#e8ecf5;'>₹{_subtotal:,.2f}</b></div>"
            st.markdown(_h1, unsafe_allow_html=True)
            _h2 = "<div class='summary-row'><span>Discount</span><span style='color:#ffc107;font-size:0.82rem;font-style:italic;'>Pending owner approval</span></div>"
            st.markdown(_h2, unsafe_allow_html=True)
            st.markdown("<hr class='summary-divider'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:0.78rem;color:#b8c0d8;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:4px;'>Payable</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='summary-total-value'>₹{_subtotal:,.2f}</div>", unsafe_allow_html=True)
            st.markdown("<div class='summary-pending'>💡 Final amount with discount will be confirmed on Telegram after owner approves.</div>", unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
        # ═══ END 3D AMAZON CART ═══'''

NEW = TEMPLATE.split("\n")
src = "\n".join(lines[:start_i] + NEW + lines[end_i:])
APP.write_text(src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ 3D Amazon cart installed")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
