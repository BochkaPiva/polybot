from typing import List, Dict, Any, Optional
import logging
from .document_processor import DocumentProcessor
from .opensearch_client import OpenSearchClient
from admin.core.config import settings

class SearchService:
    """Сервис для работы с документами и поиском."""
    
    def __init__(self):
        """Инициализация сервиса."""
        self.logger = logging.getLogger(__name__)
        self.processor = DocumentProcessor()
        self.opensearch = OpenSearchClient()
        
    def initialize(self) -> bool:
        """
        Инициализация сервиса и создание индекса.
        
        Returns:
            True, если инициализация прошла успешно
        """
        try:
            return self.opensearch.create_index()
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации сервиса: {str(e)}")
            return False
            
    async def index_document(self, document_id: int, title: str, content: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Обработка и индексация документа.
        
        Args:
            document_id: ID документа
            title: Заголовок документа
            content: Содержимое документа
            metadata: Дополнительные метаданные
            
        Returns:
            True, если документ успешно проиндексирован
        """
        try:
            self.logger.info(f"Начало индексации документа {document_id}")
            
            # Обрабатываем документ
            chunks = await self.processor.process_document(
                document_id=document_id,
                title=title,
                content=content,
                metadata=metadata
            )
            
            if not chunks:
                self.logger.error(f"Не удалось обработать документ {document_id}")
                return False
                
            self.logger.info(f"Документ {document_id} разбит на {len(chunks)} чанков")
            
            # Индексируем чанки
            success = await self.opensearch.index_document(document_id, chunks)
            
            if success:
                self.logger.info(f"Документ {document_id} успешно проиндексирован")
            else:
                self.logger.error(f"Не удалось проиндексировать документ {document_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при индексации документа {document_id}: {str(e)}", exc_info=True)
            return False
            
    def search(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск документов по запросу.
        
        Args:
            query: Поисковый запрос
            size: Количество результатов
            
        Returns:
            Список найденных документов
        """
        try:
            return self.opensearch.search(query, size)
        except Exception as e:
            self.logger.error(f"Ошибка при поиске: {str(e)}")
            return []
            
    def delete_document(self, document_id: int) -> bool:
        """
        Удаление документа из индекса.
        
        Args:
            document_id: ID документа
            
        Returns:
            True, если документ успешно удален
        """
        try:
            return self.opensearch.delete_document(document_id)
        except Exception as e:
            self.logger.error(f"Ошибка при удалении документа {document_id}: {str(e)}")
            return False
            
    def reindex_document(self, document_id: int, title: str, content: str,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Переиндексация документа.
        
        Args:
            document_id: ID документа
            title: Заголовок документа
            content: Содержимое документа
            metadata: Дополнительные метаданные
            
        Returns:
            True, если документ успешно переиндексирован
        """
        try:
            # Сначала удаляем старые данные
            if not self.delete_document(document_id):
                return False
                
            # Затем индексируем заново
            return self.index_document(document_id, title, content, metadata)
            
        except Exception as e:
            self.logger.error(f"Ошибка при переиндексации документа {document_id}: {str(e)}")
            return False 