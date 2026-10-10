"""bot_ask.py — /ask command for Telegram. Wires ask_engine into bot.py."""
from datetime import datetime

try:
    from ask_engine import ask
    ASK_OK = True
except Exception as e:
    ASK_OK = False
    ASK_ERR = str(e)


def handle_ask(question: str) -> str:
    """Process a /ask question and return formatted reply."""
    if not ASK_OK:
        return f"❌ Ask engine not available: {ASK_ERR}"

    if not question or not question.strip():
        return (
            "📝 *How to use /ask*\n\n"
            "Type a question after the command:\n\n"
            "Examples:\n"
            "• `/ask how many orders do we have`\n"
            "• `/ask top 3 retailers by outstanding`\n"
            "• `/ask which orders are pending`\n"
            "• `/ask which retailer owes the most`\n"
            "• `/ask stock expiring in 30 days`\n"
        )

    question = question.strip()

    try:
        result = ask(question)
    except Exception as e:
        return f"❌ Error: {e}"

    if not result.get("ok"):
        err = result.get("error", "Unknown error")
        return f"❌ {err}\n\nTry rephrasing the question."

    answer = result.get("answer", "")
    return answer


# ═══════════════════════════════════════════════════════════
# DROP-IN HANDLER for bot.py
# ═══════════════════════════════════════════════════════════
def register_ask_handler(bot_app):
    """
    Register /ask on an existing Telegram bot.
    Usage in bot.py:
        from bot_ask import register_ask_handler
        register_ask_handler(app)   # where app is your Application / bot
    """
    try:
        from telegram import Update
        from telegram.ext import CommandHandler, ContextTypes
    except ImportError:
        return False

    async def ask_command(update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        # Get the question text after "/ask "
        msg = update.message
        if not msg:
            return
        text = msg.text or ""
        # Strip "/ask" prefix
        parts = text.split(maxsplit=1)
        question = parts[1] if len(parts) > 1 else ""

        # Send "thinking..." message
        thinking = await msg.reply_text("🤔 Thinking...")

        reply = handle_ask(question)

        # Send answer (Markdown)
        try:
            await thinking.edit_text(reply, parse_mode="Markdown")
        except Exception:
            await thinking.edit_text(reply)

    bot_app.add_handler(CommandHandler("ask", ask_command))
    return True


# ═══════════════════════════════════════════════════════════
# Sync wrapper (for bots that use non-async handlers)
# ═══════════════════════════════════════════════════════════
def handle_ask_sync(update, context):
    """Sync version — if your bot uses synchronous handlers."""
    msg = update.message
    if not msg:
        return
    text = msg.text or ""
    parts = text.split(maxsplit=1)
    question = parts[1] if len(parts) > 1 else ""
    thinking = msg.reply_text("🤔 Thinking...")
    reply = handle_ask(question)
    try:
        thinking.edit_text(reply, parse_mode="Markdown")
    except Exception:
        thinking.edit_text(reply)
