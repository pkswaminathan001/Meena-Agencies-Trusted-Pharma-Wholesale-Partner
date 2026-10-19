#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY="../.venv/bin/python"

echo "═══ OTP helper behavior ═══"
$PY - <<'PY'
import os, sys
sys.path.insert(0, "apps_isolated")
import meena

# 1. Behavior shape — returns (bool, str) not bare bool
os.environ.pop("TELEGRAM_BOT_TOKEN", None)
r = meena.direct_send_otp("0", "test")
assert isinstance(r, tuple) and len(r) == 2, f"expected (bool, detail) tuple, got {type(r)}"
assert r[0] is False, f"expected failure for invalid chat, got {r!r}"
print("✅ direct_send_otp() returns (False, detail) on failure")

# 2. With a syntactically-valid fake token and unreachable chat — must return (False, _), not raise
os.environ["TELEGRAM_BOT_TOKEN"] = "111111:fake-token-for-test"
r2 = meena.direct_send_otp("-1", "test")
assert isinstance(r2, tuple) and r2[0] is False
print("✅ direct_send_otp() never raises on Telegram error")
PY
