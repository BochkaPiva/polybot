from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from admin.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    system_filename = Column(String, nullable=False)
    file_type = Column(String)
    file_size = Column(BigInteger)
    content_text = Column(Text)
    text_version = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 