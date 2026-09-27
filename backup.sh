#!/bin/bash
# Auto-backup PharmaMind data every run
cd "/home/swaminathan/Desktop/swami/AGI Pharma Application/pharma-agi"

BACKUP_DIR="$HOME/PharmaBackups"
mkdir -p "$BACKUP_DIR"

# Timestamp
TS=$(date +"%Y%m%d_%H%M%S")

# Zip important files
tar -czf "$BACKUP_DIR/pharma_backup_$TS.tar.gz" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='*.bak' \
    --exclude='audit_archive_*' \
    *.json *.jsonl *.csv *.db *.py .env 2>/dev/null

# Keep only last 30 backups
cd "$BACKUP_DIR"
ls -t pharma_backup_*.tar.gz 2>/dev/null | tail -n +31 | xargs -r rm

# Report
COUNT=$(ls pharma_backup_*.tar.gz 2>/dev/null | wc -l)
LATEST=$(ls -t pharma_backup_*.tar.gz 2>/dev/null | head -1)
SIZE=$(du -h "$LATEST" 2>/dev/null | cut -f1)
echo "✅ Backup: $LATEST ($SIZE)"
echo "   Total backups kept: $COUNT"
echo "   Location: $BACKUP_DIR"
