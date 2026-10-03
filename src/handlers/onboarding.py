from telegram import Update
from services import user_service
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)


WELCOME_MESSAGE = """👋 Hello! Welcome to your new nutrition tracker. 🥗

I'm here to help you log your meals and stay on top of your macros without the hassle. 

To get started, we need to set up your baseline. 🎯
What is your daily calorie goal? (e.g., 2500)"""

PROTEIN_MESSAGE = """Perfect! 🔥 

Next up, what is your daily protein goal in grams? (e.g., 150)"""

FAT_MESSAGE = """Awesome! 🍗 

Now, what is your daily fat goal in grams? (e.g., 70)"""

CARBS_MESSAGE = """Almost done! 🥑 

Finally, what is your daily carb goal in grams? (e.g., 250)"""

SUCCESS_MESSAGE = """All set! 🎉 

Your daily targets are locked in. You are ready to start logging your meals! 🥗"""


WAITING_CALORIES, WAITING_PROTEIN, WAITING_FAT, WAITING_CARBS = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = user.id

    print("/start from user-id:  ", user_id); #log

    # getting the user by id
    existing_user = user_service.get_user(user_id)

    # user alreasy exists
    if existing_user:
        await update.message.reply_text(
            f"👋 Welcome back!\n\n"
            f"Here are your current daily goals:\n"
            f"🔥 Calories: {existing_user.calorie_goal} calories\n"
            f"🥩 Protein: {existing_user.protein_goal}\n"
            f"🥑 Fat: {existing_user.fat_goal}\n"
            f"🌾 Carbs: {existing_user.carb_goal} \n\n"
            "Let's set your new targets. What is your daily calorie goal? (e.g., 2500)")

    # new user
    else:
        await update.message.reply_text(WELCOME_MESSAGE)

    # Required: tells PTB this conversation step is done for now
    return WAITING_CALORIES


async def process_calories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit() or int(text) < 500 or int(text) > 10000:
        await update.message.reply_text("Must be a number between 500 and 10.000")
        # Остаемся в том же состоянии, если ввод некорректен
        return WAITING_CALORIES

    # Записываем значение во временный контекст пользователя
    context.user_data["calorie_goal"] = int(text)

    await update.message.reply_text(PROTEIN_MESSAGE)

    return WAITING_PROTEIN



async def process_protein(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit() or int(text) < 0 or int(text) > 500:
        await update.message.reply_text("Must be a number between 0 and 500")
        return WAITING_PROTEIN

    context.user_data["protein_goal"] = int(text)

    await update.message.reply_text(FAT_MESSAGE)

    return WAITING_FAT


async def process_fat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit() or int(text) < 0 or int(text) > 400:
        await update.message.reply_text("Must be a number between 0 and 400")
        return WAITING_FAT

    context.user_data["fat_goal"] = int(text)

    await update.message.reply_text(CARBS_MESSAGE)

    return WAITING_CARBS

async def process_carbs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit() or int(text) < 0 or int(text) > 1000:
        await update.message.reply_text("Must be a number between 0 and 1000")
        return WAITING_CARBS

    context.user_data["carb_goal"] = int(text)

    print("Goal set: \nCalories: ", context.user_data["calorie_goal"], "\nProtein: ", context.user_data["protein_goal"])
    print("storing to the database......")

    # save data to db
    user_service.save_goals(update.effective_user.id,
                            context.user_data["calorie_goal"],
                            context.user_data["protein_goal"],
                            context.user_data["fat_goal"],
                            context.user_data["carb_goal"])

    await update.message.reply_text(
        f"Profile saved!\n"
        f"Goals:\n"
        f"{context.user_data["calorie_goal"]} calories\n"
        f"{context.user_data["protein_goal"]}g of protein.\n"
        f"{context.user_data["fat_goal"]}g of fat.\n"
        f"{context.user_data["carb_goal"]}g of carbs."
    )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Action cancelled.")

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
            ],
            WAITING_FAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_fat)
            ],
            WAITING_CARBS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_carbs)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )