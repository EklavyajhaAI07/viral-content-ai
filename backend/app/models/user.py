from typing import Dict, Optional
from app.core.security import hash_password
import uuid

_users: Dict[str, dict] = {}

# Seed demo user
_demo_id = str(uuid.uuid4())
_users["demo@viral.ai"] = {
    "id": _demo_id,
    "email": "demo@viral.ai",
    "name": "Demo User",
    "hashed_password": hash_password("demo1234"),
}

def get_user_by_email(email: str) -> Optional[dict]:
    return _users.get(email)

def get_user_by_id(user_id: str) -> Optional[dict]:
    for u in _users.values():
        if u["id"] == user_id:
            return u
    return None

def create_user(email: str, name: str, password: str) -> dict:
    if email in _users:
        raise ValueError("Email already registered")
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "hashed_password": hash_password(password),
    }
    _users[email] = user
    return user
