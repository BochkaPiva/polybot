from typing import AsyncGenerator
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_auth_keyboard() -> InlineKeyboardMarkup:
    """Get authentication keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="Авторизоваться", callback_data="auth")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main keyboard"""
    keyboard = [
        [KeyboardButton(text="📚 Меню справочника")],
        [KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
