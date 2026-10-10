"""sql_safety.py — Block dangerous SQL queries. Only SELECT allowed."""
import re

BLOCKED_KEYWORDS = {
    "drop", "delete", "truncate", "update", "insert", "alter", "create",
    "replace", "grant", "revoke", "exec", "execute", "attach", "detach",
    "pragma", "vacuum", "reindex", "call", "merge", "load", "outfile",
    "dumpfile", "shutdown", "kill", "reset",
}

ALLOWED_STARTS = ("select", "with")


def is_safe(sql: str) -> dict:
    """Return {'safe': bool, 'reason': str}."""
    if not sql or not sql.strip():
        return {"safe": False, "reason": "Empty query"}

    # Remove comments
    cleaned = re.sub(r"--[^\n]*", "", sql)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip().lower()

    if not cleaned.startswith(ALLOWED_STARTS):
        return {"safe": False, "reason": "Query must start with SELECT or WITH"}

    # Check for blocked keywords anywhere
    words = re.findall(r"\b\w+\b", cleaned)
    for w in words:
        if w in BLOCKED_KEYWORDS:
            return {"safe": False, "reason": f"Blocked keyword: {w.upper()}"}

    # Block multiple statements (;)
    # Allow only ONE trailing semicolon
    semicolons = cleaned.count(";")
    if semicolons > 1 or (semicolons == 1 and not cleaned.endswith(";")):
        return {"safe": False, "reason": "Multiple statements not allowed"}

    # Force row limit if not present
    if "limit" not in cleaned:
        sql = sql.rstrip().rstrip(";") + " LIMIT 500"

    return {"safe": True, "sql": sql}
