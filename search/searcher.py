import logging
from typing import List, Dict, Any

from search.client import OpenSearchClient

logger = logging.getLogger(__name__)

class DocumentSearcher:
    """Class for searching documents"""
    
    def __init__(self):
        """Initialize document searcher"""
        self.client = OpenSearchClient()
    
    async def search(self, query: str, size: int = 5) -> List[Dict[str, Any]]:
        """Search for documents"""
        response = await self.client.search(query, size)
        if not response:
            return []
        
        results = []
        for hit in response['hits']['hits']:
            result = {
                'id': hit['_source']['id'],
                'title': hit['_source']['title'],
                'score': hit['_score'],
                'highlights': []
            }
            
            # Add highlights
            if 'highlight' in hit:
                if 'title' in hit['highlight']:
                    result['highlights'].extend(hit['highlight']['title'])
                if 'content' in hit['highlight']:
                    result['highlights'].extend(hit['highlight']['content'])
            
            results.append(result)
        
        return results
    
    async def close(self):
        """Close client connection"""
        await self.client.close()