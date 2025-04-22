from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .core.database import get_async_session
from .core.models import User, Document
from .api import users, documents

# Базовые настройки для шаблонов
TEMPLATE_SETTINGS = {
    "PROJECT_NAME": "PolyBot Admin"
}

app = FastAPI(title="Admin Panel")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="admin/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="admin/templates")

# Подключаем роутеры
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

@app.get("/")
async def index(request: Request, db: AsyncSession = Depends(get_async_session)):
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "settings": TEMPLATE_SETTINGS
        }
    )

@app.get("/documents")
async def documents_page(request: Request, db: AsyncSession = Depends(get_async_session)):
    query = select(Document)
    result = await db.execute(query)
    documents = result.scalars().all()
    return templates.TemplateResponse(
        "documents.html",
        {
            "request": request,
            "documents": documents,
            "settings": TEMPLATE_SETTINGS
        }
    ) 