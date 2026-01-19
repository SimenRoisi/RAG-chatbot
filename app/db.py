import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

# load_dotenv() # handled by pydantic settings
DATABASE_URL = settings.DATABASE_URL

kwargs = {}
# Always use NullPool for serverless environments (Vercel, AWS Lambda, etc.)
# This prevents "Device or resource busy" errors in serverless functions
kwargs["poolclass"] = NullPool

engine = create_async_engine(DATABASE_URL, echo=False, **kwargs)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session