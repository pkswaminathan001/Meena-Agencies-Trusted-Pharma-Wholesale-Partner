#!/bin/bash
cd "/home/swaminathan/Desktop/swami/AGI Pharma Application/pharma-agi"

# Activate venv
if [ -f "$HOME/venvs/pharma/bin/activate" ]; then
    source "$HOME/venvs/pharma/bin/activate"
else
    echo "⚠️  Venv not found at ~/venvs/pharma"
    echo "   Run: python3 -m virtualenv ~/venvs/pharma"
fi

# Start click server if not running
if ! pgrep -f click_server.py > /dev/null; then
    nohup python3 click_server.py > click_server.log 2>&1 &
    echo "✅ Click server started"
fi

# Start Streamlit with fast settings
echo "🚀 Starting PharmaMind..."
streamlit run app.py \
    --server.fileWatcherType=none \
    --server.runOnSave=false
