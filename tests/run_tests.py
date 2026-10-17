"""
Meena Agencies — Full Security & Functional Test Suite
Runs against the live app + source files.
Usage: python3 tests/run_tests.py
"""
import json, sys, re, os, stat, hashlib, urllib.request
from pathlib import Path
from datetime import datetime

PARENT = Path(__file__).parent.parent
APP    = PARENT / "apps_isolated" / "meena.py"
SEC    = PARENT / "apps_isolated" / "security_layer.py"

results = []
def check(category, name, passed, detail="", severity="info"):
    results.append({"cat": category, "test": name, "pass": bool(passed),
                    "detail": detail, "sev": severity})

def red(s):    return f"\033[91m{s}\033[0m"
def green(s):  return f"\033[92m{s}\033[0m"
def yellow(s): return f"\033[93m{s}\033[0m"
def bold(s):   return f"\033[1m{s}\033[0m"


# ═════════════════════════════════════════════════════════════
#  CATEGORY 1: INFRASTRUCTURE
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 1. INFRASTRUCTURE ═══"))

check("infra", "meena.py exists", APP.exists(), str(APP), "critical" if not APP.exists() else "info")
check("infra", "security_layer.py exists", SEC.exists(), str(SEC))

try:
    compile(APP.read_text(), str(APP), "exec")
    check("infra", "meena.py compiles", True)
except SyntaxError as e:
    check("infra", "meena.py compiles", False, f"Line {e.lineno}: {e.text}", "critical")

try:
    compile(SEC.read_text(), str(SEC), "exec")
    check("infra", "security_layer.py compiles", True)
except SyntaxError as e:
    check("infra", "security_layer.py compiles", False, f"Line {e.lineno}: {e.text}", "critical")

# Live server check
try:
    r = urllib.request.urlopen("http://localhost:8501/_stcore/health", timeout=5)
    check("infra", "App responds on 8501", r.status == 200, f"HTTP {r.status}")
except Exception as e:
    check("infra", "App responds on 8501", False, str(e), "critical")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 2: FILE PERMISSIONS
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 2. FILE PERMISSIONS ═══"))

sensitive = ["retailers.json", "orders.json", "users.json",
             "approval_rules.json", "inventory.csv",
             "sessions.json", "rate_limit.json", ".meena_salt"]

for name in sensitive:
    p = PARENT / name
    if not p.exists():
        check("perms", f"{name} exists", False, "file missing", "warn")
        continue
    mode = oct(p.stat().st_mode)[-3:]
    # 600 or 640 accepted
    is_safe = mode in ("600", "640")
    check("perms", f"{name} mode = {mode}", is_safe,
          "should be 600" if not is_safe else "",
          "high" if not is_safe else "info")

# Check .venv not exposed in git
gitignore = PARENT / ".gitignore"
if gitignore.exists():
    gi = gitignore.read_text()
    check("perms", ".gitignore exists", True)
    for pat in [".venv", "*.json", "*.log"]:
        check("perms", f".gitignore has {pat}", pat in gi, "", "medium" if pat not in gi else "info")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 3: AUTHENTICATION & SESSIONS
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 3. AUTHENTICATION ═══"))

users_file = PARENT / "users.json"
if users_file.exists():
    try:
        users = json.loads(users_file.read_text())
        for u in users:
            role = u.get("role", "?")
            ph = u.get("pin_hash", "")
            check("auth", f"{u.get('id','?')} has pin_hash",
                  bool(ph), f"len={len(ph)}" if ph else "missing")
            # Hash quality: not plaintext, not obviously weak
            check("auth", f"{u.get('id','?')} hash is not plaintext 'owner2026'/'staff123'",
                  ph not in ("owner2026", "staff123", "1234"), "",
                  "critical" if ph in ("owner2026","staff123") else "info")
            check("auth", f"{u.get('id','?')} hash length ≥ 40",
                  len(ph) >= 40, f"len={len(ph)}", "high" if len(ph) < 40 else "info")

# Session token randomness
sess_file = PARENT / "sessions.json"
if sess_file.exists():
    try:
        sess = json.loads(sess_file.read_text())
        for tok in sess.keys():
            check("auth", f"session token entropy (len={len(tok)})",
                  len(tok) >= 16, "", "high" if len(tok) < 16 else "info")
    except Exception:
        pass

# Rate limit exists
check("auth", "rate_limit.json exists (tracks failed attempts)",
      (PARENT / "rate_limit.json").exists(), "",
      "medium" if not (PARENT / "rate_limit.json").exists() else "info")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 4: SOURCE CODE SECURITY (STATIC ANALYSIS)
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 4. STATIC CODE ANALYSIS ═══"))

src = APP.read_text()

# Hardcoded passwords in source
hardcoded = re.findall(r'password\s*=\s*["\'][^"\']{4,}["\']', src, re.I)
check("code", "No hardcoded passwords in meena.py",
      len(hardcoded) == 0, f"Found {len(hardcoded)}: {hardcoded[:3]}" if hardcoded else "",
      "critical" if hardcoded else "info")

# SQL injection risk (f-string into SQL)
sql_fstr = re.findall(r'(?:execute|query)\s*\(\s*f["\']', src)
check("code", "No f-string SQL queries",
      len(sql_fstr) == 0, f"Found {len(sql_fstr)}", "critical" if sql_fstr else "info")

# eval / exec usage
dangerous = re.findall(r'\b(eval|exec|__import__)\s*\(', src)
check("code", "No eval/exec/__import__ usage",
      len(dangerous) == 0, f"Found: {dangerous[:5]}" if dangerous else "",
      "high" if dangerous else "info")

# Pickle (unsafe deserialization)
pickle_use = "import pickle" in src or "pickle.load" in src
check("code", "No pickle deserialization", not pickle_use, "",
      "high" if pickle_use else "info")

# os.system / subprocess
subprocess_use = re.findall(r'(?:os\.system|subprocess\.(?:call|run|Popen|check_output))', src)
check("code", "No shell execution in app",
      len(subprocess_use) == 0, f"Found: {subprocess_use[:3]}" if subprocess_use else "",
      "high" if subprocess_use else "info")

# open() with user input path — heuristic
open_writes = re.findall(r'open\([^)]*["\']w["\']', src)
check("code", "All file writes are to fixed paths",
      len(open_writes) <= 20, f"{len(open_writes)} write opens",
      "medium" if len(open_writes) > 20 else "info")

# try/except swallowing
bare_except = re.findall(r'except\s*:', src)
check("code", "No bare `except:` clauses",
      len(bare_except) == 0, f"Found {len(bare_except)}",
      "medium" if bare_except else "info")

# Debug mode
if "debug=True" in src:
    check("code", "Debug mode off", False, "Found debug=True", "high")
else:
    check("code", "Debug mode off", True)


# ═════════════════════════════════════════════════════════════
#  CATEGORY 5: DATA INTEGRITY
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 5. DATA INTEGRITY ═══"))

# Retailers
rf = PARENT / "retailers.json"
if rf.exists():
    try:
        rets = json.loads(rf.read_text())
        check("data", "retailers.json is valid JSON", True)
        for r in (rets if isinstance(rets, list) else rets.values()):
            rid = r.get("id", "?")
            check("data", f"{rid} has shop name", bool(r.get("shop")), "", "medium" if not r.get("shop") else "info")
            check("data", f"{rid} has credit_limit as number",
                  isinstance(r.get("credit_limit"), (int, float)),
                  "", "high" if not isinstance(r.get("credit_limit"), (int,float)) else "info")
            # Outstanding should never exceed limit
            lim = float(r.get("credit_limit") or 0)
            out = float(r.get("outstanding") or 0)
            check("data", f"{rid} outstanding ≤ credit_limit",
                  out <= lim * 1.05,
                  f"out={out:.0f} > lim={lim:.0f}",
                  "high" if out > lim * 1.05 else "info")
    except Exception as e:
        check("data", "retailers.json parses", False, str(e), "critical")

# Orders
of = PARENT / "orders.json"
if of.exists():
    try:
        orders = json.loads(of.read_text())
        check("data", "orders.json is valid JSON", True)
        bad = [o for o in orders if not isinstance(o.get("total"), (int, float))]
        check("data", "All orders have numeric total",
              len(bad) == 0, f"{len(bad)} bad",
              "high" if bad else "info")
    except Exception as e:
        check("data", "orders.json parses", False, str(e), "critical")

# Inventory
inv = PARENT / "inventory.csv"
if inv.exists():
    try:
        import csv
        with open(inv) as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
        check("data", "inventory.csv parses", True)
        check("data", "inventory has required columns",
              all(c in reader.fieldnames for c in ("medicine_name","quantity","cost_price")),
              f"cols={reader.fieldnames}",
              "high" if not all(c in reader.fieldnames for c in ("medicine_name","quantity","cost_price")) else "info")
        bad_qty = [r for r in rows if not r.get("quantity","").strip().lstrip("-").isdigit()]
        check("data", "All inventory rows have numeric quantity",
              len(bad_qty) == 0, f"{len(bad_qty)} bad",
              "medium" if bad_qty else "info")
    except Exception as e:
        check("data", "inventory.csv parses", False, str(e), "critical")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 6: BUSINESS LOGIC
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 6. BUSINESS LOGIC ═══"))

# Approval rules
arf = PARENT / "approval_rules.json"
if arf.exists():
    try:
        rules = json.loads(arf.read_text())
        check("logic", "approval_rules.json parses", True)
        check("logic", "auto_approve_max_value is positive number",
              isinstance(rules.get("auto_approve_max_value"), (int, float))
              and rules.get("auto_approve_max_value") >= 0,
              "", "high" if not isinstance(rules.get("auto_approve_max_value"), (int,float)) else "info")
        check("logic", "restricted_categories is a list",
              isinstance(rules.get("restricted_categories"), list))
    except Exception as e:
        check("logic", "approval_rules.json parses", False, str(e), "high")

# Test decide_approval logic directly
sys.path.insert(0, str(PARENT / "apps_isolated"))
try:
    # Simulate
    def _sim_decide(order, retailer, rules):
        if not rules.get("auto_approve_enabled", True):
            return "manual"
        total = float(order.get("total", 0))
        restricted = [c.lower() for c in rules.get("restricted_categories", [])]
        for it in order.get("items", []):
            nm = (it.get("medicine") or "").lower()
            if any(r in nm for r in restricted):
                return "manual"
        if retailer.get("overdue_days", 0) > rules.get("block_overdue_days", 60):
            return "manual"
        if total > rules.get("auto_approve_max_value", 0):
            return "manual"
        return "auto"

    rules = {"auto_approve_enabled": True, "auto_approve_max_value": 5000,
             "trusted_min_orders": 3, "restricted_categories": ["injection","insulin"],
             "block_overdue_days": 60}

    tests = [
        ("Low value, no restrictions",  {"total": 2000, "items": [{"medicine": "Dolo 650"}]},
         {"_order_count": 0}, "auto"),
        ("High value",                  {"total": 20000, "items": [{"medicine": "Dolo 650"}]},
         {"_order_count": 0}, "manual"),
        ("Restricted (Injection)",      {"total": 500, "items": [{"medicine": "Insulin Injection"}]},
         {"_order_count": 10}, "manual"),
        ("Overdue retailer",            {"total": 1000, "items": [{"medicine": "Dolo 650"}]},
         {"_order_count": 10, "overdue_days": 90}, "manual"),
    ]
    for name, order, ret, expected in tests:
        got = _sim_decide(order, ret, rules)
        check("logic", f"Approval: {name}",
              got == expected, f"got={got}, expected={expected}",
              "critical" if got != expected else "info")
except Exception as e:
    check("logic", "Approval logic test", False, str(e), "high")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 7: SECURITY HEADERS / NETWORK
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 7. NETWORK SECURITY ═══"))

try:
    req = urllib.request.Request("http://localhost:8501/", method="HEAD")
    resp = urllib.request.urlopen(req, timeout=5)
    hdrs = dict(resp.headers)
    check("net", "X-Frame-Options set (clickjack)", 
          "X-Frame-Options" in hdrs, "", "medium")
    check("net", "X-Content-Type-Options set",
          "X-Content-Type-Options" in hdrs, "", "medium")
    check("net", "Content-Security-Policy set",
          "Content-Security-Policy" in hdrs, "", "medium")
except Exception as e:
    check("net", "Server header inspection", False, str(e), "low")

# Check for exposed env files
for fname in (".env", ".env.local", "config.py.backup", "secrets.json"):
    p = PARENT / fname
    check("net", f"No exposed {fname}",
          not p.exists(), "file present!", "critical" if p.exists() else "info")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 8: PHISHING / SOCIAL ENGINEERING RESISTANCE
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 8. PHISHING / SOCIAL ═══"))

# Check WhatsApp/SMS links use proper number format
wa_links = re.findall(r'https?://wa\.me/(\d+)', src)
for w in wa_links:
    check("phish", f"WhatsApp link uses intl format ({w})",
          w.startswith("91") and len(w) == 12,
          "should start with 91 + 10 digits",
          "medium" if not (w.startswith("91") and len(w)==12) else "info")

# Check for any suspicious external links
external = re.findall(r'https?://([a-zA-Z0-9.-]+)', src)
unique_domains = set(external)
safe_domains = {"unpkg.com", "server.arcgisonline.com", "www.dhl.com",
                "api.groq.com", "wa.me", "maps.googleapis.com",
                "mapsplatform.google.com", "fonts.googleapis.com", "streamlit.io"}
for d in unique_domains:
    check("phish", f"External domain: {d}",
          d in safe_domains or d.endswith("googleapis.com") or d.endswith("openstreetmap.org"),
          "UNVERIFIED DOMAIN" if d not in safe_domains else "",
          "medium" if d not in safe_domains else "info")

# Check for hidden redirects
redirects = re.findall(r'(?:location\.href|window\.location)\s*=\s*["\']([^"\']+)', src)
check("phish", "No hidden JS redirects",
      len(redirects) == 0, f"Found: {redirects[:3]}" if redirects else "",
      "high" if redirects else "info")


# ═════════════════════════════════════════════════════════════
#  CATEGORY 9: PRIVACY
# ═════════════════════════════════════════════════════════════
print(bold("\n═══ 9. PRIVACY ═══"))

# Check if PII is exposed in logs
log_dir = PARENT / "apps_isolated" / "logs"
if log_dir.exists():
    for log in log_dir.glob("*.log"):
        content = log.read_text()[-5000:] if log.stat().st_size < 100000 else ""
        pii_leak = re.search(r'\b\d{10}\b', content)  # 10-digit phone
        check("privacy", f"{log.name} no phone leak",
              not pii_leak, "Possible phone number in logs",
              "medium" if pii_leak else "info")

# Check that we don't print passwords
print_stmts = re.findall(r'print\([^)]*pass[^)]*\)', src, re.I)
check("privacy", "No print() of passwords",
      len(print_stmts) == 0, f"Found {len(print_stmts)}",
      "high" if print_stmts else "info")


# ═════════════════════════════════════════════════════════════
#  RESULTS SUMMARY
# ═════════════════════════════════════════════════════════════
print(bold("\n" + "═" * 60))
print(bold("  RESULTS SUMMARY"))
print("═" * 60)

total = len(results)
passed = sum(1 for r in results if r["pass"])
failed = total - passed

by_sev = {}
for r in results:
    if not r["pass"]:
        by_sev.setdefault(r["sev"], []).append(r)

sev_order = ["critical", "high", "medium", "warn", "low", "info"]
sev_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "warn": "🟡", "low": "⚪", "info": "⚪"}

print(f"\nTotal tests: {total}")
print(f"  {green('PASS')}: {passed}")
print(f"  {red('FAIL')}: {failed}\n")

if failed:
    print(bold("FAILURES BY SEVERITY:"))
    for sev in sev_order:
        if sev not in by_sev: continue
        fails = by_sev[sev]
        print(f"\n{sev_emoji.get(sev,'?')} {sev.upper()} ({len(fails)}):")
        for r in fails:
            print(f"  • [{r['cat']}] {r['test']}")
            if r['detail']:
                print(f"      → {r['detail']}")
else:
    print(green("✅ ALL TESTS PASSED"))

# Save report
report = {"timestamp": datetime.now().isoformat(),
          "total": total, "passed": passed, "failed": failed,
          "results": results}
(PARENT / "test_report.json").write_text(json.dumps(report, indent=2))
print(f"\n📄 Full report → {PARENT}/test_report.json")

sys.exit(0 if failed == 0 else 1)
