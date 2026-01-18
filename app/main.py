from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from .db import engine
from .routers import users, usage, assist, documents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: 
    yield
    # shutdown:
    await engine.dispose()

app = FastAPI(title="Minimal API", lifespan=lifespan)

@app.get("/healthz")
async def healthz():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/")
def root():
    return {"service": "Minimal API", "docs": "/docs"}

app.include_router(users.router)
app.include_router(usage.router)
app.include_router(assist.router)
app.include_router(documents.router)
