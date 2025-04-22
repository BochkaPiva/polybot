from typing import List, Dict, Any, Optional
import logging
from opensearchpy import AsyncOpenSearch
from opensearchpy.helpers import bulk
from admin.core.config import settings
from datetime import datetime
from search.text_cleaner import TextCleaner
from search.embeddings import embedding_generator

logger = logging.getLogger(__name__)

class OpenSearchClient:
    """Класс для работы с OpenSearch."""
    
    def __init__(self):
        """Инициализация клиента OpenSearch."""
        self.client = AsyncOpenSearch(
            hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASS),
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False,
        )
        self.index = settings.OPENSEARCH_INDEX
        self.text_cleaner = TextCleaner()
        self.embedding_generator = embedding_generator
        
    async def create_index(self):
        """Create the OpenSearch index if it doesn't exist"""
        try:
            if not await self.client.indices.exists(index=self.index):
                await self.client.indices.create(
                    index=self.index,
                    body={
                        "settings": {
                            "analysis": {
                                "analyzer": {
                                    "default": {
                                        "type": "russian"
                                    }
                                }
                            }
                        },
                        "mappings": {
                            "properties": {
                                "content": {
                                    "type": "text",
                                    "analyzer": "russian"
                                },
                                "title": {
                                    "type": "text",
                                    "analyzer": "russian"
                                },
                                "file_path": {
                                    "type": "keyword"
                                },
                                "file_type": {
                                    "type": "keyword"
                                },
                                "embedding": {
                                    "type": "knn_vector",
                                    "dimension": 1024,
                                    "method": {
                                        "name": "hnsw",
                                        "space_type": "cosinesimil",
                                        "engine": "nmslib"
                                    }
                                }
                            }
                        }
                    }
                )
                logger.info(f"Created OpenSearch index: {self.index}")
            else:
                logger.info(f"OpenSearch index {self.index} already exists")
        except Exception as e:
            logger.error(f"Error creating OpenSearch index: {str(e)}")
            raise
            
    async def index_document(self, doc_id: str, title: str, content: str, file_path: str):
        """Индексация документа в OpenSearch"""
        try:
            # Очищаем и нормализуем текст
            cleaned_content = self.text_cleaner.clean_text(content)
            
            # Формируем документ для индексации
            document = {
                'title': title,
                'content': cleaned_content,
                'file_path': file_path,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Добавляем эмбеддинг, если он доступен
            try:
                embedding = self.embedding_generator.generate_embedding(cleaned_content)
                if embedding is not None:
                    document['embedding'] = embedding
            except Exception as e:
                logger.warning(f"Не удалось сгенерировать эмбеддинг для документа {doc_id}: {str(e)}")
            
            # Индексируем документ
            response = await self.client.index(
                index=self.index,
                id=doc_id,
                body=document
            )
            
            logger.info(f"Документ {doc_id} успешно проиндексирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при индексации документа {doc_id}: {str(e)}")
            return False
            
    async def bulk_index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Массовая индексация документов.
        
        Args:
            documents: Список документов для индексации
            
        Returns:
            True, если все документы проиндексированы успешно
        """
        try:
            actions = [
                {
                    "_index": self.index,
                    "_id": doc["chunk_id"],
                    "_source": doc
                }
                for doc in documents
            ]
            success, failed = bulk(self.client, actions)
            if failed:
                logger.warning(f"Не удалось проиндексировать {len(failed)} документов")
            return success > 0
        except Exception as e:
            logger.error(f"Ошибка при массовой индексации: {str(e)}")
            return False
            
    async def search(self, query: dict = None, size: int = 10, highlight: dict = None) -> Dict:
        """Search for documents"""
        try:
            body = {
                "size": size,
                "query": query
            }
            
            if highlight:
                body["highlight"] = highlight
            
            response = await self.client.search(
                index=self.index,
                body=body
            )
            return response
        except Exception as e:
            logger.error(f"Error searching OpenSearch: {str(e)}")
            return {"hits": {"hits": []}}
            
    async def delete_document(self, doc_id: str):
        """Delete a document from OpenSearch"""
        try:
            await self.client.delete(
                index=self.index,
                id=doc_id
            )
            logger.info(f"Deleted document {doc_id} from OpenSearch")
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            raise

    async def recreate_index(self) -> bool:
        """
        Recreate the OpenSearch index.
        
        Returns:
            True if the index was recreated successfully
        """
        try:
            if await self.client.indices.exists(index=self.index):
                await self.client.indices.delete(index=self.index)
                logger.info(f"Index {self.index} deleted")
            return await self.create_index()
        except Exception as e:
            logger.error(f"Error recreating index: {str(e)}")
            raise

    async def close(self):
        """Close the OpenSearch client"""
        await self.client.close()

# Create client instance
opensearch_client = OpenSearchClient() 