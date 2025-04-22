from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import shutil
from ..core import security
from ..core.database import get_async_session
from ..core.schemas import DocumentResponse, DocumentCreate, DocumentUpdate
from ..core.models import Document, User
from ..core.config import settings

router = APIRouter()

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).offset(skip).limit(limit)
    result = await db.execute(query)
    documents = result.scalars().all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/", response_model=DocumentResponse)
async def create_document(
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    # Check file type
    file_type = file.filename.split(".")[-1].lower()
    if file_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document record
    document = Document(
        title=title,
        file_path=file_path,
        file_type=file_type
        # Temporarily disabled owner_id
        # owner_id=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update document fields
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(document, field, value)
    
    await db.commit()
    await db.refresh(document)
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file if exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    await db.delete(document)
    await db.commit()
    return None 