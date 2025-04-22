import asyncio
import logging
from sqlalchemy import text
from admin.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_table():
    try:
        async with engine.connect() as conn:
            # Get column information
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'documents'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            logger.info("Columns in documents table:")
            for col in columns:
                logger.info(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
            
            # Get row count
            result = await conn.execute(text("SELECT COUNT(*) FROM documents"))
            count = result.scalar()
            logger.info(f"\nTotal documents in table: {count}")
            
    except Exception as e:
        logger.error(f"Error checking table: {e}")

if __name__ == "__main__":
    asyncio.run(check_table()) 