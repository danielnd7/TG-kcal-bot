from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from os import getenv
from dotenv import load_dotenv
from handlers import register_all_handlers


# Load variables from .env file
load_dotenv()

# Access the token securely
TOKEN = getenv("TELEGRAM_BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"Received msg from {update.effective_user.id}: {text}")  # <-- this prints the message in your console
    await update.message.reply_text(f"You said: {text}")



if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handler for /start
    #app.add_handler(CommandHandler("start", start))
    register_all_handlers(app)

    # Message handler for any text message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot with long polling
    app.run_polling()