from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import auth, trends, content, strategy
from app.core.redis_client import redis_client
from fastapi.security import HTTPBearer

security = HTTPBearer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── LIFESPAN ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Viral Content AI API...")
    try:
        pong = await redis_client.ping()
        if pong:
            logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable: {e}")
    yield
    logger.info("👋 Shutting down...")
    await redis_client.close()


# ─── APP ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Viral Content AI",
    description="""
## AI-powered content strategy engine

Each endpoint runs **one focused agent** — call them independently or chain them:

1. `GET /api/trends` → discover trending hashtags + viral angles
2. `POST /api/content/hook` → generate scroll-stopping hooks
3. `POST /api/content/caption` → write full platform-native caption
4. `POST /api/content/hashtags` → 3-tier hashtag strategy  
5. `POST /api/content/predict-virality` → score 0–100 with breakdown
6. `POST /api/content/thumbnail` → AI-generated thumbnail image
7. `POST /api/strategy/generate` → 7-day content calendar + growth plan
""",
    version="2.0.0",
    lifespan=lifespan,
)


# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── ROUTES ───────────────────────────────────────────────────────────────────
# These prefixes match frontend/src/lib/api.ts exactly

app.include_router(auth.router,      prefix="/api/auth",     tags=["Auth"])
app.include_router(trends.router,    prefix="/api/trends",   tags=["Trends"])
app.include_router(content.router,   prefix="/api/content",  tags=["Content"])
app.include_router(strategy.router,  prefix="/api/strategy", tags=["Strategy"])


# ─── HEALTH ───────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "version": "2.0.0",
        "docs": "/docs",
        "message": "Viral AI Creator Cockpit — one agent per endpoint",
    }

@app.get("/health", tags=["Health"])
async def health():
    redis_ok = False
    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass
    return {
        "api": "ok",
        "redis": "ok" if redis_ok else "unavailable",
        "engine": "CrewAI Modular v2",
    }