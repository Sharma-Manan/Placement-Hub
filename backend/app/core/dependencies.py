from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser


def require_coordinator(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    if current_user.role != "coordinator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coordinators can perform this action"
        )
    return current_user


def require_student(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can perform this action"
        )
    return current_user