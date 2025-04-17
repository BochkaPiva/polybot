from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os
from datetime import datetime

from db.models import Document

class DocumentRepository:
    def __init__(self, session: AsyncSession, upload_dir: str = "uploads"):
        self.session = session
        self.upload_dir = upload_dir
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def get_all_documents(self) -> List[Document]:
        """Get all documents"""
        result = await self.session.execute(select(Document))
        return result.scalars().all()
    
    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return await self.session.get(Document, document_id)
    
    async def create_document(self, title: str, description: str, file_path: str, file_type: str) -> Document:
        """Create a new document"""
        document = Document(
            title=title,
            description=description,
            file_path=file_path,
            file_type=file_type,
            indexed=False
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document
    
    async def update_document(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document"""
        document = await self.get_document_by_id(document_id)
        if not document:
            return None
        
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        document.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(document)
        return document
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete document"""
        document = await self.get_document_by_id(document_id)
        if not document:
            return False
        
        # Delete file if it exists
        file_path = os.path.join(self.upload_dir, document.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await self.session.delete(document)
        await self.session.commit()
        return True
    
    async def save_file(self, file, filename: str) -> str:
        """Save file to disk and return relative path"""
        # Generate unique filename to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file.read())
        
        return unique_filename