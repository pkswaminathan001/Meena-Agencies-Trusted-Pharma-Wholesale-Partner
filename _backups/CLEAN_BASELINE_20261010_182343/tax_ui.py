"""Tax Center UI for accounting tab"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from tax_center import (get_gstr1_data, calculate_gstr3b, get_tax_calendar,
                        get_itc_summary, get_tds_summary, generate_gstr1_excel)


def render_tax_center(retailers, orders):
    st.markdown("### 🧾 Tax Center — GST / TDS / Income Tax")
    st.caption("Filing helpers for Indian pharma wholesale")

    tc1, tc2, tc3, tc4, tc5 = st.tabs([
        "📊 GST Summary", "📋 GSTR-1", "📅 Tax Calendar",
        "💰 ITC Tracker", "🏦 TDS"
    ])

    today = datetime.now()
    month_start = today.replace(day=1)

    # === TAB 1: GST SUMMARY ===
    with tc1:
        st.markdown("#### 📊 GSTR-3B Summary (This Month)")
        from_date = st.date_input("From", value=month_start.date(), key="gst3b_from")
        to_date = st.date_input("To", value=today.date(), key="gst3b_to")

        g3b = calculate_gstr3b(from_date, to_date)

        c1, c2 = st.columns(2)
        c1.metric("Output Tax (Sales GST)", f"₹{g3b['output_tax']:,.2f}")
        c2.metric("Input Tax Credit (Purchase GST)", f"₹{g3b['itc']:,.2f}")

        st.markdown("---")
        if g3b["net_payable"] > 0:
            st.error(f"### 🔴 Net GST Payable: ₹{g3b['net_payable']:,.2f}")
            st.caption("Pay by 20th of next month via GST portal challan")
        elif g3b["carry_forward"] > 0:
            st.info(f"### 🟢 ITC to Carry Forward: ₹{g3b['carry_forward']:,.2f}")
        else:
            st.success("### ✅ No net GST payable this period")

    # === TAB 2: GSTR-1 ===
    with tc2:
        st.markdown("#### 📋 GSTR-1 — Outward Supplies (B2B Sales)")
        c1, c2 = st.columns(2)
        with c1:
            g1_from = st.date_input("From", value=month_start.date(), key="g1_from")
        with c2:
            g1_to = st.date_input("To", value=today.date(), key="g1_to")

        invoices = get_gstr1_data(g1_from, g1_to, retailers)

        if invoices:
            idf = pd.DataFrame(invoices)
            st.dataframe(idf, use_container_width=True, hide_index=True)

            total_taxable = sum(i["taxable_value"] for i in invoices)
            total_gst = sum(i["cgst"] + i["sgst"] for i in invoices)
            c1, c2, c3 = st.columns(3)
            c1.metric("Invoices", len(invoices))
            c2.metric("Taxable Value", f"₹{total_taxable:,.2f}")
            c3.metric("Total GST", f"₹{total_gst:,.2f}")

            csv = idf.to_csv(index=False)
            st.download_button(
                "📥 Download GSTR-1 CSV (for portal upload)",
                data=csv,
                file_name=f"gstr1_{g1_from}_{g1_to}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No B2B invoices in this period.")

    # === TAB 3: TAX CALENDAR ===
    with tc3:
        st.markdown("#### 📅 Upcoming Tax Due Dates")
        events = get_tax_calendar()
        for e in events:
            days_left = (e["date"] - today).days
            if days_left < 0:
                color = "🔴"
                tag = "OVERDUE"
            elif days_left <= 7:
                color = "🟡"
                tag = f"{days_left} days"
            else:
                color = "🟢"
                tag = f"{days_left} days"

            st.markdown(f"""
            <div class="card">
                {color} <b>{e['date'].strftime('%d-%b-%Y').upper()}</b> — {e['event']} <span style="color:#8892b0;">({tag})</span>
            </div>
            """, unsafe_allow_html=True)

    # === TAB 4: ITC TRACKER ===
    with tc4:
        st.markdown("#### 💰 Input Tax Credit Tracker")
        c1, c2 = st.columns(2)
        with c1:
            itc_from = st.date_input("From", value=(today - timedelta(days=90)).date(), key="itc_from")
        with c2:
            itc_to = st.date_input("To", value=today.date(), key="itc_to")

        itc = get_itc_summary(itc_from, itc_to)
        st.metric("Total ITC Available", f"₹{itc['total']:,.2f}")

        if itc["entries"]:
            for e in itc["entries"]:
                st.markdown(f"`{e['date']}` **{e['ref']}** — {e['description'][:60]} — **₹{e['amount']:,.2f}**")
        else:
            st.info("No ITC recorded. Add purchase entries via Journal → Manual JV.")

    # === TAB 5: TDS ===
    with tc5:
        st.markdown("#### 🏦 TDS Tracker")
        st.caption("TDS applies to rent, professional fees, contracts. NOT to trade margins.")

        tds = get_tds_summary()
        st.metric("Total TDS Liability", f"₹{tds['total']:,.2f}")

        if tds["entries"]:
            for e in tds["entries"]:
                st.markdown(f"`{e['date']}` **{e['ref']}** — {e['description']} — **₹{e['amount']:,.2f}**")
        else:
            st.info("No TDS entries yet.")

        st.markdown("---")
        st.markdown("**Common TDS Rates:**")
        st.markdown("""
        | Section | Payment Type | Rate (Individual) | Rate (Company) |
        |---------|--------------|-------------------|----------------|
        | 194C | Contract work | 1% | 2% |
        | 194I | Rent (>₹2.4L/yr) | 10% | 10% |
        | 194J | Professional fees | 10% | 10% |
        | 194H | Commission | 5% | 5% |
        """)
