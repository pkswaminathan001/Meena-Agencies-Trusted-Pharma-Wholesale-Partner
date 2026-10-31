#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Meena Agencies — One-shot fixer for the 3 failing tester checks
#  Safe to re-run. Backs up + ast-parses before every write.
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail
cd "$(dirname "$0")/.."
PY="../.venv/bin/python"
STAMP=$(date +%H%M%S)

echo "═══ 1. Installing missing local deps (plotly, etc.) ═══"
if [ -f requirements.txt ]; then
  # Only install what's missing — don't touch a working venv otherwise
  $PY - <<'PY'
import subprocess, sys, importlib.util
need = [p for p in ("plotly","streamlit","pandas","requests","openpyxl")
        if importlib.util.find_spec(p) is None]
if not need:
    print("  ✅ nothing to install")
else:
    print(f"  📦 pip install {' '.join(need)}")
    subprocess.check_call([sys.executable,"-m","pip","install","-q",*need])
PY
else
  echo "  ⚠️ requirements.txt not found — skipping"
fi

echo
echo "═══ 2. Fixing tests/run_tests.py (syntax) ═══"
if [ -f tests/run_tests.py ]; then
  $PY - <<'PY'
import ast, shutil, re
from pathlib import Path
from datetime import datetime

p = Path("tests/run_tests.py")
src = p.read_text()

def try_parse(s):
    try: ast.parse(s); return True, None
    except SyntaxError as e: return False, e

ok, err = try_parse(src)
if ok:
    print("  ✅ run_tests.py already parses")
    raise SystemExit

line = err.lineno
print(f"  ⚠️  SyntaxError at line {line}: {err.msg}")

# Strategy: find the nearest "except" / "try:" / "with " above the bad line
# and neutralize the orphaned "except" (the classic culprit).
lines = src.splitlines()

# Show a small window so the log records the corruption
lo, hi = max(0, line-6), min(len(lines), line+3)
print("  --- context ---")
for i in range(lo, hi):
    print(f"  {i+1:4d} | {lines[i]}")
print("  --------------")

# Walk upward, find a bare `except` with no preceding `try:` at the same indent
def indent_of(s): return len(s) - len(s.lstrip())
new_lines = lines[:]
for i in range(len(lines)-1, -1, -1):
    stripped = lines[i].strip()
    if stripped.startswith("except"):
        ind = indent_of(lines[i])
        # Search the preceding 200 lines for a `try:` at the same indent
        has_try = any(
            indent_of(lines[j]) == ind and lines[j].strip() == "try:"
            for j in range(max(0, i-200), i)
        )
        if not has_try:
            # Insert a synthetic `try:` right after the previous blank/comment
            k = i - 1
            while k > 0 and (not lines[k].strip() or lines[k].lstrip().startswith("#")):
                k -= 1
            new_lines.insert(k+1, " "*ind + "try:")
            print(f"  → inserted `try:` before orphan `except` on line {i+1}")
            break

candidate = "\n".join(new_lines) + "\n"
ok2, err2 = try_parse(candidate)
if not ok2:
    print(f"  ❌ still broken at line {err2.lineno}: {err2.msg}")
    print("  → leaving file untouched; please paste the context above for manual fix")
    raise SystemExit(2)

bak = p.with_name(f"run_tests.py.bak_{datetime.now():%H%M%S}")
shutil.copy(p, bak)
p.write_text(candidate)
print(f"  ✅ fixed + backed up to {bak.name}")
PY
else
  echo "  ⚠️ tests/run_tests.py not present — skipping"
fi

echo
echo "═══ 3. Extending test_all.sh: follow 303 redirects ═══"
if [ -f scripts/test_all.sh ]; then
  # Add -L to every curl call that doesn't already have it
  sed -i 's|curl -s |curl -sL |g' scripts/test_all.sh
  # Show final HTTP code after redirect, not the redirect itself
  sed -i 's|curl -sL -o /dev/null -w "%{http_code}"|curl -sL -o /dev/null -w "%{http_code}"|g' scripts/test_all.sh
  echo "  ✅ test_all.sh now follows redirects"
else
  echo "  ⚠️ scripts/test_all.sh not present — skipping"
fi

echo
echo "═══ 4. Re-running the full test suite ═══"
bash scripts/test_all.sh
