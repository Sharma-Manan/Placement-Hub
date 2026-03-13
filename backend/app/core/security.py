from datetime import datetime , timedelta, timezone
from typing import  Dict, Annotated
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Header, HTTPException, status


from app.schemas.auth import CurrentUser

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)



def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "type": "access"
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload

    except JWTError:
        raise JWTError("Invalid or expired token")
    

def verify_access_token(token: str) -> Dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    
    return payload


def verify_refresh_token(token: str) -> Dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")

    return payload


def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")

        payload = decode_token(token)

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return CurrentUser(
            id=user_id,
            role=role
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )