from models import User
from repositories import user_repo


def get_user(user_id: int) -> User | None:
    return user_repo.get(user_id)


def save_goals(user_id: int, calories: int, protein: int, fat: int, carbs: int) -> User:
    user = User(user_id, calories, protein, fat, carbs)
    user_repo.save(user)
    return user