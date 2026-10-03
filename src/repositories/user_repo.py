from dataclasses import asdict
from db import get_connection
from models import User


def get(user_id: int) -> User | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    return User(**row) if row else None


def save(user: User) -> None:
    """Insert the user, or update it if it already exists (upsert)."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, calorie_goal, protein_goal, fat_goal, carb_goal)
            VALUES (:user_id, :calorie_goal, :protein_goal, :fat_goal, :carb_goal)
            ON CONFLICT(user_id) DO UPDATE SET
                calorie_goal = excluded.calorie_goal,
                protein_goal = excluded.protein_goal,
                fat_goal     = excluded.fat_goal,
                carb_goal    = excluded.carb_goal
            """,
            asdict(user), # Convert the dto into dict
        )