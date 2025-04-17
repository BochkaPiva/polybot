from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import MenuItem

class MenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_menu_items_by_level(self, level: int, parent_id: Optional[int] = None) -> List[MenuItem]:
        """Get menu items by level and optional parent ID"""
        query = select(MenuItem).where(MenuItem.level == level)
        if parent_id is not None:
            query = query.where(MenuItem.parent_id == parent_id)
        query = query.order_by(MenuItem.order)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_menu_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID"""
        return await self.session.get(MenuItem, item_id)
    
    async def create_menu_item(self, title: str, description: str = None, 
                              parent_id: int = None, level: int = 1, 
                              order: int = 0, content: str = None,
                              media_urls: dict = None) -> MenuItem:
        """Create a new menu item"""
        menu_item = MenuItem(
            title=title,
            description=description,
            parent_id=parent_id,
            level=level,
            order=order,
            content=content,
            media_urls=media_urls
        )
        self.session.add(menu_item)
        await self.session.commit()
        await self.session.refresh(menu_item)
        return menu_item
    
    async def update_menu_item(self, item_id: int, **kwargs) -> Optional[MenuItem]:
        """Update menu item"""
        menu_item = await self.get_menu_item_by_id(item_id)
        if not menu_item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(menu_item, key):
                setattr(menu_item, key, value)
        
        await self.session.commit()
        await self.session.refresh(menu_item)
        return menu_item
    
    async def delete_menu_item(self, item_id: int) -> bool:
        """Delete menu item"""
        menu_item = await self.get_menu_item_by_id(item_id)
        if not menu_item:
            return False
        
        await self.session.delete(menu_item)
        await self.session.commit()
        return True
