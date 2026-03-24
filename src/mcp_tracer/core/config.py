"""
Core configuration for AgentTrace.
All settings are loaded from environment variables via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AgentTrace"
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")  # ... means required, no default

    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Single instance — import this everywhere
settings = Settings()