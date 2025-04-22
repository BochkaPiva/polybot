from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from config import DATABASE_URL
from db.models import Base

# Create SQLAlchemy engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Включаем логирование SQL-запросов только в режиме отладки
    future=True
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create declarative base
Base = declarative_base()

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        # Проверяем существование базы данных
        result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'poliom_bot'"))
        if not result.scalar():
            await conn.execute(text("CREATE DATABASE poliom_bot"))
        
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
