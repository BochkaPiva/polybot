from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Create router
router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "🤖 <b>Бот-справочник предприятия 'Полиом'</b>\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/menu - Показать главное меню справочника\n"
        "/help - Показать эту справку\n\n"
        "В меню справочника вы можете:\n"
        "• Просматривать разделы и подразделы\n"
        "• Получать информацию по интересующим вопросам\n"
        "• Задавать свои вопросы через кнопку 'Задать свой вопрос'\n\n"
        "Если у вас возникли проблемы с использованием бота, "
        "пожалуйста, обратитесь к администратору."
    )
    
    await message.answer(help_text, parse_mode="HTML")

@router.message()
async def echo(message: Message, is_authenticated: bool):
    """Handle all other messages"""
    if not is_authenticated:
        await message.answer(
            "Для работы с ботом необходимо авторизоваться.\n"
            "Используйте команду /start для авторизации."
        )
        return
    
    await message.answer(
        "Я не понимаю эту команду. Пожалуйста, используйте меню или команду /help для справки."
    )
