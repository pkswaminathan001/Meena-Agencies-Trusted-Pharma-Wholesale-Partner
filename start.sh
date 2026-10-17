#!/bin/bash
cd "$(dirname "$0")"
pkill -9 -f streamlit 2>/dev/null
pkill -9 -f chatbot.py 2>/dev/null
sleep 2
nohup ../.venv/bin/python apps_isolated/chatbot.py > apps_isolated/logs/chatbot_stdout.log 2>&1 &
nohup ../.venv/bin/python -m streamlit run apps_isolated/meena.py --server.port=8501 --server.headless=true > apps_isolated/logs/meena.log 2>&1 &
sleep 8
curl -s http://localhost:8501/_stcore/health >/dev/null && echo "✅ App up" || echo "❌ App down"
