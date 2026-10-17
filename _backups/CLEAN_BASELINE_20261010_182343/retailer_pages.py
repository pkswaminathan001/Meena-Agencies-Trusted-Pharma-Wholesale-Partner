"""
retailer_pages.py — 8 new sidebar pages for retailers.
Each function renders one page. Self-contained data loaders.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
from inr import inr


# ── DATA LOADERS (self-contained) ──
def _orders():
    p = Path("orders.json")
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return []
    return []


def _inventory():
    try:
        conn = sqlite3.connect("inventory.db")
        df = pd.read_sql("SELECT * FROM inventory", conn)
        conn.close()
        df["selling_price"] = (df["cost_price"] * 1.25).round(2)
        return df
    except Exception:
        return pd.DataFrame()


def _my(retailer_id):
    return [o for o in _orders() if o.get("retailer_id") == retailer_id]


def _head(icon, title, sub=""):
    st.markdown(f"### {icon} {title}")
    if sub:
        st.caption(sub)


# ═══════════════════════════════════════════════════════════
# 1. REORDER LAST
# ═══════════════════════════════════════════════════════════
def render_reorder(r):
    _head("🔁", "Reorder Last Order", "One tap to repeat your previous order")

    orders = _my(r["id"])
    orders = [o for o in orders if o.get("items")]
    if not orders:
        st.info("No previous orders yet. Place your first order from **Place Order**.")
        return

    last = orders[-1]
    st.markdown(f"**Order ID:** `{last.get('order_id', '—')}`  ")
    st.markdown(f"**Placed:** {last.get('placed_at', '—')}  ")
    st.markdown(f"**Total:** {inr(last.get('total', 0), 2)}")

    st.markdown("---")
    st.markdown("**Items:**")
    total = 0
    for item in last.get("items", []):
        qty = int(item.get("qty", 1))
        price = float(item.get("price", 0))
        line = qty * price
        total += line
        st.markdown(f"- {item.get('medicine', '—')} × {qty} = {inr(line, 2)}")

    st.markdown(f"### Grand Total: {inr(total, 2)}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛒 Load into Cart", use_container_width=True, type="primary"):
            cart = []
            for item in last.get("items", []):
                cart.append({
                    "medicine": item.get("medicine", ""),
                    "batch": item.get("batch", ""),
                    "qty": int(item.get("qty", 1)),
                    "price": float(item.get("price", 0)),
                })
            st.session_state["cart"] = cart
            st.session_state["retailer_page"] = "cart"
            st.success("Cart loaded — go to Cart to review")
            st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.session_state["retailer_page"] = "home"
            st.rerun()


# ═══════════════════════════════════════════════════════════
# 2. LEDGER / BALANCE
# ═══════════════════════════════════════════════════════════
def render_ledger(r):
    _head("💰", "My Ledger", "Balance, credit and payment history")

    limit = float(r.get("credit_limit", 0))
    out = float(r.get("outstanding", 0))
    avail = limit - out
    used_pct = (out / limit * 100) if limit else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Credit Limit", f"{inr(limit)}")
    c2.metric("Outstanding", f"{inr(out)}", delta=f"{used_pct:.0f}% used", delta_color="inverse")
    c3.metric("Available", f"{inr(avail)}")

    st.markdown("---")
    st.markdown("**Payment History**")
    pays = r.get("payment_history", [])
    if not pays:
        st.info("No payments recorded yet.")
    else:
        df = pd.DataFrame([{
            "Date": p.get("date", "")[:16].replace("T", " "),
            "Amount": f"{inr(p.get('amount', 0))}",
            "Mode": p.get("mode", "cash").upper(),
            "Reference": p.get("reference", "—"),
        } for p in reversed(pays[-20:])])
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Recent Orders**")
    orders = _my(r["id"])[-10:]
    if orders:
        df = pd.DataFrame([{
            "Order": o.get("order_id", ""),
            "Date": o.get("placed_at", "")[:11],
            "Total": f"{inr(o.get('total', 0), 2)}",
            "Status": o.get("status", ""),
        } for o in reversed(orders)])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No orders yet.")


# ═══════════════════════════════════════════════════════════
# 3. NOTIFICATIONS
# ═══════════════════════════════════════════════════════════
def render_notifications(r):
    _head("🔔", "Notifications", "Updates on your orders and account")

    orders = _my(r["id"])
    if not orders:
        st.info("No notifications yet.")
        return

    for o in reversed(orders[-15:]):
        status = o.get("status", "Pending")
        emoji = {
            "Approved": "✅", "Delivered": "📦", "Pending": "⏳",
            "Cancelled": "❌", "Dispatched": "🚚", "Rejected": "🚫",
        }.get(status, "🔔")
        st.markdown(
            f"{emoji} **{status}** — Order `{o.get('order_id', '')}` "
            f"· {inr(o.get('total', 0), 2)}  "
            f"<span style='color:#8892b0;font-size:0.85rem;'>{o.get('placed_at', '')}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")


# ═══════════════════════════════════════════════════════════
# 4. OFFERS & SCHEMES
# ═══════════════════════════════════════════════════════════
def render_offers(r):
    _head("🎁", "Offers & Schemes", "Current deals for your shop")

    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(0,212,170,0.10),rgba(123,97,255,0.10));
                border:1px solid rgba(0,212,170,0.3);border-radius:12px;
                padding:16px 20px;margin:12px 0;">
        <div style="font-size:1.05rem;font-weight:800;color:#00d4aa;">🔁 Reorder Bonus</div>
        <div style="color:#e8eaf6;margin-top:4px;">Order 2× within 15 days — get <b>2% extra discount</b></div>
    </div>
    <div style="background:linear-gradient(135deg,rgba(255,181,71,0.10),rgba(196,30,58,0.10));
                border:1px solid rgba(255,181,71,0.3);border-radius:12px;
                padding:16px 20px;margin:12px 0;">
        <div style="font-size:1.05rem;font-weight:800;color:#ffb547;">💊 Bulk Deal</div>
        <div style="color:#e8eaf6;margin-top:4px;">Buy 50 boxes of any SKU — get <b>1 box free</b></div>
    </div>
    <div style="background:linear-gradient(135deg,rgba(255,77,109,0.10),rgba(123,97,255,0.10));
                border:1px solid rgba(255,77,109,0.3);border-radius:12px;
                padding:16px 20px;margin:12px 0;">
        <div style="font-size:1.05rem;font-weight:800;color:#ff4d6d;">📅 Expiry Saver</div>
        <div style="color:#e8eaf6;margin-top:4px;">Special prices on near-expiry stock — check with your rep</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Offers change every month. Contact your sales rep for latest.")


# ═══════════════════════════════════════════════════════════
# 5. FAVORITES / FREQUENT
# ═══════════════════════════════════════════════════════════
def render_favorites(r):
    _head("⭐", "Frequently Ordered", "Your top medicines — tap to reorder")

    orders = _my(r["id"])
    if not orders:
        st.info("Place a few orders and your frequent items will appear here.")
        return

    counts = {}
    details = {}
    for o in orders:
        for it in o.get("items", []):
            name = it.get("medicine", "")
            if not name:
                continue
            counts[name] = counts.get(name, 0) + int(it.get("qty", 1))
            details[name] = it

    if not counts:
        st.info("No items found in your orders.")
        return

    top = sorted(counts.items(), key=lambda x: -x[1])[:12]

    st.caption(f"Based on {len(orders)} orders")
    cols = st.columns(2)
    for i, (name, qty) in enumerate(top):
        with cols[i % 2]:
            info = details[name]
            price = float(info.get("price", 0))
            st.markdown(f"""
            <div style="background:rgba(26,31,58,0.7);border-left:3px solid #00d4aa;
                        border-radius:8px;padding:10px 12px;margin:4px 0;">
                <div style="font-weight:700;color:#e8eaf6;">{name}</div>
                <div style="font-size:0.75rem;color:#8892b0;">
                    Ordered {qty} times · {inr(price, 2)} each
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 Add", key=f"fav_{i}", use_container_width=True):
                st.session_state["cart"].append({
                    "medicine": name,
                    "batch": info.get("batch", ""),
                    "qty": 1,
                    "price": price,
                })
                st.success(f"Added {name}")
                st.rerun()


# ═══════════════════════════════════════════════════════════
# 6. CONTACT US
# ═══════════════════════════════════════════════════════════
def render_contact(r):
    _head("📞", "Contact Us", "We're here to help")

    st.markdown("""
    <div style="background:rgba(26,31,58,0.7);border-radius:12px;padding:20px;margin:12px 0;">
        <div style="font-size:1.1rem;font-weight:900;color:#00d4aa;">Meena Agencies</div>
        <div style="color:#8892b0;margin-top:4px;">Wholesale Pharma Distributor</div>
        <div style="margin-top:16px;color:#e8eaf6;line-height:2;">
            📞 <b>Sales:</b> 7338824033<br>
            📞 <b>Orders:</b> 6382130536<br>
            ✉️ <b>Email:</b> meena.agencies@gmail.com<br>
            🏢 <b>Address:</b> Thanjavur, Tamil Nadu
        </div>
        <div style="margin-top:16px;color:#8892b0;font-size:0.85rem;">
            GST: 33AIMB1112W · WBB-27-00012w · Drug Licence: 12/13/2026
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("[📞 Call Sales](tel:7338824033)", unsafe_allow_html=True)
    with c2:
        st.markdown("[💬 Telegram](https://t.me/Swaminathan_Inc_bot)", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# 7. STOCK CHECK
# ═══════════════════════════════════════════════════════════
def render_stock_check(r):
    _head("🔍", "Stock Check", "Search any medicine — see stock & price instantly")

    q = st.text_input("Search medicine", placeholder="e.g. Dolo, ORS, Azithromycin",
                      label_visibility="collapsed")

    df = _inventory()
    if df.empty:
        st.warning("Inventory data unavailable.")
        return

    if not q:
        st.caption("Type to search…")
        return

    sub = df[df["medicine_name"].str.contains(q, case=False, na=False)].head(30)
    if sub.empty:
        st.info(f"No medicines matching **{q}**.")
        return

    st.caption(f"{len(sub)} result(s)")
    for _, row in sub.iterrows():
        st.markdown(f"""
        <div style="background:rgba(26,31,58,0.7);border-left:3px solid #00d4aa;
                    border-radius:8px;padding:10px 14px;margin:6px 0;
                    display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-weight:700;color:#e8eaf6;">{row['medicine_name']}</div>
                <div style="font-size:0.75rem;color:#8892b0;">
                    Batch {row['batch']} · Exp {row['expiry_date']}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-weight:800;color:#00d4aa;">₹{row['selling_price']:.2f}</div>
                <div style="font-size:0.75rem;color:#00d47a;">✅ {int(row['quantity'])} in stock</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# 8. MY BUSINESS
# ═══════════════════════════════════════════════════════════
def render_business_stats(r):
    _head("📊", "My Business", "Your shop's purchase history")

    orders = [o for o in _my(r["id"]) if o.get("status") in ("Approved", "Delivered")]
    if not orders:
        st.info("No approved orders yet.")
        return

    total = sum(o.get("total", 0) for o in orders)
    avg = total / len(orders)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders", len(orders))
    c2.metric("Total Spent", f"{inr(total)}")
    c3.metric("Avg Order", f"{inr(avg)}")

    st.markdown("---")
    st.markdown("**Month-wise Spend**")

    monthly = {}
    for o in orders:
        dt_str = o.get("placed_at", "")
        try:
            dt = datetime.strptime(dt_str[:11], "%d-%b-%Y")
            key = dt.strftime("%b %Y")
            monthly[key] = monthly.get(key, 0) + o.get("total", 0)
        except Exception:
            continue

    if monthly:
        df = pd.DataFrame([
            {"Month": k, "Spend": f"{inr(v)}"}
            for k, v in sorted(monthly.items())
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Top 5 Medicines Bought**")
    counts = {}
    for o in orders:
        for it in o.get("items", []):
            n = it.get("medicine", "")
            counts[n] = counts.get(n, 0) + int(it.get("qty", 1))
    for name, qty in sorted(counts.items(), key=lambda x: -x[1])[:5]:
        st.markdown(f"- **{name}** — {qty} units")
