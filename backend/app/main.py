from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import analyze, generate, trends, auth
from app.core.config import settings
from app.core.redis_client import redis_client

from fastapi.security import HTTPBearer
from fastapi import Security

security = HTTPBearer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Viral Content AI API...")
    try:
        await redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis not available: {e} — caching disabled")
    yield
    logger.info("👋 Shutting down...")
    await redis_client.close()


app = FastAPI(
    title="Viral Content AI",
    description="AI-powered content strategy engine with CrewAI agents",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/auth", tags=["Auth"])
app.include_router(analyze.router,  prefix="/api",      tags=["Analyze"])
app.include_router(generate.router, prefix="/api",      tags=["Generate"])
app.include_router(trends.router,   prefix="/api",      tags=["Trends"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    redis_ok = False
    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass
    return {"api": "ok", "redis": "ok" if redis_ok else "unavailable"}
