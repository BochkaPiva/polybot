from pydantic import BaseSettings, ConfigDict, validator
import os
from typing import List, Optional

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "Polybot Admin"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5433
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "poliom_bot"
    
    # Bot settings
    BOT_TOKEN: Optional[str] = None
    ADMIN_IDS: str = ""
    
    @validator("ADMIN_IDS")
    def parse_admin_ids(cls, v: str) -> List[str]:
        if not v:
            return []
        return [id.strip() for id in v.split(",")]
    
    # OpenSearch settings
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASS: str = "admin"
    OPENSEARCH_INDEX: str = "poliom_knowledge"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File upload settings
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "doc", "docx", "txt"]
    UPLOAD_DIR: str = "uploads"
    
    # Admin settings
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_EMAIL: str = "admin@example.com"

settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 