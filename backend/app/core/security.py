from datetime import datetime , timedelta
from typing import Optional, Dict

from jose import jwt, JWTError

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "type": "access"
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
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


def get_user_id_from_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    return payload.get("sub")


def get_user_role_from_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    return payload.get("role")