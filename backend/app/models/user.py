from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base, SessionLocal
from app.core.security import hash_password
import enum


class PlanType(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    plan = Column(Enum(PlanType), default=PlanType.free)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def get_user_by_email(email: str) -> dict | None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.full_name or user.username,
            "hashed_password": user.hashed_password,
            "plan": user.plan,
        }
    finally:
        db.close()


def create_user(email: str, name: str, password: str) -> dict:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email already registered")
        user = User(
            email=email,
            username=email.split("@")[0],
            full_name=name,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.full_name,
        }
    finally:
        db.close()
