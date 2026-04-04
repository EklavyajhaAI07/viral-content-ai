from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.crew_service import run_generate, run_virality_only
from app.core.security import get_current_user

router = APIRouter()

# Schema definitions...
class GenerateRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    tone: str = "engaging"
    target_audience: str = "general"

class ViralityRequest(BaseModel):
    topic: str
    platform: str = "instagram"

# 🔥 FIX: Change "/generate" to "" to avoid /api/generate/generate
@router.post("", name="Generate Content")
async def generate_content(
    req: GenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    result = await run_generate(req.topic, req.platform, req.tone, req.target_audience)
    return {"source": "api", "data": result}

# 🔥 FIX: Keep as "/virality" or "/predict-virality" 
# This results in /api/generate/virality (cleaner)
@router.post("/virality", name="Predict Virality")
async def predict_virality(
    req: ViralityRequest,
    current_user: dict = Depends(get_current_user)
):
    result = await run_virality_only(req.topic, req.platform)
    return {"source": "api", "data": result}