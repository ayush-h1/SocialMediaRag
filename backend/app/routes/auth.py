import os, time
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.auth import LoginRequest, TokenResponse, UserOut
import jwt

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

def create_token(username: str) -> str:
    now = int(time.time())
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + JWT_EXPIRES_MIN * 60,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = creds.credentials
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    # demo: accept any non-empty username/password
    if not payload.username or not payload.password:
        raise HTTPException(status_code=400, detail="Username/password required")
    token = create_token(payload.username)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserOut)
def me(user: str = Depends(current_user)):
    return UserOut(username=user)
