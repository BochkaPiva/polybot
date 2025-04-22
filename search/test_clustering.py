import asyncio
import logging
import numpy as np
from document_clustering import DocumentClusterer
from document_processor import DocumentProcessor
from cluster_storage import ClusterStorage
from opensearchpy import OpenSearch

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация OpenSearch
OPENSEARCH_CONFIG = {
    'hosts': ['http://localhost:9200'],
    'http_auth': ('admin', 'admin'),
    'use_ssl': False,
    'verify_certs': False,
    'ssl_show_warn': False
}

async def test_clustering():
    """Тестирование кластеризации документов"""
    
    # Создаем тестовые документы
    test_docs = [
        """
        ПОЛОЖЕНИЕ
        О ПРЕМИРОВАНИИ РАБОТНИКОВ
        
        1. Общие положения
        1.1. Область применения
        Настоящее Положение распространяется на всех работников.
        """,
        
        """
        ПОЛОЖЕНИЕ
        ОБ ОПЛАТЕ ТРУДА
        
        1. Общие положения
        1.1. Область применения
        Настоящее Положение определяет порядок оплаты труда.
        """,
        
        """
        ИНСТРУКЦИЯ
        ПО ОХРАНЕ ТРУДА
        
        1. Общие требования
        1.1. Область применения
        Настоящая инструкция обязательна для всех работников.
        """,
        
        """
        РЕГЛАМЕНТ
        РАБОТЫ С ДОКУМЕНТАМИ
        
        1. Общие положения
        1.1. Назначение
        Настоящий регламент устанавливает порядок работы с документами.
        """
    ]
    
    # Создаем процессор документов
    processor = DocumentProcessor()
    
    # Обрабатываем документы
    processed_docs = []
    for i, doc in enumerate(test_docs):
        chunks = await processor.process_document(
            document_id=i,
            title=f"Документ {i+1}",
            content=doc
        )
        if chunks:
            processed_docs.append(chunks[0])  # Берем первый чанк
            
    logger.info(f"Обработано {len(processed_docs)} документов")
    
    # Создаем тестовые эмбеддинги (в реальности они будут получены из модели)
    embedding_dim = 384  # Размерность эмбеддингов
    embeddings = []
    
    # Генерируем похожие эмбеддинги для похожих документов
    base_embedding = np.random.randn(embedding_dim)
    
    # Положения (похожи друг на друга)
    embeddings.append(base_embedding + np.random.randn(embedding_dim) * 0.1)
    embeddings.append(base_embedding + np.random.randn(embedding_dim) * 0.1)
    
    # Инструкция (отличается от положений)
    embeddings.append(np.random.randn(embedding_dim))
    
    # Регламент (отличается от всех)
    embeddings.append(np.random.randn(embedding_dim))
    
    embeddings = np.array(embeddings)
    
    # Создаем кластеризатор
    clusterer = DocumentClusterer(eps=0.5, min_samples=2)
    
    # Выполняем кластеризацию
    clusters = clusterer.cluster_documents(embeddings, processed_docs)
    
    # Выводим результаты
    logger.info(f"\nНайдено {len(clusters)} кластеров:")
    for cluster in clusters:
        summary = clusterer.get_cluster_summary(cluster)
        logger.info("\nИнформация о кластере:")
        logger.info(f"ID кластера: {summary['cluster_id']}")
        logger.info(f"Размер: {summary['size']} документов")
        logger.info(f"Основной тип документов: {summary['main_document_type']}")
        logger.info(f"Распределение типов: {summary['document_types']}")
        
        logger.info("\nДокументы в кластере:")
        for doc in cluster['documents']:
            logger.info(f"- {doc['title']} (ID: {doc['document_id']})")
            
    # Создаем клиент OpenSearch
    opensearch_client = OpenSearch(**OPENSEARCH_CONFIG)
    
    # Создаем хранилище кластеров
    storage = ClusterStorage(opensearch_client)
    
    # Инициализируем индекс
    logger.info("\nИнициализация индекса в OpenSearch...")
    await storage.init_index()
    
    # Сохраняем кластеры
    logger.info("Сохранение кластеров в OpenSearch...")
    success = await storage.store_clusters(clusters)
    if success:
        logger.info("Кластеры успешно сохранены")
    else:
        logger.error("Ошибка при сохранении кластеров")
        return
        
    # Тестируем поиск кластера по эмбеддингу
    logger.info("\nТестирование поиска кластера по эмбеддингу...")
    test_embedding = embeddings[0].tolist()  # Используем первый документ как запрос
    found_cluster = await storage.find_cluster_for_embedding(test_embedding)
    
    if found_cluster:
        logger.info("Найден кластер:")
        logger.info(f"ID кластера: {found_cluster['cluster_id']}")
        logger.info(f"Количество документов: {len(found_cluster['documents'])}")
    else:
        logger.info("Подходящий кластер не найден")
        
    # Тестируем поиск похожих документов
    logger.info("\nТестирование поиска похожих документов...")
    query_embedding = embeddings[0]  # Используем первый документ как запрос
    similar_docs = clusterer.find_similar_documents(
        query_embedding,
        embeddings,
        processed_docs
    )
    
    logger.info("\nПохожие документы:")
    for doc in similar_docs:
        logger.info(f"- {doc['title']} (score: {doc['similarity_score']:.3f})")

if __name__ == "__main__":
    asyncio.run(test_clustering()) 