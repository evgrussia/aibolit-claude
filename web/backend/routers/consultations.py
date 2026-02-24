"""Consultation and triage endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.agents.specializations import get_specialization
from src.safety.disclaimers import DisclaimerType, get_disclaimer
from src.safety.red_flags import RedFlagDetector
from src.utils.database import get_consultation_history, load_patient, save_consultation
from ..auth import get_optional_user
from ..services import claude_service
from ..services.audit_service import AuditLogService
from ..services.consultation_service import build_consultation
from ..services.triage_service import engine as triage_engine

logger = logging.getLogger("aibolit.consultations")

router = APIRouter(prefix="/consultations", tags=["consultations"])

_red_flag_detector = RedFlagDetector()


class TriageRequest(BaseModel):
    complaints: str


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


@router.post("/triage")
def triage(req: TriageRequest):
    """Analyze complaints and suggest the best specialist(s)."""
    if not req.complaints or len(req.complaints.strip()) < 3:
        raise HTTPException(400, "Опишите жалобы (минимум 3 символа)")
    matches = triage_engine.triage(req.complaints.strip(), top_n=3)
    # Also check red flags
    flags = _red_flag_detector.detect(req.complaints)
    result: dict = {
        "recommendations": [
            {
                "specialty_id": m.specialty_id,
                "name_ru": m.name_ru,
                "description": m.description,
                "relevance": m.score,
                "reason": m.reason,
            }
            for m in matches
        ],
    }
    if flags:
        immediate = [f for f in flags if f.urgency >= 5]
        if immediate:
            result["emergency"] = {
                "call": "103 / 112",
                "message": "Обнаружены признаки, требующие экстренной медицинской помощи!",
                "flags": [{"description": f.description, "action": f.action} for f in immediate],
            }
        result["red_flags"] = [
            {"description": f.description, "urgency": int(f.urgency), "action": f.action}
            for f in flags
        ]
        AuditLogService.log_medical(
            "red_flag_detected",
            data={"source": "triage", "flags_count": len(flags),
                  "emergency": bool([f for f in flags if f.urgency >= 5])},
            actor="system",
            level="WARNING",
        )

    AuditLogService.log_medical(
        "triage_completed",
        data={"recommendations_count": len(matches),
              "top_specialty": matches[0].specialty_id if matches else None},
    )

    return result


@router.post("/start")
async def start_consultation(
    req: ConsultStartRequest,
    current_user: dict | None = Depends(get_optional_user),
):
    # Auto-fill patient_id from token if not provided
    patient_id = req.patient_id
    if not patient_id and current_user:
        patient_id = current_user.get("patient_id")

    # Build the base structured response (doctor info, tests, ICD codes)
    base = build_consultation(req.specialty, req.complaints, patient_id)
    if "error" in base:
        return base

    # Claude CLI is mandatory — no fallback to template
    spec = get_specialization(req.specialty)
    if not spec:
        raise HTTPException(404, "Специализация не найдена")

    if not claude_service.is_available():
        raise HTTPException(503, "AI-сервис временно недоступен (Claude CLI не найден)")

    patient_context = ""
    if patient_id:
        patient = load_patient(patient_id)
        if patient:
            patient_context = patient.summary()
        else:
            logger.warning("Patient %s not found for consultation", patient_id)

    try:
        ai_text = await claude_service.generate_consultation(
            specialty_name=spec.name_ru,
            complaints=req.complaints,
            patient_context=patient_context or "Карта пациента не загружена",
            specialization=spec,
        )
    except Exception:
        logger.exception("Claude service error for specialty=%s", req.specialty)
        raise HTTPException(503, "AI-сервис временно недоступен (ошибка генерации)")

    if not ai_text:
        logger.warning("Empty AI response for specialty=%s, complaints=%s", req.specialty, req.complaints[:100])
        raise HTTPException(503, "AI-сервис временно недоступен (пустой ответ от Claude)")

    base["consultation"]["summary"] = ai_text
    base["ai_generated"] = True

    # --- Medical Safety: disclaimers ---
    disclaimers = [DisclaimerType.GENERAL, DisclaimerType.DIAGNOSIS]
    if req.specialty == "pediatrician":
        disclaimers.append(DisclaimerType.CHILDREN)
    base["disclaimer"] = " ".join(get_disclaimer(d) for d in disclaimers)

    # --- Medical Safety: red-flag detection ---
    flags = _red_flag_detector.detect(req.complaints)
    if flags:
        immediate = [f for f in flags if f.urgency >= 5]
        if immediate:
            base["emergency"] = {
                "call": "103 / 112",
                "message": "Обнаружены признаки, требующие экстренной медицинской помощи!",
                "flags": [
                    {"category": f.category, "description": f.description, "action": f.action}
                    for f in immediate
                ],
            }
            base["disclaimer"] = (
                get_disclaimer(DisclaimerType.EMERGENCY) + " " + base["disclaimer"]
            )
            logger.warning(
                "RED FLAGS detected for specialty=%s: %s",
                req.specialty,
                [f.description for f in immediate],
            )
        base["red_flags"] = [
            {"category": f.category, "description": f.description, "urgency": int(f.urgency), "action": f.action}
            for f in flags
        ]

    logger.info("AI consultation generated for specialty=%s", req.specialty)

    # Save consultation AFTER AI enrichment
    save_consultation(
        specialty=req.specialty,
        complaints=req.complaints,
        response=base,
        patient_id=patient_id,
    )

    AuditLogService.log_medical(
        "ai_consultation_completed",
        data={"specialty": req.specialty, "patient_id": patient_id,
              "ai_generated": True, "red_flags_count": len(flags) if flags else 0},
        actor=current_user,
    )

    return base
