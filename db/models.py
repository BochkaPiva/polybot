from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    auth_code = Column(String(10), nullable=True)
    is_authenticated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    auth_attempts = relationship("AuthAttempt", back_populates="user")

class AuthAttempt(Base):
    __tablename__ = "auth_attempts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    attempt_time = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="auth_attempts")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True)
    level = Column(Integer, default=1)
    order = Column(Integer, default=0)
    content = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)  # Store URLs to images/videos
    
    # Relationships
    parent = relationship("MenuItem", remote_side=[id], backref="children")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # PDF, DOCX, TXT
    content_text = Column(Text, nullable=True)  # Extracted text content
    indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
