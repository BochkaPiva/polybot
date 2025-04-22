import asyncio
import logging
from sqlalchemy import text
from .core.database import async_session_maker, Base, engine
from .core.models import User, Document, Chat

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the database by creating all tables."""
    logger.info("Starting database initialization...")
    
    async with engine.begin() as conn:
        try:
            # Check if tables exist
            tables = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            existing_tables = [row[0] for row in tables]
            
            # Only create tables if they don't exist
            if not any(table in existing_tables for table in ['users', 'documents', 'chats']):
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully!")
            else:
                logger.info("Database tables already exist.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(init_db()) 