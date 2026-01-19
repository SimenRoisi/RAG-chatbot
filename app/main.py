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



from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... imports ...

app.include_router(users.router)
app.include_router(usage.router)
app.include_router(assist.router)
app.include_router(documents.router)

# Serve Frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")
