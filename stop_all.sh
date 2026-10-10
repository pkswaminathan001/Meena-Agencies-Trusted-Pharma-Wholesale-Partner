#!/bin/bash
echo "🛑 Stopping all Meena Agencies services..."
pkill -f "python3 bot.py" 2>/dev/null && echo "   ✅ Bot stopped"
pkill -f "python3 rep_server.py" 2>/dev/null && echo "   ✅ Rep server stopped"
pkill -f "python3 click_server.py" 2>/dev/null && echo "   ✅ Click server stopped"
pkill -f "http.server 8503" 2>/dev/null && echo "   ✅ PWA server stopped"
pkill -f "streamlit run" 2>/dev/null && echo "   ✅ Streamlit stopped"
echo ""
echo "✅ All services stopped."
