from fastapi import APIRouter, Depends, Query
from app.services.crew_service import run_trends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/trends")
async def trends(
    topic: str = Query(..., min_length=2),
    platform: str = Query(default="all"),
    current_user: dict = Depends(get_current_user)
):
    return await run_trends(topic, platform)
