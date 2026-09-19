Разделение логики строится по слоям ответственности: точка входа, конфигурация, обработчики запросов (хендлеры), бизнес-логика (сервисы) и работа с хранилищем (база данных).

---

### Рекомендуемая структура проекта

```text
src/
├── config.py             # Токены, переменные окружения, настройки подключения
├── main.py               # Точка входа: сборка Application, регистрация роутеров, запуск
├── db.py                 # Подключение к БД, пул соединений, миграции / сессии
├── llm.py                # Клиент и обертка над LLM-моделями
│
├── handlers/             # Слой представления (только прием команд и ответов в Telegram)
│   ├── __init__.py       # Единая функция регистрации всех хендлеров
│   ├── onboarding.py     # ConversationHandler для первичного анкетирования
│   ├── meals.py          # Логика трекинга еды (текст, фото, калории)
│   └── common.py         # /help, /cancel, обработка системных ошибок
│
├── services/             # Бизнес-логика (не знает ничего про telegram-объекты)
│   ├── user_service.py   # Регистрация, обновление профиля, получение целевых КБЖУ
│   └── meal_service.py   # Подсчет дневных калорий, валидация записей еды
│
└── repositories/         # Слой запросов к БД (CRUD операции)
    ├── user_repo.py
    └── meal_repo.py

```

*(Если проект пока небольшой, слой `repositories/` можно объединить с `services/` или оставить чистые SQL/ORM-функции в `services/`).*

---

### Как связать модули между собой

**1. `handlers/__init__.py` (Сборщик маршрутов)**

Вместо импорта каждого хендлера по отдельности в главный файл, пакет `handlers` предоставляет одну функцию регистрации:

```python
# src/handlers/__init__.py
from telegram.ext import Application
from .onboarding import get_onboarding_handler
from .meals import get_meals_handlers
from .common import get_common_handlers

def register_all_handlers(app: Application) -> None:
    # 1. Сценарии с состояниями (ConversationHandler) регистрируются первыми
    app.add_handler(get_onboarding_handler())
    
    # 2. Предметные хендлеры
    for handler in get_meals_handlers():
        app.add_handler(handler)
        
    # 3. Общие команды (/help, /cancel, fallback-текст)
    for handler in get_common_handlers():
        app.add_handler(handler)

```

**2. `handlers/onboarding.py` (Изолированный сценарий)**

Хендлеры вызывают сервисный слой и возвращают готовый объект:

```python
# src/handlers/onboarding.py
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from services.user_service import save_user_profile

WAITING_CALORIES, WAITING_PROTEIN = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! Какова суточная норма калорий?")
    return WAITING_CALORIES

# ...остальные шаги диалога...

def get_onboarding_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_CALORIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_calories)],
            # ...
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

```

**3. `main.py` (Чистая точка сборки)**

Файл `bot.py` переименовывается в `main.py`, где остается только код инициализации жизненного цикла:

```python
# src/main.py
from telegram.ext import Application
from config import BOT_TOKEN
from handlers import register_all_handlers

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация всех хендлеров одной строкой
    register_all_handlers(app)

    app.run_polling()

if __name__ == "__main__":
    main()

```

---

### Архитектурные преимущества

* **Отсутствие циклических импортов:** `main.py` знает о `handlers`, `handlers` знают о `services`, `services` знают о `db.py` и `llm.py`. Поток зависимостей однонаправленный.
* **Изоляция бизнес-логики:** Хендлеры работают только с парсингом сообщений Telegram (`update.message.text`, отправка ответа) и вызывают чистые Python-функции из `services/`.
* **Тестируемость:** Функции расчета БЖУ и парсинга через LLM можно тестировать юнит-тестами без необходимости эмулировать Telegram API или мокать объекты `Update`.

---
---
# мой промт
```
И так, проверь правильно ли я понял логику всей архитектуры:
В main.py (который запускается первым) импортируется register_all_handlers (функция из пакета handlers). В самом main только запускается бот и вызывается эта функция которая уже добавляет все хендлеры. Вроде такого:
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    register_all_handlers(app)
    app.run_polling()

после чего в бот добавляется независимый ConversationHandler из пакета handlers (например  онбординг, со всеми нужными ему функциями). Я правильно все понял?
```
# gmn
```markdown
Да, логика понята абсолютно точно.

Архитектурная цепочка выстроена верно:

1. **`main.py`** выступает исключительно точкой сборки и запуска (Entrypoint / Composition Root): он инициализирует окружение, конфигурирует инстанс `Application`, вызывает `register_all_handlers(app)` и стартует `run_polling()`. В нём нет логики парсинга сообщений или работы с данными.
2. **`handlers/__init__.py`** берет на себя роль агрегатора маршрутов. Внутри `register_all_handlers(app)` вызываются методы добавления хендлеров (`app.add_handler(...)`), упорядочивая их приоритет (сначала изолированные сценарии, затем общие команды).
3. **`handlers/onboarding.py`** инкапсулирует сценарий регистрации: содержит функцию-фабрику `get_onboarding_handler()`, объявляет внутренние шаги диалога и возвращает готовый, полностью изолированный `ConversationHandler`.

При такой схеме компоненты слабо связаны (loose coupling): добавление нового модуля (например, трекинга приёмов пищи) потребует лишь создания файла в `handlers/` и добавления одной строки регистрации в `register_all_handlers`.
```