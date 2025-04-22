from .client import SearchClient, search_client
from .indexer import DocumentIndexer
from .searcher import DocumentSearcher
from .service import SearchService

# Создаем глобальный экземпляр сервиса
search_service = SearchService()

__all__ = ['SearchClient', 'search_client', 'DocumentIndexer', 'DocumentSearcher', 'search_service']