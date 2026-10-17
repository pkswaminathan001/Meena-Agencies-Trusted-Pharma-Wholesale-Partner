"""flash_offers_ui.py — UI for creating, approving, sending flash offers."""
import streamlit as st
import pandas as pd
from datetime import datetime
import flash_offers as fo


def render_owner_flash_offers(retailers, orders):
    """Full flash offer management for owner."""
    st.markdown("#### 🌅 Flash Offers — 7 AM to 9 AM")
    st.caption("Different discount per customer · Owner approval required · Auto-send at 7 AM")

    # ─── Window status banner ───
    status = fo.window_status_text()
    is_window = fo.is_flash_window()
    _bg = "rgba(0,212,122,0.15)" if is_window else "rgba(123,97,255,0.10)"
    _border = "#00d47a" if is_window else "#7b61ff"
    st.markdown(
        f'<div style="background:{_bg};border-left:5px solid {_border};'
        f'border-radius:12px;padding:14px 20px;margin-bottom:16px;">'
        f'<div style="font-size:1.1rem;font-weight:700;color:{_border};">{status}</div>'
        f'<div style="font-size:0.75rem;color:#8892b0;margin-top:4px;">'
        f'Current time: {datetime.now().strftime("%I:%M %p")} · '
        f'Window: 7:00 AM – 9:00 AM</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ─── Summary KPIs ───
    s = fo.summary()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div style="background:rgba(26,31,58,0.7);border:1px solid #8892b0;border-radius:10px;padding:10px;text-align:center;"><div style="color:#8892b0;font-size:0.65rem;">TOTAL</div><div style="color:#e8eaf6;font-size:1.4rem;font-weight:800;">{s["total"]}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="background:rgba(255,181,71,0.12);border:1px solid #ffb547;border-radius:10px;padding:10px;text-align:center;"><div style="color:#8892b0;font-size:0.65rem;">DRAFT</div><div style="color:#ffb547;font-size:1.4rem;font-weight:800;">{s["draft"]}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div style="background:rgba(0,212,255,0.12);border:1px solid #00d4ff;border-radius:10px;padding:10px;text-align:center;"><div style="color:#8892b0;font-size:0.65rem;">APPROVED</div><div style="color:#00d4ff;font-size:1.4rem;font-weight:800;">{s["approved"]}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div style="background:rgba(0,212,122,0.12);border:1px solid #00d47a;border-radius:10px;padding:10px;text-align:center;"><div style="color:#8892b0;font-size:0.65rem;">SENT</div><div style="color:#00d47a;font-size:1.4rem;font-weight:800;">{s["sent"]}</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div style="background:rgba(136,146,176,0.12);border:1px solid #8892b0;border-radius:10px;padding:10px;text-align:center;"><div style="color:#8892b0;font-size:0.65rem;">EXPIRED</div><div style="color:#8892b0;font-size:1.4rem;font-weight:800;">{s["expired"]}</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # ─── Sub-tabs ───
    ft1, ft2, ft3, ft4 = st.tabs([
        "🆕 Create", "📋 Manage", "📤 Send Now", "⚙️ Auto-Schedule"
    ])

    # ═══ FT1: CREATE ═══
    with ft1:
        st.markdown("##### 🆕 Create Flash Offer")
        st.caption("Each customer gets their OWN discount %. Different per customer.")

        with st.form("create_flash"):
            # Customer picker
            _ret_options = [f"{r['id']} — {r['shop']}" for r in retailers]
            _picked = st.selectbox("Choose ONE customer", _ret_options, key="flash_ret")

            # Template picker
            _tmpl_keys = list(fo.AD_TEMPLATES.keys())
            _tmpl_labels = [fo.AD_TEMPLATES[k]["name"] for k in _tmpl_keys]
            _tmpl_pick = st.selectbox("Marketing ad template", _tmpl_labels)

            # Get template text
            _tmpl_key = _tmpl_keys[_tmpl_labels.index(_tmpl_pick)]
            _default_ad = fo.AD_TEMPLATES[_tmpl_key]["text"]

            # Editable ad text
            _ad_text = st.text_area("Ad text (editable)", value=_default_ad, height=80)

            # Discount %
            c1, c2 = st.columns(2)
            with c1:
                _pct = st.number_input("Discount % for THIS customer", min_value=0.0,
                                       max_value=30.0, value=10.0, step=0.5)
            with c2:
                _days = st.number_input("Valid days", min_value=1, max_value=30, value=1)

            _notes = st.text_input("Internal note (optional)")

            if st.form_submit_button("✨ Create Offer (as DRAFT)", use_container_width=True, type="primary"):
                _rid = _picked.split(" — ")[0]
                _rshop = _picked.split(" — ")[1]
                offer = fo.create_flash_offer(
                    retailer_id=_rid,
                    shop_name=_rshop,
                    discount_pct=float(_pct),
                    ad_text=_ad_text.strip(),
                    valid_days=int(_days),
                    notes=_notes,
                )
                st.success(f"✅ Created {offer['id']} — status: DRAFT")
                st.info("➡️ Now go to **📋 Manage** tab → approve it")
                st.rerun()

        st.markdown("---")
        st.markdown("**Bulk create for ALL retailers:**")
        st.caption("Set one discount for all OR each gets same % — approve individually later.")

        with st.form("bulk_flash"):
            _bulk_pct = st.number_input("Bulk discount %", min_value=0.0, max_value=30.0, value=8.0, step=0.5)
            _bulk_tmpl_label = st.selectbox("Bulk template", _tmpl_labels, key="bulk_tmpl")
            if st.form_submit_button("📢 Create DRAFT for all customers", use_container_width=True):
                _bulk_key = _tmpl_keys[_tmpl_labels.index(_bulk_tmpl_label)]
                _bulk_ad = fo.AD_TEMPLATES[_bulk_key]["text"]
                count = 0
                for r in retailers:
                    if r.get("status") == "Blocked":
                        continue
                    fo.create_flash_offer(
                        retailer_id=r["id"],
                        shop_name=r["shop"],
                        discount_pct=float(_bulk_pct),
                        ad_text=_bulk_ad,
                    )
                    count += 1
                st.success(f"✅ Created {count} DRAFT offers — approve each in 📋 Manage")
                st.rerun()

    # ═══ FT2: MANAGE ═══
    with ft2:
        st.markdown("##### 📋 Manage Offers")
        all_offers = fo.list_offers()
        if not all_offers:
            st.info("No offers yet. Create one in 🆕 Create tab.")
        else:
            # Group by status
            statuses = ["DRAFT", "APPROVED", "SENT", "EXPIRED", "REJECTED"]
            for _status in statuses:
                _group = [o for o in all_offers if o["status"] == _status]
                if not _group:
                    continue

                _icon = {"DRAFT": "✏️", "APPROVED": "✅", "SENT": "📤",
                         "EXPIRED": "⏰", "REJECTED": "❌"}.get(_status, "•")
                _color = {"DRAFT": "#ffb547", "APPROVED": "#00d4ff", "SENT": "#00d47a",
                          "EXPIRED": "#8892b0", "REJECTED": "#ff4d6d"}.get(_status, "#8892b0")

                st.markdown(
                    f'<div style="font-size:0.9rem;color:{_color};font-weight:700;'
                    f'margin-top:14px;letter-spacing:1px;">'
                    f'{_icon} {_status} ({len(_group)})</div>',
                    unsafe_allow_html=True,
                )

                for o in _group:
                    _html = (
                        f'<div style="background:rgba(26,31,58,0.7);border-left:4px solid {_color};'
                        f'border-radius:10px;padding:10px 14px;margin:6px 0;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                        f'<div>'
                        f'<div style="color:#e8eaf6;font-weight:600;">{o["shop_name"]} — {o["retailer_id"]}</div>'
                        f'<div style="font-size:0.7rem;color:#8892b0;">{o["id"]}</div>'
                        f'</div>'
                        f'<div style="text-align:right;">'
                        f'<div style="color:{_color};font-size:1.3rem;font-weight:800;">{o["discount_pct"]:.1f}%</div>'
                        f'<div style="font-size:0.65rem;color:#8892b0;">{o["valid_date"]}</div>'
                        f'</div></div></div>'
                    )
                    st.markdown(_html, unsafe_allow_html=True)

                    # Action buttons
                    if _status == "DRAFT":
                        c1, c2, c3 = st.columns([1, 1, 2])
                        with c1:
                            if st.button(f"✅ Approve", key=f"app_{o['id']}",
                                         use_container_width=True, type="primary"):
                                fo.approve_offer(o["id"])
                                st.rerun()
                        with c2:
                            if st.button(f"❌ Reject", key=f"rej_{o['id']}",
                                         use_container_width=True):
                                fo.reject_offer(o["id"], "Owner rejected")
                                st.rerun()
                    elif _status == "APPROVED":
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            if st.button(f"📤 Send Now", key=f"snd_{o['id']}",
                                         use_container_width=True, type="primary"):
                                res = fo.send_flash_offer(o["id"])
                                if res.get("ok"):
                                    st.success(res["msg"])
                                else:
                                    st.error(res["msg"])
                                st.rerun()

    # ═══ FT3: SEND NOW ═══
    with ft3:
        st.markdown("##### 📤 Send Approved Offers Now")
        st.caption("Manually trigger send — bypasses auto-schedule")

        approved = fo.list_offers("APPROVED")
        if not approved:
            st.info("No approved offers waiting. Approve some in 📋 Manage first.")
        else:
            st.markdown(f"**{len(approved)} approved offer(s) ready**")
            for o in approved:
                st.markdown(
                    f'<div style="background:rgba(0,212,255,0.10);border-left:4px solid #00d4ff;'
                    f'border-radius:10px;padding:10px 14px;margin:6px 0;">'
                    f'<b style="color:#00d4ff;">{o["shop_name"]}</b> '
                    f'<span style="color:#8892b0;">— {o["discount_pct"]:.1f}% off</span></div>',
                    unsafe_allow_html=True,
                )

            if st.button("🚀 Send ALL Approved Now", use_container_width=True, type="primary"):
                sent = 0
                failed = 0
                for o in approved:
                    res = fo.send_flash_offer(o["id"])
                    if res.get("ok"):
                        sent += 1
                    else:
                        failed += 1
                st.success(f"✅ Sent: {sent} · Failed: {failed}")
                st.rerun()

    # ═══ FT4: AUTO-SCHEDULE ═══
    with ft4:
        st.markdown("##### ⚙️ Auto-Schedule")
        st.caption("Send all approved offers automatically at 7:00 AM daily")

        st.markdown(
            '<div style="background:linear-gradient(135deg,rgba(0,212,122,0.12),rgba(0,212,122,0.04));'
            'border-left:5px solid #00d47a;border-radius:12px;padding:14px 20px;">'
            '<div style="color:#00d47a;font-weight:700;font-size:1.05rem;">🌅 7:00 AM Auto-Send</div>'
            '<div style="color:#e8eaf6;font-size:0.85rem;margin-top:6px;">'
            'Every morning at 7 AM, the scheduler will:</div>'
            '<div style="color:#8892b0;font-size:0.8rem;margin-top:6px;">'
            '1. Mark yesterday\'s offers as EXPIRED<br>'
            '2. Send all APPROVED offers for today<br>'
            '3. Log send status for your records</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("")
        st.markdown("**Run scheduler now (for testing):**")
        if st.button("▶️ Run Scheduler Once", use_container_width=True):
            result = fo.run_scheduler_once()
            st.json(result)

        st.markdown("---")
        st.markdown("**Setup Instructions (one-time):**")
        st.code(
            '# Run this in terminal to install the 7 AM timer:\n'
            'python3 flash_offers_scheduler.py install',
            language="bash",
        )


# ═══════════════════════════════════════════════════════════
# CUSTOMER VIEW — shows flash offer if within window
# ═══════════════════════════════════════════════════════════
def render_customer_flash_offer(retailer):
    """Customer sees their active flash offer if within 7-9 AM window."""
    if not fo.is_flash_window():
        return

    # Find today's sent offer for this customer
    today = datetime.now().strftime("%Y-%m-%d")
    all_offers = fo.list_offers()
    my_offer = next(
        (o for o in all_offers
         if o["retailer_id"] == retailer["id"]
         and o["valid_date"] == today
         and o["status"] == "SENT"),
        None,
    )

    if not my_offer:
        return

    # Show banner
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(255,181,71,0.20),rgba(255,77,109,0.15));'
        f'border:2px solid #ffb547;border-radius:16px;padding:20px;margin:12px 0;'
        f'box-shadow:0 0 30px rgba(255,181,71,0.3);">'
        f'<div style="text-align:center;">'
        f'<div style="font-size:1.3rem;color:#ffb547;font-weight:800;letter-spacing:1px;">'
        f'🌅 FLASH SALE — TODAY ONLY</div>'
        f'<div style="font-size:2.8rem;font-weight:900;color:#ffb547;margin-top:8px;'
        f'text-shadow:0 0 20px #ffb547;">{my_offer["discount_pct"]:.1f}%</div>'
        f'<div style="color:#e8eaf6;font-size:0.9rem;margin-top:4px;">off on your next order</div>'
        f'<div style="color:#8892b0;font-size:0.75rem;margin-top:8px;">'
        f'⏰ Valid 7:00 AM – 9:00 AM only · 🔒 Exclusive to you</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
