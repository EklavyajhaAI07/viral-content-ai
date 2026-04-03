from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContentRequest(BaseModel):
    topic: str
    platform: Optional[str] = "instagram"
    tone: Optional[str] = "engaging"
    target_audience: Optional[str] = None

class ContentResponse(BaseModel):
    job_id: int
    topic: str
    caption: str
    hashtags: List[str]
    virality_score: float
    best_posting_time: str
    platform_tips: str
    status: str

    class Config:
        from_attributes = True
