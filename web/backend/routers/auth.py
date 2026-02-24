"""Authentication endpoints: register, login, me."""
import logging
import re
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.models.patient import Patient, Gender, BloodType, Allergy
from src.utils.database import (
    save_patient, create_user, get_user_by_username, get_user_by_id,
    update_user_password, delete_user,
    revoke_token, is_token_revoked,
)
from ..auth import (
    hash_password, verify_password, create_token, get_current_user,
    create_access_token, create_refresh_token, decode_token,
)
from ..rate_limit import check_auth_rate_limit, check_register_rate_limit
from ..services.audit_service import AuditLogService

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
    consent_personal_data: bool = False
    consent_medical_ai: bool = False


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    token: str
    refresh_token: str
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

    # R1.5: Informed consent validation
    if not req.consent_personal_data:
        raise HTTPException(
            400,
            "Необходимо согласие на обработку персональных данных (152-ФЗ)",
        )
    if not req.consent_medical_ai:
        raise HTTPException(
            400,
            "Необходимо согласие на использование AI-ассистента. "
            "AI не заменяет врача и предоставляет информацию справочного характера.",
        )

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
        user_id = create_user(
            req.username, pw_hash, patient_id,
            consent_personal_data=req.consent_personal_data,
            consent_medical_ai=req.consent_medical_ai,
        )
    except Exception as e:
        if "UNIQUE" in str(e).upper() or "unique" in str(e).lower():
            raise HTTPException(409, "Пользователь с таким логином уже существует")
        logger.exception("Failed to create user: %s", req.username)
        raise HTTPException(500, "Ошибка при создании аккаунта")

    logger.info("[REGISTER] user=%s, patient=%s", req.username, patient_id)

    AuditLogService.log_security(
        "user_registered",
        f"Зарегистрирован пользователь {req.username}",
        data={"user_id": user_id, "patient_id": patient_id, "username": req.username},
        request=request,
    )

    token = create_access_token(user_id, patient_id, username=req.username)
    refresh = create_refresh_token(user_id, patient_id, username=req.username)
    return AuthResponse(token=token, refresh_token=refresh, patient_id=patient_id, username=req.username)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, request: Request):
    check_auth_rate_limit(request)

    user = get_user_by_username(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        logger.warning("[LOGIN_FAIL] user=%s", req.username)
        AuditLogService.log_security(
            "login_failed",
            f"Неудачная попытка входа: {req.username}",
            data={"username": req.username},
            request=request,
        )
        raise HTTPException(401, "Неверный логин или пароль")

    logger.info("[LOGIN] user=%s, patient=%s", user["username"], user["patient_id"])

    AuditLogService.log_security(
        "user_logged_in",
        f"Пользователь {user['username']} вошёл в систему",
        data={"user_id": user["id"], "patient_id": user["patient_id"]},
        actor={"user_id": user["id"], "username": user["username"]},
        request=request,
    )

    token = create_access_token(user["id"], user["patient_id"], username=user["username"])
    refresh = create_refresh_token(user["id"], user["patient_id"], username=user["username"])
    return AuthResponse(
        token=token,
        refresh_token=refresh,
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

    AuditLogService.log_security(
        "password_changed",
        f"Пользователь {user['username']} сменил пароль",
        actor=current_user,
    )

    return {"message": "Пароль успешно изменён"}


@router.delete("/me")
def delete_account(current_user: dict = Depends(get_current_user)):
    if not delete_user(current_user["user_id"]):
        raise HTTPException(404, "Пользователь не найден")

    AuditLogService.log_security(
        "account_deleted",
        f"Аккаунт удалён: user_id={current_user['user_id']}",
        data={"user_id": current_user["user_id"], "patient_id": current_user.get("patient_id")},
        actor=current_user,
    )

    return {"message": "Аккаунт удалён"}


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(req: RefreshRequest):
    """Exchange a valid refresh token for new access + refresh tokens.

    Uses jti (JWT ID) to prevent token reuse — each refresh token
    can only be used once (rotation).
    """
    payload = decode_token(req.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(401, "Недействительный refresh-токен")

    # Check jti blocklist (if token has jti — old tokens without jti still work)
    jti = payload.get("jti")
    if jti and is_token_revoked(jti):
        logger.warning("[REFRESH_REUSE] Revoked token reuse attempt, user_id=%s, jti=%s", payload.get("user_id"), jti)
        AuditLogService.log_security(
            "refresh_token_reuse",
            f"Попытка повторного использования refresh-токена",
            data={"user_id": payload.get("user_id"), "jti": jti},
        )
        raise HTTPException(401, "Refresh-токен уже использован")

    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(401, "Пользователь не найден")

    # Revoke the old refresh token
    if jti:
        from datetime import datetime, timezone
        exp_ts = payload.get("exp", 0)
        expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        revoke_token(jti, user["id"], expires_at)

    new_access = create_access_token(user["id"], user["patient_id"], username=user["username"])
    new_refresh = create_refresh_token(user["id"], user["patient_id"], username=user["username"])

    return AuthResponse(
        token=new_access,
        refresh_token=new_refresh,
        patient_id=user["patient_id"] or "",
        username=user["username"],
    )
