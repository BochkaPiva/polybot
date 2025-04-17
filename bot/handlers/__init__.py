from aiogram import Dispatcher

from .auth import router as auth_router
from .menu import router as menu_router
from .search import router as search_router
from .common import router as common_router

def register_all_handlers(dp: Dispatcher):
    """Register all handlers"""
    # Order matters: auth first, then menu, then search, then common
    dp.include_router(auth_router)
    dp.include_router(menu_router)
    dp.include_router(search_router)
    dp.include_router(common_router)