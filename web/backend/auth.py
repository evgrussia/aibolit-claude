"""Authentication helpers: password hashing, JWT tokens, FastAPI dependency."""
import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request

from .config import SECRET_KEY, JWT_ALGORITHM

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False


def hash_password(password: str) -> str:
    """Hash password with bcrypt (preferred) or SHA-256 + salt (fallback)."""
    if _HAS_BCRYPT:
        return "bcrypt:" + bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Legacy fallback — will be used only if bcrypt is not installed
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash (supports both bcrypt and legacy SHA-256)."""
    if stored_hash.startswith("bcrypt:"):
        if not _HAS_BCRYPT:
            return False
        return bcrypt.checkpw(password.encode(), stored_hash[7:].encode())
    # Legacy SHA-256 format: salt:hash
    if ":" not in stored_hash:
        return False
    salt, h = stored_hash.split(":", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == h


def create_access_token(user_id: int, patient_id: str | None, username: str = "") -> str:
    """Create a short-lived JWT access token (15 min)."""
    payload = {
        "user_id": user_id,
        "patient_id": patient_id,
        "username": username,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, patient_id: str | None, username: str = "") -> str:
    """Create a long-lived JWT refresh token (7 days)."""
    payload = {
        "user_id": user_id,
        "patient_id": patient_id,
        "username": username,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_token(user_id: int, patient_id: str | None, username: str = "") -> str:
    """Create access token (backward-compatible alias)."""
    return create_access_token(user_id, patient_id, username)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token. Raises HTTPException on failure."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Недействительный токен")


def get_current_user(request: Request) -> dict:
    """FastAPI dependency: extract and validate Bearer token.
    Returns {"user_id": int, "patient_id": str | None}.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Требуется авторизация")
    token = auth_header[7:]
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(401, "Ожидается access-токен")
    return {
        "user_id": payload["user_id"],
        "patient_id": payload.get("patient_id"),
        "username": payload.get("username", ""),
    }


def get_optional_user(request: Request) -> dict | None:
    """FastAPI dependency: extract Bearer token if present, return None otherwise."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return {
            "user_id": payload["user_id"],
            "patient_id": payload.get("patient_id"),
            "username": payload.get("username", ""),
        }
    except HTTPException:
        return None
