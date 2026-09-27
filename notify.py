import os, smtplib, requests
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_notification(channel, chat_id_or_phone, message, subject="PharmaMind Alert"):
    if not chat_id_or_phone:
        print(f"[SKIP] No recipient for {channel}")
        return False, "No recipient"

    if channel == "console":
        print(f"\n{'='*60}\n📱 TO: {chat_id_or_phone}\n{'='*60}\n{message}\n{'='*60}\n")
        return True, "Console"

    elif channel == "telegram":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            print(f"[TELEGRAM SKIPPED] No TELEGRAM_BOT_TOKEN in .env")
            return False, "No bot token"
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            r = requests.post(url, json={"chat_id": chat_id_or_phone, "text": message, "parse_mode": "HTML"}, timeout=10)
            if r.status_code != 200:
                print(f"[TELEGRAM ERROR] {r.text}")
            return r.status_code == 200, r.text
        except Exception as e:
            print(f"[TELEGRAM EXCEPTION] {e}")
            return False, str(e)

    elif channel == "email":
        sender = os.getenv("EMAIL_SENDER", "")
        password = os.getenv("EMAIL_PASSWORD", "")
        if not sender: return False, "No email config"
        try:
            msg = MIMEText(message, "html")
            msg["Subject"] = subject; msg["From"] = sender; msg["To"] = chat_id_or_phone
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(sender, password); s.send_message(msg)
            return True, "Email sent"
        except Exception as e:
            return False, str(e)

    return False, f"Unknown channel: {channel}"

def get_active_channel():
    return os.getenv("NOTIFY_CHANNEL", "console")

def format_order_sms(order, retailer, include_balance=True, for_owner=False):
    items_text = "\n".join([f"  • {i['medicine']}: {i['qty']} units" for i in order["items"]])
    header = "🚨 <b>NEW ORDER PLACED</b>" if for_owner else "✅ <b>ORDER CONFIRMED</b>"
    msg = f"""{header}

<b>Order ID:</b> {order['order_id']}
<b>Retailer:</b> {retailer['id']} - {retailer['shop']}
<b>Time:</b> {order['placed_at']}
<b>Location:</b> {order.get('location', 'Not specified')}

<b>Items:</b>
{items_text}

<b>Total:</b> ₹{order['total']:,.2f}"""
    if include_balance:
        msg += f"\n\n<b>Outstanding:</b> ₹{retailer['outstanding']:,.2f}"
    return msg

def format_otp_sms(order, otp):
    return f"""🔐 <b>PharmaMind OTP</b>

Order <b>{order['order_id']}</b>
Total: ₹{order['total']:,.2f}

<b>Your OTP: {otp}</b>

Valid 10 min. Do not share."""
