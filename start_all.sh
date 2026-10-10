#!/bin/bash
# ═══════════════════════════════════════════════
# Meena Agencies — Full Stack Startup
# ═══════════════════════════════════════════════

cd "/home/swaminathan/Desktop/swami/AGI Pharma Application/pharma-agi"

echo "═══════════════════════════════════════════════"
echo "   MEENA AGENCIES — Starting All Services"
echo "═══════════════════════════════════════════════"
echo ""

# ─── Stop old processes ───
echo "🧹 Stopping old processes..."
pkill -f "python3 bot.py" 2>/dev/null
pkill -f "python3 rep_server.py" 2>/dev/null
pkill -f "python3 click_server.py" 2>/dev/null
pkill -f "http.server 8503" 2>/dev/null
pkill -f "streamlit run" 2>/dev/null
sleep 2

# ─── 1. Start Streamlit app ───
echo "1️⃣  Starting Streamlit app (port 8501)..."
nohup streamlit run app.py --server.fileWatcherType=none --server.runOnSave=false --server.headless=true > streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "   ✅ Streamlit: PID $STREAMLIT_PID"

# ─── 2. Start Telegram bot ───
echo "2️⃣  Starting Telegram bot..."
nohup python3 bot.py > bot.log 2>&1 &
BOT_PID=$!
echo "   ✅ Bot: PID $BOT_PID"

# ─── 3. Start Rep tracking server ───
echo "3️⃣  Starting Rep tracking server (port 8502)..."
nohup /usr/bin/python3 rep_server.py > rep_server.log 2>&1 &
REP_PID=$!
echo "   ✅ Rep server: PID $REP_PID"

# ─── 4. Start Click capture server ───
echo "4️⃣  Starting Click capture server (port 8766)..."
nohup python3 click_server.py > click_server.log 2>&1 &
CLICK_PID=$!
echo "   ✅ Click server: PID $CLICK_PID"

# ─── 5. Start Rep PWA server ───
if [ -d "rep_pwa" ]; then
    echo "5️⃣  Starting Rep PWA server (port 8503)..."
    cd rep_pwa
    nohup python3 -m http.server 8503 > ../rep_pwa.log 2>&1 &
    PWA_PID=$!
    cd ..
    echo "   ✅ PWA server: PID $PWA_PID"
else
    echo "5️⃣  ⚠️  rep_pwa folder not found, skipping"
fi

sleep 3

# ─── Verify all services ───
echo ""
echo "═══════════════════════════════════════════════"
echo "   SERVICE STATUS"
echo "═══════════════════════════════════════════════"

if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
    echo "✅ Streamlit:      http://localhost:8501"
else
    echo "❌ Streamlit:      FAILED — check streamlit.log"
fi

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Telegram Bot:   Running"
else
    echo "❌ Telegram Bot:   FAILED — check bot.log"
fi

if ps -p $REP_PID > /dev/null 2>&1; then
    echo "✅ Rep Server:     http://localhost:8502"
else
    echo "❌ Rep Server:     FAILED — check rep_server.log"
fi

if ps -p $CLICK_PID > /dev/null 2>&1; then
    echo "✅ Click Server:   http://localhost:8766"
else
    echo "❌ Click Server:   FAILED — check click_server.log"
fi

echo ""
echo "📱 Rep PWA:       http://$(hostname -I | awk '{print $1}'):8503"
echo ""
echo "═══════════════════════════════════════════════"
echo "   All services launched!"
echo "   To stop: ./stop_all.sh"
echo "═══════════════════════════════════════════════"
