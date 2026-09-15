from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from os import getenv
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Access the token securely
TOKEN = getenv("TELEGRAM_BOT_TOKEN")

# async def defines a coroutine.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me anything, and I'll print it in the console.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print("Received message:", text)  # <-- this prints the message in your console
    await update.message.reply_text(f"You said: {text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handler for /start
    app.add_handler(CommandHandler("start", start))

    # Message handler for any text message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot with long polling
    app.run_polling()