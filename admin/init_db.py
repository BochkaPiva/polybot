import asyncio
import logging
from sqlalchemy import text

from admin.core.database import engine, async_session_maker
from admin.core.models import Base

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    try:
        logger.info("Starting database initialization...")
        
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully!")
        
        # Проверяем подключение
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db()) 