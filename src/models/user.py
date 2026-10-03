from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    calorie_goal: int | None = None
    protein_goal: int | None = None
    fat_goal: int | None = None
    carb_goal: int | None = None