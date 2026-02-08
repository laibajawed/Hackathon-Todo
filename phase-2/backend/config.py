"""
Configuration module for FastAPI application.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = ""

    # JWT Authentication
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Environment
    ENVIRONMENT: str = "development"

    # CORS - Allow multiple origins (comma-separated)
    CORS_ORIGINS: str = "http://localhost:3000,https://hackathon-todo-kappa.vercel.app,https://*.vercel.app"

    # AI Configuration (Phase 3 Chatbot)
    # Primary: Google Gemini
    GEMINI_API_KEY: str = ""
    AI_MODEL: str = "gemini/gemini-2.5-flash"
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7

    # Fallback: Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "groq/llama-3.1-8b-instant"
    GROQ_MAX_TOKENS: int = 1000
    GROQ_TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
