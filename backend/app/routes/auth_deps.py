# backend/app/routes/auth_deps.py
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Callable

import jwt  # provided by the PyJWT package
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# -------------------------
# Config (env-driven)
# -------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")          # set in Render → Environment
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_ACCESS_TTL_MIN = int(os.getenv("JWT_ACCESS_TTL_MIN", "60"))  # 60 min default
JWT_ISS = os.getenv("JWT_ISS", "socialmediarag")           # optional; set to your service name
JWT_AUD = os.getenv("JWT_AUD")                             # optional; if set, token must include this aud

# Single instance of HTTP Bearer auth (no auto 403; we return proper 401 + WWW-Authenticate)
bearer = HTTPBearer(auto_error=False)


# -------------------------
# Token helpers
# -------------------------
def create_access_token(
    sub: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """
    Create a signed JWT access token.
    - sub: subject/user id
    - extra_claims: additional claims (e.g., {"scopes": ["read", "write"]})
    - expires_minutes: override default TTL
    """
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(minutes=expires_minutes or JWT_ACCESS_TTL_MIN)

    payload: Dict[str, Any] = {
        "sub": sub,
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if JWT_ISS:
        payload["iss"] = JWT_ISS
    if JWT_AUD:
        payload["aud"] = JWT_AUD
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode & validate a JWT token; verifies exp, optional iss/aud."""
    options = {"verify_aud": JWT_AUD is not None}
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALG],
        audience=JWT_AUD if JWT_AUD else None,
        options=options,
        issuer=JWT_ISS if JWT_ISS else None,
    )


# -------------------------
# FastAPI dependencies
# -------------------------
async def current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> Dict[str, Any]:
    """
    Require a valid Bearer token.
    - On missing/invalid token → 401 with WWW-Authenticate: Bearer
    - Returns decoded JWT payload (dict) on success
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload  # You can map this to a user model/db lookup if needed.
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_scope(scope: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Dependency factory to enforce a specific scope in the token.
    Usage:
        @router.get("/admin")
        def admin_route(user = Depends(require_scope("admin"))): ...
    """
    def _dep(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
        scopes = user.get("scopes") or user.get("scope") or []
        if isinstance(scopes, str):
            scopes = scopes.split()
        if scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient scope",
            )
        return user

    return _dep


__all__ = [
    "current_user",
    "create_access_token",
    "decode_token",
    "require_scope",
]
