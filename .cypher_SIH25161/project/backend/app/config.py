from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    APP_ENV: str = "dev"
    
    API_KEY: Optional[str] = None
    
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_THREATS_TABLE: str = "threats"
    
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
