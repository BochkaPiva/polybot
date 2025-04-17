from typing import List
from typing import AsyncGenerator
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.models import MenuItem

def get_menu_keyboard(menu_items: List[MenuItem], level: int) -> InlineKeyboardMarkup:
    """Get menu keyboard based on menu items"""
    keyboard = []
    
    # Add menu items
    for item in menu_items:
        keyboard.append([
            InlineKeyboardButton(
                text=item.title,
                callback_data=f"menu:{item.id}"
            )
        ])
    
    # Add "Ask your question" button if it's first level
    if level == 1:
        keyboard.append([
            InlineKeyboardButton(
                text="Задать свой вопрос",
                callback_data="ask_question"
            )
        ])
    
    # Add back button if not on first level
    if level > 1:
        keyboard.append([
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="menu:back"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
