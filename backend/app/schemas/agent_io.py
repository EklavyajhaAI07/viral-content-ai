from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TrendItem(BaseModel):
    topic: str
    hashtags: List[str]
    platforms: List[str]
    velocity_score: float
    niche: str
    peak_prediction_hours: int
    fetched_at: datetime

class TrendOutput(BaseModel):
    trends: List[TrendItem]
    total_count: int
    generated_at: datetime

class ViralityBreakdown(BaseModel):
    hook_strength: float
    hashtag_relevance: float
    trend_alignment: float
    emotional_tone: float
    posting_time_fit: float

class ViralityOutput(BaseModel):
    virality_score: float
    confidence: float
    grade: str
    breakdown: ViralityBreakdown
    improvements: List[str]
    predicted_reach: int
    predicted_engagement_rate: float

class AgentInput(BaseModel):
    topic: str
    platform: Optional[str] = "instagram"
    tone: Optional[str] = "engaging"
    target_audience: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None
