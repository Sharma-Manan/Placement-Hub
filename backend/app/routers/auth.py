from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
import bcrypt
from uuid import UUID
import uuid


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

allowed_coordinators = [
    "tpo@college.edu",
    "admin@college.edu"
]

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

    # 2. Restrict coordinator registration
    if payload.role == "coordinator" and payload.email not in allowed_coordinators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to register as coordinator"
        )

    # 3. Hash password
    hashed_password = bcrypt.hashpw(
        payload.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    # 4. Create user
    user = User(
        email=payload.email,
        password_hash=hashed_password,
        role=payload.role,
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_active=True,
    )
    db.add(user)
    db.flush()  # get user.id before creating Student/Coordinator

    # 5. Create role-specific record with full skeleton data
    if payload.role == "student":
        student = Student(
            user_id=user.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            roll_no=f"TEMP-{uuid.uuid4()}",
            department_id="",
            graduation_year=0,
            cgpa=0.0,
            tenth_percentage=0.0,
            twelfth_percentage=0.0,
            active_backlogs=0,
            total_backlogs=0,
            branch="CSE",
            is_profile_complete=False,
            placement_status="unplaced",
        )
        db.add(student)

    elif payload.role == "coordinator":
        coordinator = Coordinator(
            user_id=user.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            is_primary=False,
        )
        db.add(coordinator)

    # 6. Commit everything together
    db.commit()
    db.refresh(user)

    # 7. Generate tokens
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
    
    #  Restrict coordinator login
    if user.role == "coordinator" and user.email not in allowed_coordinators:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to login as coordinator"
        )

    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(refresh_token: str):
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
