"""
bot_memory.py — Conversation memory for the Meena chatbot.
Stores last 10 messages per chat so the bot can follow up naturally.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


MEMORY_FILE = Path("bot_memory.json")
MAX_HISTORY = 10
RETAIN_DAYS = 30


def _load():
    if not MEMORY_FILE.exists():
        return {}
    try:
        return json.loads(MEMORY_FILE.read_text())
    except Exception:
        return {}


def _save(data):
    try:
        MEMORY_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def _cleanup(data):
    """Remove old conversations."""
    cutoff = (datetime.now() - timedelta(days=RETAIN_DAYS)).isoformat()
    cleaned = {}
    for chat_id, history in data.items():
        recent = [h for h in history if h.get("ts", "") > cutoff]
        if recent:
            cleaned[chat_id] = recent[-MAX_HISTORY:]
    return cleaned


def add(chat_id: str, user_msg: str, bot_reply: str):
    """Save one exchange (user + bot) to memory."""
    data = _load()
    data = _cleanup(data)
    key = str(chat_id)
    if key not in data:
        data[key] = []
    data[key].append({
        "ts": datetime.now().isoformat(),
        "user": user_msg[:500],   # cap length
        "bot": bot_reply[:1000],
    })
    # Keep last MAX_HISTORY exchanges
    if len(data[key]) > MAX_HISTORY:
        data[key] = data[key][-MAX_HISTORY:]
    _save(data)


def get(chat_id: str) -> list:
    """Return last N exchanges for this chat."""
    data = _load()
    return data.get(str(chat_id), [])


def clear(chat_id: str):
    """Clear memory for one chat."""
    data = _load()
    if str(chat_id) in data:
        del data[str(chat_id)]
        _save(data)


def last_user_message(chat_id: str) -> str:
    """Return the most recent user message."""
    history = get(chat_id)
    return history[-1]["user"] if history else ""


def stats():
    """Return count of chats with memory."""
    data = _load()
    return {
        "chats": len(data),
        "total_messages": sum(len(v) for v in data.values()),
    }


if __name__ == "__main__":
    print("=== bot_memory.py self-test ===")
    # Test add + get
    test_chat = "TEST_CHAT_001"
    clear(test_chat)
    add(test_chat, "hi", "Hi! How can I help?")
    add(test_chat, "any late payments?", "3 retailers owe you money...")
    add(test_chat, "send them reminders", "✅ Sent to 3 retailers.")
    history = get(test_chat)
    print(f"Saved {len(history)} exchanges")
    for h in history:
        print(f"  User: {h['user'][:40]}")
        print(f"  Bot:  {h['bot'][:40]}")
    print()
    print("Stats:", stats())
    clear(test_chat)
    print("Memory cleared.")
