"""
accounting_classify.py — Traditional Indian account classification.
Personal / Real / Nominal + Golden Rules.
"""
import sys
from pathlib import Path as _Path
_THIS_DIR = _Path(__file__).parent.resolve()
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from accounting.db import get_conn

# Personal: Persons, companies, capital, debtors, creditors
# Real: Assets (tangible + intangible), cash, stock
# Nominal: Income, expenses, losses, gains

# Map our chart of accounts codes to traditional types
TRADITIONAL_TYPE = {
    # Assets → Real (except debtors/creditors which are Personal)
    "1000": ("Real",     "Cash is a real account — debit what comes in, credit what goes out"),
    "1010": ("Real",     "Bank is a real account — debit receipts, credit payments"),
    "1020": ("Real",     "Bank — same as primary"),
    "1030": ("Real",     "UPI wallet is a real account"),
    "1100": ("Personal", "Retailers owe us — debit increases their debt"),
    "1200": ("Real",     "Stock is a real account — debit purchases, credit sales/issues"),
    "1210": ("Real",     "Devices — real account"),
    "1300": ("Personal", "Advance to suppliers — supplier is personal account"),
    "1400": ("Real",     "GST credit — real account"),
    "1410": ("Real",     "GST credit — real account"),
    "1420": ("Real",     "GST credit — real account"),
    "1500": ("Real",     "Furniture — real account"),
    "1510": ("Real",     "Equipment — real account"),
    "1520": ("Real",     "Vehicle — real account"),
    "1530": ("Real",     "Accumulated depreciation"),
    # Liabilities → Personal (persons/entities we owe)
    "2000": ("Personal", "Suppliers we owe — personal account"),
    "2100": ("Personal", "GST owed to government — government is a personal account"),
    "2110": ("Personal", "GST owed"),
    "2120": ("Personal", "GST owed"),
    "2200": ("Personal", "Bank loan — bank is a personal account"),
    "2210": ("Personal", "Owner loan — owner is a personal account"),
    "2300": ("Personal", "Salaries owed to staff — personal accounts"),
    "2310": ("Personal", "TDS owed to government — personal account"),
    # Equity → Personal (owner is a person)
    "3000": ("Personal", "Owner capital — owner is personal account"),
    "3100": ("Personal", "Owner drawings — personal"),
    "3200": ("Personal", "Retained earnings — owner's equity"),
    # Income → Nominal
    "4000": ("Nominal", "Sales — nominal account, credit increases"),
    "4010": ("Nominal", "Sales — nominal"),
    "4100": ("Nominal", "Discount received — nominal income"),
    "4200": ("Nominal", "Interest income — nominal"),
    "4900": ("Nominal", "Other income — nominal"),
    # Expense → Nominal
    "5000": ("Nominal", "COGS — nominal expense"),
    "5010": ("Nominal", "Salaries — nominal expense"),
    "5020": ("Nominal", "Rent — nominal expense"),
    "5030": ("Nominal", "Utilities — nominal expense"),
    "5040": ("Nominal", "Transport — nominal expense"),
    "5050": ("Nominal", "Packing — nominal expense"),
    "5060": ("Nominal", "Telephone — nominal expense"),
    "5070": ("Nominal", "Stationery — nominal expense"),
    "5080": ("Nominal", "Professional fees — nominal expense"),
    "5090": ("Nominal", "Bank charges — nominal"),
    "5100": ("Nominal", "Repairs — nominal"),
    "5110": ("Nominal", "Marketing — nominal"),
    "5120": ("Nominal", "Travel — nominal"),
    "5130": ("Nominal", "Depreciation — nominal (non-cash)"),
    "5140": ("Nominal", "Interest on loans — nominal expense"),
    "5190": ("Nominal", "Miscellaneous — nominal"),
    # New: Bad debts
    "5200": ("Nominal", "Bad Debts Written Off — nominal expense"),
    "5210": ("Nominal", "Bad Debt Provision — nominal expense"),
    "1150": ("Personal", "Provision for Bad Debts (contra-asset)"),
}

# The 3 Golden Rules of Accounting — for the Help section
GOLDEN_RULES = {
    "Personal": {
        "rule": "Debit the receiver, Credit the giver",
        "example": "Retailer pays ₹5,000 cash → Dr Cash, Cr Retailer (receiver of cash is giver of payment)",
        "icon": "👤",
    },
    "Real": {
        "rule": "Debit what comes in, Credit what goes out",
        "example": "Buy furniture for ₹10,000 cash → Dr Furniture, Cr Cash",
        "icon": "🏛️",
    },
    "Nominal": {
        "rule": "Debit all expenses and losses, Credit all incomes and gains",
        "example": "Pay rent ₹5,000 → Dr Rent (expense), Cr Cash",
        "icon": "📊",
    },
}


def get_traditional_type(account_code):
    """Return (Personal|Real|Nominal, reason) for an account code."""
    return TRADITIONAL_TYPE.get(account_code, ("Real", "Default classification"))


def list_accounts_by_traditional_type(book_id):
    """Group all accounts by Personal / Real / Nominal."""
    from accounting.chart import list_accounts
    accounts = list_accounts(book_id)
    grouped = {"Personal": [], "Real": [], "Nominal": []}
    for a in accounts:
        ttype, reason = get_traditional_type(a["code"])
        a["traditional_type"] = ttype
        a["traditional_reason"] = reason
        grouped[ttype].append(a)
    return grouped


if __name__ == "__main__":
    from accounting.db import init_db
    from accounting.chart import create_book
    init_db()
    create_book("MEENA", "Meena Agencies")

    print("═" * 70)
    print("  TRADITIONAL ACCOUNT CLASSIFICATION")
    print("═" * 70)

    grouped = list_accounts_by_traditional_type("MEENA")
    for ttype in ["Personal", "Real", "Nominal"]:
        rule = GOLDEN_RULES[ttype]
        print(f"\n{rule['icon']}  {ttype.upper()} — {rule['rule']}")
        print("─" * 70)
        for a in grouped[ttype][:8]:
            print(f"   {a['code']}  {a['name'][:45]}")
        if len(grouped[ttype]) > 8:
            print(f"   ... and {len(grouped[ttype]) - 8} more")
