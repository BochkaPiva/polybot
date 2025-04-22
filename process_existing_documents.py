import asyncio
import logging
from sqlalchemy import text
from admin.core.database import engine
import docx
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def extract_text_from_docx(file_path: str) -> str:
    """Извлечение текста из DOCX файла"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return None
            
        logger.info(f"Извлечение текста из файла: {file_path}")
        doc = docx.Document(file_path)
        extracted_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        if not extracted_text.strip():
            logger.error(f"Не удалось извлечь текст из файла: {file_path}")
            return None
            
        logger.info(f"Успешно извлечен текст длиной {len(extracted_text)} символов")
        return extracted_text
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста: {str(e)}", exc_info=True)
        return None

async def process_documents():
    """Обработка всех существующих документов"""
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
            
            logger.info(f"Найдено {len(documents)} документов для обработки")
            
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
                
                # Формируем путь к файлу
                file_path = os.path.join("uploads", doc.system_filename)
                
                # Извлекаем текст
                extracted_text = await extract_text_from_docx(file_path)
                if extracted_text:
                    # Обновляем документ в базе данных
                    update_stmt = text("""
                        UPDATE documents 
                        SET content_text = :content_text
                        WHERE id = :doc_id
                    """)
                    await conn.execute(update_stmt, {"content_text": extracted_text, "doc_id": doc.id})
                    await conn.commit()
                    logger.info(f"Документ {doc.original_filename} успешно обновлен")
                else:
                    logger.error(f"Не удалось обработать документ {doc.original_filename}")
                    
    except Exception as e:
        logger.error(f"Ошибка при обработке документов: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(process_documents()) 