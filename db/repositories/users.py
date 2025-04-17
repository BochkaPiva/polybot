from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import random
import string

from db.models import User, AuthAttempt

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Get user by Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalars().first()
    
    async def get_user_by_full_name(self, full_name: str) -> User:
        """Get user by full name"""
        result = await self.session.execute(
            select(User).where(User.full_name == full_name)
        )
        return result.scalars().first()
    
    async def create_user(self, telegram_id: int, full_name: str, username: str = None) -> User:
        """Create a new user"""
        auth_code = self._generate_auth_code()
        user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            auth_code=auth_code,
            is_authenticated=False
        )
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError:
            await self.session.rollback()
            return None
    
    async def authenticate_user(self, user_id: int, success: bool = True) -> bool:
        """Mark user as authenticated and record the attempt"""
        user = await self.session.get(User, user_id)
        if not user:
            return False
        
        # Record authentication attempt
        auth_attempt = AuthAttempt(user_id=user.id, success=success)
        self.session.add(auth_attempt)
        
        if success:
            user.is_authenticated = True
        
        await self.session.commit()
        return True
    
    async def record_failed_attempt(self, user_id: int) -> int:
        """Record failed authentication attempt and return count of recent failures"""
        auth_attempt = AuthAttempt(user_id=user_id, success=False)
        self.session.add(auth_attempt)
        await self.session.commit()
        
        # Count recent failed attempts (could add time window)
        result = await self.session.execute(
            select(AuthAttempt)
            .where(AuthAttempt.user_id == user_id, AuthAttempt.success == False)
        )
        return len(result.scalars().all())
    
    def _generate_auth_code(self, length: int = 6) -> str:
        """Generate random authentication code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
