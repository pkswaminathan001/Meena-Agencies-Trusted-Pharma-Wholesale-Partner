from pathlib import Path

print("=" * 60)
print("  Paste your tokens below. Press Enter after each.")
print("  Do NOT include < > or quotes. Just the raw token.")
print("=" * 60)
print()

tg = input("Telegram bot token: ").strip().strip('"').strip("'")
groq = input("Groq API key: ").strip().strip('"').strip("'")

# Auto-strip any angle brackets that sneak in
tg = tg.strip('<>').strip()
groq = groq.strip('<>').strip()

# Sanity check
print()
if ":" not in tg:
    print(f"⚠️  Telegram token has no colon. Length: {len(tg)}")
else:
    print(f"✅ Telegram token: {len(tg)} chars, has colon")
if not groq.startswith("gsk_"):
    print(f"⚠️  Groq key doesn't start with gsk_. Starts with: {groq[:8]}")
else:
    print(f"✅ Groq key: {len(groq)} chars, starts with gsk_")

# Write .env
Path(".env").write_text(
    f"NOTIFY_CHANNEL=telegram\n"
    f"TELEGRAM_BOT_TOKEN={tg}\n"
    f"GROQ_API_KEY={groq}\n"
)
print()
print("✅ .env saved. Now run the verify script.")
