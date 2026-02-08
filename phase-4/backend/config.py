"""
Configuration module for FastAPI application.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # JWT Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Environment
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # AI Configuration (Phase 3 Chatbot)
    # Groq only (no fallback)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_MAX_TOKENS: int = 1000
    GROQ_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7

    # Rate Limiting
    RATE_LIMIT_RPM: int = 30
    RATE_LIMIT_TPM: int = 6000

    # Conversation Settings
    MAX_CONTEXT_TOKENS: int = 8000
    MAX_MESSAGES_PER_CONVERSATION: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
