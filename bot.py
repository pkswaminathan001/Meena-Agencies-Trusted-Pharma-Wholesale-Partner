"""
bot.py v3 — Meena Agencies Telegram bot with AI triage + owner approval.
Every retailer message → classified → owner gets card with [Approve] [Reply] [Deny].
"""
import os, json, time, logging, requests
from pathlib import Path
from middleware import resolve_identity, audit, filter_orders_for
import intent_router
import promotions

RETAILERS_FILE = Path("retailers.json")
ORDERS_FILE    = Path("orders.json")
SERVICE_LOG    = Path("service_log.json")
PENDING_FILE   = Path("pending_replies.json")
POLL_INTERVAL  = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")


def env(key, default=""):
    for line in Path(".env").read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    return default


TOKEN = env("TELEGRAM_BOT_TOKEN")
OWNER = int(env("OWNER_CHAT_ID", "0") or 0)
API   = f"https://api.telegram.org/bot{TOKEN}"
LAST_UPDATE = 0


# ─── helpers ───────────────────────────────────────────────
def send(chat_id, text, buttons=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    try:
        requests.post(f"{API}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        logging.error(f"send failed: {e}")


def answer_callback(cb_id, text="OK"):
    try:
        requests.post(f"{API}/answerCallbackQuery",
                      json={"callback_query_id": cb_id, "text": text}, timeout=10)
    except Exception as e:
        logging.error(f"answer cb failed: {e}")


def _load(p):
    try: return json.loads(p.read_text())
    except: return []


def _save(p, d):
    p.write_text(json.dumps(d, indent=2))


# ═══════════════════════════════════════════════════════════
# Retailer onboarding (unchanged)
# ═══════════════════════════════════════════════════════════
def handle_start(chat_id, args):
    ident = resolve_identity(chat_id)

    if ident["role"] == "owner":
        send(chat_id, (
            "👋 <b>Welcome, Owner</b>\n\n"
            "Commands:\n"
            "/whoami /help /pending /service\n\n"
            "To onboard a retailer, share this link:\n"
            "<code>t.me/Swaminathan_Inc_bot?start=RET001</code>"
        ))
        return

    if args and ident["role"] != "retailer":
        code = args.strip().upper()
        data = _load(RETAILERS_FILE)
        match = next((r for r in data if r["id"] == code), None)
        if not match:
            send(chat_id, f"❌ Code <b>{code}</b> not found.")
            return
        existing = str(match.get("telegram_chat_id", "")).strip()
        if existing and existing != str(chat_id):
            send(chat_id, "⚠️ Already linked to another phone.")
            return
        match["telegram_chat_id"] = str(chat_id)
        match["onboarded_at"] = time.strftime("%d-%b-%Y %H:%M").upper()
        _save(RETAILERS_FILE, data)
        audit(chat_id, "ONBOARD", f"retailer={code}")
        send(chat_id, (
            f"✅ <b>Welcome, {match.get('shop','')}!</b>\n\n"
            f"Owner: {match.get('owner','')}\n"
            f"ID: <code>{code}</code>\n\n"
            f"Send /help for commands."
        ))
        return

    if ident["role"] == "retailer":
        r = ident["retailer"]
        send(chat_id, f"👋 <b>Hi {r.get('owner','')}</b>\n\nShop: {r.get('shop','')}\nSend /help.")
        return

    send(chat_id, "👋 Welcome to Meena Agencies.\nPlease register with the link from our team.")


def handle_whoami(chat_id):
    ident = resolve_identity(chat_id)
    if ident["role"] == "owner":
        send(chat_id, f"🧑‍💼 <b>OWNER</b>\nchat_id: <code>{chat_id}</code>")
    elif ident["role"] == "retailer":
        r = ident["retailer"]
        send(chat_id, f"🏪 <b>{r['shop']}</b>\nOwner: {r.get('owner','')}\nID: <code>{r['id']}</code>")
    else:
        send(chat_id, f"❓ Not registered. chat_id: <code>{chat_id}</code>")


def handle_help(chat_id):
    ident = resolve_identity(chat_id)
    if ident["role"] == "owner":
        send(chat_id, (
            "<b>Owner Commands</b>\n"
            "/whoami /help\n"
            "/pending — open retailer messages\n"
            "/service — last 10 retailer messages\n"
            "\n"
            "Every retailer message arrives here with\n"
            "[Approve] [Reply] [Deny] buttons."
        ))
    elif ident["role"] == "retailer":
        send(chat_id, (
            "<b>Your Commands</b>\n"
            "/whoami /myorders /myprofile\n"
            "/help\n\n"
            "💬 Send any message — we reply personally."
        ))
    else:
        send(chat_id, "Please register first. Contact 7338824033.")


def handle_myorders(chat_id):
    ident = resolve_identity(chat_id)
    if ident["role"] != "retailer":
        send(chat_id, "Retailer-only command."); return
    orders = _load(ORDERS_FILE)
    mine = filter_orders_for(chat_id, orders)
    if not mine:
        send(chat_id, "📦 No orders yet."); return
    recent = sorted(mine, key=lambda o: o.get("placed_at",""), reverse=True)[:5]
    lines = ["<b>📦 Your recent orders</b>\n"]
    for o in recent:
        lines.append(f"• <code>{o['order_id']}</code>\n  ₹{o.get('total',0):,.2f} · <b>{o.get('status','?')}</b>\n  {o.get('placed_at','')}\n")
    send(chat_id, "\n".join(lines))


def handle_myprofile(chat_id):
    ident = resolve_identity(chat_id)
    if ident["role"] != "retailer":
        send(chat_id, "Retailer-only command."); return
    r = ident["retailer"]
    send(chat_id, (
        f"🏪 <b>{r['shop']}</b>\n"
        f"Owner: {r.get('owner','')}\n"
        f"Phone: {r.get('phone','—')}\n"
        f"Credit limit: ₹{r.get('credit_limit',0):,.0f}\n"
        f"Outstanding: ₹{r.get('outstanding',0):,.0f}"
    ))


# ═══════════════════════════════════════════════════════════
# RETAILER MESSAGE → INTENT → OWNER CARD
# ═══════════════════════════════════════════════════════════
def relay_to_owner(chat_id, retailer, text):
    """Classify + create pending card for owner."""
    result = intent_router.classify(text)
    intent = result["intent"]
    conf   = result["confidence"]
    source = result["source"]

    pending = _load(PENDING_FILE)
    ticket_id = f"T{int(time.time())}"
    ticket = {
        "ticket_id": ticket_id,
        "chat_id": str(chat_id),
        "retailer_id": retailer["id"],
        "shop": retailer["shop"],
        "owner_name": retailer.get("owner", ""),
        "message": text,
        "intent": intent,
        "confidence": conf,
        "source": source,
        "created_at": time.strftime("%d-%b-%Y %H:%M").upper(),
        "status": "PENDING",
    }
    pending.append(ticket)
    _save(PENDING_FILE, pending)

    # Log
    slog = _load(SERVICE_LOG)
    slog.append(ticket)
    _save(SERVICE_LOG, slog)

    # Auto-reply to retailer
    auto = intent_router.AUTO_REPLIES.get(intent, intent_router.AUTO_REPLIES["chitchat"])
    send(chat_id, auto)

    # Card to owner
    icon = {"order_request":"🛒","complaint":"⚠️","question":"❓","payment":"💳","chitchat":"💬"}.get(intent, "📨")
    card = (
        f"{icon} <b>New message · {retailer['id']}</b>\n"
        f"<b>{retailer['shop']}</b> · {retailer.get('owner','')}\n"
        f"─────────────────────────\n"
        f"“{text}”\n"
        f"─────────────────────────\n"
        f"Intent: <b>{intent}</b> ({source}, {conf:.2f})\n"
        f"Ticket: <code>{ticket_id}</code>"
    )
    buttons = [
        [
            {"text": "✅ Approve", "callback_data": f"ap:{ticket_id}"},
            {"text": "✍️ Reply",    "callback_data": f"rp:{ticket_id}"},
            {"text": "🚫 Deny",     "callback_data": f"dn:{ticket_id}"},
        ]
    ]
    send(OWNER, card, buttons)


# ═══════════════════════════════════════════════════════════
# OWNER BUTTON HANDLERS
# ═══════════════════════════════════════════════════════════
def handle_callback(update):
    cb = update.get("callback_query") or {}
    cb_id   = cb.get("id")
    from_id = cb.get("from", {}).get("id")
    data    = cb.get("data", "")
    logging.info(f"CALLBACK from={from_id} data={data}")

    if from_id != OWNER:
        logging.warning(f"CALLBACK_DENIED from={from_id} data={data}")
        answer_callback(cb_id, "Not allowed.")
        return

    if ":" not in data:
        answer_callback(cb_id, "Bad data")
        return

    # ─── Promotion callbacks ───
    if data.startswith("pm:"):
        parts = data.split(":")
        # pm:seg:all  |  pm:send:P123  |  pm:cancel:x
        action = parts[1]
        value  = ":".join(parts[2:]) if len(parts) > 2 else ""

        if action == "cancel":
            send(OWNER, "❌ Promotion cancelled.")
            answer_callback(cb_id, "Cancelled")
            return

        if action == "seg":
            state_p = Path("promote_state.json")
            state = _load(state_p)
            state["segment"] = value
            state["step"] = "awaiting_text"
            _save(state_p, state)
            send(OWNER, (
                f"✅ Segment: <b>{value}</b>\n\n"
                f"Now <b>type the offer text</b> (one line).\n"
                f"Example:\n"
                f"<i>Monsoon Health Drive — 12% off ORS, Zinc, Antibiotics</i>"
            ))
            answer_callback(cb_id, "Segment saved")
            return

        if action == "send":
            promos = promotions.list_promotions()
            promo = next((x for x in promos if x["id"] == value), None)
            if not promo:
                send(OWNER, "❌ Promo not found.")
                answer_callback(cb_id, "Not found")
                return
            send(OWNER, f"📤 Broadcasting <b>{promo['title']}</b>…")
            result = promotions.send_broadcast(value, send)
            send(OWNER, (
                f"✅ <b>Broadcast complete</b>\n\n"
                f"Sent: <b>{result['sent']}</b>\n"
                f"Skipped: {result['skipped']}\n"
                f"Failed: {result['failed']}"
            ))
            answer_callback(cb_id, "Sent")
            return

        answer_callback(cb_id, "Unknown action")
        return

    # ─── Service ticket callbacks ───
    action, ticket_id = data.split(":", 1)
    pending = _load(PENDING_FILE)
    ticket = next((t for t in pending if t["ticket_id"] == ticket_id), None)
    if not ticket:
        answer_callback(cb_id, "Ticket not found.")
        return

    if action == "ap":
        send(int(ticket["chat_id"]), "✅ Your message was reviewed. We'll confirm shortly.")
        ticket["status"] = "APPROVED"
        answer_callback(cb_id, "Approved")
    elif action == "dn":
        send(int(ticket["chat_id"]), "❌ Your message was reviewed. Owner will reply.")
        ticket["status"] = "DENIED"
        answer_callback(cb_id, "Denied")
    elif action == "rp":
        _save(PENDING_FILE, pending)
        state = _load(Path("owner_state.json"))
        state["awaiting_reply_for"] = ticket_id
        _save(Path("owner_state.json"), state)
        send(OWNER, f"✍️ Type your reply now for <b>{ticket['shop']}</b>.")
        answer_callback(cb_id, "Type reply")
        return

    _save(PENDING_FILE, pending)
    audit(from_id, f"TICKET_{action.upper()}", f"ticket={ticket_id}")


def handle_owner_reply(chat_id, text):
    """If owner is in reply mode, relay message and clear state."""
    state_p = Path("owner_state.json")
    state = _load(state_p)
    tid = state.get("awaiting_reply_for")
    if not tid:
        return False

    pending = _load(PENDING_FILE)
    ticket = next((t for t in pending if t["ticket_id"] == tid), None)
    if not ticket:
        state.pop("awaiting_reply_for", None)
        _save(state_p, state)
        return False

    # Send to retailer
    send(int(ticket["chat_id"]), f"💬 <b>From Meena Agencies</b>\n\n{text}")
    ticket["status"] = "REPLIED"
    ticket["owner_reply"] = text
    _save(PENDING_FILE, pending)

    state.pop("awaiting_reply_for", None)
    _save(state_p, state)

    send(OWNER, f"✅ Reply sent to <b>{ticket['shop']}</b>.")
    audit(chat_id, "OWNER_REPLY", f"ticket={tid}")
    return True


# ═══════════════════════════════════════════════════════════
# OWNER VIEWS
# ═══════════════════════════════════════════════════════════
def handle_pending(chat_id):
    pending = _load(PENDING_FILE)
    open_tickets = [t for t in pending if t["status"] == "PENDING"]
    if not open_tickets:
        send(chat_id, "✅ No pending tickets."); return
    lines = [f"<b>📥 {len(open_tickets)} pending</b>\n"]
    for t in open_tickets[-5:]:
        lines.append(
            f"• <code>{t['ticket_id']}</code> · <b>{t['intent']}</b>\n"
            f"  {t['shop']}: “{t['message'][:50]}”"
        )
    send(chat_id, "\n".join(lines))


def handle_service(chat_id):
    try:
        slog = _load(SERVICE_LOG)
    except Exception:
        slog = []
    if not isinstance(slog, list) or not slog:
        send(chat_id, "No messages yet."); return
    lines = ["<b>📋 Last 10 messages</b>\n"]
    count = 0
    for t in slog[-10:]:
        if not isinstance(t, dict):
            continue
        intent = t.get("intent", "?")
        shop = t.get("shop", "?")
        msg = str(t.get("message", ""))[:40]
        lines.append(f"• [{intent}] {shop}: “{msg}”")
        count += 1
    if count == 0:
        send(chat_id, "No valid messages."); return
    send(chat_id, "\n".join(lines))




# ═══════════════════════════════════════════════════════════
# /promote — owner creates & sends marketing broadcast
# ═══════════════════════════════════════════════════════════
def handle_promote(chat_id):
    """Interactive promote — step 1: choose segment."""
    buttons = [
        [{"text": "🆕 New", "callback_data": "pm:seg:new"},
         {"text": "🥈 Silver", "callback_data": "pm:seg:silver"}],
        [{"text": "🥇 Gold", "callback_data": "pm:seg:gold"},
         {"text": "💎 Platinum", "callback_data": "pm:seg:platinum"}],
        [{"text": "📢 All Retailers", "callback_data": "pm:seg:all"}],
        [{"text": "❌ Cancel", "callback_data": "pm:cancel:x"}],
    ]
    send(chat_id, "<b>📣 New Promotion</b>\n\nWhich segment?", buttons)


def handle_promote_callback(chat_id, action, value):
    """Called from handle_callback when data starts with pm:"""
    if action == "cancel":
        send(chat_id, "❌ Cancelled.")
        return

    if action == "seg":
        # Save chosen segment and ask for offer text
        state_p = Path("promote_state.json")
        state = _load(state_p)
        state["segment"] = value
        state["step"] = "awaiting_text"
        _save(state_p, state)
        send(chat_id, (
            f"Segment: <b>{value}</b>\n\n"
            f"Now send the <b>offer text</b> (one line).\n"
            f"Example: <i>Monsoon Health Drive — 12% off ORS, Zinc, Antibiotics</i>"
        ))
        return

    if action == "send":
        # value = promo id
        promos = promotions.list_promotions()
        promo = next((p for p in promos if p["id"] == value), None)
        if not promo:
            send(chat_id, "❌ Promo not found.")
            return
        send(chat_id, f"📤 Broadcasting <b>{promo['title']}</b>…")
        result = promotions.send_broadcast(value, send)
        send(chat_id, (
            f"✅ <b>Broadcast complete</b>\n\n"
            f"Sent: <b>{result['sent']}</b>\n"
            f"Skipped: {result['skipped']}\n"
            f"Failed: {result['failed']}"
        ))
        return


# ═══════════════════════════════════════════════════════════
# DISPATCH
# ═══════════════════════════════════════════════════════════
def handle_message(update):
    msg  = update.get("message") or update.get("edited_message") or {}
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = (msg.get("text") or "").strip()
    if not chat_id or not text: return
    if chat.get("type") != "private":
        logging.warning(f"GROUP_REFUSED {chat_id}"); return

    ident = resolve_identity(chat_id)

    # Owner commands first
    if ident["role"] == "owner":
        # Reply-mode intercept
        if not text.startswith("/") and handle_owner_reply(chat_id, text):
            return
        if   text.startswith("/start"):    handle_start(chat_id, text[6:].strip())
        elif text.startswith("/whoami"):   handle_whoami(chat_id)
        elif text.startswith("/help"):     handle_help(chat_id)
        elif text.startswith("/pending"):  handle_pending(chat_id)
        elif text.startswith("/service"):  handle_service(chat_id)
        elif text.startswith("/promote"):  handle_promote(chat_id)
        else:
            # Check if owner is in promote-step mode
            state_p = Path("promote_state.json")
            state = _load(state_p)
            if state.get("step") == "awaiting_text":
                segment = state.get("segment", "all")
                # Create promotion
                promo = promotions.create_promotion(
                    title=text[:60],
                    segment=segment,
                    offer_text=text,
                    badge_lines=["SPECIAL OFFER"],
                    valid_until="",
                    kind="daily",
                )
                state.pop("step", None)
                _save(state_p, state)
                btn = [
                    [{"text": "✅ Send to all", "callback_data": f"pm:send:{promo['id']}"}],
                    [{"text": "❌ Cancel", "callback_data": "pm:cancel:x"}],
                ]
                send(chat_id, (
                    f"<b>Preview</b>\n\n"
                    f"Segment: <b>{segment}</b>\n"
                    f"Offer: {text}\n"
                    f"ID: <code>{promo['id']}</code>\n\n"
                    f"Send now?"
                ), btn)
            else:
                send(chat_id, "Owner command received.")
        return

    # Retailer commands
    if ident["role"] == "retailer":
        if   text.startswith("/start"):     handle_start(chat_id, text[6:].strip())
        elif text.startswith("/whoami"):    handle_whoami(chat_id)
        elif text.startswith("/help"):      handle_help(chat_id)
        elif text.startswith("/myorders"):  handle_myorders(chat_id)
        elif text.startswith("/myprofile"): handle_myprofile(chat_id)
        else:
            # Any free text → triage + owner card
            relay_to_owner(chat_id, ident["retailer"], text)
        return

    # Unknown
    send(chat_id, "Please register first. Contact 7338824033.")


def main():
    global LAST_UPDATE
    print(f"🤖 Bot v3 polling · owner={OWNER}")
    print("   Ctrl+C to stop.\n")
    try: requests.get(f"{API}/deleteWebhook", timeout=5)
    except Exception: pass

    while True:
        try:
            r = requests.get(f"{API}/getUpdates",
                             params={"offset": LAST_UPDATE + 1, "timeout": 10},
                             timeout=15).json()
            for upd in r.get("result", []):
                LAST_UPDATE = upd["update_id"]
                try:
                    if "callback_query" in upd:
                        handle_callback(upd)
                    else:
                        handle_message(upd)
                except Exception as e:
                    logging.error(f"handler: {e}")
        except KeyboardInterrupt:
            print("\n👋 Stopped."); break
        except Exception as e:
            logging.error(f"poll: {e}"); time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
