"""inr.py — Indian number format: ₹2,00,000 not ₹200,000."""
def inr(n, decimals=0):
    try:
        f = float(n)
    except (TypeError, ValueError):
        return "₹0"
    neg = f < 0
    f = abs(f)
    if decimals > 0:
        s = f"{f:.{decimals}f}"
        int_part, dec_part = s.split(".")
    else:
        int_part = str(int(round(f)))
        dec_part = ""
    if len(int_part) <= 3:
        grouped = int_part
    else:
        last3 = int_part[-3:]
        rest = int_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        grouped = ",".join(groups) + "," + last3
    result = "₹" + grouped
    if dec_part:
        result += "." + dec_part
    if neg:
        result = "-" + result
    return result

if __name__ == "__main__":
    for v, e in [(200000,"₹2,00,000"),(145000,"₹1,45,000"),(55000,"₹55,000"),(2078,"₹2,078")]:
        got = inr(v)
        print(("✅" if got == e else "❌"), f"inr({v}) = {got}")
