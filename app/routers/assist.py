from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from openai import APIError, OpenAIError

from ..db import get_session
from ..schemas import AssistRequest, AssistResponse
from ..dependencies import require_api_key
from ..llm import chat_once, get_embedding, contextualize_query, get_openai
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
    RAG-enabled LLM proxy with memory.
    """
    
    # Use centralized config for system prompt
    system_prompt = settings.SYSTEM_PROMPT
    
    try:
        # Convert Pydantic models to dicts for OpenAI
        messages = [{"role": m.role, "content": m.content} for m in body.messages]
        
        # 1. Contextualize query
        # Rewrite the *search query* but keep the chat history for the final answer
        standalone_query = await contextualize_query(messages, model=settings.OPENAI_MODEL)
        
        # 2. Get embedding for the STANDALONE query
        query_emb = await get_embedding(standalone_query)
        
        # 3. Search for relevant chunks
        stmt = (
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_emb))
            .limit(3)
        )
        chunks = (await session.execute(stmt)).scalars().all()
        
        context_text = "\n\n".join([c.content for c in chunks])
        if context_text:
            # Inject context into the system prompt or as a new system message
            # Better strategy: Add a system message with context just before the user's latest input?
            # Or append to the system prompt.
            detailed_system_prompt = (
                f"{system_prompt}\n\n"
                f"Relevant Context:\n{context_text}"
            )
        else:
            detailed_system_prompt = system_prompt

        # Call LLM with full history + context
        client = get_openai()  # Direct client usage for full history support
        
        full_messages = [
            {"role": "system", "content": detailed_system_prompt},
            *messages
        ]
        
        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=full_messages,
            temperature=0.3,
        )
        reply = resp.choices[0].message.content.strip()

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
