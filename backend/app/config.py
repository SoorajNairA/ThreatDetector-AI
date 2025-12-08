"""Configuration management for Guardian Security Platform"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    APP_ENV: str = "dev"
    
    # Security
    API_KEY: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_THREATS_TABLE: str = "threats"
    
    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    
    # Server
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
