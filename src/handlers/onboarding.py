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

WAITING_CALORIES, WAITING_PROTEIN = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        await update.message.reply_text(
            "Welcome to your nutrition tracker! Let's set your targets. What is your daily calorie goal? (e.g., 2500)")

    # Required: tells PTB this conversation step is done for now
    return WAITING_CALORIES


async def process_calories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("Not an integer!")
        # Остаемся в том же состоянии, если ввод некорректен
        return WAITING_CALORIES

    # Записываем значение во временный контекст пользователя
    context.user_data["calorie_goal"] = int(text)

    await update.message.reply_text("Perfect! Now please entr the protein goal:")
    # Переходим к следующему состоянию
    return WAITING_PROTEIN



async def process_protein(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("Not an integer!")
        return WAITING_PROTEIN

    context.user_data["protein_goal"] = int(text)

    print("Goal set: \nCalories: ", context.user_data["calorie_goal"], "\nProtein: ", context.user_data["protein_goal"])
    print("storing to the database......")



    await update.message.reply_text(
        f"Profile saved\nGoals: {context.user_data["calorie_goal"]} calories, {context.user_data["protein_goal"]}g protein."
    )
    # Завершаем сценарий — бот выходит из режима ожидания
    return ConversationHandler.END


def get_onboarding_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_CALORIES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_calories)
            ],
            WAITING_PROTEIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_protein)
            ]
        },
        fallbacks=[],
    )