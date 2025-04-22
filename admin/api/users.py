from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
from datetime import datetime
from ..core.database import get_async_session
from ..core.schemas import UserResponse, UserCreate, UserUpdate
from ..core.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

def serialize_user(user: User) -> dict:
    """Сериализует объект пользователя в словарь с правильной обработкой дат"""
    return {
        "id": user.id,
        "full_name": user.full_name,
        "department": user.department,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session)
):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return [serialize_user(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user)

@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        logger.info(f"Received user data: {user_create.dict()}")
        user = User(
            full_name=user_create.full_name,
            department=user_create.department
        )
        logger.info(f"Creating user with data: {user.full_name}, {user.department}")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Successfully created user with id: {user.id}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=serialize_user(user)
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating user: {error_msg}")
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Failed to create user: {error_msg}"}
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return serialize_user(user)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error updating user: {error_msg}")
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Failed to update user: {error_msg}"}
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return None 