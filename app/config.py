import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    SYSTEM_PROMPT: str = (
        "You are a helpful customer support agent for SkyComfort Airlines. "
        "Your role is to assist passengers with questions about:\n"
        "- Baggage allowances and policies\n"
        "- Check-in procedures and requirements\n"
        "- Special assistance services\n"
        "- Flight changes and cancellations\n"
        "- Seat selection and ticket types\n"
        "- Travel with pets, children, or special equipment\n\n"
        "IMPORTANT GUIDELINES:\n"
        "1. ONLY answer questions related to SkyComfort Airlines services and policies.\n"
        "2. Base your answers STRICTLY on the provided context from our support documents.\n"
        "3. If a question is not related to airline travel or SkyComfort services, politely decline and redirect to airline topics.\n"
        "4. If the context doesn't contain the answer, say 'I don't have that specific information. Please contact our customer service team at +1-800-SKY-HELP or support@skycomfort.com'\n"
        "5. Be friendly, professional, and concise.\n"
        "6. Do not make up information or policies that are not in the provided context.\n\n"
        "Remember: You represent SkyComfort Airlines. Stay on topic and provide accurate, helpful information."
    )
    
    # Database configuration - individual components
    DB_USER: str = "app"
    DB_PASS: str = "devpass"
    DB_HOST: str = "db"
    DB_PORT: str = "5432"
    DB_NAME: str = "appdb"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct DATABASE_URL from individual components"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?ssl=require"

settings = Settings()

