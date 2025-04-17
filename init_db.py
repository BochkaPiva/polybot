import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from config import BOT_TOKEN
from db.base import init_db, async_session
from db.models import User, MenuItem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def create_initial_users():
    """Create initial users"""
    async with async_session() as session:
        # Check if users already exist
        async with session.begin():
            # Create test user
            test_user = User(
                telegram_id=0,  # Will be updated when user logs in
                full_name="Иванов Иван Иванович",
                auth_code="123456",
                is_authenticated=False
            )
            session.add(test_user)
            
            # Add more users as needed
            
            logger.info("Initial users created")

async def create_initial_menu():
    """Create initial menu structure"""
    async with async_session() as session:
        async with session.begin():
            # Create first level menu items
            general_info = MenuItem(
                title="Общая информация",
                description="Общая информация о предприятии",
                level=1,
                order=1
            )
            session.add(general_info)
            
            contacts = MenuItem(
                title="Контакты",
                description="Контактная информация",
                level=1,
                order=2
            )
            session.add(contacts)
            
            faq = MenuItem(
                title="Часто задаваемые вопросы",
                description="Ответы на часто задаваемые вопросы",
                level=1,
                order=3
            )
            session.add(faq)
            
            # Commit to get IDs
            await session.commit()
            
            # Create second level menu items for general info
            history = MenuItem(
                title="История предприятия",
                description="История создания и развития предприятия",
                parent_id=general_info.id,
                level=2,
                order=1,
                content="ООО «Полиом» — совместное предприятие ГК «Титан», «Газпром нефти» и СИБУРа. Завод производит полипропилен под торговой маркой SIBEX."
            )
            session.add(history)
            
            mission = MenuItem(
                title="Миссия и ценности",
                description="Миссия и ценности предприятия",
                parent_id=general_info.id,
                level=2,
                order=2,
                content="Миссия предприятия: производство качественной продукции для удовлетворения потребностей клиентов."
            )
            session.add(mission)
            
            # Create second level menu items for contacts
            address = MenuItem(
                title="Адрес",
                description="Адрес предприятия",
                parent_id=contacts.id,
                level=2,
                order=1,
                content="644035, Россия, г. Омск, Красноярский тракт, 137"
            )
            session.add(address)
            
            phone = MenuItem(
                title="Телефон",
                description="Контактные телефоны",
                parent_id=contacts.id,
                level=2,
                order=2,
                content="Приемная: +7 (3812) 79-02-07\nОтдел кадров: +7 (3812) 79-02-09"
            )
            session.add(phone)
            
            # Create second level menu items for FAQ
            work_faq = MenuItem(
                title="Вопросы о работе",
                description="Часто задаваемые вопросы о работе",
                parent_id=faq.id,
                level=2,
                order=1,
                content="Здесь будут ответы на часто задаваемые вопросы о работе."
            )
            session.add(work_faq)
            
            products_faq = MenuItem(
                title="Вопросы о продукции",
                description="Часто задаваемые вопросы о продукции",
                parent_id=faq.id,
                level=2,
                order=2,
                content="Здесь будут ответы на часто задаваемые вопросы о продукции."
            )
            session.add(products_faq)
            
            logger.info("Initial menu created")

async def main():
    """Initialize database and create initial data"""
    logger.info("Initializing database...")
    await init_db()
    
    logger.info("Creating initial users...")
    await create_initial_users()
    
    logger.info("Creating initial menu...")
    await create_initial_menu()
    
    logger.info("Database initialization completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")