import sqlite3

DB_PATH = "bot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH) # opens connection to the file .db
    conn.row_factory = sqlite3.Row  # Changes the returned row type from a standard Python tuple to a sqlite3.Row object
    return conn

def get_user(user_id: int) -> dict | None:
    """Returns user record as a dict, or None if user does not exist."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def create_user(user_id: int):
    """Inserts a new user record with empty goals (NULL)."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )

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