import asyncio
import logging
from datetime import datetime

from admin.core.database import async_session_maker
from admin.core.models import User, Document, Chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_test_data():
    try:
        async with async_session_maker() as session:
            # Создаем тестового пользователя
            test_user = User(
                unique_id="123456789",
                username="test_user",
                first_name="Test",
                last_name="User",
                is_active=True,
                is_admin=True
            )
            session.add(test_user)
            await session.flush()
            logger.info(f"Created test user with ID: {test_user.id}")

            # Создаем тестовый документ
            test_doc = Document(
                title="Test Document",
                content="This is a test document content",
                file_path="/path/to/test.pdf",
                file_type="pdf"
            )
            session.add(test_doc)
            await session.flush()
            logger.info(f"Created test document with ID: {test_doc.id}")

            # Создаем тестовый чат
            test_chat = Chat(
                user_id=test_user.id,
                message="Hello, bot!",
                response="Hello, user!"
            )
            session.add(test_chat)
            await session.commit()
            logger.info(f"Created test chat with ID: {test_chat.id}")

            logger.info("Test data added successfully!")

    except Exception as e:
        logger.error(f"Error adding test data: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(add_test_data()) 