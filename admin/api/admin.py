from fastapi import APIRouter, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..core import security
from ..core.database import get_async_session
from ..core.models import User, Document, Chat
from ..core.schemas import UserResponse, DocumentResponse, ChatResponse
from ..core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="admin/templates")

@router.get("/")
async def admin_root():
    return RedirectResponse(url="/admin/dashboard")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "settings": settings
        }
    )

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_session)
):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    if not username or not password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Username and password are required",
                "settings": settings
            }
        )
    
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not security.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password",
                "settings": settings
            }
        )
    
    if not user.is_active:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "User is inactive",
                "settings": settings
            }
        )
    
    if not user.is_admin:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "User is not an admin",
                "settings": settings
            }
        )
    
    # Create JWT token
    access_token = security.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,  # Set to True in production
        samesite="lax"
    )
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@router.get("/dashboard")
async def dashboard(
    request: Request,
    current_user: User = Depends(security.get_current_active_admin)
):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "current_user": current_user,
            "settings": settings
        }
    )

@router.get("/users")
async def users_page(
    request: Request,
    current_user: User = Depends(security.get_current_active_admin),
    db: AsyncSession = Depends(get_async_session)
):
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "current_user": current_user,
            "settings": settings,
            "users": users
        }
    )

@router.get("/documents")
async def documents_page(
    request: Request,
    current_user: User = Depends(security.get_current_active_admin),
    db: AsyncSession = Depends(get_async_session)
):
    query = select(Document)
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return templates.TemplateResponse(
        "documents.html",
        {
            "request": request,
            "current_user": current_user,
            "settings": settings,
            "documents": documents
        }
    )

@router.get("/chats")
async def chats_page(
    request: Request,
    current_user: User = Depends(security.get_current_active_admin),
    db: AsyncSession = Depends(get_async_session)
):
    query = select(Chat)
    result = await db.execute(query)
    chats = result.scalars().all()
    
    return templates.TemplateResponse(
        "chats.html",
        {
            "request": request,
            "current_user": current_user,
            "settings": settings,
            "chats": chats
        }
    ) 