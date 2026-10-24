import os
import re
import subprocess
from pathlib import Path
from dotenv import load_dotenv

print("🤖 MEENA AGENCIES BOT SETUP")
print("========================================")
token = input("Paste your NEW BotFather token here and press Enter: ").strip()

if not token or ":" not in token:
    print("❌ Invalid token format. Please try again.")
    exit()

# 1. Save to .env safely
env_path = Path(".env")
env_path.write_text(f"TELEGRAM_BOT_TOKEN={token}\n")
print("✅ Token saved to .env")

# 2. Update bot.py to ensure it loads .env
bot_path = Path("bot.py")
text = bot_path.read_text()

if "from dotenv import load_dotenv" not in text:
    text = "from dotenv import load_dotenv\nfrom pathlib import Path\nload_dotenv(Path(__file__).parent / '.env')\n" + text

# Replace any hardcoded BOT_TOKEN line
text = re.sub(r'BOT_TOKEN = .*', 'BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")', text)
bot_path.write_text(text)
print("✅ bot.py updated to load from .env")

# 3. Start the bot
print("🚀 Starting the bot...\n")
subprocess.run(["python3", "bot.py"])
