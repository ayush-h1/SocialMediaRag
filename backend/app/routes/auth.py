# backend/app/routes/auth.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import Base, engine, SessionLocal
from ..models import User
from ..schemas import LoginIn, Token, UserCreate, UserOut
from ..security import hash_password, verify_password, make_token
from ..deps.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Ensure tables exist (idempotent on import)
Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user and return a JWT.
    """
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=body.email,
        name=body.name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()

    token = make_token(sub=user.email)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(body: LoginIn, db: Session = Depends(get_db)):
    """
    Verify credentials and return a JWT.
