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

class OpenSearchClient:
    """Client for OpenSearch operations"""
    
    def __init__(self):
        """Initialize OpenSearch client"""
        self.client = AsyncOpenSearch(
            hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS) if OPENSEARCH_USER and OPENSEARCH_PASS else None,
            use_ssl=False,
            verify_certs=False,
            connection_class=RequestsHttpConnection
        )
        self.index = OPENSEARCH_INDEX
    
    async def create_index(self):
        """Create index if it doesn't exist"""
        try:
            if not await self.client.indices.exists(index=self.index):
                await self.client.indices.create(
                    index=self.index,
                    body={
                        "settings": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0,
                            "analysis": {
                                "analyzer": {
                                    "russian_analyzer": {
                                        "type": "custom",
                                        "tokenizer": "standard",
                                        "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                                    }
                                },
                                "filter": {
                                    "russian_stop": {
                                        "type": "stop",
                                        "stopwords": "_russian_"
                                    },
                                    "russian_stemmer": {
                                        "type": "stemmer",
                                        "language": "russian"
                                    }
                                }
                            }
                        },
                        "mappings": {
                            "properties": {
                                "id": {"type": "integer"},
                                "title": {
                                    "type": "text",
                                    "analyzer": "russian_analyzer"
                                },
                                "content": {
                                    "type": "text",
                                    "analyzer": "russian_analyzer"
                                },
                                "file_type": {"type": "keyword"},
                                "created_at": {"type": "date"},
                                "updated_at": {"type": "date"}
                            }
                        }
                    }
                )
                logger.info(f"Index {self.index} created")
            else:
                logger.info(f"Index {self.index} already exists")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    async def index_document(self, doc_id, document):
        """Index a document"""
        try:
            await self.client.index(
                index=self.index,
                id=doc_id,
                body=document,
                refresh=True
            )
            logger.info(f"Document {doc_id} indexed")
            return True
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {e}")
            return False
    
    async def search(self, query, size=5):
        """Search for documents"""
        try:
            response = await self.client.search(
                index=self.index,
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^2", "content"],
                            "fuzziness": "AUTO"
                        }
                    },
                    "highlight": {
                        "fields": {
                            "title": {},
                            "content": {}
                        }
                    }
                },
                size=size
            )
            return response
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return None
    
    async def delete_document(self, doc_id):
        """Delete a document"""
        try:
            await self.client.delete(
                index=self.index,
                id=doc_id,
                refresh=True
            )
            logger.info(f"Document {doc_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    async def update_document(self, doc_id, document):
        """Update a document"""
        try:
            await self.client.update(
                index=self.index,
                id=doc_id,
                body={"doc": document},
                refresh=True
            )
            logger.info(f"Document {doc_id} updated")
            return True
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False
    
    async def close(self):
        """Close client connection"""
        await self.client.close()