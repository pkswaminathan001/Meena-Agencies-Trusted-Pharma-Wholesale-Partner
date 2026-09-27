"""
accounting_book.py — Traditional Indian ledger book UI.
Paper texture, ruled lines, Personal/Real/Nominal color coding.
"""
import sys
from pathlib import Path as _Path
_THIS_DIR = _Path(__file__).parent.resolve()
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import streamlit as st
import pandas as pd
from datetime import datetime
from accounting.db import init_db
from accounting.chart import create_book, list_accounts
from accounting.bookkeeper import sync_all
from accounting.reports import day_book, ledger, profit_and_loss, balance_sheet
from accounting.journal import trial_balance
from accounting_classify import get_traditional_type, GOLDEN_RULES, list_accounts_by_traditional_type
from bad_debts import debt_report, summary as debt_summary


BOOK = "MEENA"


def _fmt(v):
    try:
        return f"{float(v):,.2f}"
    except Exception:
        return "0.00"


# ═══════════════════════════════════════════════════════════
# PAPER TEXTURE CSS — makes it look like a real book
# ═══════════════════════════════════════════════════════════
def inject_book_css():
    st.markdown("""
    <style>
    /* Paper texture background for the book */
    .book-page {
        background: linear-gradient(180deg, #fefaf0 0%, #f9f3e5 100%);
        border: 1px solid #d4c5a0;
        border-radius: 4px;
        padding: 24px 32px;
        box-shadow:
            0 2px 4px rgba(0,0,0,0.1),
            inset 0 0 80px rgba(212,197,160,0.15);
        position: relative;
        font-family: 'Georgia', 'Times New Roman', serif;
        color: #2c1810;
    }
    .book-page::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(90deg, #8b0000, #c41e3a);
        border-radius: 4px 0 0 4px;
    }
    /* Ruled lines like a ledger */
    .book-ledger-line {
        border-bottom: 1px solid #d4c5a0;
        padding: 6px 0;
        font-size: 0.9rem;
    }
    /* Traditional type colors */
    .personal-account { color: #0066cc; font-weight: 600; }
    .real-account { color: #008844; font-weight: 600; }
    .nominal-account { color: #cc6600; font-weight: 600; }
    /* Journal entry row */
    .journal-row {
        display: flex;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px dotted #d4c5a0;
        font-family: 'Courier New', monospace;
    }
    /* Golden rule card */
    .golden-card {
        background: linear-gradient(135deg, #fff8e7 0%, #ffeaa7 100%);
        border-left: 5px solid #d4a017;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.85rem;
    }
    .golden-card h4 {
        margin: 0 0 6px 0;
        color: #8b6914;
        font-size: 1rem;
    }
    .golden-rule {
        font-weight: 700;
        color: #8b0000;
        font-size: 1rem;
        margin: 4px 0;
        font-style: italic;
    }
    /* Book header */
    .book-title {
        font-family: 'Georgia', serif;
        font-size: 1.8rem;
        color: #8b0000;
        text-align: center;
        border-bottom: 3px double #8b0000;
        padding-bottom: 8px;
        margin-bottom: 4px;
        letter-spacing: 2px;
    }
    .book-subtitle {
        text-align: center;
        color: #8b6914;
        font-style: italic;
        font-size: 0.85rem;
        margin-bottom: 16px;
    }
    /* Account type badges */
    .ttype-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-personal { background: #d0e8ff; color: #004a99; }
    .badge-real     { background: #d4f5dd; color: #006633; }
    .badge-nominal  { background: #ffe4cc; color: #994400; }
    /* Bad debt pill */
    .debt-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


def _ttype_badge(code):
    ttype, _ = get_traditional_type(code)
    cls = {"Personal": "badge-personal", "Real": "badge-real", "Nominal": "badge-nominal"}.get(ttype, "badge-real")
    return f'<span class="ttype-badge {cls}">{ttype}</span>'


# ═══════════════════════════════════════════════════════════
# MAIN RENDER
# ═══════════════════════════════════════════════════════════
def render(retailers, orders):
    init_db()
    create_book(BOOK, "Meena Agencies")
    inject_book_css()

    # Header
    st.markdown("""
    <div class="book-title">📖  MEENA AGENCIES — LEDGER BOOK</div>
    <div class="book-subtitle">Traditional Double-Entry Accounting · Personal · Real · Nominal</div>
    """, unsafe_allow_html=True)

    # 7 sub-tabs
    tabs = st.tabs([
        "📊 Financial Snapshot",
        "📖 Read the Book",
        "👤 Personal",
        "🏛️ Real",
        "📊 Nominal",
        "⚠️ Bad Debts",
        "❓ Help & AI Assistant"
    ])

    # ═══════════════════════════════════════════════════════
    # TAB 1 — FINANCIAL SNAPSHOT
    # ═══════════════════════════════════════════════════════
    with tabs[0]:
        bs = balance_sheet(BOOK)
        pl = profit_and_loss(BOOK)
        tb = trial_balance(BOOK)

        # Big metric cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="book-page" style="padding:16px;text-align:center;">
                <div style="font-size:0.75rem;color:#8b6914;letter-spacing:1px;">TOTAL ASSETS</div>
                <div style="font-size:1.6rem;font-weight:800;color:#008844;">₹{_fmt(bs['total_assets'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="book-page" style="padding:16px;text-align:center;">
                <div style="font-size:0.75rem;color:#8b6914;letter-spacing:1px;">LIABILITIES</div>
                <div style="font-size:1.6rem;font-weight:800;color:#8b0000;">₹{_fmt(bs['total_liabilities'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="book-page" style="padding:16px;text-align:center;">
                <div style="font-size:0.75rem;color:#8b6914;letter-spacing:1px;">EQUITY</div>
                <div style="font-size:1.6rem;font-weight:800;color:#004a99;">₹{_fmt(bs['total_equity'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            color = "#008844" if pl["net_profit"] >= 0 else "#8b0000"
            st.markdown(f"""
            <div class="book-page" style="padding:16px;text-align:center;">
                <div style="font-size:0.75rem;color:#8b6914;letter-spacing:1px;">NET PROFIT</div>
                <div style="font-size:1.6rem;font-weight:800;color:{color};">₹{_fmt(pl['net_profit'])}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📈 Income vs Expense")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Total Income** : ₹{_fmt(pl['total_income'])}")
            for i in pl["income"][:5]:
                st.markdown(f"- {i['name']}: ₹{_fmt(i['amount'])}")
        with c2:
            st.markdown(f"**Total Expense** : ₹{_fmt(pl['total_expense'])}")
            for e in pl["expense"][:5]:
                st.markdown(f"- {e['name']}: ₹{_fmt(e['amount'])}")

    # ═══════════════════════════════════════════════════════
    # TAB 2 — READ THE BOOK (Day Book / Journal)
    # ═══════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown("#### 📖 Read the Book — Daily Journal Entries")
        st.caption("Every transaction entered in traditional T-format")

        date_str = st.date_input("Pick a date", datetime.now()).strftime("%Y-%m-%d")
        entries = day_book(BOOK, date_str)

        if not entries:
            st.info("No entries on this date. Try another date or run Sync first.")
        else:
            for e in entries:
                st.markdown(f"""
                <div class="book-page">
                    <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#8b6914;">
                        <span><b>Entry #{e['entry']['entry_id']}</b> · {e['entry']['entry_date']}</span>
                        <span>Source: {e['entry']['source']} · {e['entry']['source_ref'] or '—'}</span>
                    </div>
                    <div style="margin-top:6px;font-style:italic;color:#2c1810;font-size:0.9rem;">
                        {e['entry']['narration']}
                    </div>
                    <table style="width:100%;margin-top:10px;border-collapse:collapse;font-family:'Courier New',monospace;">
                        <tr style="border-bottom:2px solid #8b6914;">
                            <th style="text-align:left;padding:4px 8px;color:#8b0000;">Account</th>
                            <th style="text-align:right;padding:4px 8px;color:#8b0000;">Debit (₹)</th>
                            <th style="text-align:right;padding:4px 8px;color:#8b0000;">Credit (₹)</th>
                        </tr>
                        {''.join(f'''
                        <tr style="border-bottom:1px dotted #d4c5a0;">
                            <td style="padding:4px 8px;">
                                {line['account_name']} {_ttype_badge(line['account_code'])}
                            </td>
                            <td style="text-align:right;padding:4px 8px;color:#004a99;">
                                {_fmt(line['debit']) if line['debit'] else '—'}
                            </td>
                            <td style="text-align:right;padding:4px 8px;color:#008844;">
                                {_fmt(line['credit']) if line['credit'] else '—'}
                            </td>
                        </tr>
                        ''' for line in e['lines'])}
                    </table>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # TAB 3/4/5 — Personal / Real / Nominal grouping
    # ═══════════════════════════════════════════════════════
    grouped = list_accounts_by_traditional_type(BOOK)

    def _render_group(ttype_key, tab_index):
        with tabs[tab_index]:
            rule = GOLDEN_RULES[ttype_key]
            st.markdown(f"""
            <div class="golden-card">
                <h4>{rule['icon']} {ttype_key.upper()} ACCOUNTS</h4>
                <div class="golden-rule">"{rule['rule']}"</div>
                <div style="color:#5c4a1e;"><b>Example:</b> {rule['example']}</div>
            </div>
            """, unsafe_allow_html=True)

            accounts = grouped.get(ttype_key, [])
            if not accounts:
                st.info(f"No {ttype_key.lower()} accounts.")
                return

            for a in accounts:
                # Get balance
                from accounting.journal import account_balance
                bal = account_balance(BOOK, a["code"])
                if bal["balance"] == 0 and bal["debit"] == 0 and bal["credit"] == 0:
                    continue

                st.markdown(f"""
                <div class="book-ledger-line">
                    <b>{a['code']} — {a['name']}</b>
                    <span style="float:right;">
                        Dr ₹{_fmt(bal['debit'])} · Cr ₹{_fmt(bal['credit'])} · 
                        <b>Bal ₹{_fmt(bal['balance'])}</b>
                    </span>
                </div>
                """, unsafe_allow_html=True)

    _render_group("Personal", 2)
    _render_group("Real", 3)
    _render_group("Nominal", 4)

    # ═══════════════════════════════════════════════════════
    # TAB 6 — BAD DEBTS
    # ═══════════════════════════════════════════════════════
    with tabs[5]:
        st.markdown("#### ⚠️ Bad Debt & Recovery Analysis")
        report = debt_report(retailers, orders)
        s = debt_summary(report)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Outstanding", f"₹{_fmt(s['total_outstanding'])}")
        c2.metric("Likely Bad Debt", f"₹{_fmt(s['likely_bad'])}")
        c3.metric("At Risk", f"₹{_fmt(s['at_risk'])}")
        c4.metric("Expected Recovery", f"{s['recovery_pct']}%")

        st.markdown("---")
        if report:
            df = pd.DataFrame([{
                "Category": r["category"],
                "Retailer": r["shop"],
                "Owner": r["owner"],
                "Phone": r["phone"],
                "Outstanding": f"₹{_fmt(r['outstanding'])}",
                "Last Order": r["last_order"],
                "Status": r["status"],
            } for r in report])
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        else:
            st.success("✅ No outstanding debts!")

        st.markdown("---")
        st.markdown("##### 💡 Legal write-off guidance")
        st.markdown("""
        - **Under 90 days**: 🟢 Normal — send payment reminders
        - **90-180 days**: 🟡 Send formal demand notice
        - **180-365 days**: 🟠 Legal notice under NI Act Section 138
        - **Over 365 days**: 🔴 Write off as bad debt → **deductible under Section 36(1)(vii) of Income Tax Act**
        """)

    # ═══════════════════════════════════════════════════════
    # TAB 7 — HELP & AI
    # ═══════════════════════════════════════════════════════
    with tabs[6]:
        st.markdown("#### ❓ Help & AI Accounting Assistant")
        st.caption("Ask any accounting question — get instant answers")

        # Quick guidance cards
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.expander("📘 How do I record a sale?"):
                st.markdown("""
                **Sale on credit to retailer:**
                - Debit: Retailer's Account (Personal) — they received goods
                - Credit: Sales Account (Nominal) — you earned income

                **Rule:** Debit the receiver, Credit the giver.
                """)
        with c2:
            with st.expander("💰 How do I record payment?"):
                st.markdown("""
                **Cash payment from retailer:**
                - Debit: Cash (Real) — cash came IN
                - Credit: Retailer's Account (Personal) — they paid

                **Rule:** Debit what comes in, Credit what goes out.
                """)
        with c3:
            with st.expander("📝 How do I record expenses?"):
                st.markdown("""
                **Pay rent ₹5,000 cash:**
                - Debit: Rent Expense (Nominal) — expense increases
                - Credit: Cash (Real) — cash goes OUT

                **Rule:** Debit all expenses, Credit all incomes.
                """)

        st.markdown("---")

        # AI Chat
        st.markdown("##### 🤖 Ask the AI Accountant")
        st.caption("Examples: 'Where do I record vehicle repair?' · 'How to write off bad debt?'")

        if "acc_chat" not in st.session_state:
            st.session_state.acc_chat = []

        # Display chat history
        for msg in st.session_state.acc_chat[-6:]:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**AI Accountant:** {msg['content']}")

        question = st.text_input("Your question:", key="acc_question",
                                  placeholder="e.g. Where do I record vehicle insurance?")
        if st.button("Ask AI Accountant", use_container_width=True, type="primary"):
            if question.strip():
                st.session_state.acc_chat.append({"role": "user", "content": question})

                # Try to use Groq if available
                try:
                    from groq import Groq
                    import os
                    from dotenv import load_dotenv
                    load_dotenv()
                    key = os.getenv("GROQ_API_KEY")
                    if key:
                        client = Groq(api_key=key)
                        prompt = f"""You are an Indian chartered accountant helping a pharma wholesale business owner.

Chart of accounts codes they use:
- 1000 Cash, 1010 Bank, 1100 Accounts Receivable, 1200 Inventory
- 2000 Accounts Payable, 2100-2120 GST Payable
- 3000 Owner Capital, 3100 Drawings
- 4000 Sales, 5000 COGS, 5010 Salaries, 5020 Rent, 5040 Transport, 5080 Professional Fees
- 5200 Bad Debts

Golden Rules:
- Personal: Debit receiver, Credit giver
- Real: Debit what comes in, Credit what goes out
- Nominal: Debit expenses/losses, Credit income/gains

Answer in 2-3 short paragraphs. Give a concrete journal entry (Debit X, Credit Y).
Always mention which account codes from the chart above to use.

Question: {question}"""
                        r = client.chat.completions.create(
                            model="qwen/qwen3.8-27b",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=500,
                        )
                        answer = r.choices[0].message.content
                    else:
                        answer = "⚠️ No Groq API key in .env"
                except Exception as e:
                    answer = f"⚠️ AI unavailable: {e}"

                st.session_state.acc_chat.append({"role": "assistant", "content": answer})
                st.rerun()

        if st.session_state.acc_chat:
            if st.button("Clear chat"):
                st.session_state.acc_chat = []
                st.rerun()
