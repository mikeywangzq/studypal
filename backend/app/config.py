"""
Configuration management for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "StudyPal - AI Learning Assistant"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/learning_assistant"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_TEMPERATURE: float = 0.5
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 30

    # Vector Store
    VECTOR_DB: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    SIMILARITY_THRESHOLD: float = 0.7
    TOP_K: int = 20
    TOP_N: int = 5

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    MAX_UPLOAD_SIZE_MB: int = 100
    SUPPORTED_EXTENSIONS: str = ".md,.txt,.cpp,.c,.py,.java,.js,.ts,.jsx,.tsx"

    # Text Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Cache
    CACHE_TTL_SECONDS: int = 600
    ENABLE_QUERY_CACHE: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
