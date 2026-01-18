import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    SYSTEM_PROMPT: str = (
        "Du er en hjelpsom AI-assistent for kundeservice. "
        "Svar kort, presist og hjelpsomt."
    )
    DATABASE_URL: str = "postgresql+asyncpg://app:devpass@db:5432/appdb"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
