"""
staff_messages.py — Staff → Owner messaging.
Staff sends message → Owner reads later → Owner replies.
"""
import json
from datetime import datetime
from pathlib import Path

MSG_FILE = Path("staff_messages.json")


def _load() -> list:
    if not MSG_FILE.exists():
        return []
    try:
        return json.loads(MSG_FILE.read_text())
    except Exception:
        return []


def _save(data: list):
    MSG_FILE.write_text(json.dumps(data, indent=2))


def send_message(staff_id: str, staff_name: str, subject: str, body: str,
                 priority: str = "normal"):
    """Staff sends message to owner."""
    msgs = _load()
    msg = {
        "id": f"MSG{int(datetime.now().timestamp())}",
        "from_id": staff_id,
        "from_name": staff_name,
        "subject": subject,
        "body": body,
        "priority": priority,  # normal | urgent
        "sent_at": datetime.now().strftime("%d-%b-%Y %H:%M"),
        "read": False,
        "replied": False,
        "reply": "",
        "replied_at": "",
    }
    msgs.append(msg)
    _save(msgs)

    # Also notify owner via Telegram
    try:
        import notify_pro
        env = Path(".env").read_text() if Path(".env").exists() else ""
        owner_chat = ""
        for line in env.splitlines():
            if line.startswith("OWNER_CHAT_ID="):
                owner_chat = line.split("=", 1)[1].strip()
                break
        if owner_chat:
            icon = "🚨" if priority == "urgent" else "💬"
            notify_pro.send_telegram(
                owner_chat,
                f"{icon} <b>Message from {staff_name}</b>\n\n"
                f"<b>{subject}</b>\n{body}\n\n"
                f"<i>Read in app → Staff Messages</i>"
            )
    except Exception:
        pass

    return msg["id"]


def get_unread_for_owner() -> list:
    return [m for m in _load() if not m.get("read")]


def get_all_for_owner() -> list:
    return list(reversed(_load()))


def get_sent_by_staff(staff_id: str) -> list:
    """Staff sees messages THEY sent + owner replies."""
    return [m for m in _load() if m.get("from_id") == staff_id]


def mark_read(msg_id: str):
    msgs = _load()
    for m in msgs:
        if m["id"] == msg_id:
            m["read"] = True
            break
    _save(msgs)


def reply(msg_id: str, reply_text: str):
    msgs = _load()
    for m in msgs:
        if m["id"] == msg_id:
            m["reply"] = reply_text
            m["replied"] = True
            m["replied_at"] = datetime.now().strftime("%d-%b-%Y %H:%M")
            m["read"] = True
            break
    _save(msgs)
