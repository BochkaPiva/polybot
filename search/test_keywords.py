import asyncio
import logging
from keyword_extractor import KeywordExtractor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_keyword_extraction():
    """Тестирование извлечения ключевых слов"""
    
    # Создаем тестовые документы
    test_docs = [
        {
            "id": 1,
            "title": "Положение о премировании работников",
            "content": """
            ПОЛОЖЕНИЕ
            О ПРЕМИРОВАНИИ РАБОТНИКОВ
            
            1. Общие положения
            1.1. Область применения
            Настоящее Положение распространяется на всех работников.
            
            1.2. Цель премирования
            Премирование направлено на повышение эффективности труда.
            """
        },
        {
            "id": 2,
            "title": "Инструкция по охране труда",
            "content": """
            ИНСТРУКЦИЯ
            ПО ОХРАНЕ ТРУДА
            
            1. Общие требования
            1.1. Область применения
            Настоящая инструкция обязательна для всех работников.
            
            1.2. Требования безопасности
            Работники обязаны соблюдать правила безопасности.
            """
        }
    ]
    
    # Создаем экстрактор ключевых слов
    extractor = KeywordExtractor(
        language="ru",
        max_keywords=5,
        deduplication_threshold=0.8
    )
    
    # Извлекаем ключевые слова для каждого документа
    for doc in test_docs:
        logger.info(f"\nОбработка документа: {doc['title']}")
        doc_with_keywords = extractor.extract_keywords_for_document(doc)
        
        logger.info("\nИзвлеченные ключевые слова:")
        for kw in doc_with_keywords["keywords"]:
            logger.info(f"- {kw['keyword']} (score: {kw['score']:.3f})")
            
        logger.info("\nТеги документа:")
        for tag in doc_with_keywords["tags"]:
            logger.info(f"- {tag}")

if __name__ == "__main__":
    asyncio.run(test_keyword_extraction()) 