from aiogram import Dispatcher
from .auth import AuthMiddleware
from .database import DatabaseMiddleware

def setup_middlewares(dp: Dispatcher):
    """Setup all middlewares"""
    # Register middlewares
    dp.message.middleware(DatabaseMiddleware())  # Database middleware must be first
    dp.callback_query.middleware(DatabaseMiddleware())
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
