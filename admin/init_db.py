import asyncio
from sqlalchemy import text
from admin.core.database import engine, Base
from admin.core.models import User

async def init_db():
    async with engine.begin() as conn:
        # Drop existing tables
        await conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))
        
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        
        print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db()) 