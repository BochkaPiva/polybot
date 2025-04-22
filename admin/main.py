from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
from fastapi.responses import HTMLResponse, RedirectResponse

# Add the admin directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from admin.core.config import settings
    from admin.core.database import get_async_session, init_db
    from admin.core.models import User, Document, Chat
    from admin.core.schemas import UserResponse, DocumentResponse, ChatResponse
    from admin.api import auth, users, documents, admin
except ImportError as e:
    print(f"Error importing modules: {e}")
    raise

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="admin/static"), name="static")

# Mount templates directory
templates = Jinja2Templates(directory="admin/templates")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

@app.get("/")
async def root():
    return RedirectResponse(url="/admin/login")

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=List[DocumentResponse])
async def get_documents(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(Document))
        documents = result.scalars().all()
        return documents
    except Exception as e:
        print(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats", response_model=List[ChatResponse])
async def get_chats(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(Chat))
        chats = result.scalars().all()
        return chats
    except Exception as e:
        print(f"Error getting chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template routes
@app.get("/admin/users", response_class=HTMLResponse)
async def users_page(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "settings": settings
        }
    )

@app.get("/admin/documents", response_class=HTMLResponse)
async def documents_page(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Document))
    documents = result.scalars().all()
    return templates.TemplateResponse("documents.html", {"request": request, "documents": documents})

@app.get("/admin/chats", response_class=HTMLResponse)
async def chats_page(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Chat))
    chats = result.scalars().all()
    return templates.TemplateResponse("chats.html", {"request": request, "chats": chats}) 