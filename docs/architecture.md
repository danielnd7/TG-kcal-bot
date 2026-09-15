```text
[ Пользователь ] 
       │ 
       ├─► Текст: "250г жареной курицы и 200г вареного риса"
       └─► Голос (Audio) ──► [ Whisper API ] ──► (Текст)
                                 │
                                 ▼
                     [ LLM API (Structured JSON) ]
                     Форматирует неструктурированный ввод в схему
                                 │
                                 ▼
         JSON: [
           {"name": "курица жареная", "weight_g": 250},
           {"name": "рис вареный", "weight_g": 200}
         ]
                                 │
                                 ▼
                     [ Сервис поиска КБЖУ ]
                                 │
          ┌──────────────────────┴──────────────────────┐
    (Есть в БД)                                   (Нет в БД)
          │                                             │
          ▼                                             ▼
  Берём КБЖУ из SQLite                        Запрос к Open Food Facts API
                                              (Fallback: запрос КБЖУ у LLM)
                                                        │
                                                        ▼
                                              Сохраняем в SQLite (кэш)
                                 │
                                 ▼
                     [ Калькулятор прогресса ]
                     Суммирует день, считает дефицит
                                 │
                                 ▼
                     [ Ответ пользователю в TG ]
                     Инлайн-кнопки [Редактировать] / [Подтвердить]

```

---


**Stick with `python-telegram-bot`. Do not switch to `aiogram`.**

`python-telegram-bot` (PTB) v20+ is fully async, robust, and has one massive advantage for your exact use case: a **built-in `JobQueue**` (backed by APScheduler). You won't need to manually configure and manage an external scheduler thread for daily reminders—it runs out-of-the-box inside your bot application. `python-dotenv` is the standard tool for managing secrets, so keep that as well.

---

### Barebones MVP Architecture

For a true MVP running on your machine, eliminate external food APIs, Docker, audio processing, and heavy ORMs. The leanest functional design requires just **two packages beyond your skeleton** and **three simple files**.

```text
User Text ("250g chicken, 200g rice")
              │
              ▼
    [ python-telegram-bot ]
              │
              ▼
    [ LLM API (Single Call) ] ──► Returns clean JSON with estimated macros
              │
              ▼
      [ sqlite3 (Built-in) ] ──► Stores meal & calculates daily sum
              │
              ▼
     Bot Reply with Progress (Current vs. Daily Target)

```

---

### 1. Minimal Stack

* **`python-telegram-bot[job-queue]`**: Handles commands, incoming messages, and scheduled reminder jobs.
* **`python-dotenv`**: Loads `BOT_TOKEN` and `LLM_API_KEY` from `.env`.
* **`sqlite3`**: Built directly into Python's standard library (zero installation, single-file database).
* **LLM Client (`openai` or `google-genai`)**: One API call via JSON mode / Structured Outputs to parse text and calculate macros simultaneously.

---

### 2. Database Schema (2 Tables in `sqlite3`)

You only need two flat tables:

**`users`**

* `user_id` (INTEGER, Primary Key) — Telegram user ID.
* `calorie_goal` (INTEGER)
* `protein_goal` (INTEGER)
* `fat_goal` (INTEGER)
* `carb_goal` (INTEGER)

**`meals`**

* `id` (INTEGER, Primary Key, Autoincrement)
* `user_id` (INTEGER)
* `name` (TEXT)
* `weight_g` (INTEGER)
* `calories` (REAL)
* `protein` (REAL)
* `fat` (REAL)
* `carbs` (REAL)
* `created_at` (TIMESTAMP, default `CURRENT_TIMESTAMP`)

---

### 3. Core Execution Flow

**Step 1: Ingestion & LLM Call**
The user sends: `"250g grilled chicken and 200g boiled basmati rice"`.
Pass the raw text directly to the LLM with a system prompt instructing it to act as a nutritional parser. For an MVP, ask the LLM to return **both the parsed item and estimated macros** in one shot. This eliminates the need to integrate a third-party food database on day one.

Expected JSON output:

```json
[
  {"name": "grilled chicken breast", "weight_g": 250, "calories": 412, "protein": 77.5, "fat": 9.0, "carbs": 0.0},
  {"name": "boiled basmati rice", "weight_g": 200, "calories": 242, "protein": 5.0, "fat": 0.6, "carbs": 53.0}
]

```

**Step 2: Database Storage & Calculation**

* Insert each item into `meals`.
* Run a single SQL aggregation:
```sql
SELECT SUM(calories), SUM(protein), SUM(fat), SUM(carbs) 
FROM meals 
WHERE user_id = ? AND date(created_at) = date('now');

```



**Step 3: User Response**
Return a formatted text message:

> **Logged:**
> • Grilled chicken breast (250g): 412 kcal | 77.5g P
> • Boiled basmati rice (200g): 242 kcal | 5.0g P
> **Today's Progress:**
> Calories: 1,850 / 2,500 kcal
> Protein: 140 / 180g
> Fat: 55 / 70g
> Carbs: 200 / 280g

**Step 4: Scheduled Reminder (Built-in JobQueue)**
Use PTB's native scheduler to run a daily check at target hours (e.g., 20:00):

```python
application.job_queue.run_daily(
    daily_reminder_callback,
    time=datetime.time(hour=20, minute=0, tzinfo=user_tz),
    chat_id=user_id
)

```

The callback fetches today's consumed protein/calories against the target in `users`. If `consumed_protein < target_protein * 0.7`, send a ping alert.

---

### 4. Project Layout

Keep the repository flat and focused:

```text
├── .env                # BOT_TOKEN, LLM_API_KEY
├── database.py         # Init tables, insert_meal(), get_daily_stats(), set_goals()
├── llm.py              # Single function: parse_food_text(raw_text) -> list[dict]
└── main.py             # PTB Application, message handlers, JobQueue reminders

```
