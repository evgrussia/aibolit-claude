"""Consultation history endpoints."""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.utils.database import get_consultation_history
from ..auth import get_optional_user

router = APIRouter(prefix="/consultations", tags=["consultations"])


class ConsultStartRequest(BaseModel):
    specialty: str
    complaints: str
    patient_id: str | None = None


@router.get("")
def list_consultations(
    specialty: str | None = None,
    limit: int = Query(50, le=200),
):
    return get_consultation_history(specialty=specialty, limit=limit)


@router.post("/start")
def start_consultation(req: ConsultStartRequest, current_user: dict | None = Depends(get_optional_user)):
    from src.mcp_server import _handle_consultation
    # Auto-fill patient_id from token if not provided
    patient_id = req.patient_id
    if not patient_id and current_user:
        patient_id = current_user.get("patient_id")
    return _handle_consultation(req.specialty, req.complaints, patient_id)
