from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.users import UserRepository

class AuthMiddleware(BaseMiddleware):
    """Middleware to check if user is authenticated"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Get session from data (will be injected by another middleware)
        session: AsyncSession = data.get("session")
        
        # Skip middleware if no session available
        if not session:
            return await handler(event, data)
        
        # Get user from database
        user_repo = UserRepository(session)
        
        # Extract user ID based on event type
        if isinstance(event, Message):
            user = await user_repo.get_user_by_telegram_id(event.from_user.id)
        elif isinstance(event, CallbackQuery):
            user = await user_repo.get_user_by_telegram_id(event.from_user.id)
        else:
            # Skip for other event types
            return await handler(event, data)
        
        # Add user to data
        data["user"] = user
        
        # Check if user exists and is authenticated
        if user and user.is_authenticated:
            data["is_authenticated"] = True
        else:
            data["is_authenticated"] = False
        
        return await handler(event, data)
