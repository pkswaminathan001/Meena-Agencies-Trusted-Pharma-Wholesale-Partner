"""
peacock_calendar.py — Date range picker with peacock styling.
Customer picks a range → sees bills for that range → downloads PDF.
"""
import streamlit as st
from datetime import datetime, timedelta, date


def _parse_order_date(order):
    """Try to parse an order's placed_at into a date."""
    raw = order.get("placed_at", "")
    for fmt in ("%d-%b-%Y %H:%M", "%d-%b-%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except Exception:
            continue
    return None


def _inject_calendar_css():
    if st.session_state.get("_peacock_cal_done"):
        return
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════
       PEACOCK-THEMED CALENDAR — cyan → purple gradient
       ═══════════════════════════════════════════════════════ */

    /* Streamlit's date input container */
    [data-testid="stDateInput"] label,
    [data-testid="stDateInput"] > div > div {
        color: #e8eaf6 !important;
        font-weight: 600 !important;
    }
    [data-testid="stDateInput"] input {
        background: linear-gradient(135deg, rgba(0,212,170,0.08), rgba(123,97,255,0.08)) !important;
        border: 2px solid transparent !important;
        border-radius: 12px !important;
        color: #e8eaf6 !important;
        font-weight: 700 !important;
        padding: 10px 14px !important;
        transition: border-color .2s ease, box-shadow .2s ease !important;
        background-clip: padding-box !important;
    }
    [data-testid="stDateInput"] input:focus {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 4px rgba(0,212,170,0.22) !important;
    }

    /* Calendar popover (baseweb) */
    [data-baseweb="popover"] [data-baseweb="calendar"] {
        background: linear-gradient(160deg, #0d1130, #0a0e27) !important;
        border: 1px solid rgba(0,212,170,0.35) !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 60px rgba(0,212,170,0.25) !important;
    }

    /* Month/year header */
    [data-baseweb="calendar"] > div:first-child {
        background: linear-gradient(90deg, rgba(0,212,170,0.18), rgba(123,97,255,0.18)) !important;
        border-radius: 14px 14px 0 0 !important;
        color: #e8eaf6 !important;
        font-weight: 800 !important;
    }

    /* Weekday row */
    [data-baseweb="calendar"] [aria-hidden="true"] {
        color: #8892b0 !important;
        font-size: 0.7rem !important;
        letter-spacing: 1px !important;
    }

    /* Day cells */
    [data-baseweb="calendar"] button {
        color: #cbd5f0 !important;
        border-radius: 8px !important;
        transition: all .15s ease !important;
    }
    [data-baseweb="calendar"] button:hover {
        background: rgba(0,212,170,0.18) !important;
        color: #00d4aa !important;
        transform: scale(1.08) !important;
    }
    /* Selected / in-range day */
    [data-baseweb="calendar"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #00d4aa, #7b61ff) !important;
        color: #fff !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 16px rgba(0,212,170,0.45) !important;
    }
    /* Today */
    [data-baseweb="calendar"] button[aria-current="date"] {
        border: 2px solid #00d4aa !important;
        color: #00d4aa !important;
    }

    /* Range container card */
    .pk-range-card {
        background: linear-gradient(160deg, rgba(16,22,54,0.85), rgba(10,14,39,0.85));
        border: 1px solid rgba(0,212,170,0.28);
        border-radius: 18px;
        padding: 22px 24px;
        margin: 12px 0 20px 0;
        position: relative;
        overflow: hidden;
    }
    .pk-range-card::before {
        content: "";
        position: absolute; top: -40%; right: -20%;
        width: 240px; height: 240px;
        background: radial-gradient(circle, rgba(123,97,255,0.35), transparent 70%);
        pointer-events: none;
    }
    .pk-range-title {
        font-size: 1.35rem;
        color: #1e2430;
        letter-spacing: -0.01em;
        text-transform: none;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .pk-range-heading {
        font-size: 1.15rem;
        color: #e8eaf6;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .pk-range-sub {
        font-size: 0.82rem;
        color: #a8b2d1;
    }
    .pk-range-summary {
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
    }
    .pk-stat {
        display: flex; flex-direction: column;
    }
    .pk-stat-label {
        font-size: 0.65rem; color: #6b7490;
        letter-spacing: 1.4px; text-transform: uppercase;
        font-weight: 700;
    }
    .pk-stat-value {
        font-size: 1.35rem; font-weight: 900;
        color: #00d4aa; line-height: 1.15;
    }
    
    /* Section labels */
    .pk-section-label {
        font-size: 0.68rem;
        color: #8892b0;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 800;
        margin: 18px 0 8px 2px;
    }
    /* Quick-pick buttons — smaller, cleaner */
    [data-testid="stButton"] > button[kind="secondary"][key^="qp_"] {
        font-size: 0.75rem !important;
        padding: 6px 12px !important;
        background: rgba(0,212,170,0.06) !important;
        border: 1px solid rgba(0,212,170,0.22) !important;
        color: #8892b0 !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        min-height: 32px !important;
    }
    [data-testid="stButton"] > button[kind="secondary"][key^="qp_"]:hover {
        background: rgba(0,212,170,0.15) !important;
        color: #00d4aa !important;
        border-color: rgba(0,212,170,0.55) !important;
    }

    @media (max-width: 768px) {
        .pk-range-card { padding: 16px 14px !important; }
        .pk-range-heading { font-size: 1rem !important; }
        .pk-stat-value { font-size: 1.15rem !important; }
        .pk-stat { min-width: 45% !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        [data-testid="column"] { min-width: 100% !important; }
    }
    /* Larger tap on cards (whole card is a button) */
    [data-testid="stButton"] > button {
        min-height: 48px !important;
    }
</style>
    """, unsafe_allow_html=True)
    st.session_state["_peacock_cal_done"] = True


def render_bill_range_picker(all_orders, retailer=None, company=None):
    """Show a peacock-styled date range picker + filtered bills + download."""

    # ── Tight top padding for Bill History only ──
    st.markdown(
        "<style>"
        # Kill block container top padding
        ".block-container { padding-top: 0.05rem !important; margin-top: 0 !important; }"
        "[data-testid=\"stMainBlockContainer\"] { padding-top: 0.05rem !important; margin-top: 0 !important; }"
        "[data-testid=\"stAppViewContainer\"] > .main { padding-top: 0 !important; }"
        "[data-testid=\"stAppViewContainer\"] > .main > div:first-child { padding-top: 0 !important; }"
        # Tight vertical gap
        "[data-testid=\"stVerticalBlock\"] { gap: 0.3rem !important; }"
        # Collapse ONLY the mobile sidebar toggle wrapper (matches by title)
        "[data-testid=\"stElementContainer\"]:has(button[title=\"Toggle menu\"]) { "
        "  height: 0 !important; min-height: 0 !important; max-height: 0 !important; "
        "  margin: 0 !important; padding: 0 !important; position: absolute !important; "
        "  top: 0 !important; left: 0 !important; width: auto !important; "
        "  z-index: 999999 !important; "
        "}"
        # Collapse the fixed cart popover wrapper
        "[data-testid=\"stElementContainer\"]:has([data-testid=\"stPopover\"]) { "
        "  height: 0 !important; min-height: 0 !important; max-height: 0 !important; "
        "  margin: 0 !important; padding: 0 !important; "
        "}"
        # Section label — no top margin
        ".pk-section-label { margin-top: 0 !important; padding-top: 0 !important; }"
        # Also collapse any markdown container that only contains <style>
        "[data-testid=\"stElementContainer\"]:has(style) { "
        "  height: 0 !important; min-height: 0 !important; max-height: 0 !important; "
        "  margin: 0 !important; padding: 0 !important; "
        "}"
        "</style>",
        unsafe_allow_html=True,
    )

    _inject_calendar_css()

    # ── Header (professional, no duplicate title) ──
    st.markdown("""
    <div class="pk-range-card">
        <div class="pk-range-title">Statement Period</div>
        <div class="pk-range-heading">Select the dates for your statement</div>
        <div class="pk-range-sub">Use the calendar or quick picks below. Downloads include every order in the selected range.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Default range: last 30 days ──
    today = date.today()
    default_from = today - timedelta(days=30)
    if "bill_date_from" not in st.session_state:
        st.session_state.bill_date_from = default_from
    if "bill_date_to" not in st.session_state:
        st.session_state.bill_date_to = today

    # ── Quick picks ──
    st.markdown('<div class="pk-section-label">Quick Ranges</div>', unsafe_allow_html=True)
    qp1, qp2, qp3, qp4 = st.columns(4)
    with qp1:
        if st.button("Today", use_container_width=True, key="qp_today"):
            st.session_state.bill_date_from = today
            st.session_state.bill_date_to = today
            st.rerun()
    with qp2:
        if st.button("This Week", use_container_width=True, key="qp_week"):
            start = today - timedelta(days=today.weekday())
            st.session_state.bill_date_from = start
            st.session_state.bill_date_to = today
            st.rerun()
    with qp3:
        if st.button("This Month", use_container_width=True, key="qp_month"):
            st.session_state.bill_date_from = today.replace(day=1)
            st.session_state.bill_date_to = today
            st.rerun()
    with qp4:
        if st.button("Last 30 days", use_container_width=True, key="qp_30"):
            st.session_state.bill_date_from = today - timedelta(days=30)
            st.session_state.bill_date_to = today
            st.rerun()

    # ── Calendar range inputs ──
    st.markdown('<div class="pk-section-label">Custom Range</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        dfrom = st.date_input(
            "From",
            value=st.session_state.bill_date_from,
            key="pk_date_from",
            format="DD/MM/YYYY",
        )
    with c2:
        dto = st.date_input(
            "To",
            value=st.session_state.bill_date_to,
            key="pk_date_to",
            format="DD/MM/YYYY",
        )
    st.session_state.bill_date_from = dfrom
    st.session_state.bill_date_to = dto

    if dfrom > dto:
        st.error("⚠️ 'From' date must be before 'To' date.")
        return

    # ── Filter orders in range ──
    filtered = []
    for o in all_orders:
        od = _parse_order_date(o)
        if od and dfrom <= od <= dto:
            filtered.append(o)

    # ── Summary ──
    total_value = sum(float(o.get("total", 0)) for o in filtered)
    st.markdown(f"""
    <div class="pk-range-summary">
        <div class="pk-stat">
            <div class="pk-stat-label">Bills in Range</div>
            <div class="pk-stat-value">{len(filtered)}</div>
        </div>
        <div class="pk-stat">
            <div class="pk-stat-label">Total Value</div>
            <div class="pk-stat-value">₹{total_value:,.2f}</div>
        </div>
        <div class="pk-stat">
            <div class="pk-stat-label">Period</div>
            <div class="pk-stat-value" style="font-size:0.95rem;">
                {dfrom.strftime('%d %b')} → {dto.strftime('%d %b %Y')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # ── Download buttons ──
    if filtered and retailer:
        dl1, dl2 = st.columns(2)
        with dl1:
            try:
                import statement_pdf
                pdf = statement_pdf.generate_statement_pdf(
                    retailer, filtered,
                    company or {"name": "Meena Agencies"},
                )
                st.download_button(
                    "📥 Download Statement (PDF)",
                    data=pdf,
                    file_name=f"statement_{dfrom.strftime('%Y%m%d')}_{dto.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="pk_pdf_dl",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as e:
                st.warning(f"PDF generation unavailable: {e}")
        with dl2:
            import csv, io
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["Order ID", "Date", "Total", "Status", "Items"])
            for o in filtered:
                items_str = "; ".join(
                    f"{it.get('medicine','')} x{it.get('qty',0)}" for it in o.get("items", [])
                )
                writer.writerow([
                    o.get("order_id", ""),
                    o.get("placed_at", ""),
                    o.get("total", 0),
                    o.get("status", ""),
                    items_str,
                ])
            st.download_button(
                "📄 Download CSV",
                data=buf.getvalue(),
                file_name=f"bills_{dfrom.strftime('%Y%m%d')}_{dto.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="pk_csv_dl",
                use_container_width=True,
            )
    elif not filtered:
        st.info(f"No bills found between {dfrom.strftime('%d %b %Y')} and {dto.strftime('%d %b %Y')}.")

    # ── List bills ──
    if filtered:
        st.markdown('<div class="pk-section-label">Orders in Selected Period</div>', unsafe_allow_html=True)
        try:
            import customer_bill
            customer_bill.render_order_list(filtered)
        except Exception as e:
            import traceback
            st.warning(f"⚠️ Could not render rich order list: {e}")
            with st.expander("Show traceback"):
                st.code(traceback.format_exc())
            for o in filtered:
                st.markdown(
                    f"- `{o.get('order_id','')}` · "
                    f"₹{o.get('total',0):,.2f} · {o.get('status','')}"
                )
