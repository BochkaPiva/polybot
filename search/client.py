import logging
from opensearchpy import AsyncOpenSearch, RequestsHttpConnection

from config import (
    OPENSEARCH_HOST,
    OPENSEARCH_PORT,
    OPENSEARCH_USER,
    OPENSEARCH_PASS,
    OPENSEARCH_INDEX
)

logger = logging.getLogger(__name__)

class SearchClient:
    def __init__(self):
        self.client = AsyncOpenSearch(
            hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False,
        )
        self.index = OPENSEARCH_INDEX

    async def init_index(self):
        """Инициализация индекса OpenSearch"""
        if not await self.client.indices.exists(index=self.index):
            await self.client.indices.create(
                index=self.index,
                body={
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "russian": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "russian_morphology", "english_morphology"]
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "title": {"type": "text", "analyzer": "russian"},
                            "content": {"type": "text", "analyzer": "russian"},
                            "tags": {"type": "keyword"},
                            "file_type": {"type": "keyword"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
            )

    async def index_document(self, doc_id: int, title: str, content: str, tags: list, file_type: str):
        """Индексация документа"""
        await self.client.index(
            index=self.index,
            id=str(doc_id),
            body={
                "title": title,
                "content": content,
                "tags": tags,
                "file_type": file_type,
                "created_at": "now"
            }
        )

    async def search(self, query: str, size: int = 10):
        """Поиск по документам"""
        response = await self.client.search(
            index=self.index,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "content"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": size
            }
        )
        return response['hits']['hits']

    async def delete_document(self, doc_id: int):
        """Удаление документа из индекса"""
        await self.client.delete(index=self.index, id=str(doc_id))

# Создаем глобальный экземпляр клиента
search_client = SearchClient()