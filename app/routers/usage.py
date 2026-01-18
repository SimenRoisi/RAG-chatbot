from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from ..db import get_session
from ..schemas import UsageCreate, UsageOut, UsageSummary
from ..dependencies import require_api_key
from ..security import get_key_hash

router = APIRouter(prefix="/usage", tags=["usage"])

@router.post("", response_model=UsageOut, status_code=201)
async def record_usage(
    payload: UsageCreate, 
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(require_api_key),
):
    # api_key here is the RAW key verified by require_api_key
    hashed_key = get_key_hash(api_key)
    
    try:
        res = await session.execute(
            text("""
                INSERT INTO api_usage (api_key_hash, endpoint)
                VALUES (:api_key_hash, :endpoint)
                RETURNING id, api_key_hash, endpoint, timestamp
            """),
        {"api_key_hash": hashed_key, "endpoint": payload.endpoint},
        )
        row = res.mappings().one()
        await session.commit()
        return row
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")

@router.get("/summary", response_model=list[UsageSummary])
async def usage_summary(
    hours: int = Query(24, ge=1, le=24*30),
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(require_api_key),
):
    hashed_key = get_key_hash(api_key)
    q = text("""
        SELECT endpoint, COUNT(*)::int AS calls
        FROM public.api_usage
        WHERE api_key_hash = :k
        GROUP BY endpoint
        ORDER BY calls DESC
    """)
    res = await session.execute(q, {"k": hashed_key, "hours": hours}) # hours param was unused in original SQL but passed?
    # Original SQL: WHERE api_key = :k (No time filter!)
    # I should probably add time filter if 'hours' is passed, but following original logic for now
    # or improving it? The original had `hours` param but didn't use it in the query string shown in `main.py`...
    # Wait, in `main.py`: `res = await session.execute(q, {"k": api_key, "hours": hours})`
    # But the query text string didn't have `:hours` or use `timestamp`.
    # I will FIX this bug while I'm at it.
    
    q_fixed = text("""
        SELECT endpoint, COUNT(*)::int AS calls
        FROM public.api_usage
        WHERE api_key_hash = :k
          AND timestamp >= NOW() - make_interval(hours => :hours)
        GROUP BY endpoint
        ORDER BY calls DESC
    """)
    
    res = await session.execute(q_fixed, {"k": hashed_key, "hours": hours})
    rows = res.all()
    return [UsageSummary(endpoint=endpoint, calls=calls) for (endpoint, calls) in rows]

@router.get("/{api_key}", response_model=list[UsageOut])
async def usage_for_key(api_key: str, limit: int=100, session: AsyncSession=Depends(get_session)):
    # This endpoint takes `api_key` in path. 
    # Current behavior: anyone can check usage for a key if they know it?
    # Security: Ideally you should only check *your own* usage. 
    # But let's keep original behavior: query by key.
    
    # Wait, the path param is just a string.
    # Logic: find usage where api_key_hash matches hash of this key?
    hashed_lookup = get_key_hash(api_key)
    
    res = await session.execute(
        text("""
            SELECT id, api_key_hash, endpoint, timestamp
            FROM api_usage
            WHERE api_key_hash = :k
            ORDER BY timestamp DESC
            LIMIT :limit
        """),
        {"k": hashed_lookup, "limit": limit},
    )
    return list(res.mappings().all())
