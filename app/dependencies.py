from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .db import get_session
from .security import get_key_hash

async def require_api_key(
        x_api_key: str = Header(..., alias="X-API-Key"),
        session: AsyncSession = Depends(get_session),
) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail = "Missing X-API key")
    
    hashed_key = get_key_hash(x_api_key)
    
    res = await session.execute(
        text("SELECT 1 FROM users WHERE api_key_hash = :k"),
        {"k": hashed_key},
    )
    if res.scalar() is None:
        raise HTTPException(status_code=401, detail = "Invalid API key")
    return x_api_key
