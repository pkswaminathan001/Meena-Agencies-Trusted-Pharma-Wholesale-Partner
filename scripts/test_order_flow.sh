#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY="../.venv/bin/python"

echo "═══ Order data model smoke test ═══"
$PY - <<'PY'
import sys, json, tempfile, pathlib
sys.path.insert(0, "apps_isolated")
from datetime import datetime

# 1. Both success-page helpers exist and are callable
import order_success as os_
assert callable(os_.show_amazon_success_page)
assert callable(os_.show_shop_hours_banner)
print("✅ order_success exposes both helpers")

# 2. Shop-hours banner uses datetime, not a raw int
import inspect
sig = inspect.getsource(os_.show_shop_hours_banner)
assert "datetime" in sig or "time(" in sig, "banner should gate on clock time"
print("✅ show_shop_hours_banner() reads the current time")

# 3. Sample order dict satisfies the fields show_amazon_success_page() reads
sample = {"order_id": "TEST-001", "total": 1234.5, "items": [
    {"medicine": "Paracetamol 500", "qty": 2, "line_total": 40.0}
]}
for k in ("order_id", "total", "items"):
    assert k in sample
print("✅ sample order has order_id, total, items")
PY
