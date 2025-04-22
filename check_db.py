import asyncio
import logging
from sqlalchemy import text
from admin.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_table_structure():
    """Проверяет структуру таблицы documents"""
    try:
        async with engine.connect() as conn:
            # Получаем информацию о колонках таблицы documents
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'documents'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            
            if not columns:
                logger.info("Таблица documents не существует")
                return
                
            logger.info("Структура таблицы documents:")
            for col in columns:
                logger.info(f"Колонка: {col[0]}")
                logger.info(f"Тип данных: {col[1]}")
                logger.info(f"Может быть NULL: {col[2]}")
                logger.info(f"Значение по умолчанию: {col[3]}")
                logger.info("---")
                
    except Exception as e:
        logger.error(f"Ошибка при проверке таблицы: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(check_table_structure()) 