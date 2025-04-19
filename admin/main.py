from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from admin.core.database import get_async_session
from admin.core.models import User, Document, Chat
from admin.core.schemas import UserResponse, DocumentResponse, ChatResponse

app = FastAPI(title="PolyBot Admin API")

@app.get("/")
async def root():
    return {"message": "PolyBot Admin API is running"}

@app.get("/users", response_model=List[UserResponse])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(Document))
        documents = result.scalars().all()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats", response_model=List[ChatResponse])
async def get_chats(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(Chat))
        chats = result.scalars().all()
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 