from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.repositories.users import UserRepository
from db.base import get_session
from db.models import Employee

class AuthMiddleware(BaseMiddleware):
    """Middleware to check if user is authenticated"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем команду /start без проверки
        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)

        async with get_session() as session:
            # Проверяем, есть ли у пользователя telegram_id в базе
            query = select(Employee).where(
                Employee.telegram_id == event.from_user.id,
                Employee.is_active == True
            )
            result = await session.execute(query)
            employee = result.scalar_one_or_none()

            if not employee:
                if isinstance(event, Message):
                    await event.answer(
                        "Вы не авторизованы. Пожалуйста, используйте команду /start для авторизации."
                    )
                return

            # Добавляем информацию о сотруднике в data
            data["employee"] = employee
            return await handler(event, data)
