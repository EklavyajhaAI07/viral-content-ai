from fastapi import APIRouter, HTTPException, Depends
from app.schemas.requests import RegisterRequest, LoginRequest, TokenResponse
from app.models.user import get_user_by_email, create_user
from app.core.security import verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    try:
        user = create_user(req.email, req.name, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]}
    }

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]}
    }

@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
