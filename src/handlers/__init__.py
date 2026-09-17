# src/handlers/__init__.py
from telegram.ext import Application
from .onboarding import get_onboarding_handler

def register_all_handlers(app: Application) -> None:
    # 1. Сценарии с состояниями (ConversationHandler) регистрируются первыми
    app.add_handler(get_onboarding_handler())