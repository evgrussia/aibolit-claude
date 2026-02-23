"""Authentication helpers: password hashing, JWT tokens, FastAPI dependency."""
import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request

from .config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_DAYS

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


def create_token(user_id: int, patient_id: str | None, username: str = "") -> str:
    """Create a JWT token with 7-day expiration."""
    payload = {
        "user_id": user_id,
        "patient_id": patient_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


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
        return {
            "user_id": payload["user_id"],
            "patient_id": payload.get("patient_id"),
            "username": payload.get("username", ""),
        }
    except HTTPException:
        return None
