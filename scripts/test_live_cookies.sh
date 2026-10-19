#!/usr/bin/env bash
set -u
BASE="https://meena-agencies-trusted-pharma-wholesale-partner.streamlit.app"
JAR=$(mktemp)
trap 'rm -f "$JAR"' EXIT

echo "═══ Cloud reachability (cookie-aware) ═══"

step() {
  local name="$1" url="$2"
  local out code
  out=$(curl -s -b "$JAR" -c "$JAR" -o /tmp/step_body -w "%{http_code} %{redirect_url}" "$url")
  code=${out%% *}
  local redirect=${out#* }
  printf "  %-22s → %s%s\n" "$name" "$code" "${redirect:+  →$redirect}"
  STEP_CODE=$code
}

# 1. First GET — likely 303 to canonical
step "GET /"          "$BASE/"
# 2. Second GET — cookies now set; follow any redirect
step "GET / (2nd)"    "$BASE/"
# 3. Health
step "GET /_stcore/health" "$BASE/_stcore/health"

# 4. Deep link, cookie-aware
for p in home retailer_cart my_orders; do
  step "GET ?page=$p" "$BASE/?page=$p"
done

# 5. Final body scan
echo
echo "═══ Error-string scan ═══"
for pat in ModuleNotFoundError SyntaxError IndentationError "Traceback" "Encountered an error"; do
  if grep -q "$pat" /tmp/step_body; then echo "  ❌ found '$pat'"; else echo "  ✅ no '$pat'"; fi
done
