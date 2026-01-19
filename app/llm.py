import os 
from fastapi import HTTPException, status
from openai import OpenAI, APIError, RateLimitError, APITimeoutError

_client = None

_client = None

def get_openai():
    global _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    _client = OpenAI(api_key=api_key, timeout=20) #seconds
    return _client

async def chat_once(system_prompt: str, user_prompt: str,  model: str = "gpt-4o-mini") -> str:
    """
    Minimal chat-kall.
    """
    client = get_openai()
    try:
        resp = client.chat.completions.create(
            model = model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature = 0.3,
        )
        return resp.choices[0].message.content.strip()
    except RateLimitError as e:
        # 429 Too Many Requests (kvote/ratelimit)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="LLM rate limit")
    except APITimeoutError as e:
        # 504 Gateway Timeout (tidsavbrudd mot tredjepart)
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="LLM timeout")
    except APIError as e:
        # 502 Bad Gateway (generell tredjepartsfeil)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM upstream error")

async def get_embedding(text: str) -> list[float]:
    client = get_openai()
    text = text.replace("\n", " ")
    try:
        resp = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return resp.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail="Embedding failed")

async def contextualize_query(messages: list[dict], model: str = "gpt-4o-mini") -> str:
    """
    If there is history, rewrite the last message to be standalone.
    """
    if len(messages) <= 1:
        # No history, just use the last message content
        return messages[-1]["content"]
    
    client = get_openai()
    
    # Construct a prompt to rewrite the query
    system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just rewrite it if needed. Return ONLY the reformulated question."
    )
    
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages # Pass full history
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"Contextualization failed: {e}")
        # Fallback: just use the last message
        return messages[-1]["content"]