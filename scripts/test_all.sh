#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Meena Agencies — Full Test Suite
#  Usage:   bash scripts/test_all.sh
#  Exit 0 = all green. Exit non-zero = first failing stage printed.
# ═══════════════════════════════════════════════════════════════════
set -u
cd "$(dirname "$0")/.."              # repo root
PY="../.venv/bin/python"
URL="https://meena-agencies-trusted-pharma-wholesale-partner.streamlit.app/"
PASS=0; FAIL=0
ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
bad()  { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
hdr()  { echo; echo "═══ $1 ═══"; }

# ──────────────────────────────────────────────────────────────────
hdr "1. Repo / git sanity"
# ──────────────────────────────────────────────────────────────────
git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  && ok "inside a git repo" || bad "not a git repo"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$BRANCH" = "main" ] && ok "on branch main" || bad "on branch '$BRANCH' (expected main)"

if git fetch origin main -q 2>/dev/null; then
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse origin/main)
  if [ "$LOCAL" = "$REMOTE" ]; then
    ok "local == origin/main ($LOCAL)"
  else
    bad "local ($LOCAL) ≠ origin/main ($REMOTE) — push before testing live!"
  fi
else
  bad "cannot fetch origin/main (network?)"
fi

# Untracked .py files that SHOULD be tracked
UNTRACKED=$(git ls-files --others --exclude-standard '*.py' | grep -v '\.bak' || true)
if [ -z "$UNTRACKED" ]; then
  ok "no untracked .py files"
else
  bad "untracked .py files present:"; echo "$UNTRACKED" | sed 's/^/       /'
fi

# ──────────────────────────────────────────────────────────────────
hdr "2. Python syntax (py_compile every .py)"
# ──────────────────────────────────────────────────────────────────
BAD_SYNTAX=0
while IFS= read -r f; do
  if ! $PY -m py_compile "$f" 2>/tmp/pyc.err; then
    bad "syntax error in $f"; sed 's/^/       /' /tmp/pyc.err | head -3
    BAD_SYNTAX=1
  fi
done < <(git ls-files '*.py' 'apps_isolated/*.py')
[ $BAD_SYNTAX -eq 0 ] && ok "all tracked .py files compile"

# ──────────────────────────────────────────────────────────────────
hdr "3. Import health (order_success, meena)"
# ──────────────────────────────────────────────────────────────────
$PY - <<'PY' && ok "order_success imports standalone"
import sys; sys.path.insert(0,'apps_isolated')
import order_success
for fn in ("show_amazon_success_page","show_shop_hours_banner"):
    assert hasattr(order_success, fn), f"missing {fn}"
PY

$PY - <<'PY' && ok "meena imports order_success safely"
import sys; sys.path.insert(0,'apps_isolated')
import meena
assert hasattr(meena,"show_amazon_success_page") or hasattr(meena,"_get_success_helpers"), \
    "meena has no access to order_success helpers"
PY

# ──────────────────────────────────────────────────────────────────
hdr "4. Required secrets (TELEGRAM_BOT_TOKEN presence)"
# ──────────────────────────────────────────────────────────────────
if [ -f .streamlit/secrets.toml ]; then
  ok ".streamlit/secrets.toml exists locally"
  grep -q 'TELEGRAM_BOT_TOKEN' .streamlit/secrets.toml \
    && ok "TELEGRAM_BOT_TOKEN present in secrets.toml" \
    || bad "TELEGRAM_BOT_TOKEN missing from secrets.toml"
else
  bad ".streamlit/secrets.toml missing (needed for local run; Cloud uses dashboard secrets)"
fi

# ──────────────────────────────────────────────────────────────────
hdr "5. Requirements completeness"
# ──────────────────────────────────────────────────────────────────
if [ -f requirements.txt ]; then
  ok "requirements.txt present"
  for pkg in streamlit requests; do
    grep -qi "^${pkg}" requirements.txt && ok "  $pkg listed" || bad "  $pkg NOT listed"
  done
else
  bad "requirements.txt missing"
fi

# ──────────────────────────────────────────────────────────────────
hdr "6. Headless Streamlit boot (30s smoke test)"
# ──────────────────────────────────────────────────────────────────
LOG=/tmp/streamlit_test.log
rm -f "$LOG"
timeout 35s $PY -m streamlit run apps_isolated/meena.py \
  --server.headless true --server.port 8599 \
  --browser.gatherUsageStats false >"$LOG" 2>&1 &
SPID=$!
sleep 12
if curl -sf -o /dev/null "http://localhost:8599/_stcore/health"; then
  ok "Streamlit app responds on :8599"
else
  bad "Streamlit did not start — see $LOG"
  tail -20 "$LOG" | sed 's/^/       /'
fi
kill $SPID 2>/dev/null; wait $SPID 2>/dev/null || true

# ──────────────────────────────────────────────────────────────────
hdr "7. Live Cloud URL reachable"
# ──────────────────────────────────────────────────────────────────
JAR=$(mktemp); trap 'rm -f "$JAR"' EXIT
HTTP=$(curl -sL -b "$JAR" -c "$JAR" -o /dev/null -w "%{http_code}" --max-time 20 "$URL")
case "$HTTP" in
  200) ok "GET $URL (followed) → 200" ;;
  000) bad "GET $URL → no response (network/DNS)" ;;
  *)   bad "GET $URL → HTTP $HTTP after redirects" ;;
esac

H=$(curl -sL -b "$JAR" -c "$JAR" -o /dev/null -w "%{http_code}" --max-time 20 "${URL%/}/_stcore/health")
[ "$H" = "200" ] && ok "Cloud /_stcore/health (followed) → 200" || bad "Cloud health → $H after redirects"

# ──────────────────────────────────────────────────────────────────
hdr "8. Cloud error-page probe"
# ──────────────────────────────────────────────────────────────────
BODY=$(curl -s --max-time 20 "$URL")
for pat in ModuleNotFoundError SyntaxError IndentationError "Traceback" "Encountered an error"; do
  if echo "$BODY" | grep -q "$pat"; then
    bad "Cloud page contains '$pat' — app is NOT healthy"
  else
    ok "no '$pat' on live page"
  fi
done

# ──────────────────────────────────────────────────────────────────
hdr "SUMMARY"
# ──────────────────────────────────────────────────────────────────
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
[ $FAIL -eq 0 ] && { echo "  🟢 ALL GREEN"; exit 0; } || { echo "  🔴 FAILURES — fix above"; exit 1; }
