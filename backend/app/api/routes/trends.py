from fastapi import APIRouter, Depends, Query
from app.services.crew_service import run_trends
from app.tools.trend_engine import fetch_all_trends
from app.core.security import get_current_user

router = APIRouter()


@router.get("/trends")
async def trends(
    topic: str = Query(..., min_length=2, description="Topic to find trends for"),
    platform: str = Query(default="all", description="instagram|tiktok|youtube|linkedin|twitter|all"),
    raw: bool = Query(default=False, description="Return raw API data without AI analysis"),
    current_user: dict = Depends(get_current_user),
):
    """
    Returns real trending data from Google Trends + YouTube,
    analyzed by the Trend Scout AI agent.
    """
    if raw:
        # Skip AI — return raw data instantly
        data = await fetch_all_trends(topic, platform)
        return {"topic": topic, "platform": platform, "raw_data": data, "status": "completed"}

    return await run_trends(topic, platform)
