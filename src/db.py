import sqlite3

DB_PATH = "bot.db"

def init_db():
    """Initializes the database and creates required tables if they don't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Enable WAL mode for better concurrency handling
        cursor.execute("PRAGMA journal_mode=WAL;")

        # 1. Create the users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                calorie_goal INTEGER,
                protein_goal INTEGER,
                fat_goal INTEGER,
                carb_goal INTEGER
            );
        """)

        # 2. Create the meals table (needed for logging)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                weight_g INTEGER NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL,
                carbs REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
        """)
        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database and tables initialized successfully in bot.db")