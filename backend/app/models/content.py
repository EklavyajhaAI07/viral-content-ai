from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class ContentJob(Base):
    __tablename__ = "content_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    platform = Column(String)
    status = Column(String, default="pending")  # pending, processing, done, failed
    virality_score = Column(Float)
    best_posting_time = Column(String)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
