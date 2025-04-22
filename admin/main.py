from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from .core.database import get_async_session
from .core.models import User, Document
from .api import users, documents

# Создаем директорию для загрузки файлов, если она не существует
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Admin Panel")

# Монтируем статическую директорию для загрузки файлов
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Подключаем шаблоны
templates = Jinja2Templates(directory="admin/templates")

# Добавляем вспомогательные функции для шаблонов
def get_file_icon(file_type: str) -> str:
    """Возвращает класс иконки Font Awesome в зависимости от типа файла"""
    if not file_type:
        return "fa-file"
        
    file_type = file_type.lower()
    if file_type.startswith("image/"):
        return "fa-file-image"
    elif file_type == "application/pdf":
        return "fa-file-pdf"
    elif file_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return "fa-file-word"
    elif file_type == "text/plain":
        return "fa-file-alt"
    elif file_type.startswith("video/"):
        return "fa-file-video"
    elif file_type.startswith("audio/"):
        return "fa-file-audio"
    else:
        return "fa-file"

def get_file_color(file_type: str) -> str:
    """Возвращает класс цвета Bootstrap в зависимости от типа файла"""
    if not file_type:
        return "secondary"
        
    file_type = file_type.lower()
    if file_type.startswith("image/"):
        return "success"
    elif file_type == "application/pdf":
        return "danger"
    elif file_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return "primary"
    elif file_type == "text/plain":
        return "info"
    elif file_type.startswith("video/"):
        return "warning"
    elif file_type.startswith("audio/"):
        return "warning"
    else:
        return "secondary"

def is_previewable(file_type: str) -> bool:
    """Проверяет, можно ли предварительно просмотреть файл"""
    if not file_type:
        return False
        
    file_type = file_type.lower()
    return (
        file_type.startswith("image/") or
        file_type == "application/pdf" or
        file_type == "text/plain"
    )

# Добавляем функции в контекст шаблонов
templates.env.globals.update({
    "get_file_icon": get_file_icon,
    "get_file_color": get_file_color,
    "is_previewable": is_previewable
})

# Подключаем роутеры
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# Настройки для шаблонов
TEMPLATE_SETTINGS = {
    "site_name": "Admin Panel",
    "site_description": "Управление пользователями и документами"
}

@app.get("/")
async def root(request: Request, db: AsyncSession = Depends(get_async_session)):
    # Получаем количество пользователей
    users_query = select(User)
    users_result = await db.execute(users_query)
    users_count = len(users_result.scalars().all())
    
    # Получаем количество документов
    documents_query = select(Document)
    documents_result = await db.execute(documents_query)
    documents_count = len(documents_result.scalars().all())
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "settings": TEMPLATE_SETTINGS,
            "users_count": users_count,
            "documents_count": documents_count
        }
    )

@app.get("/users")
async def users_page(request: Request, db: AsyncSession = Depends(get_async_session)):
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