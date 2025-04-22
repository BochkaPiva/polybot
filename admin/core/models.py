from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from admin.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Добавляем связь с документами
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)  # Оригинальное имя файла
    system_filename = Column(String, nullable=False)    # Системное имя файла (с уникальным идентификатором)
    file_type = Column(String)                         # MIME-тип файла
    file_size = Column(Integer)                        # Размер в байтах
    content_text = Column(Text)                        # Извлеченный текст для поиска
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь с пользователем, который загрузил документ
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="documents") 