"""Patient CRUD and data endpoints."""
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, UploadFile, File

from src.models.patient import (
    Patient, VitalSigns, LabResult, Diagnosis, Medication, Allergy, Gender, BloodType,
)
from .auth import _parse_date, _parse_gender, _parse_blood_type
from src.utils.database import (
    list_patients, load_patient, save_patient, delete_patient,
    search_patients, add_vitals as db_add_vitals, add_lab_result as db_add_lab_result,
    add_diagnosis as db_add_diagnosis, add_medication as db_add_medication,
    add_allergy as db_add_allergy,
    get_lab_trends, get_vitals_trends, get_consultation_history,
    get_patients_by_diagnosis,
    delete_sub_record, update_sub_record, update_patient_fields,
)
from ..auth import get_current_user, get_optional_user
from ..schemas.patient import (
    PatientSummary, PatientResponse, RegisterPatientRequest,
    AddVitalsRequest, AddLabResultRequest, BulkAddLabResultsRequest,
    AddDiagnosisRequest, AddMedicationRequest,
    AddAllergyRequest, UpdatePatientRequest,
    AllergySchema, MedicationSchema, DiagnosisSchema, LabResultSchema, VitalSignsSchema,
)

router = APIRouter(prefix="/patients", tags=["patients"])

# Allowed sub-record table names (defense-in-depth, also validated in database.py)
_ALLOWED_TABLES = {"allergies", "medications", "diagnoses", "lab_results", "vitals"}


def _patient_to_response(p: Patient) -> PatientResponse:
    """Convert Patient dataclass to Pydantic response."""
    return PatientResponse(
        id=p.id,
        first_name=p.first_name,
        last_name=p.last_name,
        full_name=p.full_name,
        age=p.age,
        date_of_birth=p.date_of_birth.isoformat(),
        gender=p.gender.value,
        blood_type=p.blood_type.value if p.blood_type else None,
        allergies=[
            AllergySchema(id=a.id, substance=a.substance, reaction=a.reaction, severity=a.severity)
            for a in p.allergies
        ],
        medications=[
            MedicationSchema(
                id=m.id, name=m.name, dosage=m.dosage, frequency=m.frequency, route=m.route,
                start_date=m.start_date.isoformat() if m.start_date else None,
                end_date=m.end_date.isoformat() if m.end_date else None,
                prescribing_doctor=m.prescribing_doctor, notes=m.notes,
            )
            for m in p.medications
        ],
        diagnoses=[
            DiagnosisSchema(
                id=d.id, icd10_code=d.icd10_code, name=d.name,
                date_diagnosed=d.date_diagnosed.isoformat(),
                status=d.status, notes=d.notes, confidence=d.confidence,
            )
            for d in p.diagnoses
        ],
        lab_results=[
            LabResultSchema(
                id=lr.id, test_name=lr.test_name, value=lr.value, unit=lr.unit,
                reference_range=lr.reference_range, date=lr.date.isoformat(),
                is_abnormal=lr.is_abnormal, notes=lr.notes,
            )
            for lr in p.lab_results
        ],
        vitals_history=[
            VitalSignsSchema(
                id=v.id, timestamp=v.timestamp.isoformat(),
                systolic_bp=v.systolic_bp, diastolic_bp=v.diastolic_bp,
                heart_rate=v.heart_rate, temperature=v.temperature,
                spo2=v.spo2, respiratory_rate=v.respiratory_rate,
                weight=v.weight, height=v.height, blood_glucose=v.blood_glucose,
            )
            for v in p.vitals_history
        ],
        family_history=p.family_history,
        surgical_history=p.surgical_history,
        lifestyle=p.lifestyle,
        notes=p.notes,
    )


def _check_patient_access(patient_id: str, current_user: dict | None) -> None:
    """If user is authenticated, verify they can only access their own patient data."""
    if current_user and current_user.get("patient_id"):
        if patient_id != current_user["patient_id"]:
            raise HTTPException(403, "Доступ запрещён")


@router.get("/me", response_model=PatientResponse)
def get_my_patient(current_user: dict = Depends(get_current_user)):
    """Get the authenticated user's own patient record."""
    patient_id = current_user.get("patient_id")
    if not patient_id:
        raise HTTPException(404, "Карта пациента не привязана к аккаунту")
    p = load_patient(patient_id)
    if not p:
        raise HTTPException(404, "Карта пациента не найдена")
    return _patient_to_response(p)


@router.get("", response_model=list[PatientSummary])
def get_patients(_: dict = Depends(get_current_user)):
    return list_patients()


@router.get("/search", response_model=list[PatientSummary])
def search(q: str = Query(..., min_length=1), _: dict = Depends(get_current_user)):
    return search_patients(q)


@router.get("/by-diagnosis", response_model=list[dict])
def patients_by_diagnosis(icd10: str = Query(..., min_length=1), _: dict = Depends(get_current_user)):
    return get_patients_by_diagnosis(icd10)


@router.post("", response_model=dict)
def register_patient(req: RegisterPatientRequest, _: dict = Depends(get_current_user)):
    dob = _parse_date(req.date_of_birth)
    gender = _parse_gender(req.gender)
    blood_type = _parse_blood_type(req.blood_type)

    patient = Patient(
        id=str(uuid.uuid4())[:8],
        first_name=req.first_name,
        last_name=req.last_name,
        date_of_birth=dob,
        gender=gender,
        blood_type=blood_type,
        allergies=[
            Allergy(substance=a.substance, reaction=a.reaction, severity=a.severity)
            for a in req.allergies
        ],
        family_history=req.family_history,
    )
    pid = save_patient(patient)
    return {"id": pid, "message": f"Пациент {patient.full_name} зарегистрирован"}


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    p = load_patient(patient_id)
    if not p:
        raise HTTPException(404, f"Пациент {patient_id} не найден")
    return _patient_to_response(p)


@router.delete("/{patient_id}")
def remove_patient(patient_id: str, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    if not delete_patient(patient_id):
        raise HTTPException(404, f"Пациент {patient_id} не найден")
    return {"message": "Пациент удалён"}


@router.post("/{patient_id}/vitals")
def add_vitals(patient_id: str, req: AddVitalsRequest, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    vitals = VitalSigns(
        timestamp=datetime.now(),
        systolic_bp=req.systolic_bp, diastolic_bp=req.diastolic_bp,
        heart_rate=req.heart_rate, temperature=req.temperature,
        spo2=req.spo2, respiratory_rate=req.respiratory_rate,
        weight=req.weight, height=req.height, blood_glucose=req.blood_glucose,
    )
    try:
        row_id = db_add_vitals(patient_id, vitals)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"id": row_id, "message": "Витальные показатели записаны"}


@router.post("/{patient_id}/labs")
def add_lab(patient_id: str, req: AddLabResultRequest, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    lr = LabResult(
        test_name=req.test_name,
        value=req.value,
        unit=req.unit,
        reference_range=req.reference_range,
        date=date.today(),
    )
    try:
        row_id = db_add_lab_result(patient_id, lr)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"id": row_id, "message": f"Результат '{req.test_name}' добавлен"}


_ALLOWED_UPLOAD_TYPES = {
    "text/csv", "text/plain", "text/tab-separated-values",
    "application/pdf",
    "image/jpeg", "image/png", "image/webp",
}
_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/{patient_id}/labs/upload-parse")
async def parse_lab_file(
    patient_id: str,
    file: UploadFile = File(...),
    current_user: dict | None = Depends(get_optional_user),
):
    _check_patient_access(patient_id, current_user)
    if not load_patient(patient_id):
        raise HTTPException(404, f"Пациент {patient_id} не найден")

    # Validate content type
    ct = (file.content_type or "").lower()
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # Accept by MIME or extension
    ext_to_mime = {"csv": "text/csv", "txt": "text/plain", "tsv": "text/tab-separated-values",
                   "pdf": "application/pdf", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                   "png": "image/png", "webp": "image/webp"}
    effective_ct = ct if ct in _ALLOWED_UPLOAD_TYPES else ext_to_mime.get(ext, ct)

    if effective_ct not in _ALLOWED_UPLOAD_TYPES:
        raise HTTPException(400, f"Неподдерживаемый формат файла. Допустимы: PDF, JPEG, PNG, WEBP, CSV, TXT")

    content = await file.read()
    if len(content) > _MAX_UPLOAD_SIZE:
        raise HTTPException(400, "Файл слишком большой (максимум 10 МБ)")

    from ..services.lab_parser_service import parse_csv, parse_with_ai

    if effective_ct in {"text/csv", "text/plain", "text/tab-separated-values"}:
        result = parse_csv(content, filename)
    else:
        result = await parse_with_ai(content, filename, effective_ct)

    result["source_file"] = filename
    return result


@router.post("/{patient_id}/labs/bulk")
def add_labs_bulk(
    patient_id: str,
    req: BulkAddLabResultsRequest,
    current_user: dict | None = Depends(get_optional_user),
):
    _check_patient_access(patient_id, current_user)
    if not load_patient(patient_id):
        raise HTTPException(404, f"Пациент {patient_id} не найден")

    ids: list[int] = []
    for item in req.results:
        lr = LabResult(
            test_name=item.test_name,
            value=item.value,
            unit=item.unit,
            reference_range=item.reference_range,
            date=date.today(),
        )
        try:
            row_id = db_add_lab_result(patient_id, lr)
            ids.append(row_id)
        except ValueError as e:
            raise HTTPException(404, str(e))
    return {"ids": ids, "count": len(ids), "message": f"Добавлено {len(ids)} результатов"}


@router.post("/{patient_id}/diagnoses")
def add_diag(patient_id: str, req: AddDiagnosisRequest, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    diag = Diagnosis(
        icd10_code=req.icd10_code,
        name=req.name,
        status=req.status,
        notes=req.notes,
        confidence=req.confidence,
    )
    try:
        row_id = db_add_diagnosis(patient_id, diag)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"id": row_id, "message": f"Диагноз {req.icd10_code} добавлен"}


@router.post("/{patient_id}/medications")
def add_med(patient_id: str, req: AddMedicationRequest, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    med = Medication(
        name=req.name, dosage=req.dosage, frequency=req.frequency,
        route=req.route, notes=req.notes,
    )
    try:
        row_id = db_add_medication(patient_id, med)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"id": row_id, "message": f"Препарат '{req.name}' назначен"}


@router.get("/{patient_id}/lab-trends")
def lab_trends(patient_id: str, test: str = Query(..., min_length=1), limit: int = 20, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    return get_lab_trends(patient_id, test, limit)


@router.get("/{patient_id}/vitals-history")
def vitals_history(patient_id: str, limit: int = 20, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    return get_vitals_trends(patient_id, limit)


@router.get("/{patient_id}/consultations")
def patient_consultations(patient_id: str, limit: int = 50, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    return get_consultation_history(patient_id=patient_id, limit=limit)


@router.post("/{patient_id}/allergies")
def add_allergy(patient_id: str, req: AddAllergyRequest, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    allergy = Allergy(substance=req.substance, reaction=req.reaction, severity=req.severity)
    try:
        row_id = db_add_allergy(patient_id, allergy)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"id": row_id, "message": f"Аллергия '{req.substance}' добавлена"}


@router.delete("/{patient_id}/{table}/{record_id}")
def delete_record(patient_id: str, table: str, record_id: int, current_user: dict | None = Depends(get_optional_user)):
    if table not in _ALLOWED_TABLES:
        raise HTTPException(400, f"Недопустимая таблица: {table}")
    _check_patient_access(patient_id, current_user)
    try:
        if not delete_sub_record(patient_id, table, record_id):
            raise HTTPException(404, "Запись не найдена")
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"message": "Запись удалена"}


@router.patch("/{patient_id}/{table}/{record_id}")
def update_record(
    patient_id: str, table: str, record_id: int,
    fields: dict = Body(...),
    current_user: dict | None = Depends(get_optional_user),
):
    if table not in _ALLOWED_TABLES:
        raise HTTPException(400, f"Недопустимая таблица: {table}")
    _check_patient_access(patient_id, current_user)
    try:
        if not update_sub_record(patient_id, table, record_id, fields):
            raise HTTPException(404, "Запись не найдена или нет изменений")
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"message": "Запись обновлена"}


@router.patch("/{patient_id}")
def update_patient(patient_id: str, req: UpdatePatientRequest, current_user: dict | None = Depends(get_optional_user)):
    _check_patient_access(patient_id, current_user)
    p = load_patient(patient_id)
    if not p:
        raise HTTPException(404, f"Пациент {patient_id} не найден")

    # Direct field updates via SQL for core patient fields
    core_fields = {}
    if req.first_name is not None:
        core_fields["first_name"] = req.first_name
    if req.last_name is not None:
        core_fields["last_name"] = req.last_name
    if req.date_of_birth is not None:
        _parse_date(req.date_of_birth)  # validate format
        core_fields["date_of_birth"] = req.date_of_birth
    if req.gender is not None:
        _parse_gender(req.gender)  # validate enum
        core_fields["gender"] = req.gender
    if req.blood_type is not None:
        _parse_blood_type(req.blood_type)  # validate enum
        core_fields["blood_type"] = req.blood_type if req.blood_type else None
    if req.notes is not None:
        core_fields["notes"] = req.notes

    if core_fields:
        update_patient_fields(patient_id, core_fields)

    # List fields still use save_patient (replace-all strategy)
    needs_save = False
    if req.family_history is not None:
        p.family_history = req.family_history
        needs_save = True
    if req.surgical_history is not None:
        p.surgical_history = req.surgical_history
        needs_save = True
    if req.lifestyle is not None:
        p.lifestyle = req.lifestyle
        needs_save = True

    if needs_save:
        # Reload patient to get updated core fields
        p = load_patient(patient_id)
        if p:
            if req.family_history is not None:
                p.family_history = req.family_history
            if req.surgical_history is not None:
                p.surgical_history = req.surgical_history
            if req.lifestyle is not None:
                p.lifestyle = req.lifestyle
            save_patient(p)

    return {"message": "Данные пациента обновлены"}
