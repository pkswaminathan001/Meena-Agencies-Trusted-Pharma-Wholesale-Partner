"""
accounting_ui_full.py — Self-contained accounting engine + UI.
No external package — everything in this one file.
"""
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "accounting.db"

# ═══════════════════════════════════════════════════════════
# CHART OF ACCOUNTS
# ═══════════════════════════════════════════════════════════
DEFAULT_CHART = [
    ("1000", "Cash in Hand", "asset", "current"),
    ("1010", "Bank — Primary", "asset", "current"),
    ("1030", "UPI / Digital Wallet", "asset", "current"),
    ("1100", "Accounts Receivable (Retailers)", "asset", "current"),
    ("1200", "Inventory — Medicines", "asset", "current"),
    ("1300", "Advances to Suppliers", "asset", "current"),
    ("1400", "GST Input Credit", "asset", "current"),
    ("1500", "Furniture & Fixtures", "asset", "fixed"),
    ("1510", "Computer & Equipment", "asset", "fixed"),
    ("1520", "Vehicle", "asset", "fixed"),
    ("2000", "Accounts Payable (Suppliers)", "liability", "current"),
    ("2100", "GST Output Payable", "liability", "current"),
    ("2200", "Bank Loans", "liability", "long"),
    ("2300", "Salaries Payable", "liability", "current"),
    ("3000", "Owner's Capital", "equity", "capital"),
    ("3100", "Owner's Drawings", "equity", "drawings"),
    ("3200", "Retained Earnings", "equity", "retained"),
    ("4000", "Sales — Medicines", "income", "operating"),
    ("4100", "Discount Received", "income", "other"),
    ("5000", "Cost of Goods Sold", "expense", "direct"),
    ("5010", "Salaries & Wages", "expense", "operating"),
    ("5020", "Rent", "expense", "operating"),
    ("5030", "Electricity & Water", "expense", "operating"),
    ("5040", "Transport & Freight", "expense", "operating"),
    ("5060", "Telephone & Internet", "expense", "operating"),
    ("5070", "Office & Stationery", "expense", "operating"),
    ("5080", "Professional Fees (CA)", "expense", "operating"),
    ("5090", "Bank Charges", "expense", "operating"),
    ("5120", "Travel & Conveyance", "expense", "operating"),
    ("5200", "Bad Debts Written Off", "expense", "operating"),
]

TRADITIONAL_TYPE = {
    "1000": "Real", "1010": "Real", "1030": "Real", "1100": "Personal",
    "1200": "Real", "1300": "Personal", "1400": "Real", "1500": "Real",
    "1510": "Real", "1520": "Real", "2000": "Personal", "2100": "Personal",
    "2200": "Personal", "2300": "Personal", "3000": "Personal",
    "3100": "Personal", "3200": "Personal", "4000": "Nominal",
    "4100": "Nominal", "5000": "Nominal", "5010": "Nominal",
    "5020": "Nominal", "5030": "Nominal", "5040": "Nominal",
    "5060": "Nominal", "5070": "Nominal", "5080": "Nominal",
    "5090": "Nominal", "5120": "Nominal", "5200": "Nominal",
}

GOLDEN_RULES = {
    "Personal": {"rule": "Debit the receiver, Credit the giver", "icon": "👤",
                 "example": "Retailer pays cash → Dr Cash, Cr Retailer"},
    "Real": {"rule": "Debit what comes in, Credit what goes out", "icon": "🏛️",
             "example": "Buy furniture → Dr Furniture, Cr Cash"},
    "Nominal": {"rule": "Debit expenses & losses, Credit incomes & gains", "icon": "📊",
                "example": "Pay rent → Dr Rent, Cr Cash"},
}


# ═══════════════════════════════════════════════════════════
# DB LAYER
# ═══════════════════════════════════════════════════════════
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS books (
        book_id TEXT PRIMARY KEY, book_name TEXT, fiscal_year TEXT DEFAULT '2026-27')""")
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        code TEXT, book_id TEXT, name TEXT, type TEXT, category TEXT,
        PRIMARY KEY (code, book_id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS entries (
        entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id TEXT, entry_date TEXT, narration TEXT,
        source TEXT, source_ref TEXT, hash TEXT,
        UNIQUE(book_id, source, source_ref))""")
    c.execute("""CREATE TABLE IF NOT EXISTS lines (
        line_id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER, account_code TEXT, book_id TEXT,
        debit REAL DEFAULT 0, credit REAL DEFAULT 0, memo TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS balances (
        book_id TEXT, account_code TEXT,
        debit_total REAL DEFAULT 0, credit_total REAL DEFAULT 0,
        PRIMARY KEY (book_id, account_code))""")
    conn.commit()
    conn.close()


def create_book(book_id, book_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO books VALUES (?, ?, '2026-27')", (book_id, book_name))
    for code, name, atype, cat in DEFAULT_CHART:
        c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, ?, ?, ?)",
                  (code, book_id, name, atype, cat))
    conn.commit()
    conn.close()


def post_entry(book_id, entry_date, narration, lines, source="manual", source_ref=None):
    total_dr = sum(l.get("debit", 0) or 0 for l in lines)
    total_cr = sum(l.get("credit", 0) or 0 for l in lines)
    if abs(total_dr - total_cr) > 0.01 or total_dr == 0:
        return None
    conn = get_conn()
    c = conn.cursor()
    if source and source_ref:
        existing = c.execute("SELECT entry_id FROM entries WHERE book_id=? AND source=? AND source_ref=?",
                             (book_id, source, source_ref)).fetchone()
        if existing:
            conn.close()
            return None
    h = hashlib.sha256(f"{book_id}|{entry_date}|{narration}".encode()).hexdigest()[:16]
    try:
        c.execute("INSERT INTO entries (book_id, entry_date, narration, source, source_ref, hash) VALUES (?,?,?,?,?,?)",
                  (book_id, entry_date, narration, source, source_ref, h))
        eid = c.lastrowid
        for l in lines:
            dr = l.get("debit", 0) or 0
            cr = l.get("credit", 0) or 0
            c.execute("INSERT INTO lines (entry_id, account_code, book_id, debit, credit, memo) VALUES (?,?,?,?,?,?)",
                      (eid, l["account"], book_id, dr, cr, l.get("memo", "")))
            c.execute("""INSERT INTO balances VALUES (?,?,?,?)
                        ON CONFLICT(book_id, account_code) DO UPDATE SET
                        debit_total = debit_total + excluded.debit_total,
                        credit_total = credit_total + excluded.credit_total""",
                      (book_id, l["account"], dr, cr))
        conn.commit()
        return eid
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()


def sync_from_files(book_id):
    """Read orders.json + retailers.json → post entries."""
    posted = skipped = 0
    try:
        retailers = json.loads(Path("retailers.json").read_text())
        orders = json.loads(Path("orders.json").read_text()) if Path("orders.json").exists() else []
    except Exception:
        return {"posted": 0, "skipped": 0}

    for o in orders:
        if o.get("status") != "Approved":
            continue
        amt = float(o.get("total", 0) or 0)
        if amt <= 0:
            continue
        r = next((x for x in retailers if x["id"] == o.get("retailer_id")), None)
        if not r:
            continue
        date = datetime.now().strftime("%Y-%m-%d")
        try:
            date = datetime.strptime(str(o.get("placed_at", ""))[:11], "%d-%b-%Y").strftime("%Y-%m-%d")
        except Exception:
            pass
        eid = post_entry(book_id, date, f"Sale {o['order_id']} to {r['shop']}",
                         [{"account": "1100", "debit": amt, "memo": "AR"},
                          {"account": "4000", "credit": amt, "memo": "Sales"}],
                         "order", o["order_id"])
        if eid: posted += 1
        else: skipped += 1

    for r in retailers:
        for p in r.get("payment_history", []) or []:
            amt = float(p.get("amount", 0) or 0)
            if amt <= 0: continue
            mode = str(p.get("mode", "cash")).lower()
            asset = {"cash": "1000", "cheque": "1010", "upi": "1030",
                     "neft": "1010", "rtgs": "1010", "card": "1010"}.get(mode, "1000")
            ref = f"{r['id']}-{p.get('date','')[:19]}-{amt}"
            eid = post_entry(book_id, datetime.now().strftime("%Y-%m-%d"),
                             f"Payment from {r['shop']} via {mode}",
                             [{"account": asset, "debit": amt, "memo": p.get("reference","")},
                              {"account": "1100", "credit": amt, "memo": "AR settled"}],
                             "payment", ref)
            if eid: posted += 1
            else: skipped += 1

    return {"posted": posted, "skipped": skipped}


# ═══════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════
def trial_balance(book_id):
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("""SELECT a.code, a.name, a.type,
                        COALESCE(b.debit_total,0) as dr, COALESCE(b.credit_total,0) as cr
                        FROM accounts a LEFT JOIN balances b
                        ON b.book_id = a.book_id AND b.account_code = a.code
                        WHERE a.book_id = ? ORDER BY a.code""", (book_id,)).fetchall()
    conn.close()
    result = []
    t_dr = t_cr = 0
    for r in rows:
        if r["dr"] == 0 and r["cr"] == 0: continue
        result.append({"code": r["code"], "name": r["name"], "type": r["type"],
                       "debit": round(r["dr"], 2), "credit": round(r["cr"], 2)})
        t_dr += r["dr"]; t_cr += r["cr"]
    return {"accounts": result, "total_debit": round(t_dr, 2),
            "total_credit": round(t_cr, 2), "balanced": abs(t_dr - t_cr) < 0.01}


def profit_and_loss(book_id):
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("""SELECT a.code, a.name, a.type,
                        COALESCE(b.debit_total,0) as dr, COALESCE(b.credit_total,0) as cr
                        FROM accounts a LEFT JOIN balances b
                        ON b.book_id = a.book_id AND b.account_code = a.code
                        WHERE a.book_id = ? AND a.type IN ('income','expense')""", (book_id,)).fetchall()
    conn.close()
    inc, exp = [], []
    t_i = t_e = 0
    for r in rows:
        if r["type"] == "income":
            amt = r["cr"] - r["dr"]
            if abs(amt) > 0.01: inc.append({"name": r["name"], "amount": round(amt, 2)}); t_i += amt
        else:
            amt = r["dr"] - r["cr"]
            if abs(amt) > 0.01: exp.append({"name": r["name"], "amount": round(amt, 2)}); t_e += amt
    return {"income": inc, "expense": exp, "total_income": round(t_i, 2),
            "total_expense": round(t_e, 2), "net_profit": round(t_i - t_e, 2)}


def balance_sheet(book_id):
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("""SELECT a.code, a.name, a.type,
                        COALESCE(b.debit_total,0) as dr, COALESCE(b.credit_total,0) as cr
                        FROM accounts a LEFT JOIN balances b
                        ON b.book_id = a.book_id AND b.account_code = a.code
                        WHERE a.book_id = ? AND a.type IN ('asset','liability','equity')""", (book_id,)).fetchall()
    conn.close()
    assets, liabs, eqs = [], [], []
    t_a = t_l = t_e = 0
    for r in rows:
        if r["type"] == "asset":
            amt = r["dr"] - r["cr"]
            if abs(amt) > 0.01: assets.append({"name": r["name"], "amount": round(amt, 2)}); t_a += amt
        elif r["type"] == "liability":
            amt = r["cr"] - r["dr"]
            if abs(amt) > 0.01: liabs.append({"name": r["name"], "amount": round(amt, 2)}); t_l += amt
        else:
            amt = r["cr"] - r["dr"]
            if abs(amt) > 0.01: eqs.append({"name": r["name"], "amount": round(amt, 2)}); t_e += amt
    pl = profit_and_loss(book_id)
    if abs(pl["net_profit"]) > 0.01:
        eqs.append({"name": "Retained (Net Profit)", "amount": pl["net_profit"]})
        t_e += pl["net_profit"]
    return {"assets": assets, "liabilities": liabs, "equity": eqs,
            "total_assets": round(t_a, 2), "total_liabilities": round(t_l, 2),
            "total_equity": round(t_e, 2),
            "balanced": abs(t_a - (t_l + t_e)) < 1.0}


def account_balance(book_id, code):
    conn = get_conn()
    row = conn.execute("SELECT debit_total, credit_total FROM balances WHERE book_id=? AND account_code=?",
                       (book_id, code)).fetchone()
    atype_row = conn.execute("SELECT type FROM accounts WHERE book_id=? AND code=?",
                             (book_id, code)).fetchone()
    conn.close()
    if not row:
        return {"debit": 0, "credit": 0, "balance": 0}
    dr, cr = row["debit_total"], row["credit_total"]
    atype = atype_row["type"] if atype_row else "asset"
    bal = (dr - cr) if atype in ("asset", "expense") else (cr - dr)
    return {"debit": round(dr, 2), "credit": round(cr, 2), "balance": round(bal, 2)}


# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════
def _fmt(v):
    try: return f"{float(v):,.2f}"
    except: return "0.00"


def inject_book_css():
    st.markdown("""
    <style>
    .book-page {
        background: linear-gradient(180deg, #fefaf0 0%, #f9f3e5 100%);
        border: 1px solid #d4c5a0; border-radius: 4px;
        padding: 20px 26px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08), inset 0 0 60px rgba(212,197,160,0.12);
        position: relative; font-family: Georgia, serif; color: #2c1810;
        margin-bottom: 12px;
    }
    .book-page::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: linear-gradient(90deg, #8b0000, #c41e3a);
    }
    .book-title {
        font-family: Georgia, serif; font-size: 1.6rem; color: #8b0000;
        text-align: center; border-bottom: 3px double #8b0000;
        padding-bottom: 6px; margin-bottom: 4px; letter-spacing: 2px;
    }
    .book-subtitle { text-align: center; color: #8b6914; font-style: italic;
                     font-size: 0.8rem; margin-bottom: 14px; }
    .golden-card {
        background: linear-gradient(135deg, #fff8e7 0%, #ffeaa7 100%);
        border-left: 5px solid #d4a017; border-radius: 6px;
        padding: 10px 14px; margin: 8px 0; font-size: 0.85rem;
    }
    .golden-card h4 { margin: 0 0 6px 0; color: #8b6914; font-size: 0.95rem; }
    .golden-rule { font-weight: 700; color: #8b0000; font-size: 0.95rem;
                   margin: 4px 0; font-style: italic; }
    .ledger-line {
        border-bottom: 1px dotted #d4c5a0; padding: 6px 0; font-size: 0.85rem;
        font-family: 'Courier New', monospace;
    }
    .ttype-badge {
        display: inline-block; padding: 2px 8px; border-radius: 10px;
        font-size: 0.65rem; font-weight: 700;
    }
    .badge-personal { background: #d0e8ff; color: #004a99; }
    .badge-real     { background: #d4f5dd; color: #006633; }
    .badge-nominal  { background: #ffe4cc; color: #994400; }
    </style>
    """, unsafe_allow_html=True)


def _ttype_badge(code):
    tt = TRADITIONAL_TYPE.get(code, "Real")
    cls = {"Personal": "badge-personal", "Real": "badge-real",
           "Nominal": "badge-nominal"}.get(tt, "badge-real")
    return f'<span class="ttype-badge {cls}">{tt}</span>'


def render_accounting_tab(retailers, orders, df, save_retailers, save_orders, log_action):
    BOOK = "MEENA"
    init_db()
    create_book(BOOK, "Meena Agencies")
    inject_book_css()

    st.markdown('<div class="book-title">📖 MEENA AGENCIES — LEDGER BOOK</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="book-subtitle">Traditional Double-Entry · Personal · Real · Nominal</div>',
                unsafe_allow_html=True)

    tabs = st.tabs(["📊 Snapshot", "📖 Day Book", "👤 Personal", "🏛️ Real",
                    "📊 Nominal", "⚠️ Bad Debts", "❓ Help & AI"])

    # TAB 1 — Snapshot
    with tabs[0]:
        bs = balance_sheet(BOOK)
        pl = profit_and_loss(BOOK)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="book-page" style="padding:14px;text-align:center;">'
                        f'<div style="font-size:0.7rem;color:#8b6914;">ASSETS</div>'
                        f'<div style="font-size:1.4rem;font-weight:800;color:#008844;">'
                        f'₹{_fmt(bs["total_assets"])}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="book-page" style="padding:14px;text-align:center;">'
                        f'<div style="font-size:0.7rem;color:#8b6914;">LIABILITIES</div>'
                        f'<div style="font-size:1.4rem;font-weight:800;color:#8b0000;">'
                        f'₹{_fmt(bs["total_liabilities"])}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="book-page" style="padding:14px;text-align:center;">'
                        f'<div style="font-size:0.7rem;color:#8b6914;">EQUITY</div>'
                        f'<div style="font-size:1.4rem;font-weight:800;color:#004a99;">'
                        f'₹{_fmt(bs["total_equity"])}</div></div>', unsafe_allow_html=True)
        with c4:
            color = "#008844" if pl["net_profit"] >= 0 else "#8b0000"
            st.markdown(f'<div class="book-page" style="padding:14px;text-align:center;">'
                        f'<div style="font-size:0.7rem;color:#8b6914;">NET PROFIT</div>'
                        f'<div style="font-size:1.4rem;font-weight:800;color:{color};">'
                        f'₹{_fmt(pl["net_profit"])}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔄 Sync Orders → Journal", use_container_width=True, type="primary"):
            res = sync_from_files(BOOK)
            st.success(f"✅ Posted {res['posted']} new entries · Skipped {res['skipped']}")
            st.rerun()

    # TAB 2 — Day Book
    with tabs[1]:
        st.markdown("#### 📖 Day Book — Journal Entries")
        from_date = st.date_input("Pick date", datetime.now(), key="acc_date")
        conn = get_conn()
        date_str = from_date.strftime("%Y-%m-%d")
        entries = conn.execute("SELECT * FROM entries WHERE book_id=? AND entry_date=? ORDER BY entry_id",
                               (BOOK, date_str)).fetchall()
        if not entries:
            st.info("No entries on this date. Click Sync on Snapshot tab first.")
        else:
            for e in entries:
                lines = conn.execute("""SELECT l.*, a.name as aname FROM lines l
                                        LEFT JOIN accounts a ON a.code=l.account_code AND a.book_id=l.book_id
                                        WHERE l.entry_id=? ORDER BY l.line_id""", (e["entry_id"],)).fetchall()
                html_lines = ""
                for l in lines:
                    html_lines += (f'<tr style="border-bottom:1px dotted #d4c5a0;">'
                                   f'<td style="padding:3px 6px;">{l["aname"]} {_ttype_badge(l["account_code"])}</td>'
                                   f'<td style="text-align:right;padding:3px 6px;color:#004a99;">'
                                   f'{_fmt(l["debit"]) if l["debit"] else "—"}</td>'
                                   f'<td style="text-align:right;padding:3px 6px;color:#008844;">'
                                   f'{_fmt(l["credit"]) if l["credit"] else "—"}</td></tr>')
                st.markdown(f'<div class="book-page">'
                            f'<div style="font-size:0.75rem;color:#8b6914;">'
                            f'<b>Entry #{e["entry_id"]}</b> · {e["entry_date"]} · '
                            f'{e["source"]} · {e["source_ref"] or "—"}</div>'
                            f'<div style="font-style:italic;margin:6px 0;font-size:0.9rem;">'
                            f'{e["narration"]}</div>'
                            f'<table style="width:100%;border-collapse:collapse;font-family:Courier New;">'
                            f'<tr style="border-bottom:2px solid #8b6914;">'
                            f'<th style="text-align:left;padding:3px 6px;color:#8b0000;">Account</th>'
                            f'<th style="text-align:right;padding:3px 6px;color:#8b0000;">Debit</th>'
                            f'<th style="text-align:right;padding:3px 6px;color:#8b0000;">Credit</th></tr>'
                            f'{html_lines}</table></div>', unsafe_allow_html=True)
        conn.close()

    # TAB 3/4/5 — Personal/Real/Nominal
    def render_group(ttype, tab_idx):
        with tabs[tab_idx]:
            rule = GOLDEN_RULES[ttype]
            st.markdown(f'<div class="golden-card"><h4>{rule["icon"]} {ttype.upper()} ACCOUNTS</h4>'
                        f'<div class="golden-rule">"{rule["rule"]}"</div>'
                        f'<div style="color:#5c4a1e;"><b>Example:</b> {rule["example"]}</div></div>',
                        unsafe_allow_html=True)
            conn = get_conn()
            for code, name, atype, cat in DEFAULT_CHART:
                if TRADITIONAL_TYPE.get(code) != ttype: continue
                bal = account_balance(BOOK, code)
                if bal["debit"] == 0 and bal["credit"] == 0: continue
                st.markdown(f'<div class="ledger-line"><b>{code} — {name}</b>'
                            f'<span style="float:right;">Dr ₹{_fmt(bal["debit"])} · '
                            f'Cr ₹{_fmt(bal["credit"])} · <b>Bal ₹{_fmt(bal["balance"])}</b></span></div>',
                            unsafe_allow_html=True)
            conn.close()
            if all(account_balance(BOOK, c)["balance"] == 0
                   for c, _, _, _ in DEFAULT_CHART if TRADITIONAL_TYPE.get(c) == ttype):
                st.caption("No activity yet.")

    render_group("Personal", 2)
    render_group("Real", 3)
    render_group("Nominal", 4)

    # TAB 6 — Bad Debts
    with tabs[5]:
        st.markdown("#### ⚠️ Bad Debt & Recovery")
        report = []
        for r in retailers:
            o_amt = float(r.get("outstanding", 0) or 0)
            if o_amt <= 0: continue
            my_orders = [o for o in orders if o.get("retailer_id") == r.get("id")]
            last = max((o.get("placed_at", "") for o in my_orders), default="")
            days = 9999
            try:
                last_dt = datetime.strptime(str(last)[:11], "%d-%b-%Y")
                days = (datetime.now() - last_dt).days
            except Exception:
                pass
            if days < 90: cat = "🟢 Recoverable"
            elif days < 180: cat = "🟡 At Risk"
            elif days < 365: cat = "🟠 Doubtful"
            else: cat = "🔴 Bad Debt"
            report.append({"category": cat, "shop": r.get("shop", ""),
                           "owner": r.get("owner", ""), "phone": r.get("phone", ""),
                           "outstanding": o_amt, "last_order": last or "Never",
                           "status": r.get("status", "Active")})
        report.sort(key=lambda x: x["outstanding"], reverse=True)

        if report:
            total = sum(x["outstanding"] for x in report)
            bad = sum(x["outstanding"] for x in report if "Bad Debt" in x["category"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Outstanding", f"₹{_fmt(total)}")
            c2.metric("Likely Bad Debt", f"₹{_fmt(bad)}")
            c3.metric("Recovery Expected", f"{round((total-bad)/total*100,1) if total else 100}%")
            st.dataframe(pd.DataFrame(report), use_container_width=True, hide_index=True)
        else:
            st.success("✅ No outstanding debts!")

    # TAB 7 — Help & AI
    with tabs[6]:
        st.markdown("#### ❓ Help & AI Accountant")
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.expander("📘 Record a sale?"):
                st.markdown("- Dr Retailer (Personal)\n- Cr Sales (Nominal)\n\nRule: Debit receiver, Credit giver.")
        with c2:
            with st.expander("💰 Record payment?"):
                st.markdown("- Dr Cash (Real)\n- Cr Retailer (Personal)\n\nRule: Debit what comes in.")
        with c3:
            with st.expander("📝 Record expense?"):
                st.markdown("- Dr Expense (Nominal)\n- Cr Cash (Real)\n\nRule: Debit expenses.")

        st.markdown("---")
        st.markdown("##### 🤖 Ask AI Accountant")
        if "acc_chat" not in st.session_state:
            st.session_state.acc_chat = []
        for m in st.session_state.acc_chat[-6:]:
            if m["role"] == "user": st.markdown(f"**You:** {m['content']}")
            else: st.markdown(f"**AI:** {m['content']}")
        q = st.text_input("Your question:", key="acc_q",
                          placeholder="e.g. Where to record vehicle repair?")
        if st.button("Ask", use_container_width=True) and q.strip():
            st.session_state.acc_chat.append({"role": "user", "content": q})
            try:
                from groq import Groq
                import os
                from dotenv import load_dotenv
                load_dotenv()
                k = os.getenv("GROQ_API_KEY")
                if k:
                    client = Groq(api_key=k)
                    prompt = (f"You are an Indian CA helping pharma wholesale owner. Answer in 2-3 sentences "
                              f"with a concrete journal entry using account codes like 1000 Cash, "
                              f"1010 Bank, 1100 AR, 2000 AP, 4000 Sales, 5000 COGS.\n\nQuestion: {q}")
                    r = client.chat.completions.create(model="qwen/qwen3.8-27b",
                                                       messages=[{"role": "user", "content": prompt}],
                                                       temperature=0.3, max_tokens=400)
                    ans = r.choices[0].message.content
                else:
                    ans = "⚠️ No GROQ_API_KEY in .env"
            except Exception as e:
                ans = f"⚠️ {e}"
            st.session_state.acc_chat.append({"role": "assistant", "content": ans})
            st.rerun()
        if st.session_state.acc_chat and st.button("Clear chat"):
            st.session_state.acc_chat = []
            st.rerun()
