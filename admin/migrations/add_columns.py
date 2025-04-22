import asyncio
import logging
import sys
import os

# Добавляем путь к корню проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from admin.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_columns():
    """Добавляет колонки text_version и user_id в таблицу documents"""
    try:
        async with engine.connect() as conn:
            # Добавляем колонку text_version
            await conn.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN IF NOT EXISTS text_version integer DEFAULT 1;
            """))
            
            # Добавляем колонку user_id
            await conn.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN IF NOT EXISTS user_id integer REFERENCES users(id);
            """))
            
            await conn.commit()
            logger.info("Колонки успешно добавлены")
                
    except Exception as e:
        logger.error(f"Ошибка при добавлении колонок: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(add_columns()) 