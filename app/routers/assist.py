from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from openai import APIError, OpenAIError

from ..db import get_session
from ..schemas import AssistRequest, AssistResponse
from ..dependencies import require_api_key
from ..llm import chat_once, get_embedding
from ..config import settings
from ..security import get_key_hash
from ..models import DocumentChunk

router = APIRouter(prefix="/assist", tags=["assist"])

@router.post("", response_model=AssistResponse)
async def assist(
        body: AssistRequest,
        session: AsyncSession = Depends(get_session),
        api_key: str = Depends(require_api_key),
):
    """
    RAG-enabled LLM proxy.
    """
    
    # Use centralized config for system prompt
    system_prompt = settings.SYSTEM_PROMPT
    
    try:
        # 1. Get embedding for query
        query_emb = await get_embedding(body.prompt)
        
        # 2. Search for relevant chunks
        stmt = (
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_emb))
            .limit(3)
        )
        chunks = (await session.execute(stmt)).scalars().all()
        
        context_text = "\n\n".join([c.content for c in chunks])
        if context_text:
            user_prompt = f"Context:\n{context_text}\n\nQuestion: {body.prompt}"
        else:
            user_prompt = body.prompt

        reply = await chat_once(system_prompt, user_prompt, model=settings.OPENAI_MODEL)
    except (APIError, OpenAIError) as e:
        # Surface a clean 502 instead of a 500
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}") from e
    except Exception as e:
        # Catch-all so you see a useful message
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}") from e
    
    # Explicitly log usage
    hashed_key = get_key_hash(api_key)
    await session.execute(
        text("INSERT INTO api_usage (api_key_hash, endpoint) VALUES (:k, :e)"),
        {"k": hashed_key, "e": "/assist"},
    )
    await session.commit()
    return AssistResponse(reply=reply)
