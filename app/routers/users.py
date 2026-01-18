from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from ..db import get_session
from ..schemas import UserCreate, UserOut, UserOutWithKey
from ..security import get_key_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOutWithKey, status_code=201)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    # Note: payload.api_key is what the user *wants* (or we generate it?)
    # The original code took api_key as input.
    # Refactor: We should probably let the user provide it OR generate it.
    # Original: "email": "...", "api_key": "..."
    # We will respect that for now to minimize breaking behavior on input,
    # but we will hash it.
    
    hashed_key = get_key_hash(payload.api_key)
    
    try:
        res = await session.execute(
            text("""
                 INSERT INTO users (email, api_key_hash)
                 VALUES (:email, :api_key_hash)
                 RETURNING id, email, created_at
            """),
            {"email": payload.email, "api_key_hash": hashed_key},
        )
        row = res.mappings().one()
        await session.commit()
        
        # Construct response with the raw key (only time it's returned)
        return UserOutWithKey(
            id=row.id,
            email=row.email,
            created_at=row.created_at,
            api_key=payload.api_key
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email or API key already exists")

@router.get("", response_model=list[UserOut])
async def list_users(session: AsyncSession = Depends(get_session)):
    res = await session.execute(
        text("SELECT id, email, created_at FROM users ORDER BY id")
    )
    return list(res.mappings().all())
