import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv(override=True)

SECRET_KEY = os.getenv("SECRET_KEY", "node-biz-backend-secret-key-2026-super-safe-jwt-auth")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 14


def hash_password(password: str) -> str:
    """
    평문 비밀번호를 bcrypt로 암호화(hashing)합니다.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 비밀번호와 DB에 저장된 해시 비밀번호가 일치하는지 검증합니다.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    30분 유효기간을 가진 JWT access_token을 생성합니다.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    로그인 유지를 위한 JWT refresh_token을 생성합니다.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    JWT 토큰을 검증하고 payload(claims)를 반환합니다.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
