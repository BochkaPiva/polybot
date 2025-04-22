import asyncio
import logging
import os
from sqlalchemy import text
from admin.core.database import engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def update_filenames():
    """Обновление имен файлов в базе данных"""
    try:
        # Получаем список файлов в директории uploads
        files = [f for f in os.listdir("uploads") if f.endswith(".docx")]
        logger.info(f"Найдено {len(files)} файлов в директории uploads")
        
        async with engine.connect() as conn:
            # Получаем все документы из базы данных
            result = await conn.execute(text("SELECT id FROM documents"))
            documents = result.fetchall()
            
            if len(documents) != len(files):
                logger.warning(f"Количество документов в БД ({len(documents)}) не совпадает с количеством файлов ({len(files)})")
            
            # Обновляем каждый документ
            for i, doc_id in enumerate(documents):
                if i < len(files):
                    update_stmt = text("""
                        UPDATE documents 
                        SET system_filename = :filename
                        WHERE id = :doc_id
                    """)
                    await conn.execute(update_stmt, {
                        "filename": files[i],
                        "doc_id": doc_id[0]
                    })
                    logger.info(f"Обновлен документ {doc_id[0]} с новым именем файла {files[i]}")
            
            await conn.commit()
            logger.info("Все обновления успешно сохранены")
                
    except Exception as e:
        logger.error(f"Ошибка при обновлении имен файлов: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(update_filenames()) 