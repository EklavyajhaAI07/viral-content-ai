from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class PlatformEnum(str, Enum):
    instagram = "instagram"
    tiktok = "tiktok"
    youtube = "youtube"
    linkedin = "linkedin"
    twitter = "twitter"
    all = "all"


class ToneEnum(str, Enum):
    engaging = "engaging"
    exciting = "exciting"
    professional = "professional"
    funny = "funny"
    inspirational = "inspirational"
    educational = "educational"


class AnalyzeRequest(BaseModel):
    topic: str
    platform: PlatformEnum = PlatformEnum.instagram
    tone: ToneEnum = ToneEnum.engaging
    target_audience: Optional[str] = "general"
    caption: Optional[str] = ""
    hashtags: Optional[str] = ""


class AnalyzeResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    status: str
    virality_score: int
    virality_analysis: Optional[str]
    content_package: Optional[str]
    trends: Optional[str]
    algorithm_guide: Optional[str]
    strategy: Optional[str]
    cached: bool = False
    elapsed_seconds: float = 0.0


class GenerateRequest(BaseModel):
    topic: str
    platform: PlatformEnum = PlatformEnum.instagram
    tone: ToneEnum = ToneEnum.engaging
    target_audience: Optional[str] = "general"


class GenerateResponse(BaseModel):
    job_id: str
    topic: str
    platform: str
    content_package: Optional[str]
    algorithm_guide: Optional[str]
    strategy: Optional[str]
    status: str
    cached: bool = False
    elapsed_seconds: float = 0.0


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict
