from fastapi import APIRouter, Depends
from app.schemas.requests import GenerateRequest, GenerateResponse
from app.services.crew_service import run_generate
from app.core.security import get_current_user

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, current_user: dict = Depends(get_current_user)):
    result = await run_generate(
        req.topic, req.platform.value, req.tone.value, req.target_audience
    )
    return result
