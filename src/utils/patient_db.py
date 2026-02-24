"""Patient database — backward-compatible wrapper.

Delegates all CRUD operations to the PostgreSQL-backed database module.
Retains JSON serialization helpers (_dict_to_patient, _patient_to_dict)
for use by the migration script.
"""
import json
import os
from datetime import date, datetime
from typing import Any

from ..models.patient import (
    Patient, VitalSigns, Allergy, Medication, LabResult, Diagnosis, Gender, BloodType
)

# ── Re-export public API from database module ────────────────
from .database import (           # noqa: F401
    save_patient,
    load_patient,
    list_patients,
    delete_patient,
    init_db,
)

# ── Legacy data directory (used by migration) ────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "patients")


# ── JSON encoder (kept for any external users) ───────────────

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if hasattr(obj, 'value'):
            return obj.value
        return super().default(obj)


# ── Serialization helpers (used by migration) ────────────────

def _patient_to_dict(p: Patient) -> dict:
    """Serialize patient to dict."""
    return {
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "date_of_birth": p.date_of_birth.isoformat(),
        "gender": p.gender.value,
        "blood_type": p.blood_type.value if p.blood_type else None,
        "allergies": [{"substance": a.substance, "reaction": a.reaction, "severity": a.severity} for a in p.allergies],
        "medications": [
            {"name": m.name, "dosage": m.dosage, "frequency": m.frequency, "route": m.route,
             "start_date": m.start_date.isoformat() if m.start_date else None,
             "end_date": m.end_date.isoformat() if m.end_date else None,
             "prescribing_doctor": m.prescribing_doctor, "notes": m.notes}
            for m in p.medications
        ],
        "diagnoses": [
            {"icd10_code": d.icd10_code, "name": d.name,
             "date_diagnosed": d.date_diagnosed.isoformat(),
             "status": d.status, "notes": d.notes, "confidence": d.confidence}
            for d in p.diagnoses
        ],
        "lab_results": [
            {"test_name": lr.test_name, "value": lr.value, "unit": lr.unit,
             "reference_range": lr.reference_range, "date": lr.date.isoformat(),
             "is_abnormal": lr.is_abnormal, "notes": lr.notes}
            for lr in p.lab_results
        ],
        "vitals_history": [
            {"timestamp": v.timestamp.isoformat(),
             "systolic_bp": v.systolic_bp, "diastolic_bp": v.diastolic_bp,
             "heart_rate": v.heart_rate, "temperature": v.temperature,
             "spo2": v.spo2, "respiratory_rate": v.respiratory_rate,
             "weight": v.weight, "height": v.height, "blood_glucose": v.blood_glucose}
            for v in p.vitals_history
        ],
        "family_history": p.family_history,
        "surgical_history": p.surgical_history,
        "lifestyle": p.lifestyle,
        "genetic_markers": p.genetic_markers,
        "notes": p.notes,
    }


def _dict_to_patient(d: dict) -> Patient:
    """Deserialize patient from dict."""
    return Patient(
        id=d["id"],
        first_name=d["first_name"],
        last_name=d["last_name"],
        date_of_birth=date.fromisoformat(d["date_of_birth"]),
        gender=Gender(d["gender"]),
        blood_type=BloodType(d["blood_type"]) if d.get("blood_type") else None,
        allergies=[Allergy(**a) for a in d.get("allergies", [])],
        medications=[
            Medication(
                name=m["name"], dosage=m["dosage"], frequency=m["frequency"],
                route=m.get("route", "oral"),
                start_date=date.fromisoformat(m["start_date"]) if m.get("start_date") else None,
                end_date=date.fromisoformat(m["end_date"]) if m.get("end_date") else None,
                prescribing_doctor=m.get("prescribing_doctor", ""),
                notes=m.get("notes", ""),
            )
            for m in d.get("medications", [])
        ],
        diagnoses=[
            Diagnosis(
                icd10_code=diag["icd10_code"], name=diag["name"],
                date_diagnosed=date.fromisoformat(diag["date_diagnosed"]),
                status=diag.get("status", "active"),
                notes=diag.get("notes", ""),
                confidence=diag.get("confidence", 0.0),
            )
            for diag in d.get("diagnoses", [])
        ],
        lab_results=[
            LabResult(
                test_name=lr["test_name"], value=lr["value"],
                unit=lr.get("unit", ""), reference_range=lr.get("reference_range", ""),
                date=date.fromisoformat(lr["date"]),
                is_abnormal=lr.get("is_abnormal", False),
                notes=lr.get("notes", ""),
            )
            for lr in d.get("lab_results", [])
        ],
        vitals_history=[
            VitalSigns(
                timestamp=datetime.fromisoformat(v["timestamp"]),
                systolic_bp=v.get("systolic_bp"), diastolic_bp=v.get("diastolic_bp"),
                heart_rate=v.get("heart_rate"), temperature=v.get("temperature"),
                spo2=v.get("spo2"), respiratory_rate=v.get("respiratory_rate"),
                weight=v.get("weight"), height=v.get("height"),
                blood_glucose=v.get("blood_glucose"),
            )
            for v in d.get("vitals_history", [])
        ],
        family_history=d.get("family_history", []),
        surgical_history=d.get("surgical_history", []),
        lifestyle=d.get("lifestyle", {}),
        genetic_markers=d.get("genetic_markers", {}),
        notes=d.get("notes", ""),
    )
