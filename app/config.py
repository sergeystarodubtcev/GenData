from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://user:password@localhost:3306/gendata"
    
    # JWT
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Admin
    admin_default_password: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

