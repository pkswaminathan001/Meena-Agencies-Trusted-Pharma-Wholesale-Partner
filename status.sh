#!/bin/bash
cd "$(dirname "$0")"
echo "═══ Syntax ═══"
../.venv/bin/python -m py_compile apps_isolated/meena.py && echo "meena.py compiles OK"
echo ""
echo "═══ Processes ═══"
pgrep -af chatbot.py | head -1
pgrep -af "streamlit.*meena" | head -1
echo ""
echo "═══ Health ═══"
curl -s http://localhost:8501/_stcore/health >/dev/null && echo "App up on :8501" || echo "App DOWN"
echo ""
echo "═══ Recent errors ═══"
tail -30 apps_isolated/logs/meena.log 2>/dev/null | grep -iE "error|traceback" | tail -5 || echo "none"
