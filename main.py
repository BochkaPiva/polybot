import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from bot.handlers import auth
from bot.middlewares import auth as auth_middleware
from db.base import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Команды бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/menu", description="Показать главное меню"),
        BotCommand(command="/help", description="Получить справку"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Инициализация базы данных
    await init_db()
    
    # Регистрация middleware
    dp.message.middleware(auth_middleware.AuthMiddleware())
    dp.callback_query.middleware(auth_middleware.AuthMiddleware())
    
    # Регистрация обработчиков
    dp.include_router(auth.router)
    
    # Установка команд бота
    await set_commands(bot)
    
    # Запуск бота
    logger.info("Starting bot")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
