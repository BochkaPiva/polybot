import asyncio
from search.client import search_client

async def test_search():
    query = "Расчет премии"
    print(f"\nSemantic search results for '{query}':")
    
    semantic_results = await search_client.semantic_search(query)
    for hit in semantic_results:
        source = hit.get('_source', {})
        print(f"\nScore: {hit.get('_score', 0)}")
        print(f"Title: {source.get('title', 'No title')}")
        content = source.get('content', '')[:200] + '...' if source.get('content') else 'No content'
        print(f"Content: {content}")
        print(f"File: {source.get('file_path', 'No file type')}")
    
    print(f"\nText search results for '{query}':")
    
    text_results = await search_client.text_search(query)
    for hit in text_results:
        print(f"\nScore: {hit['score']}")
        print(f"Title: {hit['title']}")
        content = hit['content']
        print(f"Content: {content}")
        print(f"File: {hit['file_type']}")
    
    await search_client.close()

if __name__ == "__main__":
    asyncio.run(test_search()) 