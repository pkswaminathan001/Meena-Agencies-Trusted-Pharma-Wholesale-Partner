#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
BASE="https://meena-agencies-trusted-pharma-wholesale-partner.streamlit.app"

echo "═══ Live Cloud probes (follow redirects) ═══"
probe() {
  local path="$1"
  local code time
  read -r code time < <(curl -sL -o /dev/null -w "%{http_code} %{time_total}" "$BASE$path")
  printf "  %-28s → %s  (%ss)\n" "$path" "$code" "$time"
}

probe "/"                # canonical root
probe "/_stcore/health"  # streamlit health
probe "/?page=home"
probe "/?page=retailer_cart"
probe "/?page=my_orders"

echo
echo "═══ Error-string scan (following redirects) ═══"
BODY=$(curl -sL "$BASE/")
for pat in ModuleNotFoundError SyntaxError IndentationError "Traceback" "Encountered an error"; do
  if grep -q "$pat" <<<"$BODY"; then
    echo "  ❌ found '$pat'"
  else
    echo "  ✅ no '$pat'"
  fi
done
