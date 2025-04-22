import logging
from opensearchpy import AsyncOpenSearch, RequestsHttpConnection
import asyncio
from datetime import datetime
import numpy as np
import os

from admin.core.config import settings

logger = logging.getLogger(__name__)

class SearchClient:
    def __init__(self):
        """Инициализация клиента OpenSearch"""
        from search.opensearch_client import opensearch_client
        self.client = opensearch_client
        self.index = settings.OPENSEARCH_INDEX

    async def init_index(self):
        """Инициализация индекса"""
        await self.client.create_index()

    async def index_document(self, doc_id: int, title: str, content: str, tags: list, file_type: str, embedding: list = None):
        """Индексация документа"""
        await self.client.index_document(
            doc_id=str(doc_id),
            title=title,
            content=content,
            file_path=file_type
        )

    async def semantic_search(self, query: str, size: int = 10):
        """Семантический поиск по документам"""
        from search.embeddings import embedding_generator
        
        # Генерируем эмбеддинг для запроса
        query_embedding = embedding_generator.generate_embedding(query)
        
        results = await self.client.search(
            query={
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": size
                    }
                }
            },
            size=size
        )
        return results if isinstance(results, list) else results.get('hits', {}).get('hits', [])

    async def text_search(self, query: str, size: int = 10):
        """Текстовый поиск по документам"""
        # Нормализуем запрос
        query = query.lower().strip()
        
        results = await self.client.search(
            query={
                "bool": {
                    "should": [
                        {
                            "match": {
                                "title": {
                                    "query": query,
                                    "boost": 2,
                                    "fuzziness": "AUTO"
                                }
                            }
                        },
                        {
                            "match": {
                                "content": {
                                    "query": query,
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            size=size,
            highlight={
                "fields": {
                    "content": {},
                    "title": {}
                }
            }
        )
        
        # Обрабатываем результаты
        hits = results.get('hits', {}).get('hits', [])
        processed_hits = []
        
        for hit in hits:
            score = hit.get('_score', 0)
            source = hit.get('_source', {})
            highlight = hit.get('highlight', {})
            
            # Формируем фрагмент текста с подсветкой
            content_highlights = highlight.get('content', [])
            title_highlights = highlight.get('title', [])
            
            processed_hit = {
                'score': score,
                'title': source.get('title', ''),
                'content': '...'.join(content_highlights) if content_highlights else source.get('content', '')[:200],
                'file_type': source.get('file_path', '')
            }
            
            processed_hits.append(processed_hit)
            
        return processed_hits

    async def delete_document(self, doc_id: int):
        """Удаление документа"""
        await self.client.delete_document(str(doc_id))

    async def close(self):
        """Закрытие клиента"""
        await self.client.close()

# Создаем глобальный экземпляр клиента
search_client = SearchClient()