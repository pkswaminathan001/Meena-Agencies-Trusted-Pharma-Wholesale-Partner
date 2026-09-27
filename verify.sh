#!/bin/bash
# Quick verification for PharmaMind code changes
cd "$(dirname "$0")"

echo "=== 1. Compile check ==="
for f in app.py invoice_pro.py statement_pdf.py statement_png.py operations.py brand.py; do
    if [ -f "$f" ]; then
        python3 -c "compile(open('$f').read(), '$f', 'exec')" 2>/dev/null && \
            echo "  ✅ $f" || echo "  ❌ $f — has syntax error"
    fi
done

echo ""
echo "=== 2. Test PDF generation ==="
python3 - << 'PYEOF'
import json
from pathlib import Path
import statement_pdf
try:
    retailers = json.loads(Path("retailers.json").read_text())
    orders = json.loads(Path("orders.json").read_text())
    company = json.loads(Path("company.json").read_text())
    pdf = statement_pdf.generate_statement_pdf(retailers[0], orders, company)
    Path("/tmp/test.pdf").write_bytes(pdf)
    from pypdf import PdfReader
    pages = len(PdfReader("/tmp/test.pdf").pages)
    print(f"  ✅ PDF generated: {len(pdf):,} bytes, {pages} page(s)")
except Exception as e:
    print(f"  ❌ PDF failed: {e}")
PYEOF

echo ""
echo "=== Done ==="
echo "Open /tmp/test.pdf to visually inspect"
