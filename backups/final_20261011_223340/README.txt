Meena Agencies — Full Application Backup
=========================================

Backup Date: Sun Oct 11 10:33:40 PM IST 2026
Source: /home/swaminathan/Desktop/swami/AGI Pharma Application/pharma-agi
Running App: http://localhost:8501

To restore this backup:
-----------------------------------------------
cd "/home/swaminathan/Desktop/swami/AGI Pharma Application/pharma-agi"
cp "backups/final_20261011_223340/meena.py" apps_isolated/meena.py
cp "backups/final_20261011_223340"/block*.py apps_isolated/ 2>/dev/null
cp "backups/final_20261011_223340"/security_layer.py apps_isolated/ 2>/dev/null
cp "backups/final_20261011_223340"/*.json . 2>/dev/null
cp "backups/final_20261011_223340"/*.csv . 2>/dev/null

pkill -9 -f streamlit
sleep 3
nohup ../.venv/bin/streamlit run apps_isolated/meena.py \
    --server.port=8501 --server.headless=true \
    > apps_isolated/logs/meena.log 2>&1 &
sleep 7
curl -s http://localhost:8501/_stcore/health
-----------------------------------------------

Login credentials:
  Owner password:  owner2026
  Retailer RET001: 3210
  Retailer RET002: 5678
  Retailer RET003: 9999

Restore point: meena.py.bak_uiv2_215931 (clean version, 139 KB)
