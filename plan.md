### Phase 1: Dependencies & Environment Setup

Lock down the minimal external tools before writing any business logic.

* **Step 1.1: Install required packages**
Run:
```bash
pip install "python-telegram-bot[job-queue]" openai pydantic

```


*(Using `openai` or `google-genai` with Pydantic handles Structured Outputs out of the box).*
* **Step 1.2: Configure `.env**`
Ensure your `.env` contains:
```env
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
LLM_API_KEY="your_api_key"

```


* **Step 1.3: Create project file structure**
Keep files flat in one directory:
```text
├── .env
├── bot.py          # Bot entry point, handlers, JobQueue
├── database.py     # SQLite init and data access queries
└── llm.py          # Extraction function returning Pydantic objects

```



---

### Phase 2: Database Schema & Access Layer (`database.py`)

Build the persistent storage layer first so your bot handlers have immediate destinations for data.

* **Step 2.1: Initialize SQLite connection & schema creation**
Write an `init_db()` function creating two tables if they do not exist:
* `user_goals`: `user_id` (INTEGER PRIMARY KEY), `calories` (REAL), `protein` (REAL), `fats` (REAL), `carbs` (REAL).
* `food_logs`: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `user_id` (INTEGER), `name` (TEXT), `weight_g` (REAL), `calories` (REAL), `protein` (REAL), `fats` (REAL), `carbs` (REAL), `logged_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP).


* **Step 2.2: Implement 4 core query functions**
* `set_user_goals(user_id, cals, p, f, c)`: `INSERT OR REPLACE INTO user_goals`.
* `get_user_goals(user_id)`: Selects target thresholds.
* `log_meal(user_id, items: list[dict])`: Inserts multiple food rows within a single transaction.
* `get_today_stats(user_id)`: Runs `SUM(calories)`, `SUM(protein)`, `SUM(fats)`, `SUM(carbs)` where `DATE(logged_at, 'localtime') = DATE('now', 'localtime')`.



---

### Phase 3: Natural Language Parsing Layer (`llm.py`)

Transform unstructured food input into strongly-typed macro values without pre-populating manual ingredient databases.

* **Step 3.1: Define Pydantic models**
```python
from pydantic import BaseModel

class FoodItem(BaseModel):
    name: str
    weight_g: float
    calories: float
    protein: float
    fats: float
    carbs: float

class MealLog(BaseModel):
    items: list[FoodItem]

```


* **Step 3.2: Implement extraction function `parse_food_input(text: str) -> MealLog**`
* Use the LLM's **Structured Outputs / JSON mode** enforcing the `MealLog` schema.
* **System Prompt constraint:** Instruct the model to calculate realistic total macros based on the extracted `weight_g` and cooking state (raw vs boiled vs fried).
* Return the validated `MealLog` object directly.



---

### Phase 4: Bot Commands & Message Handlers (`bot.py`)

Connect Telegram input to the database and parser.

* **Step 4.1: Command `/start` and `/goals**`
* `/start`: Send a brief welcome explanation of how to log food.
* `/goals 2500 180 70 260`: Parse arguments as `Calories Protein Fats Carbs` and call `set_user_goals()`. If missing arguments, prompt the user for the expected format.


* **Step 4.2: Free-text Food Logging Handler**
Attach an asynchronous `MessageHandler(filters.TEXT & ~filters.COMMAND, handle_food_entry)`:
1. Send a temporary typing indicator: `await context.bot.send_chat_action(chat_id, "typing")`.
2. Call `MealLog = parse_food_input(update.message.text)`.
3. Save items using `log_meal(user_id, items)`.
4. Fetch updated daily numbers via `get_today_stats(user_id)` and `get_user_goals(user_id)`.
5. Reply with a breakdown:
* List of logged items with individual calories/protein.
* Summary: `Total Today: Current / Goal (Remaining)`.




* **Step 4.3: Command `/today**`
* Query `get_today_stats(user_id)` and compare against `get_user_goals(user_id)`.
* Return remaining macros needed to hit daily targets.



---

### Phase 5: Reminder Automation via Built-in `JobQueue`

Add background notifications without setting up external schedulers or message brokers.

* **Step 5.1: Create notification callback**
Write an async function `check_evening_status(context: ContextTypes.DEFAULT_TYPE)`:
* Pull `get_today_stats(user_id)` and `get_user_goals(user_id)`.
* If `logged_protein < target_protein`: send a direct nudge stating the exact missing grams of protein and calories.


* **Step 5.2: Schedule job inside bot startup**
Use PTB’s native scheduler to run daily at a fixed evening time (e.g., 20:30):
```python
import datetime

application = ApplicationBuilder().token(TOKEN).build()
job_queue = application.job_queue

job_queue.run_daily(
    check_evening_status,
    time=datetime.time(hour=20, minute=30),
    chat_id=TARGET_USER_ID,
    name="daily_macro_check"
)

```



---

### Phase 6: End-to-End Verification (Manual Smoke Test)

Run the bot locally (`python bot.py`) and perform this sequential check:

1. Send `/goals 2500 180 70 250` $\rightarrow$ verify response confirms saved targets.
2. Send `"250g grilled chicken, 200g boiled basmati rice"` $\rightarrow$ verify the bot extracts both items and updates today's totals.
3. Send `/today` $\rightarrow$ verify arithmetic matches the previous entry.
4. Manually trigger the job callback or set a test interval (e.g., `run_once` in 10 seconds) $\rightarrow$ verify the nudge message arrives correctly in chat.
