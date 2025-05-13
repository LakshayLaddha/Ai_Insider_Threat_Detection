import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Insider Sentinel"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost/insider_sentinel"
    )
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # IPinfo settings
    IPINFO_API_TOKEN: str = os.getenv("IPINFO_API_TOKEN", "")
    
    # Alert thresholds
    MAX_FILE_DOWNLOADS: int = 20  # Max downloads before triggering alert
    UNUSUAL_TIME_START: int = 23   # Hour (0-23) to start unusual time monitoring
    UNUSUAL_TIME_END: int = 6      # Hour (0-23) to end unusual time monitoring
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # New Pydantic v2 configuration style
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # This allows extra fields to be ignored
    )

settings = Settings()