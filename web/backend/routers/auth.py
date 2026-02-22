"""Authentication endpoints: register, login, me."""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.models.patient import Patient, Gender, BloodType, Allergy
from src.utils.database import (
    save_patient, create_user, get_user_by_username, get_user_by_id,
    link_user_to_patient, update_user_password, delete_user,
)
from ..auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


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
def register(req: RegisterRequest):
    if get_user_by_username(req.username):
        raise HTTPException(409, "Пользователь с таким логином уже существует")

    if len(req.password) < 4:
        raise HTTPException(400, "Пароль должен содержать минимум 4 символа")

    # Create patient record
    patient = Patient(
        id=str(uuid.uuid4())[:8],
        first_name=req.first_name,
        last_name=req.last_name,
        date_of_birth=date.fromisoformat(req.date_of_birth),
        gender=Gender(req.gender),
        blood_type=BloodType(req.blood_type) if req.blood_type else None,
        allergies=[
            Allergy(substance=a.get("substance", ""), reaction=a.get("reaction", ""), severity=a.get("severity", "moderate"))
            for a in (req.allergies or [])
        ],
        family_history=req.family_history or [],
    )
    patient_id = save_patient(patient)

    # Create user linked to patient
    pw_hash = hash_password(req.password)
    user_id = create_user(req.username, pw_hash, patient_id)

    token = create_token(user_id, patient_id)
    return AuthResponse(token=token, patient_id=patient_id, username=req.username)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    user = get_user_by_username(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "Неверный логин или пароль")

    token = create_token(user["id"], user["patient_id"])
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
    if len(req.new_password) < 4:
        raise HTTPException(400, "Новый пароль должен содержать минимум 4 символа")
    new_hash = hash_password(req.new_password)
    update_user_password(current_user["user_id"], new_hash)
    return {"message": "Пароль успешно изменён"}


@router.delete("/me")
def delete_account(current_user: dict = Depends(get_current_user)):
    if not delete_user(current_user["user_id"]):
        raise HTTPException(404, "Пользователь не найден")
    return {"message": "Аккаунт удалён"}
