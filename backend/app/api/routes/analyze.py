from fastapi import APIRouter, Depends
from app.schemas.requests import AnalyzeRequest, AnalyzeResponse
from app.services.crew_service import run_full_analyze
from app.core.security import get_current_user

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, current_user: dict = Depends(get_current_user)):
    result = await run_full_analyze(
        req.topic, req.platform.value, req.tone.value,
        req.target_audience, req.caption or "", req.hashtags or ""
    )
    return result
