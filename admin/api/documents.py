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

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).where(Document.id == doc_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/", response_model=DocumentResponse)
async def create_document(
    doc_create: DocumentCreate,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    document = Document(
        title=doc_create.title,
        content=doc_create.content
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document

@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    doc_update: DocumentUpdate,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).where(Document.id == doc_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = doc_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    await db.commit()
    await db.refresh(document)
    return document

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_async_session)
    # Temporarily disabled authentication
    # current_user: User = Depends(security.get_current_active_admin)
):
    query = select(Document).where(Document.id == doc_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.delete(document)
    await db.commit()
    return None 