from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        """
        Репозиторий принимает активную сессию БД.
        Сам репозиторий сессию НЕ создает — он лишь выполняет в ней операции.
        """
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Получить пользователя по его Telegram ID.

        TODO:
        1. Написать select-запрос к модели User с фильтром по telegram_id.
           Подсказка: select(User).where(...)
        2. Выполнить запрос через await self.session.execute(...)
        3. Вернуть один результат или None (метод scalar_one_or_none()).
        """
        pass

    async def save_profile(
            self,
            telegram_id: int,
            calories: int,
            protein: int,
            fat: int,
            carbs: int,
    ) -> User:
        """
        Сохранить или обновить профиль пользователя (упрощенный логический upsert).

        TODO:
        1. Сначала вызвать self.get_by_telegram_id(telegram_id), чтобы проверить,
           существует ли уже пользователь в базе.

        2. ЕСЛИ пользователь найден:
           - Обновить его поля: user.daily_calories = calories и т.д.

        3. ЕСЛИ пользователя нет:
           - Создать экземпляр модели User с переданными параметрами.
           - Добавить его в сессию: self.session.add(new_user)
           - Присвоить переменной user = new_user

        4. Зафиксировать транзакцию: await self.session.commit()
        5. Обновить атрибуты объекта из базы: await self.session.refresh(user)
        6. Вернуть объект user.
        """
        pass