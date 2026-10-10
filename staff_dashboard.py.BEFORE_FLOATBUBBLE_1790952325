"""
staff_dashboard.py — Role 1: Counter Staff / Sales
Only 7 tasks. All confidential data blocked. Silent audit logging.
"""
import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import random

import staff_monitor
import staff_messages


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
# STAFF ORDER UI — Amazon-style card polish
# ═══════════════════════════════════════════════════════════
STAFF_CARD_CSS = """
<style>
/* Bigger, cleaner cards in the staff order grid */
[data-testid="stHorizontalBlock"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(30,45,80,0.6), rgba(15,25,50,0.7)) !important;
    border: 1px solid rgba(0,212,170,0.2) !important;
    border-radius: 14px !important;
    transition: all .25s ease !important;
    min-height: 190px !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(0,212,170,0.6) !important;
    background: linear-gradient(160deg, rgba(0,212,170,0.10), rgba(123,97,255,0.06)) !important;
    box-shadow: 0 10px 25px rgba(0,212,170,0.2) !important;
    transform: translateY(-2px);
}
/* Medicine name — larger */
[data-testid="stHorizontalBlock"] .stMarkdown {
    font-size: 0.92rem !important;
    line-height: 1.25 !important;
}
/* Add button — compact */
[data-testid="stHorizontalBlock"] .stButton > button {
    min-height: 38px !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    padding: 4px 12px !important;
}
</style>
"""


def _inject_card_css():
    try:
        import streamlit as st
        st.markdown(STAFF_CARD_CSS, unsafe_allow_html=True)
    except Exception:
        pass


def _load_json(p, default=None):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return default if default is not None else []


def _save_json(p, data):
    try:
        Path(p).write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def _load_inventory():
    """
    Load medicine catalog. Tries multiple filenames, column names, and formats.
    Returns a pandas DataFrame with normalized columns: medicine_name, quantity.
    """
    import pandas as pd
    from pathlib import Path

    # Possible filenames (in order of preference)
    candidates = [
        "inventory.csv", "inventory.csv", "Inventory.csv",
        "products.csv", "Products.csv", "stock.csv", "Stock.csv",
        "catalog.csv", "Catalog.csv", "medicines.csv", "Medicines.csv",
        "medicine_catalog.csv", "inventory_clean.csv",
    ]

    for fname in candidates:
        p = Path(fname)
        if not p.exists():
            continue
        try:
            df = pd.read_csv(fname)
            # Normalize column names
            rename_map = {}
            for c in df.columns:
                lc = str(c).lower().strip().replace(" ", "_")
                # Medicine name variations
                if lc in ("medicine_name", "medicine", "product", "product_name",
                          "name", "drug", "drug_name", "item", "item_name",
                          "particulars", "particular"):
                    rename_map[c] = "medicine_name"
                # Quantity variations
                elif lc in ("quantity", "qty", "stock", "in_stock", "available",
                            "available_qty", "closing_stock", "balance",
                            "stock_qty", "units"):
                    rename_map[c] = "quantity"
                # Batch variations
                elif lc in ("batch", "batch_no", "batchno", "batch_number"):
                    rename_map[c] = "batch"
                # Expiry variations
                elif lc in ("expiry", "exp", "exp_date", "expiry_date", "expires"):
                    rename_map[c] = "expiry"
                # Pack variations
                elif lc in ("pack", "packing", "pack_size", "unit", "units_per_pack"):
                    rename_map[c] = "pack"

            if rename_map:
                df = df.rename(columns=rename_map)

            # If still no medicine_name, use first text column
            if "medicine_name" not in df.columns and len(df.columns) > 0:
                for c in df.columns:
                    if df[c].dtype == "object":
                        df = df.rename(columns={c: "medicine_name"})
                        break

            # If no quantity column, default to 100
            if "quantity" not in df.columns:
                df["quantity"] = 100

            return df
        except Exception:
            continue

    # Try JSON as fallback
    for jname in ["inventory.json", "products.json", "medicines.json", "catalog.json"]:
        p = Path(jname)
        if p.exists():
            try:
                import json
                data = json.loads(p.read_text())
                if isinstance(data, list):
                    return pd.DataFrame(data)
                if isinstance(data, dict):
                    return pd.DataFrame(list(data.values()))
            except Exception:
                continue

    # Try SQLite as last resort
    for dbname in ["inventory.db", "pharma.db", "data.db"]:
        p = Path(dbname)
        if p.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(dbname)
                # Look for tables
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
                for tbl in tables["name"]:
                    if "inv" in tbl.lower() or "medic" in tbl.lower() or "product" in tbl.lower():
                        df = pd.read_sql(f"SELECT * FROM {tbl}", conn)
                        conn.close()
                        return df
                conn.close()
            except Exception:
                continue

    return pd.DataFrame()



def _get_tier_discount(retailer_id):
    """Get tier % for a retailer — SILENTLY, no display of rule logic."""
    try:
        import discounts as _dc
        t = _dc.get_customer_tier(retailer_id)
        if isinstance(t, tuple):
            return t[1]
    except Exception:
        pass
    return 0.0


def _safe_inventory_columns(df):
    """Return inventory columns safe for staff (NO cost, NO margin)."""
    blocked = {"cost_price", "cost", "purchase_price", "profit",
               "margin", "buying_price", "supplier_price"}
    return [c for c in df.columns if c.lower() not in blocked]




def _med_icon(medicine_name: str) -> str:
    """Return an emoji icon based on medicine name keywords."""
    if not medicine_name:
        return "💊"
    n = str(medicine_name).lower()

    # Injection / insulin
    if any(k in n for k in ["inject", "insulin", "vial", "ampoule", "syringe", "glargine"]):
        return "💉"
    # Syrup / liquid
    if any(k in n for k in ["syrup", "susp", "suspension", "liquid", "drops", "solution", "tonic"]):
        return "🧴"
    # Powder / sachet
    if any(k in n for k in ["powder", "sachet", "granules", "ors"]):
        return "🥄"
    # Inhaler / respiratory
    if any(k in n for k in ["inhaler", "respule", "rotacap", "respiratory", "asthma"]):
        return "💨"
    # Cream / ointment / gel / lotion
    if any(k in n for k in ["cream", "ointment", "gel", "lotion", "topical", "balm"]):
        return "🧴"
    # Eye / ear / nasal
    if any(k in n for k in ["eye", "ear", "nasal", "ophthalmic", "otic"]):
        return "👁️"
    # Vitamins / supplements
    if any(k in n for k in ["vitamin", "vit", "calcium", "zinc", "iron", "folic", "b-complex"]):
        return "🌱"
    # Cardiac / BP
    if any(k in n for k in ["cardiac", "heart", "bp", "amlodipine", "telmisartan",
                             "atenolol", "metoprolol", "losartan", "statin"]):
        return "❤️"
    # Diabetes
    if any(k in n for k in ["diabet", "metformin", "glimepiride", "glycomet", "sugar"]):
        return "🩸"
    # Antibiotic
    if any(k in n for k in ["amoxi", "azithro", "cef", "cipro", "doxy", "penicill",
                             "clav", "antibiotic", "ceftri"]):
        return "🦠"
    # Pain relief / anti-inflammatory
    if any(k in n for k in ["dolo", "para", "ibupro", "diclof", "aspirin",
                             "pain", "nimesulide", "naprox", "ketorol"]):
        return "🩹"
    # Allergy / antihistamine
    if any(k in n for k in ["cetiri", "lorat", "fexo", "montelu", "allegra",
                             "allergy", "histamine"]):
        return "🤧"
    # Gastric / acidity
    if any(k in n for k in ["pantop", "omepra", "ranit", "gastro", "acidity",
                             "antacid", "eno", "digene"]):
        return "🫃"
    # Cough / cold / respiratory
    if any(k in n for k in ["cough", "cold", "benadryl", "ascoril", "flu", "fever"]):
        return "🤒"
    # Dermatology
    if any(k in n for k in ["derma", "skin", "cream", "soap", "shampoo", "lotion"]):
        return "🧼"
    # Tablets / capsules (default)
    return "💊"


def _staff_info():
    sid = st.session_state.get("staff_id") or "STAFF001"
    name = st.session_state.get("staff_name") or "Counter Staff"
    return sid, name


# ═══════════════════════════════════════════════════════════
# MAIN RENDER
# ═══════════════════════════════════════════════════════════

def render():
    staff_id, staff_name = _staff_info()

    # ── Session logging (once) ──
    if not st.session_state.get("_staff_session_logged"):
        staff_monitor.log_session(staff_id, staff_name, "START")
        st.session_state["_staff_session_logged"] = True

    # ── Page view logging ──
    view = st.session_state.get("staff_view", "home")
    if st.session_state.get("_staff_last_view") != view:
        staff_monitor.log_page(staff_id, staff_name, view)
        st.session_state["_staff_last_view"] = view

    # ── Header ──
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:12px 18px;border-radius:14px;margin-bottom:16px;
                background:linear-gradient(135deg,rgba(0,212,170,0.15),rgba(123,97,255,0.10));
                border:1px solid rgba(0,212,170,0.3);">
        <div>
            <div style="font-size:1.15rem;font-weight:800;color:#eaf6ff;">
                🧑‍💼 {staff_name}
            </div>
            <div style="font-size:0.72rem;color:#8892b0;letter-spacing:1.4px;margin-top:2px;">
                STAFF ID · {staff_id} &nbsp;·&nbsp; {datetime.now().strftime('%d %b %Y, %H:%M')}
            </div>
        </div>
        <div style="color:#00d4aa;font-weight:700;font-size:0.85rem;">● On Duty</div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # HOME — 7 tasks grid
    # ═══════════════════════════════════════════════════════════
    if view == "home":
        st.markdown("### ⚡ What do you want to do?")

        # ═══ Quick Actions ═══
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🛒\n\n**New Order**\nTake phone/walk-in",
                         use_container_width=True, key="sd_new_order"):
                staff_monitor.log_action(staff_id, staff_name, "OPEN_NEW_ORDER")
                st.session_state["staff_view"] = "new_order"
                st.rerun()
        with c2:
            if st.button("🔍\n\n**Check Stock**\nIs it available?",
                         use_container_width=True, key="sd_stock"):
                staff_monitor.log_action(staff_id, staff_name, "OPEN_STOCK_LOOKUP")
                st.session_state["staff_view"] = "stock"
                st.rerun()
        with c3:
            if st.button("🏪\n\n**Look Up Retailer**\nHistory + due",
                         use_container_width=True, key="sd_retailer"):
                staff_monitor.log_action(staff_id, staff_name, "OPEN_RETAILER_LOOKUP")
                st.session_state["staff_view"] = "retailer"
                st.rerun()
        with c4:
            if st.button("💬\n\n**Message Owner**\nAsk approval",
                         use_container_width=True, key="sd_msg"):
                staff_monitor.log_action(staff_id, staff_name, "OPEN_MESSAGE_OWNER")
                st.session_state["staff_view"] = "message"
                st.rerun()

        # ═══ Orders Ready to Pack ═══
        st.markdown("---")
        all_orders = _load_json("orders.json", [])

        # Approved / Pending orders waiting for packing
        ready = [o for o in all_orders
                 if o.get("status") in ("Approved", "Pending")
                 and o.get("status") != "Cancelled"]

        st.markdown(f"### 📦 Orders Ready to Pack ({len(ready)})")
        if not ready:
            st.success("✅ No orders waiting for packing right now")
        else:
            for o in ready[:10]:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        oid = o.get("order_id", "?")
                        shop = o.get("shop", "?")
                        st.markdown(f"**{oid}** · {shop}")
                        # Source badge
                        source = o.get("source", "app")
                        badge = "📱 App" if source == "app" else "📞 Phone"
                        st.caption(f"From: {badge} · Approved: {o.get('approved_at', o.get('placed_at','—'))}")
                        # Items preview with icons
                        items = o.get("items", [])
                        preview_parts = []
                        for it in items[:4]:
                            _mi = _med_icon(it.get("medicine", "?"))
                            preview_parts.append(
                                f"{_mi} {it.get('medicine','?')} × {it.get('qty',1)}"
                            )
                        item_preview = "  ·  ".join(preview_parts)
                        if len(items) > 4:
                            item_preview += f"  + {len(items) - 4} more"
                        st.caption(f"📋 {item_preview}")
                    with c2:
                        st.markdown(f"### ₹{o.get('total',0):,.0f}")
                    with c3:
                        if st.button("👁 View", key=f"view_{oid}", use_container_width=True):
                            staff_monitor.log_action(staff_id, staff_name, "VIEW_ORDER",
                                                    details=oid)
                            st.session_state["staff_view_order"] = oid
                            st.session_state["staff_view"] = "order_detail"
                            st.rerun()

        # ═══ Packed — Awaiting Dispatch ═══
        packed = [o for o in all_orders if o.get("status") == "Packed"]
        if packed:
            st.markdown(f"### 🚚 Packed — Awaiting Dispatch ({len(packed)})")
            for o in packed[:5]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{o.get('order_id','?')}** · {o.get('shop','?')}")
                        st.caption(f"Packed: {o.get('packed_at','—')} · ₹{o.get('total',0):,.0f}")
                    with c2:
                        if st.button("🚚 Dispatch", key=f"disp_{o.get('order_id')}",
                                     use_container_width=True):
                            for oo in all_orders:
                                if oo.get("order_id") == o.get("order_id"):
                                    oo["status"] = "Dispatched"
                                    oo["dispatched_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
                                    break
                            _save_json("orders.json", all_orders)
                            staff_monitor.log_action(staff_id, staff_name, "ORDER_DISPATCHED",
                                                    details=o.get("order_id",""))
                            # Notify owner
                            try:
                                import staff_messages
                                staff_messages.send_message(
                                    staff_id, staff_name,
                                    subject=f"Order dispatched — {o.get('shop','?')}",
                                    body=f"Order {o.get('order_id','')} dispatched to {o.get('shop','')}.",
                                    priority="normal",
                                )
                            except Exception:
                                pass
                            st.success("✅ Marked dispatched")
                            st.rerun()

        # ═══ Today's Summary ═══
        st.markdown("---")
        st.markdown("### 📋 Today's Summary")
        today_str = datetime.now().strftime("%d-%b-%Y").upper()
        my_today = [o for o in all_orders
                    if str(o.get("placed_at", "")).upper().startswith(today_str)]
        k1, k2, k3 = st.columns(3)
        k1.metric("📥 Today's Orders", len(my_today))
        k2.metric("⏳ To Pack", len([o for o in my_today if o.get("status") in ("Pending", "Approved")]))
        k3.metric("✅ Completed", len([o for o in my_today if o.get("status") in ("Packed", "Dispatched", "Delivered")]))

    # ═══════════════════════════════════════════════════════════
    # TASK 1 — NEW ORDER (Amazon-style cards, one-tap add)
    # ═══════════════════════════════════════════════════════════
    elif view == "new_order":
        st.markdown("### 🛒 Take New Order")

        retailers = _load_json("retailers.json", [])
        if not retailers:
            st.error("No retailers registered yet. Contact owner.")
            if st.button("← Back"): st.session_state["staff_view"] = "home"; st.rerun()
            return

        # ═══ STEP 1: Pick retailer ═══
        options = {f"{r['id']} — {r['shop']}": r for r in retailers}
        pick_label = st.selectbox("👤 Retailer", list(options.keys()), key="sd_no_retailer")
        retailer = options[pick_label]
        tier_discount = _get_tier_discount(retailer["id"])

        # Retailer info strip
        st.markdown(f"""
        <div style="display:flex;gap:14px;align-items:center;padding:10px 14px;
                    background:linear-gradient(135deg,rgba(0,212,170,0.10),rgba(123,97,255,0.06));
                    border-radius:12px;border:1px solid rgba(0,212,170,0.25);
                    margin-bottom:14px;">
            <div style="font-size:1.6rem;">🏪</div>
            <div>
                <div style="font-weight:700;color:#eaf6ff;font-size:0.95rem;">{retailer['shop']}</div>
                <div style="color:#8892b0;font-size:0.72rem;">
                    {retailer.get('owner','—')} · {retailer.get('phone','—')}
                    · Tier: <b style="color:#00d4aa;">{tier_discount:.0f}% off</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ═══ STEP 2: Show ALL medicines as cards ═══
        _inject_card_css()
        inv = _load_inventory()
        if inv.empty:
            st.error("Inventory not loaded.")
        else:
            # Search bar
            st.markdown("#### 💊 Choose medicines")
            search = st.text_input("🔍 Search medicine",
                                   placeholder="Type to filter · e.g. Dolo, Amox, Insulin",
                                   key="sd_no_search",
                                   label_visibility="collapsed")

            # Filter
            if search and len(search) >= 2:
                filtered = inv[inv["medicine_name"].astype(str)
                               .str.contains(search, case=False, na=False)]
                staff_monitor.log_data_access(staff_id, staff_name,
                                             "ORDER_SEARCH", f"q={search}",
                                             allowed=True)
            else:
                filtered = inv

            if len(filtered) == 0:
                st.warning("No medicines match your search")
            else:
                # Show card grid — 3 per row
                st.caption(f"Showing {min(60, len(filtered))} of {len(filtered)} medicines")
                safe_cols = _safe_inventory_columns(filtered)
                display = filtered[safe_cols].head(60)

                cols = st.columns(3)
                for i, (_, row) in enumerate(display.iterrows()):
                    med = str(row.get("medicine_name", "Medicine"))
                    qty_avail = int(float(row.get("quantity", 0) or 0))
                    batch = str(row.get("batch", ""))
                    expiry = str(row.get("expiry", ""))
                    pack = str(row.get("pack", ""))

                    # Stock health
                    if qty_avail == 0:
                        stock_badge = '<span style="color:#ff5252;">❌ Out of stock</span>'
                    elif qty_avail < 20:
                        stock_badge = f'<span style="color:#ffc107;">⚠️ Only {qty_avail} left</span>'
                    else:
                        stock_badge = f'<span style="color:#00d47a;">✅ {qty_avail} in stock</span>'

                    with cols[i % 3]:
                        # Card container
                        with st.container(border=True):
                            st.markdown(f"""
                            <div style="min-height:110px;">
                                <div style="font-size:0.92rem;font-weight:700;color:#eaf6ff;
                                            line-height:1.25;min-height:44px;">💊 {med}</div>
                                <div style="font-size:0.68rem;color:#8892b0;margin-top:4px;">
                                    Batch {batch or '—'} · {pack or '10s'}
                                </div>
                                <div style="font-size:0.72rem;margin-top:6px;">{stock_badge}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Quantity + Add button
                            qcol, bcol = st.columns([1, 2])
                            with qcol:
                                qty = st.number_input("Qty", min_value=1, value=1,
                                                     step=1, key=f"sd_qty_{i}",
                                                     label_visibility="collapsed")
                            with bcol:
                                if st.button("➕ Add", key=f"sd_add_{i}",
                                             use_container_width=True,
                                             disabled=(qty_avail == 0)):
                                    if "cart_staff" not in st.session_state:
                                        st.session_state["cart_staff"] = []
                                    st.session_state["cart_staff"].append({
                                        "medicine": med,
                                        "qty": int(qty),
                                        "batch": batch,
                                    })
                                    staff_monitor.log_action(
                                        staff_id, staff_name,
                                        "ADD_TO_CART",
                                        details=f"{med} × {qty}"
                                    )
                                    st.toast(f"✅ Added {med} × {qty}", icon="🛒")
                                    st.rerun()

        # ═══ STEP 3: Current order ═══
        cart = st.session_state.get("cart_staff", [])
        if cart:
            st.markdown("---")
            st.markdown(f"### 🧾 Current Order · {len(cart)} item(s)")

            total_qty = 0
            for i, it in enumerate(cart):
                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    st.markdown(f"**{it['medicine']}**")
                    st.caption(f"Batch {it.get('batch','—')}")
                with c2:
                    st.markdown(f"**× {it['qty']}**")
                    total_qty += it["qty"]
                with c3:
                    if st.button("🗑️", key=f"sd_rm_{i}"):
                        cart.pop(i)
                        staff_monitor.log_action(staff_id, staff_name,
                                                 "REMOVE_FROM_CART",
                                                 details=it["medicine"])
                        st.rerun()

            st.info(f"📦 Total: **{total_qty}** units · **{len(cart)}** distinct medicines")

            note = st.text_input("📝 Note for owner (optional)",
                                 key="sd_no_note",
                                 placeholder="Any special instruction…")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ Clear Order", key="sd_no_clear",
                             use_container_width=True):
                    st.session_state["cart_staff"] = []
                    st.rerun()
            with col_b:
                if st.button("📤 Send Order to Owner", key="sd_no_submit",
                             use_container_width=True, type="primary"):
                    items_txt = "\n".join([f"• {it['medicine']} × {it['qty']}"
                                            for it in cart])
                    staff_messages.send_message(
                        staff_id, staff_name,
                        subject=f"New order — {retailer['shop']}",
                        body=(f"Retailer: {retailer['id']} — {retailer['shop']}\n"
                              f"Tier discount: {tier_discount:.0f}%\n\n"
                              f"Items ({len(cart)}):\n{items_txt}\n\n"
                              f"Total: {total_qty} units\n"
                              f"Note: {note}"),
                        priority="urgent",
                    )
                    staff_monitor.log_action(staff_id, staff_name,
                                             "NEW_ORDER_SUBMITTED",
                                             details=f"{retailer['id']} · {len(cart)} items")
                    st.success("✅ Order sent to owner for confirmation!")
                    st.balloons()
                    st.session_state["cart_staff"] = []
                    st.session_state["staff_view"] = "home"
                    st.rerun()

        if st.button("← Back", key="sd_no_back"):
            st.session_state["staff_view"] = "home"
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # ORDER DETAIL VIEW
    # ═══════════════════════════════════════════════════════════
    elif view == "order_detail":
        oid = st.session_state.get("staff_view_order")
        all_orders = _load_json("orders.json", [])
        o = next((x for x in all_orders if x.get("order_id") == oid), None)

        if not o:
            st.error(f"Order {oid} not found")
        else:
            st.markdown(f"### 📦 Order Details")

            # Order header card
            source = o.get("source", "app")
            badge = "📱 App Order" if source == "app" else "📞 Phone Order"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(0,212,170,0.10),rgba(123,97,255,0.06));
                        padding:16px 20px;border-radius:14px;border:1px solid rgba(0,212,170,0.25);">
                <div style="font-size:1.1rem;font-weight:800;color:#eaf6ff;">
                    {o.get('order_id','?')}
                </div>
                <div style="color:#8892b0;font-size:0.82rem;margin-top:6px;">
                    {badge} · Placed {o.get('placed_at','—')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🏪 Retailer")
                st.markdown(f"**{o.get('shop','?')}**")
                st.caption(f"ID: {o.get('retailer_id','?')}")
                # Look up retailer info
                retailers = _load_json("retailers.json", [])
                ret = next((r for r in retailers if r["id"] == o.get("retailer_id")), {})
                if ret:
                    st.caption(f"Owner: {ret.get('owner','—')}")
                    st.caption(f"Phone: {ret.get('phone','—')}")
                    st.caption(f"Address: {ret.get('address','—')}")
            with c2:
                st.markdown("#### 📊 Status")
                st.markdown(f"**{o.get('status','?')}**")
                st.caption(f"Total: ₹{o.get('total',0):,.2f}")
                st.caption(f"Items: {len(o.get('items',[]))}")

            st.markdown("---")
            st.markdown("#### 📋 Items to Pack")

            # Build one HTML block — clean single-row cards
            _items_html = ""
            for it in o.get("items", []):
                _mname = it.get("medicine", "?")
                _icon = _med_icon(_mname)
                _batch = it.get("batch", "—")
                _qty = it.get("qty", 1)
                _items_html += f"""
                <div style="
                    display:flex;align-items:center;gap:16px;
                    padding:14px 18px;margin-bottom:10px;
                    background:linear-gradient(135deg,rgba(30,45,80,0.55),rgba(15,25,50,0.65));
                    border:1px solid rgba(0,212,170,0.20);
                    border-radius:12px;
                ">
                    <div style="font-size:2rem;width:48px;text-align:center;
                                flex-shrink:0;line-height:1;">{_icon}</div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:1rem;font-weight:700;color:#eaf6ff;
                                    margin-bottom:2px;">{_mname}</div>
                        <div style="font-size:0.75rem;color:#8892b0;">Batch: {_batch}</div>
                    </div>
                    <div style="font-size:1.35rem;font-weight:800;color:#00d4aa;
                                white-space:nowrap;padding-left:10px;">× {_qty}</div>
                </div>
                """
            st.markdown(_items_html, unsafe_allow_html=True)

            st.markdown("---")

            # Action buttons based on status
            if o.get("status") in ("Approved", "Pending"):
                if st.button("📦 Mark as Packed", key="detail_pack",
                             use_container_width=True, type="primary"):
                    for oo in all_orders:
                        if oo.get("order_id") == oid:
                            oo["status"] = "Packed"
                            oo["packed_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
                            oo["packed_by"] = staff_name
                            break
                    _save_json("orders.json", all_orders)
                    staff_monitor.log_action(staff_id, staff_name, "ORDER_PACKED",
                                            details=oid)
                    # Notify owner
                    try:
                        import staff_messages
                        staff_messages.send_message(
                            staff_id, staff_name,
                            subject=f"Order packed — {o.get('shop','?')}",
                            body=f"Order {oid} packed by {staff_name}.",
                            priority="normal",
                        )
                    except Exception:
                        pass
                    st.success(f"✅ Order {oid} marked as Packed")
                    st.balloons()
                    st.session_state["staff_view"] = "home"
                    st.rerun()
            elif o.get("status") == "Packed":
                if st.button("🚚 Mark as Dispatched", key="detail_dispatch",
                             use_container_width=True, type="primary"):
                    for oo in all_orders:
                        if oo.get("order_id") == oid:
                            oo["status"] = "Dispatched"
                            oo["dispatched_at"] = datetime.now().strftime("%d-%b-%Y %H:%M").upper()
                            break
                    _save_json("orders.json", all_orders)
                    staff_monitor.log_action(staff_id, staff_name, "ORDER_DISPATCHED",
                                            details=oid)
                    st.success("✅ Order dispatched")
                    st.session_state["staff_view"] = "home"
                    st.rerun()

            if st.button("← Back to Queue", key="detail_back"):
                st.session_state["staff_view"] = "home"
                st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TASK 2 — CHECK STOCK
    # ═══════════════════════════════════════════════════════════
    elif view == "stock":
        st.markdown("### 🔍 Check Stock")
        inv = _load_inventory()
        if inv.empty:
            st.error("Inventory not loaded. Contact owner.")
        else:
            q = st.text_input("Medicine name", key="sd_stock_q",
                              placeholder="Type 3+ chars")
            if q and len(q) >= 3:
                matches = inv[inv["medicine_name"].astype(str)
                              .str.contains(q, case=False, na=False)]
                if len(matches) == 0:
                    st.warning(f"No stock found for '{q}'")
                else:
                    staff_monitor.log_data_access(staff_id, staff_name,
                                                 "STOCK_LOOKUP", f"q='{q}' matches={len(matches)}")
                    # Show ONLY safe columns — no cost, no margin
                    safe_cols = _safe_inventory_columns(matches)
                    st.dataframe(matches[safe_cols].head(30), use_container_width=True)
                    # Availability summary
                    if "quantity" in matches.columns:
                        total = int(matches["quantity"].astype(float).sum())
                        st.info(f"📦 Total available: **{total}** units across {len(matches)} batches")

        if st.button("← Back", key="sd_stk_back"):
            st.session_state["staff_view"] = "home"
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TASK 3 — LOOK UP RETAILER
    # ═══════════════════════════════════════════════════════════
    elif view == "retailer":
        st.markdown("### 🏪 Look Up Retailer")
        retailers = _load_json("retailers.json", [])
        if not retailers:
            st.error("No retailers yet")
        else:
            options = {f"{r['id']} — {r['shop']}": r for r in retailers}
            pick = st.selectbox("Retailer", list(options.keys()), key="sd_ret_pick")
            r = options[pick]
            staff_monitor.log_data_access(staff_id, staff_name,
                                         "RETAILER_LOOKUP", f"{r['id']}")

            # Show only safe retailer info
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(0,212,170,0.08),rgba(123,97,255,0.05));
                        padding:16px 20px;border-radius:14px;border:1px solid rgba(0,212,170,0.22);">
                <div style="font-size:1.25rem;font-weight:800;color:#eaf6ff;">{r['shop']}</div>
                <div style="color:#8892b0;font-size:0.85rem;margin-top:4px;">
                    Owner: {r.get('owner','—')} · Phone: {r.get('phone','—')}
                </div>
                <div style="color:#8892b0;font-size:0.85rem;margin-top:2px;">
                    Credit limit: ₹{r.get('credit_limit',0):,} · Outstanding: ₹{r.get('outstanding',0):,}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Their recent orders
            orders = _load_json("orders.json", [])
            mine = [o for o in orders if o.get("retailer_id") == r["id"]]
            recent = sorted(mine, key=lambda o: o.get("placed_at",""), reverse=True)[:5]
            st.markdown("#### Recent orders")
            if not recent:
                st.caption("No orders yet")
            else:
                for o in recent:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"**{o.get('order_id','?')}** · ₹{o.get('total',0):,.2f}")
                        c1.caption(f"{o.get('placed_at','')} · {o.get('status','?')}")
                        c2.markdown(f"**{o.get('status','?')}**")

        if st.button("← Back", key="sd_ret_back"):
            st.session_state["staff_view"] = "home"
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TASK 4 — RECORD PAYMENT
    # ═══════════════════════════════════════════════════════════
    elif view == "payment":
        st.markdown("### 💰 Record Payment")
        st.info("Record payment received from a retailer. Owner will verify.")

        retailers = _load_json("retailers.json", [])
        if not retailers:
            st.error("No retailers")
        else:
            options = {f"{r['id']} — {r['shop']}": r for r in retailers}
            pick = st.selectbox("Retailer", list(options.keys()), key="sd_pay_ret")
            r = options[pick]

            with st.form("sd_payment_form"):
                amt = st.number_input("Amount received (₹)", min_value=1.0, value=1000.0, step=100.0)
                mode = st.selectbox("Payment mode", ["Cash", "UPI", "Cheque", "NEFT", "Card"])
                ref = st.text_input("Reference / Cheque no. (optional)")
                note = st.text_input("Note (optional)")
                submitted = st.form_submit_button("📤 Send to Owner for Confirmation",
                                                 use_container_width=True, type="primary")
                if submitted:
                    staff_messages.send_message(
                        staff_id, staff_name,
                        subject=f"Payment received — {r['shop']}",
                        body=(f"Retailer: {r['id']} — {r['shop']}\n"
                              f"Amount: ₹{amt:,.2f}\n"
                              f"Mode: {mode}\n"
                              f"Reference: {ref}\n"
                              f"Note: {note}"),
                        priority="normal",
                    )
                    staff_monitor.log_action(staff_id, staff_name, "PAYMENT_RECORDED",
                                             details=f"{r['id']} · ₹{amt:,.2f} · {mode}")
                    st.success("✅ Sent to owner for confirmation")
                    st.session_state["staff_view"] = "home"
                    st.rerun()

        if st.button("← Back", key="sd_pay_back"):
            st.session_state["staff_view"] = "home"
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TASK 5 — PRINT INVOICE
    # ═══════════════════════════════════════════════════════════
    elif view == "invoice":
        st.markdown("### 📄 Print Invoice")
        orders = _load_json("orders.json", [])
        # Only show orders that are ready (Packed/Dispatched)
        ready = [o for o in orders if o.get("status") in ("Packed", "Dispatched", "Approved")]
        if not ready:
            st.info("No ready orders to invoice yet")
        else:
            options = {f"{o.get('order_id','?')} — {o.get('shop','?')} · ₹{o.get('total',0):,.2f}": o
                       for o in ready[:30]}
            pick = st.selectbox("Order", list(options.keys()), key="sd_inv_pick")
            o = options[pick]
            staff_monitor.log_action(staff_id, staff_name, "VIEW_INVOICE",
                                     details=o.get("order_id",""))

            st.markdown("#### Invoice preview")
            with st.container(border=True):
                st.markdown(f"**Order:** {o.get('order_id','?')}")
                st.markdown(f"**Retailer:** {o.get('shop','?')} ({o.get('retailer_id','?')})")
                st.markdown(f"**Placed:** {o.get('placed_at','?')}")
                st.markdown("---")
                items = o.get("items", [])
                for it in items:
                    st.markdown(f"• {it.get('medicine','?')} × {it.get('qty',1)}")
                st.markdown(f"### Total: ₹{o.get('total',0):,.2f}")

                # Generate PDF via existing invoice_pro module
                try:
                    import invoice_pro
                    if st.button("📥 Download PDF Invoice", key="sd_inv_dl", use_container_width=True):
                        try:
                            pdf_bytes = invoice_pro.generate_invoice(o)
                            st.download_button(
                                "⬇️ Save PDF",
                                data=pdf_bytes,
                                file_name=f"invoice_{o.get('order_id','')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )
                            staff_monitor.log_action(staff_id, staff_name, "INVOICE_DOWNLOADED",
                                                     details=o.get("order_id",""))
                        except Exception as e:
                            st.error(f"Could not generate PDF: {e}")
                except Exception:
                    st.info("PDF generation not available. Print screen instead.")

        if st.button("← Back", key="sd_inv_back"):
            st.session_state["staff_view"] = "home"
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TASK 6 — MESSAGE OWNER
    # ═══════════════════════════════════════════════════════════
    elif view == "message":
        st.markdown("### 💬 Message Owner")
        st.caption("Send a message to the owner. Owner is the decision maker.")

        with st.form("sd_msg_form"):
            subj = st.text_input("Subject", placeholder="e.g. Stock issue, Discount request")
            body = st.text_area("Message", height=140,
                                placeholder="Explain clearly what you need from owner.")
            prio = st.radio("Priority", ["normal", "urgent"], horizontal=True)
            if st.form_submit_button("📤 Send to Owner", use_container_width=True, type="primary"):
                if subj and body:
                    staff_messages.send_message(staff_id, staff_name, subj, body, prio)
                    staff_monitor.log_action(staff_id, staff_name, "MESSAGE_OWNER",
                                             details=f"{subj} · priority={prio}")
                    st.success("✅ Sent to owner")
                else:
                    st.error("Both subject and message required")

        # Show past sent messages + owner replies
        mine = staff_messages.get_sent_by_staff(staff_id)
        if mine:
            st.markdown("#### Previous messages")
            for m in reversed(mine[-5:]):
                with st.container(border=True):
                    st.markdown(f"**{m['subject']}** · {m['sent_at']}")
                    st.caption(m["body"][:200])
                    if m.get("replied"):
                        st.success(f"🧑‍💼 Owner reply ({m['replied_at']}): {m['reply']}")
                    else:
                        st.caption("⏳ Awaiting owner decision")

        if st.button("← Back", key="sd_msg_back"):
            st.session_state["staff_view"] = "home"
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # SIGN OUT
    # ═══════════════════════════════════════════════════════════
    st.markdown("---")
    if st.button("🚪 Sign Out", key="sd_signout"):
        staff_monitor.log_session(staff_id, staff_name, "END")
        for k in ["role","session","staff_id","staff_name","staff_view",
                  "cart_staff","_staff_session_logged","_staff_last_view"]:
            st.session_state.pop(k, None)
        st.rerun()
