import logging
from typing import List, Dict, Any

from search.client import SearchClient, search_client

logger = logging.getLogger(__name__)

class DocumentSearcher:
    """Class for searching documents"""
    
    def __init__(self):
        """Initialize document searcher"""
        self.client = search_client
    
    async def search(self, query: str, size: int = 5) -> List[Dict[str, Any]]:
        """Search for documents"""
        try:
            hits = await self.client.search(query, size)
            results = []
            
            for hit in hits:
                result = {
                    'id': hit['_id'],
                    'title': hit['_source']['title'],
                    'score': hit['_score'],
                    'content': hit['_source']['content'][:200] + '...' if len(hit['_source']['content']) > 200 else hit['_source']['content']
                }
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def close(self):
        """Close client connection"""
        await self.client.close()