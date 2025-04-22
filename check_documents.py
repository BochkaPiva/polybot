import asyncio
import logging
from sqlalchemy import text
from admin.core.database import engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_documents():
    """Проверка содержимого таблицы documents"""
    try:
        async with engine.connect() as conn:
            # Получаем все документы
            query = text("""
                SELECT id, original_filename, system_filename, file_type, file_size,
                       content_text, text_version, user_id, created_at, updated_at
                FROM documents
            """)
            result = await conn.execute(query)
            documents = result.fetchall()
            
            logger.info(f"Найдено {len(documents)} документов")
            
            for doc in documents:
                logger.info("---")
                logger.info(f"ID: {doc.id}")
                logger.info(f"Оригинальное имя: {doc.original_filename}")
                logger.info(f"Системное имя: {doc.system_filename}")
                logger.info(f"Тип файла: {doc.file_type}")
                logger.info(f"Размер: {doc.file_size} байт")
                logger.info(f"Текст: {doc.content_text[:200] if doc.content_text else 'None'}")
                logger.info(f"Версия текста: {doc.text_version}")
                logger.info(f"ID пользователя: {doc.user_id}")
                logger.info(f"Создан: {doc.created_at}")
                logger.info(f"Обновлен: {doc.updated_at}")
                logger.info("---")
                
    except Exception as e:
        logger.error(f"Ошибка при проверке документов: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(check_documents()) 