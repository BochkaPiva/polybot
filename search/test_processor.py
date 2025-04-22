import asyncio
import logging
import sys
import os

# Добавляем путь к корню проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.document_processor import DocumentProcessor
from admin.core.database import engine
from admin.models.document import Document
from sqlalchemy import select

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_processor():
    """Тестирование функциональности DocumentProcessor"""
    processor = DocumentProcessor()
    
    # Тестовый документ
    test_doc = """АКЦИОНЕРНОЕ ОБЩЕСТВО
«СИБГАЗПОЛИМЕР»

СИСТЕМА МЕНЕДЖМЕНТА

ПОЛОЖЕНИЕ

О ПРЕМИРОВАНИИ РАБОТНИКОВ

П-__-__-2025

1. Общие положения

1.1. Область применения

Настоящее Положение распространяется на всех работников АО «Сибгазполимер».

1.2. Термины и определения

- Премия - дополнительное денежное вознаграждение
- Квартал - период в три месяца
- Год - календарный год

2. Порядок премирования

2.1. Виды премий

- Ежемесячная премия
- Квартальная премия
- Годовая премия

Директор
Иванов И.И.

1"""
    
    # Тестируем очистку текста
    logger.info("Тестирование очистки текста...")
    cleaned_text = processor.clean_text(test_doc)
    logger.info(f"Очищенный текст:\n{cleaned_text}\n")
    
    # Тестируем извлечение структуры
    logger.info("Тестирование извлечения структуры...")
    structure = processor.extract_structure(test_doc)  # Используем оригинальный текст
    logger.info("Структура документа:")
    logger.info(f"Разделы: {structure['sections']}")
    logger.info(f"Подразделы: {structure['subsections']}")
    logger.info(f"Списки: {structure['lists']}\n")
    
    # Тестируем извлечение метаданных
    logger.info("Тестирование извлечения метаданных...")
    metadata = processor.extract_metadata(test_doc, "Положение о премировании.docx")  # Используем оригинальный текст
    logger.info("Метаданные документа:")
    logger.info(f"Тип документа: {metadata['document_type']}")
    logger.info(f"Область применения: {metadata['application_area']}")
    logger.info(f"Дата: {metadata['date']}\n")
    
    # Тестируем обработку документа
    logger.info("Тестирование обработки документа...")
    chunks = await processor.process_document(
        document_id=1,
        title="Положение о премировании",
        content=test_doc
    )
    
    logger.info(f"Получено {len(chunks)} чанков")
    for i, chunk in enumerate(chunks):
        logger.info(f"\nЧанк {i + 1}:")
        logger.info(f"Содержимое: {chunk['content'][:100]}...")
        logger.info(f"Метаданные: {chunk['metadata']}")

if __name__ == "__main__":
    asyncio.run(test_processor()) 