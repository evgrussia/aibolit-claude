"""Pydantic schemas for patient data."""
from pydantic import BaseModel


class AllergySchema(BaseModel):
    id: int | None = None
    substance: str
    reaction: str = ""
    severity: str = "moderate"


class MedicationSchema(BaseModel):
    id: int | None = None
    name: str
    dosage: str
    frequency: str
    route: str = "oral"
    start_date: str | None = None
    end_date: str | None = None
    prescribing_doctor: str = ""
    notes: str = ""


class DiagnosisSchema(BaseModel):
    id: int | None = None
    icd10_code: str
    name: str
    date_diagnosed: str = ""
    status: str = "active"
    notes: str = ""
    confidence: float = 0.0


class LabResultSchema(BaseModel):
    id: int | None = None
    test_name: str
    value: float | str
    unit: str = ""
    reference_range: str = ""
    date: str = ""
    is_abnormal: bool = False
    notes: str = ""


class VitalSignsSchema(BaseModel):
    id: int | None = None
    timestamp: str = ""
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    heart_rate: int | None = None
    temperature: float | None = None
    spo2: float | None = None
    respiratory_rate: int | None = None
    weight: float | None = None
    height: float | None = None
    blood_glucose: float | None = None


class PatientSummary(BaseModel):
    id: str
    name: str
    dob: str
    gender: str


class PatientResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    full_name: str
    age: int
    date_of_birth: str
    gender: str
    blood_type: str | None = None
    allergies: list[AllergySchema]
    medications: list[MedicationSchema]
    diagnoses: list[DiagnosisSchema]
    lab_results: list[LabResultSchema]
    vitals_history: list[VitalSignsSchema]
    family_history: list[str]
    surgical_history: list[str]
    lifestyle: dict[str, str]
    notes: str


class RegisterPatientRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    blood_type: str | None = None
    allergies: list[AllergySchema] = []
    family_history: list[str] = []


class AddVitalsRequest(BaseModel):
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    heart_rate: int | None = None
    temperature: float | None = None
    spo2: float | None = None
    respiratory_rate: int | None = None
    weight: float | None = None
    height: float | None = None
    blood_glucose: float | None = None


class AddLabResultRequest(BaseModel):
    test_name: str
    value: float | str
    unit: str = ""
    reference_range: str = ""


class AddDiagnosisRequest(BaseModel):
    icd10_code: str
    name: str
    status: str = "active"
    notes: str = ""
    confidence: float = 0.0


class AddMedicationRequest(BaseModel):
    name: str
    dosage: str
    frequency: str
    route: str = "oral"
    notes: str = ""


class AddAllergyRequest(BaseModel):
    substance: str
    reaction: str = ""
    severity: str = "moderate"


class UpdatePatientRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    blood_type: str | None = None
    notes: str | None = None
    family_history: list[str] | None = None
    surgical_history: list[str] | None = None
    lifestyle: dict[str, str] | None = None
