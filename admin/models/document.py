from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from admin.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 hash
    content_text = Column(Text)
    text_version = Column(Integer, default=1)  # Версия очищенного текста
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 