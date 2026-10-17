"""backup_agent.py — Nightly backup to Telegram. Complete file list."""
import os, json, zipfile, tempfile
from datetime import datetime
from pathlib import Path

# Complete list of business-critical files
BACKUP_FILES = [
    # Core business
    "retailers.json", "owner.json", "company.json", "companies.json",
    "orders.json", "users.json", "returns.json",
    # Financial
    "accounting.db", "product_prices.json", "discount_rules.json",
    "promotions.json", "flash_offers.json",
    # Activity & audit
    "activity.json", "activity_index.json",
    "audit_pro.jsonl", "audit_chain.json",
    "staff_activity_log.jsonl",
    "audit_archive_20260926_182152.jsonl",
    "audit_pro_archive_20260927_184905.jsonl",
    # Business intel
    "pharma_intel_cache.json", "pharma_intel_db.json", "pharma_intel_seen.json",
    "journal.json", "breaks.json",
    # Inventory
    "inventory.csv", "inventory.db",
    # Bot state
    "bot_memory.json", "bot_order_sessions.json", "bot_otps.json",
]

def create_backup_zip():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = tempfile.mktemp(suffix=f"_backup_{ts}.zip")
    included = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in BACKUP_FILES:
            p = Path(fname)
            if p.exists():
                zf.write(p, fname)
                included += 1
    return zip_path, included

def send_backup_to_telegram():
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token: return {"ok": False, "msg": "No bot token"}
        owner = json.load(open("owner.json"))
        chat_id = owner.get("telegram_chat_id", "").strip()
        if not chat_id: return {"ok": False, "msg": "No owner chat_id"}

        zip_path, included = create_backup_zip()
        size_mb = os.path.getsize(zip_path) / 1024 / 1024
        if size_mb > 50: return {"ok": False, "msg": f"Too large: {size_mb:.1f} MB"}

        date_str = datetime.now().strftime("%d-%b-%Y %H:%M")
        caption = f"💾 *Meena Agencies Backup*\n\nDate: {date_str}\nFiles: {included}\nSize: {size_mb:.2f} MB"

        with open(zip_path, "rb") as f:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendDocument",
                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                files={"document": f}, timeout=60)
        os.unlink(zip_path)
        if r.status_code == 200:
            return {"ok": True, "msg": f"Backup sent ({included} files, {size_mb:.2f} MB)"}
        return {"ok": False, "msg": f"Telegram error: {r.text[:150]}"}
    except Exception as e:
        return {"ok": False, "msg": str(e)}

if __name__ == "__main__":
    result = send_backup_to_telegram()
    print(f"{'✅' if result['ok'] else '❌'} {result['msg']}")
