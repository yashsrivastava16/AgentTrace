"""
Core configuration for AgentTrace.
All settings are loaded from environment variables via pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding = "utf-8", case_sensitive=True)

    # App
    APP_NAME: str = "AgentTrace"
    APP_ENV: str = Field(default='development', json_schema_extra={"env":"APP_ENV"})
    DEBUG: bool = Field(default=False, json_schema_extra={"env":"DEBUG"})

    # Database
    DATABASE_URL: str = Field(..., json_schema_extra={"env":"DATABASE_URL"})  # ... means required, no default

    # Server
    HOST: str = Field(default="0.0.0.0", json_schema_extra={"env":"HOST"})
    PORT: int = Field(default=8000, json_schema_extra={"env":"PORT"})

    #JWT
    JWT_SECRET_KEY: str = Field(..., json_schema_extra={"env":"JWT_SECRET_KEY"})
    JWT_ALGORITHM: str = Field(default="HS256", json_schema_extra={"env":"JWT_ALGORITHM"})
    JWT_EXPIRY_MINUTES: int = Field(default=43200, json_schema_extra={"env":"JWT_EXPIRY_MINUTES"})


# Single instance — import this everywhere
settings = Settings()