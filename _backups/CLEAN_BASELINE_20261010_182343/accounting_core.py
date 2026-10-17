"""Double-entry accounting engine — Indian accounting standards"""
import os, json
from datetime import datetime

JOURNAL_FILE = "journal.json"

# Standard Chart of Accounts for pharma wholesale
CHART_OF_ACCOUNTS = {
    "1000": {"name": "Cash A/c", "type": "Asset"},
    "1010": {"name": "Bank A/c", "type": "Asset"},
    "1100": {"name": "Sundry Debtors", "type": "Asset"},
    "1200": {"name": "Closing Stock", "type": "Asset"},
    "1500": {"name": "Furniture & Fixtures", "type": "Asset"},
    "2000": {"name": "Sundry Creditors", "type": "Liability"},
    "2100": {"name": "GST Output Payable", "type": "Liability"},
    "2200": {"name": "GST Input Credit", "type": "Asset"},
    "2300": {"name": "Loans Payable", "type": "Liability"},
    "3000": {"name": "Capital A/c", "type": "Equity"},
    "3100": {"name": "Drawings A/c", "type": "Equity"},
    "4000": {"name": "Sales A/c", "type": "Income"},
    "4100": {"name": "Sales Returns A/c", "type": "Income"},  # contra-income
    "5000": {"name": "Purchases A/c", "type": "Expense"},
    "5100": {"name": "Purchase Returns A/c", "type": "Expense"},  # contra-expense
    "5200": {"name": "Opening Stock", "type": "Expense"},
    "6000": {"name": "Salary A/c", "type": "Expense"},
    "6100": {"name": "Rent A/c", "type": "Expense"},
    "6200": {"name": "Electricity A/c", "type": "Expense"},
    "6300": {"name": "Telephone & Internet", "type": "Expense"},
    "6400": {"name": "Transport & Freight", "type": "Expense"},
    "6500": {"name": "Discount Allowed", "type": "Expense"},
    "6600": {"name": "Discount Received", "type": "Income"},
    "6700": {"name": "Interest Paid", "type": "Expense"},
    "6800": {"name": "Interest Received", "type": "Income"},
    "6900": {"name": "Bad Debts", "type": "Expense"},
    "7000": {"name": "Miscellaneous Expenses", "type": "Expense"},
}


def load_journal():
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE) as f: return json.load(f)
    return []


def save_journal(data):
    with open(JOURNAL_FILE, "w") as f: json.dump(data, f, indent=2)


def create_journal_entry(description, lines, ref="", source="MANUAL", user="OWNER"):
    """lines = list of {account_code, debit, credit, narration}"""
    # Validate: total debit must equal total credit
    total_dr = sum(l.get("debit", 0) for l in lines)
    total_cr = sum(l.get("credit", 0) for l in lines)
    if round(total_dr, 2) != round(total_cr, 2):
        raise ValueError(f"Debit (₹{total_dr}) != Credit (₹{total_cr})")

    journal = load_journal()
    entry = {
        "entry_id": f"JV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(journal)+1:04d}",
        "date": datetime.now().isoformat(),
        "date_display": datetime.now().strftime("%d-%b-%Y").upper(),
        "description": description,
        "ref": ref,
        "source": source,
        "user": user,
        "lines": [
            {
                "account_code": l["account_code"],
                "account_name": CHART_OF_ACCOUNTS.get(l["account_code"], {}).get("name", "Unknown"),
                "debit": round(l.get("debit", 0), 2),
                "credit": round(l.get("credit", 0), 2),
                "narration": l.get("narration", "")
            }
            for l in lines
        ],
        "total_debit": round(total_dr, 2),
        "total_credit": round(total_cr, 2)
    }
    journal.append(entry)
    save_journal(journal)
    return entry


def auto_post_order_sale(order, retailer, gst_rate=12):
    """Auto-generate journal entry when an order is approved (credit sale)."""
    base = order["total"]
    gst = round(base * gst_rate / 100, 2)
    total = round(base + gst, 2)
    return create_journal_entry(
        description=f"Credit sale to {retailer['shop']} (Order {order['order_id']})",
        lines=[
            {"account_code": "1100", "debit": total, "credit": 0,
             "narration": f"Being amount due from {retailer['shop']}"},
            {"account_code": "4000", "debit": 0, "credit": base,
             "narration": f"Being sales of goods"},
            {"account_code": "2100", "debit": 0, "credit": gst,
             "narration": f"Being GST @ {gst_rate}% on sale"},
        ],
        ref=order["order_id"],
        source="AUTO_ORDER"
    )


def auto_post_payment(retailer, amount, method):
    """Auto-generate journal entry when payment is received."""
    dr_account = "1000" if method == "Cash" else "1010"
    return create_journal_entry(
        description=f"Payment received from {retailer['shop']} via {method}",
        lines=[
            {"account_code": dr_account, "debit": amount, "credit": 0,
             "narration": f"Being amount received via {method}"},
            {"account_code": "1100", "debit": 0, "credit": amount,
             "narration": f"Being dues reduced for {retailer['shop']}"},
        ],
        ref=f"PAY-{retailer['id']}",
        source="AUTO_PAYMENT"
    )


def compute_ledger(account_code):
    """Return all entries affecting one account."""
    journal = load_journal()
    entries = []
    balance = 0
    for j in journal:
        for l in j["lines"]:
            if l["account_code"] == account_code:
                balance += l["debit"] - l["credit"]
                entries.append({
                    "date": j["date_display"],
                    "ref": j["ref"],
                    "description": j["description"],
                    "debit": l["debit"],
                    "credit": l["credit"],
                    "balance": round(balance, 2)
                })
    return entries


def compute_debtor_ledger(retailer_id):
    """Return debtor ledger filtered by retailer."""
    journal = load_journal()
    entries = []
    balance = 0
    for j in journal:
        if j["ref"] and retailer_id in j["ref"] or retailer_id in j["description"]:
            for l in j["lines"]:
                if l["account_code"] == "1100":
                    balance += l["debit"] - l["credit"]
                    entries.append({
                        "date": j["date_display"],
                        "ref": j["ref"],
                        "description": j["description"],
                        "debit": l["debit"],
                        "credit": l["credit"],
                        "balance": round(balance, 2)
                    })
    return entries


def trial_balance():
    """Return trial balance across all accounts."""
    journal = load_journal()
    balances = {}
    for j in journal:
        for l in j["lines"]:
            code = l["account_code"]
            if code not in balances:
                balances[code] = {"name": l["account_name"], "debit": 0, "credit": 0}
            balances[code]["debit"] += l["debit"]
            balances[code]["credit"] += l["credit"]

    rows = []
    total_dr = total_cr = 0
    for code, b in sorted(balances.items()):
        net = b["debit"] - b["credit"]
        dr = net if net > 0 else 0
        cr = -net if net < 0 else 0
        rows.append({
            "code": code,
            "name": b["name"],
            "debit": round(dr, 2),
            "credit": round(cr, 2)
        })
        total_dr += dr
        total_cr += cr

    return {"rows": rows, "total_debit": round(total_dr, 2), "total_credit": round(total_cr, 2),
            "balanced": round(total_dr, 2) == round(total_cr, 2)}


def profit_and_loss():
    """Indian format P&L."""
    tb = trial_balance()
    accounts = {r["code"]: r for r in tb["rows"]}

    def get_net(code):
        r = accounts.get(code, {"debit": 0, "credit": 0})
        return r["debit"] - r["credit"]

    sales = -get_net("4000")           # credit balance = positive
    sales_returns = get_net("4100")    # debit balance
    net_sales = sales - sales_returns

    purchases = get_net("5000")
    purchase_returns = -get_net("5100")
    net_purchases = purchases - purchase_returns
    opening_stock = get_net("5200")
    closing_stock = -get_net("1200")
    cogs = opening_stock + net_purchases - closing_stock
    gross_profit = net_sales - cogs

    expenses = {}
    for code, name in [("6000","Salary"),("6100","Rent"),("6200","Electricity"),
                       ("6300","Telephone"),("6400","Transport"),("6500","Discount Allowed"),
                       ("6700","Interest Paid"),("6900","Bad Debts"),("7000","Misc")]:
        expenses[name] = get_net(code)

    other_income = -get_net("6600") + -get_net("6800")  # discount received + interest received

    total_expenses = sum(expenses.values())
    net_profit = gross_profit + other_income - total_expenses

    return {
        "sales": sales, "sales_returns": sales_returns, "net_sales": net_sales,
        "opening_stock": opening_stock, "purchases": purchases,
        "purchase_returns": purchase_returns, "net_purchases": net_purchases,
        "closing_stock": closing_stock, "cogs": cogs,
        "gross_profit": gross_profit,
        "expenses": expenses, "total_expenses": total_expenses,
        "other_income": other_income,
        "net_profit": net_profit
    }


def balance_sheet():
    """Indian format Balance Sheet."""
    tb = trial_balance()
    accounts = {r["code"]: r for r in tb["rows"]}

    def dr(code):
        r = accounts.get(code, {"debit": 0, "credit": 0})
        return r["debit"] - r["credit"]

    assets = {
        "Cash": dr("1000"), "Bank": dr("1010"),
        "Sundry Debtors": dr("1100"), "Closing Stock": dr("1200"),
        "Furniture": dr("1500"),
    }
    liabilities = {
        "Sundry Creditors": -dr("2000"),
        "GST Payable": -dr("2100"),
        "Loans": -dr("2300"),
    }
    equity = {"Capital": -dr("3000"), "Drawings": dr("3100")}
    pl = profit_and_loss()
    equity["Net Profit (Current)"] = pl["net_profit"]

    total_assets = sum(v for v in assets.values() if v > 0)
    total_liab = sum(v for v in liabilities.values() if v > 0)
    total_equity = sum(v for v in equity.values())

    return {
        "assets": assets, "liabilities": liabilities, "equity": equity,
        "total_assets": round(total_assets, 2),
        "total_liab_equity": round(total_liab + total_equity, 2),
        "balanced": round(total_assets, 2) == round(total_liab + total_equity, 2)
    }


def day_book(days=7):
    from datetime import timedelta
    journal = load_journal()
    cutoff = datetime.now() - timedelta(days=days)
    return [j for j in journal if datetime.fromisoformat(j["date"]) >= cutoff]


def sales_register():
    return [j for j in load_journal() if j["source"] == "AUTO_ORDER"]


def purchase_register():
    return [j for j in load_journal() if "purchase" in j["description"].lower()]
