from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
import bcrypt
from uuid import UUID

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.models.user import User
from app.models.student import Student
from app.models.coordinator import Coordinator
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 2. Hash password
    hashed_password = bcrypt.hashpw(
        payload.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    # 3. Create user
    user = User(
        email=payload.email,
        password_hash=hashed_password,
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. Generate tokens
    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not bcrypt.checkpw(
        payload.password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled",
        )

    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    try:
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        role = role.get("role")

        access_token = create_access_token(
            user_id=UUID(user_id),
            role=role,  # role will be checked again via DB/RLS
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
