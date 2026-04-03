from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Platform(str, Enum):
    instagram = "instagram"
    tiktok = "tiktok"
    youtube = "youtube"
    linkedin = "linkedin"
    twitter = "twitter"
    all = "all"


class Tone(str, Enum):
    engaging = "engaging"
    motivational = "motivational"
    professional = "professional"
    funny = "funny"
    educational = "educational"
    inspirational = "inspirational"


# ── Auth ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


# ── Analyze ───────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300)
    platform: Platform = Platform.instagram
    tone: Tone = Tone.engaging
    target_audience: str = Field(default="general", max_length=100)
    caption: Optional[str] = Field(default="", max_length=2000)
    hashtags: Optional[str] = Field(default="", max_length=500)

class AnalyzeResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    status: str
    virality_score: Optional[int] = None
    virality_analysis: Optional[str] = None
    content_package: Optional[str] = None
    trends: Optional[str] = None
    algorithm_guide: Optional[str] = None
    strategy: Optional[str] = None
    cached: bool = False
    elapsed_seconds: Optional[float] = None


# ── Generate ──────────────────────────────────────────
class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300)
    platform: Platform = Platform.instagram
    tone: Tone = Tone.engaging
    target_audience: str = Field(default="general", max_length=100)

class GenerateResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    content_package: Optional[str] = None
    algorithm_guide: Optional[str] = None
    strategy: Optional[str] = None
    status: str
    cached: bool = False
    elapsed_seconds: Optional[float] = None


# ── Trends ────────────────────────────────────────────
class TrendsRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    platform: Platform = Platform.all

class TrendsResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    trends: Optional[str] = None
    status: str
    cached: bool = False
    elapsed_seconds: Optional[float] = None


# ── Job Status ────────────────────────────────────────
class JobStatus(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: Optional[int] = None
