## 🧭 **Project Overview**

**Goal:**
Build a Telegram bot that lets you log meals (with kcal values) and automatically summarizes your calorie intake daily — starting locally, later deployable to WSL and Raspberry Pi.

**Stack (proposed):**

* **Language:** Python
* **Bot Framework:** `python-telegram-bot` or `aiogram`
* **Database:** SQLite (phase 1) → PostgreSQL (future)
* **Deployment:** Local Windows → WSL → Raspberry Pi

---

## 🚀 **Phase 1 — Planning & Setup**

### 1.1 Define Requirements

* [ ] Define what commands bot will support (`/add`, `/stats`, `/reset`, etc.)
* [ ] Define what kind of inputs bot should accept (text like “250 pasta” or structured input)
* [ ] Decide on whether to support editing/deleting meals
* [ ] Specify what statistics to show (daily total, avg, goal comparison, etc.)
* [ ] Choose preferred time zone for “end of day” summary

### 1.2 Environment Setup

* [x] Install Python and necessary libraries (in venv)
* [x] Create virtual environment
* [x] Set up Telegram Bot token via [BotFather](https://t.me/BotFather)
* [x] Initialize Git repository for version control
* [ ] Create `.env` file for sensitive credentials

---

## 💻 **Phase 2 — Core Development**

### 2.1 Bot Skeleton

* [ ] Connect to Telegram API
* [ ] Create a simple `/start` handler to verify connection
* [ ] Implement basic logging 

### 2.2 Data Model

* [ ] Design SQLite database schema:

  * `meals`: id, user_id, kcal, description, timestamp
  * `users`: id, daily_goal, timezone (optional)
* [ ] Write DB access functions (insert, read, delete)

### 2.3 Core Features

* [ ] `/add` command — add meal manually (`/add 250 pasta`)
* [ ] `/today` — show today’s total kcal and list of meals
* [ ] `/stats` — show weekly or monthly summary
* [ ] `/reset` — clear today’s meals (optional)

### 2.4 Automatic Daily Summary

* [ ] Schedule daily summary at specified time
* [ ] Implement daily stats message (total kcal, meals count, goal reached?)
* [ ] Handle timezone correctly

---

## 🧪 **Phase 3 — Testing & Validation**

### 3.1 Unit Tests

* [ ] Write tests for DB operations
* [ ] Write tests for command parsing and message formatting
* [ ] Test message handlers

### 3.2 Manual Testing

* [ ] Test all commands on a private Telegram chat
* [ ] Validate summary timing
* [ ] Check for message formatting issues

### 3.3 Edge Cases

* [ ] Invalid kcal input (e.g., “banana” without number)
* [ ] Empty day with no meals
* [ ] Multiple users interacting with same bot

---

## ⚙️ **Phase 4 — Deployment & Infrastructure**

### 4.1 Local Deployment (Windows)

* [ ] Run bot script manually from terminal
* [ ] Verify background job (daily summary) works when PC is on

### 4.2 WSL Deployment

* [ ] Set up Python environment in WSL
* [ ] Configure persistent background process (e.g., `screen` or `systemd`)
* [ ] Validate DB access and file paths

### 4.3 Raspberry Pi Deployment

* [ ] Install required Python and dependencies
* [ ] Configure auto-start on boot (systemd or crontab)
* [ ] Test stability and connectivity

---

## 📊 **Phase 5 — Improvement & Expansion**

### 5.1 Enhancements

* [ ] Add daily/weekly kcal goal tracking
* [ ] Add charts (matplotlib or `plotly`) for stats
* [ ] Add export to CSV or Google Sheets
* [ ] Add voice message parsing (“ate 200 calories of rice”)

### 5.2 Notifications

* [ ] Add reminders to log meals if inactive for N hours
* [ ] Add motivational messages when close to goal

### 5.3 Multi-user Support

* [ ] Store separate user data
* [ ] Add `/register` and `/setgoal` commands

---

## 📅 **Suggested Timeline**

| Phase                   | Duration | Deliverable                    |
| ----------------------- | -------- | ------------------------------ |
| 1. Planning & Setup     | 1–2 days | Project skeleton ready         |
| 2. Core Development     | 4–5 days | Bot with add/stats working     |
| 3. Testing & Validation | 2–3 days | Fully functional bot           |
| 4. Deployment           | 2–3 days | Bot running on chosen platform |
| 5. Improvements         | ongoing  | Feature expansion              |

---

## 🧰 **Recommended Tools**

* **Code Editor:** VS Code
* **Database Viewer:** SQLite Browser
* **Testing:** `pytest`
* **Version Control:** Git + GitHub
* **Scheduling:** `apscheduler` or Python `asyncio` timers

