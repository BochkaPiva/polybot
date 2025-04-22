import asyncio
import os
from .core.database import get_async_session
from .core.models import User
from .core.security import get_password_hash
from sqlalchemy import select

async def init_admin():
    session = await get_async_session()
    
    # Get admin credentials from environment variables
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # In production, this should be set
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    
    # Check if admin user exists
    query = select(User).where(User.username == admin_username)
    result = await session.execute(query)
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        # Create admin user
        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_admin=True
        )
        session.add(admin_user)
        await session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(init_admin()) 