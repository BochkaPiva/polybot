import asyncio
import logging
from search.client import OpenSearchClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize OpenSearch index"""
    logger.info("Initializing OpenSearch index...")
    client = OpenSearchClient()
    
    try:
        await client.create_index()
        logger.info("OpenSearch index initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing OpenSearch index: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error during OpenSearch initialization: {e}")