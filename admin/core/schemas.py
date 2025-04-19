from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    unique_id: str
    username: str | None
    first_name: str
    last_name: str | None
    is_active: bool
    is_admin: bool

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    content: str
    file_path: str
    file_type: str

class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    user_id: int
    message: str
    response: str

class ChatResponse(ChatBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 