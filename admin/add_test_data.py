import asyncio
import logging
from sqlalchemy import select
from .core.database import async_session_maker
from .core.models import User, Document
from .core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_test_data():
    """Add test data to the database."""
    logger.info("Adding test data...")
    
    async with async_session_maker() as session:
        try:
            # Check if test user already exists
            result = await session.execute(select(User).where(User.username == "admin"))
            if result.scalar_one_or_none():
                logger.info("Test data already exists")
                return
            
            # Create test user
            test_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_admin=True
            )
            session.add(test_user)
            await session.commit()
            
            # Create test document
            test_document = Document(
                title="Test Document",
                content="This is a test document",
                file_path="/path/to/test/document.txt",
                file_type="txt",
                owner_id=test_user.id
            )
            session.add(test_document)
            await session.commit()
            
            logger.info("Test data added successfully!")
        except Exception as e:
            logger.error(f"Error adding test data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(add_test_data()) 