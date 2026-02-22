"""Consultation history endpoints."""
import logging

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.utils.database import get_consultation_history
from ..auth import get_optional_user
from ..services import claude_service

logger = logging.getLogger("aibolit.consultations")

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
async def start_consultation(
    req: ConsultStartRequest,
    current_user: dict | None = Depends(get_optional_user),
):
    from src.mcp_server import _handle_consultation
    from src.agents.specializations import get_specialization
    from src.utils.database import load_patient

    # Auto-fill patient_id from token if not provided
    patient_id = req.patient_id
    if not patient_id and current_user:
        patient_id = current_user.get("patient_id")

    # Always build the base structured response (doctor info, tests, ICD codes)
    base = _handle_consultation(req.specialty, req.complaints, patient_id)
    if "error" in base:
        return base

    # Try to enrich summary with Claude AI
    spec = get_specialization(req.specialty)
    if spec and claude_service.is_available():
        patient_context = ""
        if patient_id:
            patient = load_patient(patient_id)
            if patient:
                patient_context = patient.summary()

        ai_text = await claude_service.generate_consultation(
            specialty_name=spec.name_ru,
            complaints=req.complaints,
            patient_context=patient_context or "Карта пациента не загружена",
        )

        if ai_text:
            base["consultation"]["summary"] = ai_text
            base["ai_generated"] = True
            logger.info("AI consultation generated for specialty=%s", req.specialty)
        else:
            base["ai_generated"] = False
    else:
        base["ai_generated"] = False

    return base
