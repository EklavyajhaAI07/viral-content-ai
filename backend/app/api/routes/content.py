"""
routes/content.py
4 focused endpoints — each calls exactly one service function.

POST /api/content/hook              → hook + alt hooks + cta
POST /api/content/caption           → full caption + posting time
POST /api/content/hashtags          → 3-tier hashtag strategy
POST /api/content/predict-virality  → score + breakdown + improvements
POST /api/content/thumbnail         → AI-generated thumbnail image
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List

from app.services.crew_service import (
    service_generate_hook,
    service_generate_caption,
    service_generate_hashtags,
    service_predict_virality,
    service_generate_thumbnail,
)
from app.core.security import get_current_user

router = APIRouter()


# ─── REQUEST SCHEMAS ──────────────────────────────────────────────────────────

class HookRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    tone: str = "engaging"
    target_audience: str = "general"

class CaptionRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    tone: str = "engaging"
    target_audience: str = "general"
    hook: Optional[str] = ""        # optional: pass hook from previous call

class HashtagRequest(BaseModel):
    topic: str
    platform: str = "instagram"

class ViralityRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    caption: Optional[str] = ""
    hashtags: Optional[str] = ""

class ThumbnailRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    tone: str = "engaging"


# ─── RESPONSE SCHEMAS ─────────────────────────────────────────────────────────

class HookResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    hook: str
    alternative_hooks: List[str]
    cta: str
    format_recommendation: str
    status: str
    cached: bool
    elapsed_seconds: float

class CaptionResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    caption: str
    best_posting_time: str
    word_count: int
    status: str
    cached: bool
    elapsed_seconds: float

class HashtagTiers(BaseModel):
    niche: List[str]
    trending: List[str]
    broad: List[str]
    total_count: int

class HashtagResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    niche: List[str]
    trending: List[str]
    broad: List[str]
    total_count: int
    status: str
    cached: bool
    elapsed_seconds: float

class BreakdownScores(BaseModel):
    hook_strength: int
    hashtag_relevance: int
    trend_alignment: int
    emotional_tone: int
    posting_time_fit: int

class ViralityResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    overall_score: int
    grade: str
    confidence: float
    predicted_reach: int
    predicted_engagement_rate: float
    breakdown: BreakdownScores
    improvements: List[str]
    rewritten_hook: str
    status: str
    cached: bool
    elapsed_seconds: float


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/hook", response_model=HookResponse, summary="Generate scroll-stopping hooks")
async def generate_hook(
    req: HookRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Runs **Hook Writer** agent only.
    Returns: best hook, 3 alternative hooks, CTA, format recommendation.
    """
    result = await service_generate_hook(
        req.topic, req.platform, req.tone, req.target_audience
    )
    return result


@router.post("/caption", response_model=CaptionResponse, summary="Generate full platform-native caption")
async def generate_caption(
    req: CaptionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Runs **Caption Writer** agent only.
    Pass `hook` from the /hook endpoint to build a cohesive caption.
    Returns: full caption, best posting time, word count.
    """
    result = await service_generate_caption(
        req.topic, req.platform, req.tone, req.target_audience, req.hook or ""
    )
    return result


@router.post("/hashtags", response_model=HashtagResponse, summary="Generate 3-tier hashtag strategy")
async def generate_hashtags(
    req: HashtagRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Runs **Hashtag Strategist** agent only.
    Returns: 5 niche + 5 trending + 5 broad hashtags.
    """
    result = await service_generate_hashtags(req.topic, req.platform)
    return result


@router.post("/predict-virality", response_model=ViralityResponse, summary="Predict virality score")
async def predict_virality(
    req: ViralityRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Runs **Virality Predictor** agent only.
    Pass `caption` and `hashtags` for a more accurate score.
    Returns: score 0–100, grade, breakdown, improvements, rewritten hook.
    """
    result = await service_predict_virality(
        req.topic, req.platform, req.caption or "", req.hashtags or ""
    )
    return result


@router.post("/thumbnail", summary="Generate AI thumbnail image")
async def generate_thumbnail_endpoint(
    req: ThumbnailRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Calls **Thumbnail Service** only (no LLM agent).
    Tries Stability AI → falls back to Pollinations FLUX.
    Returns: image URL/path.
    """
    result = await service_generate_thumbnail(req.topic, req.platform, req.tone)
    return result