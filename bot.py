import telebot
from telebot import types
import sqlite3
import os
from datetime import datetime

from pathlib import Path

# Read token from .streamlit/secrets.toml — never hardcoded
_secrets_file = Path(__file__).parent / ".streamlit" / "secrets.toml"
BOT_TOKEN = ""
if _secrets_file.exists():
    for _line in _secrets_file.read_text().splitlines():
        if _line.strip().startswith("TELEGRAM_BOT_TOKEN"):
            BOT_TOKEN = _line.split("=", 1)[1].strip().strip('"').strip("'")
            break

OWNER_CHAT_ID = "8666850647"  # your Telegram user ID from @userinfobot
DB_PATH = "meena_enterprise.db"

bot = telebot.TeleBot(BOT_TOKEN)
user_carts = {}

def get_products(limit=10):
    if not os.path.exists(DB_PATH): return []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sku, qty FROM products LIMIT ?", (limit,))
    products = c.fetchall()
    conn.close()
    return products

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_catalog = types.KeyboardButton("🛒 Browse Catalog")
    btn_cart = types.KeyboardButton("🛍️ My Cart")
    btn_loc = types.KeyboardButton("📍 Share Location")
    markup.add(btn_catalog, btn_cart, btn_loc)
    
    web_app = types.WebAppInfo(url="https://international-effects-clan-herbs.trycloudflare.com")
    inline_markup = types.InlineKeyboardMarkup()
    btn_open_app = types.InlineKeyboardButton("📱 Open Store App (One-Click)", web_app=web_app)
    inline_markup.add(btn_open_app)
    
    welcome_text = (
        f"Vanakkam, {message.from_user.first_name}! 🙏\n"
        "Welcome to *Meena Agencies*.\n\n"
        "Tap the button below to open the full store app, or use the menu at the bottom."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)
    bot.send_message(message.chat.id, "👇 Click here to launch:", reply_markup=inline_markup)

@bot.message_handler(func=lambda message: message.text == "🛒 Browse Catalog")
def show_catalog(message):
    products = get_products()
    if not products:
        bot.send_message(message.chat.id, "Inventory is currently empty.")
        return
    bot.send_message(message.chat.id, "📦 *Available Medicines:*", parse_mode='Markdown')
    for sku, qty in products:
        markup = types.InlineKeyboardMarkup()
        btn_add = types.InlineKeyboardButton("➕ Add to Cart", callback_data=f"add_{sku}")
        markup.add(btn_add)
        text = f"💊 *{sku}*\nIn Stock: {qty} units\nPrice: ₹150.00"
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart(call):
    sku = call.data.replace('add_', '')
    user_id = call.from_user.id
    if user_id not in user_carts:
        user_carts[user_id] = []
    user_carts[user_id].append(sku)
    bot.answer_callback_query(call.id, f"✅ {sku} added to cart!")

@bot.message_handler(func=lambda message: message.text == "🛍️ My Cart")
def view_cart(message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        bot.send_message(message.chat.id, "Your cart is empty.")
        return
    total = len(cart) * 150.0
    text = "🛍️ *Your Cart:*\n\n"
    for item in cart:
        text += f"- {item}\n"
    text += f"\n*Total:* ₹{total:.2f}"
    markup = types.InlineKeyboardMarkup()
    btn_checkout = types.InlineKeyboardButton("💳 Pay & Checkout", callback_data="checkout")
    markup.add(btn_checkout)
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "checkout")
def checkout(call):
    user_id = call.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        bot.answer_callback_query(call.id, "Cart is empty.")
        return
    total = len(cart) * 150.0
    order_id = f"ORD-{int(datetime.now().timestamp())}"
    user_carts[user_id] = []
    bot.send_message(call.message.chat.id, f"✅ *Order Confirmed!*\nOrder ID: {order_id}\nTotal Paid: ₹{total:.2f}\n\nYour medicines will be packed shortly.", parse_mode='Markdown')
    owner_text = f"🔔 *NEW ORDER RECEIVED!*\n\nFrom: {call.from_user.first_name}\nOrder ID: {order_id}\nTotal: ₹{total:.2f}"
    bot.send_message(OWNER_CHAT_ID, owner_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📍 Share Location")
def request_location(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📍 Send Live Location", request_location=True)
    markup.add(btn)
    bot.send_message(message.chat.id, "Please share your location for tracking:", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    name = message.from_user.first_name
    lat = message.location.latitude
    lon = message.location.longitude
    bot.send_message(message.chat.id, f"✅ Location received!\nOwner has been notified.")
    owner_msg = f"📍 *LIVE LOCATION UPDATE*\n\nRep: {name}\nTime: {datetime.now().strftime('%I:%M:%S %p')}\n[View on Google Maps](https://www.google.com/maps?q={lat},{lon})"
    bot.send_message(OWNER_CHAT_ID, owner_msg, parse_mode='Markdown', disable_web_page_preview=False)

print("🚀 Bot is starting...")
bot.infinity_polling()
