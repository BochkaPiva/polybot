import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from bot.handlers import register_all_handlers
from bot.middlewares import setup_middlewares
from db.base import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Bot commands
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Получить справку"),
        BotCommand(command="/menu", description="Показать главное меню"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Initialize database
    await init_db()
    
    # Setup middlewares
    setup_middlewares(dp)
    
    # Register handlers
    register_all_handlers(dp)
    
    # Set bot commands
    await set_commands(bot)
    
    # Start polling
    logger.info("Starting bot")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
