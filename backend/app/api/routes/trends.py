"""
routes/trends.py
GET /api/trends?topic=&platform=

Runs Trend Scout agent only.
Returns structured hashtags + viral angles JSON.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List

from app.services.crew_service import service_get_trends
from app.core.security import get_current_user

router = APIRouter()


# ─── RESPONSE SCHEMA ──────────────────────────────────────────────────────────

class HashtagItem(BaseModel):
    tag: str
    velocity: int
    strongest_on: str
    peak_in_hours: int

class ViralAngle(BaseModel):
    angle: str
    description: str
    virality_score: int

class TrendsResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    hashtags: List[HashtagItem]
    viral_angles: List[ViralAngle]
    niche_classification: str
    overall_trend_velocity: int
    has_real_data: bool
    status: str
    cached: bool
    elapsed_seconds: float


# ─── ENDPOINT ─────────────────────────────────────────────────────────────────

@router.get("", response_model=TrendsResponse, summary="Discover trends for a topic")
async def get_trends(
    topic: str = Query(..., min_length=2, description="Topic to find trends for"),
    platform: str = Query(default="all", description="Target platform: instagram | tiktok | youtube | all"),
    current_user: dict = Depends(get_current_user),
):
    """
    Runs **Trend Scout** agent only.

    - Fetches real data from Google Trends + YouTube API first
    - Passes real data to agent for analysis
    - Returns structured hashtags with velocity scores + viral angles
    """
    result = await service_get_trends(topic, platform)
    return result