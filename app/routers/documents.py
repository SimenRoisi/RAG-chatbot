from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_session
from ..schemas import DocumentCreate, DocumentOut
from ..dependencies import require_api_key
from ..models import Document, User, DocumentChunk
from ..security import get_key_hash
from ..llm import get_embedding

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", response_model=list[DocumentOut])
async def list_documents(
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(require_api_key)
):
    hashed_key = get_key_hash(api_key)
    
    # look up user id by api_key_hash
    user_id = await session.scalar(select(User.id).where(User.api_key_hash == hashed_key))
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    docs = (await session.execute(
        select(Document)
        .where(Document.owner_id == user_id)
        .order_by(Document.created_at.desc())
    )).scalars().all()

    return docs

@router.post("", response_model=DocumentOut, status_code=201)
async def create_doc(
    payload: DocumentCreate,
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(require_api_key)
):
    hashed_key = get_key_hash(api_key)
    user_id = await session.scalar(select(User.id).where(User.api_key_hash == hashed_key))
    
    if user_id is None:
         raise HTTPException(status_code=404, detail="User not found")

    doc = Document(owner_id=user_id, title=payload.title, content=payload.content)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # Chunking & Embedding
    # Simple strategy: 1000 chars overlap 100
    text = payload.content
    chunk_size = 1000
    overlap = 100
    
    start = 0
    idx = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        # Get embedding
        emb = await get_embedding(chunk_text)
        
        chunk_obj = DocumentChunk(
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_text,
            embedding=emb
        )
        session.add(chunk_obj)
        
        start += (chunk_size - overlap)
        idx += 1
    
    await session.commit()
    return doc
