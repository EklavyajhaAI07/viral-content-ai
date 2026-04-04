"""
routes/strategy.py
POST /api/strategy/generate

Runs Strategist agent only.
Returns 7-day calendar + growth plan.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.services.crew_service import service_generate_strategy
from app.core.security import get_current_user

router = APIRouter()


# ─── SCHEMAS ──────────────────────────────────────────────────────────────────

class StrategyRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    virality_score: Optional[int] = 75   # pass score from /predict-virality


class StrategyResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    strategy: str
    status: str
    cached: bool
    elapsed_seconds: float


# ─── ENDPOINT ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=StrategyResponse, summary="Generate 7-day content strategy")
async def generate_strategy(
    req: StrategyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Runs **Strategist** agent only.

    Pass `virality_score` from `/api/content/predict-virality` for a 
    calibrated strategy. Defaults to 75 if not provided.

    Returns: 7-day calendar, cross-platform repurposing plan, 
    growth forecast, content gaps, A/B tests.
    """
    result = await service_generate_strategy(
        req.topic, req.platform, req.virality_score or 75
    )
    return result