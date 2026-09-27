#!/bin/bash
cd "$(dirname "$0")"

echo "═══════════════════════════════════════════"
echo "  PHARMAMIND — SYSTEM HEALTH CHECK"
echo "  $(date '+%d-%b-%Y %H:%M:%S')"
echo "═══════════════════════════════════════════"
echo ""

# 1. Python files compile
echo "▸ Python files compile:"
FAIL=0
for f in *.py; do
    if python3 -c "compile(open('$f').read(), '$f', 'exec')" 2>/dev/null; then
        echo "  ✅ $f"
    else
        echo "  ❌ $f — SYNTAX ERROR"
        FAIL=$((FAIL+1))
    fi
done
echo ""

# 2. Data files exist
echo "▸ Data files:"
for f in retailers.json orders.json inventory.csv inventory.db company.json .env; do
    if [ -f "$f" ]; then
        SIZE=$(du -h "$f" | cut -f1)
        echo "  ✅ $f ($SIZE)"
    else
        echo "  ❌ $f — MISSING"
    fi
done
echo ""

# 3. .env values
echo "▸ Credentials:"
python3 << 'PYEOF'
from pathlib import Path
if Path(".env").exists():
    c = Path(".env").read_text()
    for line in c.splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            v = line.split("=",1)[1].strip()
            print(f"  {'✅' if ':' in v else '❌'} Telegram token ({len(v)} chars)")
        elif line.startswith("GROQ_API_KEY="):
            v = line.split("=",1)[1].strip()
            print(f"  {'✅' if v.startswith('gsk_') else '❌'} Groq key ({len(v)} chars)")
        elif line.startswith("NOTIFY_CHANNEL="):
            v = line.split("=",1)[1].strip()
            print(f"  ℹ️  Channel: {v}")
PYEOF
echo ""

# 4. Services
echo "▸ Background services:"
if pgrep -f click_server.py > /dev/null; then
    echo "  ✅ Click server running"
else
    echo "  ⚠️  Click server NOT running"
fi

if pgrep -f "streamlit run" > /dev/null; then
    PORT=$(ss -tlnp 2>/dev/null | grep -oP ':850[0-9]' | head -1 | tr -d ':')
    echo "  ✅ Streamlit running on port $PORT"
else
    echo "  ⚠️  Streamlit NOT running"
fi
echo ""

# 5. Test PDF generation
echo "▸ PDF generation test:"
python3 << 'PYEOF' 2>&1 | grep -E "✅|❌|Page" | head -5
import json
from pathlib import Path
try:
    import statement_pdf
    retailers = json.loads(Path("retailers.json").read_text())
    orders = json.loads(Path("orders.json").read_text()) if Path("orders.json").exists() else []
    company = json.loads(Path("company.json").read_text())
    pdf = statement_pdf.generate_statement_pdf(retailers[0], orders, company)
    from pypdf import PdfReader
    pages = len(PdfReader(__import__("io").BytesIO(pdf)).pages)
    print(f"  ✅ Generated {len(pdf):,} bytes, {pages} page(s)")
except Exception as e:
    print(f"  ❌ {e}")
PYEOF
echo ""

# 6. Backup status
echo "▸ Backups:"
if [ -d "$HOME/PharmaBackups" ]; then
    COUNT=$(ls $HOME/PharmaBackups/pharma_backup_*.tar.gz 2>/dev/null | wc -l)
    LATEST=$(ls -t $HOME/PharmaBackups/pharma_backup_*.tar.gz 2>/dev/null | head -1)
    echo "  ✅ $COUNT backup(s)"
    [ -n "$LATEST" ] && echo "     Latest: $(basename $LATEST) ($(du -h $LATEST | cut -f1))"
else
    echo "  ⚠️  No backups yet"
fi
echo ""

# 7. Auto-backup timer
echo "▸ Auto-backup timer:"
if systemctl --user list-timers 2>/dev/null | grep -q pharma-backup; then
    echo "  ✅ Daily backup scheduled"
else
    echo "  ⚠️  Timer not installed"
fi
echo ""

echo "═══════════════════════════════════════════"
echo "  Report complete."
echo "═══════════════════════════════════════════"
