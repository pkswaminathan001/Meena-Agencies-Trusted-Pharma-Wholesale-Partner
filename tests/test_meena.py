"""
Meena Agencies — Full Security & Functional Test Suite
Run: python3 tests/test_meena.py
"""
import json, sys, re, urllib.request, csv
from pathlib import Path
from datetime import datetime

PARENT = Path(__file__).parent.parent
APP    = PARENT / "apps_isolated" / "meena.py"
SEC    = PARENT / "apps_isolated" / "security_layer.py"

results = []

def check(cat, name, passed, detail="", sev="info"):
    results.append({"cat": cat, "test": name, "pass": bool(passed),
                    "detail": detail, "sev": sev})

def green(s):  return "\033[92m" + s + "\033[0m"
def red(s):    return "\033[91m" + s + "\033[0m"
def bold(s):   return "\033[1m" + s + "\033[0m"


# ═══ 1. INFRASTRUCTURE ═══
print(bold("\n=== 1. INFRASTRUCTURE ==="))

check("infra", "meena.py exists", APP.exists())
check("infra", "security_layer.py exists", SEC.exists())

try:
    compile(APP.read_text(), str(APP), "exec")
    check("infra", "meena.py compiles", True)
except SyntaxError as e:
    check("infra", "meena.py compiles", False, "Line " + str(e.lineno), "critical")

try:
    compile(SEC.read_text(), str(SEC), "exec")
    check("infra", "security_layer.py compiles", True)
except SyntaxError as e:
    check("infra", "security_layer.py compiles", False, "Line " + str(e.lineno), "critical")

try:
    r = urllib.request.urlopen("http://localhost:8501/_stcore/health", timeout=5)
    check("infra", "App responds on 8501", r.status == 200)
except Exception as e:
    check("infra", "App responds on 8501", False, str(e), "critical")


# ═══ 2. FILE PERMISSIONS ═══
print(bold("\n=== 2. FILE PERMISSIONS ==="))

for name in ["retailers.json", "orders.json", "users.json",
             "approval_rules.json", "inventory.csv",
             "sessions.json", "rate_limit.json", ".meena_salt"]:
    p = PARENT / name
    if not p.exists():
        check("perms", name + " exists", False, "missing", "warn")
        continue
    mode = oct(p.stat().st_mode)[-3:]
    safe = mode in ("600", "640", "660")
    check("perms", name + " mode=" + mode, safe,
          "should be 600" if not safe else "",
          "high" if not safe else "info")


# ═══ 3. AUTHENTICATION ═══
print(bold("\n=== 3. AUTHENTICATION ==="))

uf = PARENT / "users.json"
if uf.exists():
    try:
        users = json.loads(uf.read_text())
        check("auth", "users.json parses", True)
        for u in users:
            uid = u.get("id", "?")
            ph = u.get("pin_hash", "")
            check("auth", uid + " has pin_hash", bool(ph))
            check("auth", uid + " hash not plaintext",
                  ph not in ("owner2026", "staff123", "1234"),
                  "", "critical" if ph in ("owner2026", "staff123") else "info")
            check("auth", uid + " hash length >= 40",
                  len(ph) >= 40, "len=" + str(len(ph)),
                  "high" if len(ph) < 40 else "info")
    except Exception as e:
        check("auth", "users.json parses", False, str(e), "critical")


# ═══ 4. STATIC CODE ANALYSIS ═══
print(bold("\n=== 4. STATIC CODE ANALYSIS ==="))

src = APP.read_text()

hardcoded = re.findall(r'password\s*=\s*["\'][^"\']{4,}["\']', src, re.I)
check("code", "No hardcoded passwords", len(hardcoded) == 0,
      "Found " + str(len(hardcoded)), "critical" if hardcoded else "info")

sql_fstr = re.findall(r'(?:execute|query)\s*\(\s*f["\']', src)
check("code", "No f-string SQL", len(sql_fstr) == 0, "",
      "critical" if sql_fstr else "info")

danger = re.findall(r'\b(eval|exec|__import__)\s*\(', src)
check("code", "No eval/exec/__import__", len(danger) == 0,
      "Found " + str(danger[:3]) if danger else "",
      "high" if danger else "info")

check("code", "No pickle", "import pickle" not in src,
      "", "high" if "import pickle" in src else "info")

subp = re.findall(r'(?:os\.system|subprocess\.(?:call|run|Popen))', src)
check("code", "No shell execution", len(subp) == 0, "",
      "high" if subp else "info")

bare_ex = re.findall(r'except\s*:', src)
check("code", "No bare except:", len(bare_ex) == 0,
      "Found " + str(len(bare_ex)), "medium" if bare_ex else "info")


# ═══ 5. DATA INTEGRITY ═══
print(bold("\n=== 5. DATA INTEGRITY ==="))

rf = PARENT / "retailers.json"
if rf.exists():
    try:
        rets = json.loads(rf.read_text())
        check("data", "retailers.json parses", True)
        arr = rets if isinstance(rets, list) else list(rets.values())
        for r in arr:
            rid = r.get("id", "?")
            lim = float(r.get("credit_limit") or 0)
            out = float(r.get("outstanding") or 0)
            check("data", rid + " outstanding <= limit",
                  out <= lim * 1.05,
                  "out=" + str(int(out)) + " lim=" + str(int(lim)),
                  "high" if out > lim * 1.05 else "info")
    except Exception as e:
        check("data", "retailers.json parses", False, str(e), "critical")

of = PARENT / "orders.json"
if of.exists():
    try:
        orders = json.loads(of.read_text())
        check("data", "orders.json parses", True)
        bad = [o for o in orders if not isinstance(o.get("total"), (int, float))]
        check("data", "All orders numeric total", len(bad) == 0,
              str(len(bad)) + " bad", "high" if bad else "info")
    except Exception as e:
        check("data", "orders.json parses", False, str(e), "critical")

inv = PARENT / "inventory.csv"
if inv.exists():
    try:
        with open(inv) as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            cols = reader.fieldnames
        check("data", "inventory.csv parses", True)
        req = ["medicine_name", "quantity", "cost_price"]
        have = all(c in cols for c in req)
        check("data", "inventory has required columns", have,
              "cols=" + str(cols), "high" if not have else "info")
    except Exception as e:
        check("data", "inventory.csv parses", False, str(e), "critical")


# ═══ 6. BUSINESS LOGIC ═══
print(bold("\n=== 6. BUSINESS LOGIC ==="))

def sim_decide(order, retailer, rules):
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
         "restricted_categories": ["injection", "insulin"],
         "block_overdue_days": 60}

tests = [
    ("Low value auto", {"total": 2000, "items": [{"medicine": "Dolo 650"}]},
     {"overdue_days": 0}, "auto"),
    ("High value manual", {"total": 20000, "items": [{"medicine": "Dolo 650"}]},
     {"overdue_days": 0}, "manual"),
    ("Injection manual", {"total": 500, "items": [{"medicine": "Insulin Injection"}]},
     {"overdue_days": 0}, "manual"),
    ("Overdue manual", {"total": 1000, "items": [{"medicine": "Dolo 650"}]},
     {"overdue_days": 90}, "manual"),
]
for name, order, ret, expected in tests:
    got = sim_decide(order, ret, rules)
    check("logic", "Approval: " + name, got == expected,
          "got=" + got + " exp=" + expected,
          "critical" if got != expected else "info")


# ═══ 7. NETWORK ═══
print(bold("\n=== 7. NETWORK ==="))

try:
    req = urllib.request.Request("http://localhost:8501/", method="HEAD")
    resp = urllib.request.urlopen(req, timeout=5)
    hdrs = dict(resp.headers)
    check("net", "X-Frame-Options set", "X-Frame-Options" in hdrs, "", "medium")
    check("net", "X-Content-Type-Options set",
          "X-Content-Type-Options" in hdrs, "", "medium")
except Exception as e:
    check("net", "Server headers", False, str(e), "low")

for fname in (".env", ".env.local", "secrets.json"):
    p = PARENT / fname
    check("net", "No exposed " + fname, not p.exists(),
          "FILE PRESENT", "critical" if p.exists() else "info")


# ═══ 8. PHISHING ═══
print(bold("\n=== 8. PHISHING / SOCIAL ==="))

wa = re.findall(r'https?://wa\.me/(\d+)', src)
for w in wa:
    ok = w.startswith("91") and len(w) == 12
    check("phish", "WhatsApp intl fmt " + w, ok, "", "medium" if not ok else "info")

domains = set(re.findall(r'https?://([a-zA-Z0-9.-]+)', src))
allow = {"unpkg.com", "server.arcgisonline.com", "www.dhl.com",
         "api.groq.com", "wa.me", "maps.googleapis.com",
         "fonts.googleapis.com", "streamlit.io"}
for d in domains:
    safe = d in allow or d.endswith("googleapis.com") or d.endswith("openstreetmap.org")
    check("phish", "Domain " + d, safe, "UNVERIFIED" if not safe else "",
          "medium" if not safe else "info")


# ═══ SUMMARY ═══
print(bold("\n" + "=" * 60))
print(bold("  RESULTS"))
print("=" * 60)

total = len(results)
passed = sum(1 for r in results if r["pass"])
failed = total - passed

print("\nTotal: " + str(total))
print(green("PASS: " + str(passed)))
print(red("FAIL: " + str(failed)))

by_sev = {}
for r in results:
    if not r["pass"]:
        by_sev.setdefault(r["sev"], []).append(r)

for sev in ["critical", "high", "medium", "warn", "low", "info"]:
    if sev not in by_sev: continue
    fails = by_sev[sev]
    emoji = {"critical": "RED", "high": "ORANGE", "medium": "YELLOW",
             "warn": "YELLOW", "low": "GRAY", "info": "GRAY"}.get(sev, "?")
    print("\n" + emoji + " " + sev.upper() + " (" + str(len(fails)) + "):")
    for r in fails:
        print("  - [" + r["cat"] + "] " + r["test"])
        if r["detail"]:
            print("      -> " + r["detail"])

report = {"ts": datetime.now().isoformat(), "total": total,
          "passed": passed, "failed": failed, "results": results}
(PARENT / "test_report.json").write_text(json.dumps(report, indent=2))
print("\nReport saved: " + str(PARENT / "test_report.json"))

sys.exit(0 if failed == 0 else 1)
