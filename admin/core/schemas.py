from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    department: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }

class DocumentBase(BaseModel):
    original_filename: str
    file_type: Optional[str] = None
    content_text: Optional[str] = None

class DocumentCreate(DocumentBase):
    system_filename: str
    file_size: int
    user_id: Optional[int] = None

class DocumentUpdate(BaseModel):
    original_filename: Optional[str] = None
    content_text: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    system_filename: str
    file_size: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        } 