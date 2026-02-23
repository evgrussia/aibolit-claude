"""Authentication endpoints: register, login, me."""
import logging
import re
import sqlite3
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.models.patient import Patient, Gender, BloodType, Allergy
from src.utils.database import (
    save_patient, create_user, get_user_by_username, get_user_by_id,
    link_user_to_patient, update_user_password, delete_user,
)
from ..auth import hash_password, verify_password, create_token, get_current_user
from ..rate_limit import check_auth_rate_limit, check_register_rate_limit

logger = logging.getLogger("aibolit.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

_PASSWORD_RE = re.compile(r'^(?=.*[a-zA-Zа-яА-ЯёЁ])(?=.*\d).{8,}$')


def _validate_password(password: str) -> None:
    """Enforce minimum password complexity: >= 8 chars, letters + digits."""
    if len(password) < 8:
        raise HTTPException(400, "Пароль должен содержать минимум 8 символов")
    if not _PASSWORD_RE.match(password):
        raise HTTPException(400, "Пароль должен содержать буквы и цифры")


def _parse_date(value: str) -> date:
    """Parse ISO date string with proper error handling."""
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise HTTPException(400, "Некорректная дата рождения. Формат: ГГГГ-ММ-ДД")


def _parse_gender(value: str) -> Gender:
    """Parse gender enum with proper error handling."""
    try:
        return Gender(value)
    except ValueError:
        valid = ", ".join(g.value for g in Gender)
        raise HTTPException(400, f"Некорректный пол. Допустимые значения: {valid}")


def _parse_blood_type(value: str | None) -> BloodType | None:
    """Parse blood type enum with proper error handling."""
    if not value:
        return None
    try:
        return BloodType(value)
    except ValueError:
        valid = ", ".join(bt.value for bt in BloodType)
        raise HTTPException(400, f"Некорректная группа крови. Допустимые значения: {valid}")


class RegisterRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    blood_type: str | None = None
    allergies: list[dict] | None = None
    family_history: list[str] | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    patient_id: str
    username: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class MeResponse(BaseModel):
    user_id: int
    username: str
    patient_id: str | None


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, request: Request):
    check_register_rate_limit(request)

    if get_user_by_username(req.username):
        raise HTTPException(409, "Пользователь с таким логином уже существует")

    _validate_password(req.password)

    # Validate inputs before creating records
    dob = _parse_date(req.date_of_birth)
    gender = _parse_gender(req.gender)
    blood_type = _parse_blood_type(req.blood_type)

    # Create patient record
    patient = Patient(
        id=str(uuid.uuid4())[:8],
        first_name=req.first_name,
        last_name=req.last_name,
        date_of_birth=dob,
        gender=gender,
        blood_type=blood_type,
        allergies=[
            Allergy(substance=a.get("substance", ""), reaction=a.get("reaction", ""), severity=a.get("severity", "moderate"))
            for a in (req.allergies or [])
        ],
        family_history=req.family_history or [],
    )
    patient_id = save_patient(patient)

    # Create user linked to patient — handle UNIQUE constraint race condition
    pw_hash = hash_password(req.password)
    try:
        user_id = create_user(req.username, pw_hash, patient_id)
    except (sqlite3.IntegrityError, Exception) as e:
        if "UNIQUE" in str(e).upper() or "unique" in str(e).lower():
            raise HTTPException(409, "Пользователь с таким логином уже существует")
        logger.exception("Failed to create user: %s", req.username)
        raise HTTPException(500, "Ошибка при создании аккаунта")

    token = create_token(user_id, patient_id, username=req.username)
    return AuthResponse(token=token, patient_id=patient_id, username=req.username)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, request: Request):
    check_auth_rate_limit(request)

    user = get_user_by_username(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "Неверный логин или пароль")

    token = create_token(user["id"], user["patient_id"], username=user["username"])
    return AuthResponse(
        token=token,
        patient_id=user["patient_id"] or "",
        username=user["username"],
    )


@router.get("/me", response_model=MeResponse)
def me(current_user: dict = Depends(get_current_user)):
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    return MeResponse(
        user_id=user["id"],
        username=user["username"],
        patient_id=user["patient_id"],
    )


@router.post("/change-password")
def change_password(req: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    if not verify_password(req.old_password, user["password_hash"]):
        raise HTTPException(400, "Неверный текущий пароль")
    _validate_password(req.new_password)
    new_hash = hash_password(req.new_password)
    update_user_password(current_user["user_id"], new_hash)
    return {"message": "Пароль успешно изменён"}


@router.delete("/me")
def delete_account(current_user: dict = Depends(get_current_user)):
    if not delete_user(current_user["user_id"]):
        raise HTTPException(404, "Пользователь не найден")
    return {"message": "Аккаунт удалён"}
