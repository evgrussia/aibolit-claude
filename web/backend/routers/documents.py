"""Medical document generation endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

from src.tools.documentation import (
    generate_medical_record,
    generate_referral,
    generate_prescription,
    generate_discharge_summary,
)

router = APIRouter(prefix="/documents", tags=["documents"])


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
