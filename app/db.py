import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

# load_dotenv() # handled by pydantic settings
DATABASE_URL = settings.DATABASE_URL

kwargs = {}
if os.getenv("TESTING") == "1":
    kwargs["poolclass"] = NullPool  # avoid reusing connections across loops

engine = create_async_engine(DATABASE_URL, echo=True, **kwargs)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session