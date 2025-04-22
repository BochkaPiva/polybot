import asyncio
import os
import logging
import hashlib
import shutil
from pathlib import Path
from search.client import search_client
from search.embeddings import embedding_generator
from search.text_cleaner import TextCleaner
from admin.core.config import settings

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляр очистителя текста
text_cleaner = TextCleaner()

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file content"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def extract_text(file_path: str) -> str:
    """Извлечение текста из файла"""
    try:
        import textract
        text = textract.process(file_path).decode('utf-8')
        # Очищаем текст от мусора
        cleaned_text = text_cleaner.clean_text(text)
        return cleaned_text
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из {file_path}: {str(e)}")
        return ""

async def reindex_documents():
    """Переиндексация всех документов"""
    try:
        # Пересоздаем индекс
        logger.info("Пересоздание индекса...")
        await search_client.client.recreate_index()
        
        # Получаем список всех файлов в директории загрузок
        upload_dir = settings.UPLOAD_DIR
        logger.info(f"Сканирование директории {upload_dir}...")
        
        # Создаем директорию для дубликатов
        duplicates_dir = os.path.join(upload_dir, "duplicates")
        os.makedirs(duplicates_dir, exist_ok=True)
        
        # Словарь для хранения хешей файлов и их содержимого
        file_hashes = {}
        file_contents = {}
        
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path) and not filename.startswith('.'):
                try:
                    # Вычисляем хеш файла
                    file_hash = calculate_file_hash(file_path)
                    
                    # Извлекаем и очищаем текст
                    content = await extract_text(file_path)
                    
                    if not content:
                        logger.warning(f"Не удалось извлечь текст из файла: {filename}")
                        continue
                    
                    # Проверяем на дубликаты по хешу и содержимому
                    is_duplicate = False
                    original_file = None
                    
                    if file_hash in file_hashes:
                        is_duplicate = True
                        original_file = file_hashes[file_hash]
                    else:
                        # Проверяем на дубликаты по содержимому
                        for orig_file, orig_content in file_contents.items():
                            if text_cleaner.is_duplicate(content, orig_content):
                                is_duplicate = True
                                original_file = orig_file
                                break
                    
                    if is_duplicate:
                        logger.warning(f"Найден дубликат файла {filename} (оригинал: {original_file})")
                        # Перемещаем дубликат в отдельную директорию
                        duplicate_path = os.path.join(duplicates_dir, filename)
                        shutil.move(file_path, duplicate_path)
                        continue
                    
                    # Сохраняем информацию о файле
                    file_hashes[file_hash] = filename
                    file_contents[filename] = content
                    
                    # Индексируем документ
                    logger.info(f"Обработка файла: {filename}")
                    await search_client.index_document(
                        doc_id=file_hash,
                        title=filename,
                        content=content,
                        tags=[],
                        file_type=os.path.splitext(filename)[1][1:].lower()
                    )
                    logger.info(f"Файл проиндексирован: {filename}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при индексации файла {filename}: {str(e)}")
                    continue
                    
        logger.info("Переиндексация завершена")
        
    except Exception as e:
        logger.error(f"Ошибка при переиндексации: {str(e)}")
    finally:
        # Закрываем клиент
        await search_client.close()

if __name__ == "__main__":
    asyncio.run(reindex_documents()) 