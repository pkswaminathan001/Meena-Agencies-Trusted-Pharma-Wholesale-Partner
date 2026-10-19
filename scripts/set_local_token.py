"""Set Telegram bot token in .streamlit/secrets.toml with validation.
Usage: ../.venv/bin/python scripts/set_local_token.py
"""
import getpass
import re
import sys
from pathlib import Path

print("Paste the Telegram bot token below (input hidden).")
print("Format: <8-10 digits>:<35 chars>, total 44-46 chars.")
print("If you see 'INVALID len=0', your clipboard was empty.")
print("If you see 'INVALID len=70', you pasted a command, not the token.")
print()
tok = getpass.getpass("Token: ").strip()

if not tok:
    print("❌ Empty — nothing pasted. Copy the token to your clipboard, then run again.")
    sys.exit(1)

if not re.fullmatch(r'\d{8,10}:[A-Za-z0-9_-]{35}', tok):
    print(f"❌ INVALID — len={len(tok)}, first 6 chars={tok[:6]!r}")
    print("   Not a Telegram bot token. Copy the token VALUE from")
    print("   Streamlit Cloud → Settings → Secrets → TELEGRAM_BOT_TOKEN.")
    sys.exit(1)

p = Path(".streamlit/secrets.toml")
p.parent.mkdir(exist_ok=True)
p.write_text(f'[general]\nenvironment = "local"\n\nTELEGRAM_BOT_TOKEN = "{tok}"\n')
p.chmod(0o600)
print(f"✅ wrote .streamlit/secrets.toml with valid token (len={len(tok)})")

import tomllib
d = tomllib.loads(p.read_text())
v = d.get("TELEGRAM_BOT_TOKEN", "")
assert re.fullmatch(r'\d{8,10}:[A-Za-z0-9_-]{35}', v), "re-read failed"
print(f"✅ re-verified from disk (len={len(v)})")

gitignore = Path(".gitignore")
if gitignore.exists() and ".streamlit/secrets.toml" in gitignore.read_text():
    print("✅ file is gitignored")
else:
    print("🚨 NOT gitignored — run: echo '.streamlit/secrets.toml' >> .gitignore")
