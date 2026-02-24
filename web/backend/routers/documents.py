"""Medical document generation + file upload/download endpoints."""
import os
import re

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel

from src.tools.documentation import (
    generate_medical_record,
    generate_referral,
    generate_prescription,
    generate_discharge_summary,
)
from src.utils.database import (
    save_document, list_documents, get_document, delete_document,
)
from ..auth import get_current_user
from ..services.audit_service import AuditLogService

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf", "image/jpeg", "image/png", "image/webp",
    "text/plain", "text/csv",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
_SAFE_FILENAME_RE = re.compile(r'[^\w\s\-\.\(\)]', re.UNICODE)


def _sanitize_filename(name: str) -> str:
    """Strip path traversal and special chars from uploaded filename."""
    name = os.path.basename(name)  # strip directory components
    name = _SAFE_FILENAME_RE.sub('_', name)  # replace unsafe chars
    return name[:255] or "untitled"  # limit length


# ── Document generation (existing) ──────────────────────────

class MedicalRecordRequest(BaseModel):
    patient_name: str
    patient_age: int
    gender: str
    complaints: str
    anamnesis: str
    examination: str
    diagnoses: list[dict]
    plan: str
    doctor_specialty: str = ""
    vitals: dict | None = None
    lab_results: list | None = None


class PrescriptionRequest(BaseModel):
    patient_name: str
    medications: list[dict]
    diagnoses: list[str]
    doctor_specialty: str = ""
    notes: str = ""


class ReferralRequest(BaseModel):
    patient_name: str
    patient_age: int
    from_specialty: str
    to_specialty: str
    reason: str
    current_diagnoses: list[str]
    relevant_results: str = ""
    urgency: str = "routine"


class DischargeSummaryRequest(BaseModel):
    patient_name: str
    patient_age: int
    gender: str
    admission_date: str
    discharge_date: str
    admission_diagnosis: str
    final_diagnosis: str
    treatment_summary: str
    discharge_condition: str
    follow_up: str
    recommendations: list[str]
    discharge_medications: list = []


@router.post("/medical-record")
def medical_record(req: MedicalRecordRequest):
    text = generate_medical_record(**req.model_dump())
    return {"document": text}


@router.post("/prescription")
def prescription(req: PrescriptionRequest):
    text = generate_prescription(**req.model_dump())
    return {"document": text}


@router.post("/referral")
def referral(req: ReferralRequest):
    text = generate_referral(**req.model_dump())
    return {"document": text}


@router.post("/discharge-summary")
def discharge_summary(req: DischargeSummaryRequest):
    text = generate_discharge_summary(**req.model_dump())
    return {"document": text}


# ── File upload / download ──────────────────────────────────

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    notes: str = Form(""),
    current_user: dict = Depends(get_current_user),
):
    patient_id = current_user.get("patient_id")
    if not patient_id:
        raise HTTPException(400, "Нет привязанной карты пациента")

    # Validate content type
    content_type = file.content_type or ""
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            415, f"Тип файла '{content_type}' не поддерживается. "
            "Допустимые: PDF, JPEG, PNG, WEBP, TXT, CSV, DOC, DOCX"
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(413, "Файл слишком большой (максимум 10 МБ)")

    safe_name = _sanitize_filename(file.filename or "untitled")

    doc_id = save_document(
        patient_id=patient_id,
        file_name=safe_name,
        file_type=content_type,
        file_size=len(content),
        content=content,
        notes=notes,
    )

    AuditLogService.log_db_create(
        "document", doc_id,
        data={"patient_id": patient_id, "file_name": safe_name, "file_type": content_type, "file_size": len(content)},
        actor=current_user,
    )

    return {"id": doc_id, "file_name": safe_name, "file_size": len(content)}


@router.get("/my")
def my_documents(current_user: dict = Depends(get_current_user)):
    patient_id = current_user.get("patient_id")
    if not patient_id:
        raise HTTPException(400, "Нет привязанной карты пациента")
    return list_documents(patient_id)


@router.get("/{doc_id}/download")
def download_document(doc_id: int, current_user: dict = Depends(get_current_user)):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Документ не найден")
    # Ownership check
    if doc["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа к этому документу")
    AuditLogService.log_business(
        "document_downloaded",
        data={"document_id": doc_id, "patient_id": doc["patient_id"], "file_name": doc["file_name"]},
        actor=current_user,
    )

    safe_name = _sanitize_filename(doc["file_name"])
    return Response(
        content=doc["content"],
        media_type=doc["file_type"] or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )


@router.delete("/{doc_id}")
def remove_document(doc_id: int, current_user: dict = Depends(get_current_user)):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Документ не найден")
    if doc["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа к этому документу")
    delete_document(doc_id)

    AuditLogService.log_db_delete(
        "document", doc_id,
        actor=current_user,
    )

    return {"ok": True}
