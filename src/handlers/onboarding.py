# src/handlers/onboarding.py
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
import db

# async def defines a coroutine.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    print("/start from user-id:  ", user_id); #log

    # getting the user by id
    existing_user = db.get_user(user_id)

    # user alreasy exists
    if existing_user:
        await update.message.reply_text(
            "Welcome back! Let's set your targets. What is your daily calorie goal? (e.g., 2500)")

    # new user
    else:
        db.create_user(user_id)
        await update.message.reply_text("Welcome to your nutrition tracker! Let's set your targets. What is your daily calorie goal? (e.g., 2500)")

    # Required: tells PTB this conversation step is done for now
    return ConversationHandler.END


def get_onboarding_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={},
        fallbacks=[],
    )