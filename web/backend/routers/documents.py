"""Medical document generation + file upload/download endpoints."""
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

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


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

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(413, "Файл слишком большой (максимум 10 МБ)")

    doc_id = save_document(
        patient_id=patient_id,
        file_name=file.filename or "untitled",
        file_type=file.content_type or "",
        file_size=len(content),
        content=content,
        notes=notes,
    )
    return {"id": doc_id, "file_name": file.filename, "file_size": len(content)}


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
    return Response(
        content=doc["content"],
        media_type=doc["file_type"] or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc["file_name"]}"'},
    )


@router.delete("/{doc_id}")
def remove_document(doc_id: int, current_user: dict = Depends(get_current_user)):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Документ не найден")
    if doc["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа к этому документу")
    delete_document(doc_id)
    return {"ok": True}
