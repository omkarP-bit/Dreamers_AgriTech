"""
Application configuration and settings
AutoGen 0.7.5 compatible
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Groq API Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # OpenWeatherMap API
    OPENWEATHER_API_KEY: str
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "farm_ai_agent"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Feature Flags
    TEST_MODE: bool = False
    MOCK_APIS: bool = False
    MOCK_HISTORICAL_WEATHER: bool = False
    USE_SEASONAL_PATTERNS: bool = True
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend port
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()