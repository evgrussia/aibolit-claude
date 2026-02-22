"""Diagnostic tool endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

from src.tools.diagnostic import (
    analyze_lab_results,
    assess_vitals,
    calculate_gfr,
    calculate_cardiovascular_risk,
)

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


class LabTestInput(BaseModel):
    test: str
    value: float


class AnalyzeLabsRequest(BaseModel):
    results: list[LabTestInput]
    gender: str | None = None


class AssessVitalsRequest(BaseModel):
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    heart_rate: int | None = None
    temperature: float | None = None
    spo2: float | None = None
    respiratory_rate: int | None = None
    blood_glucose: float | None = None


class GfrRequest(BaseModel):
    creatinine: float
    age: int
    gender: str


class CvRiskRequest(BaseModel):
    age: int
    gender: str
    systolic_bp: int
    total_cholesterol: float
    hdl: float
    smoker: bool = False
    diabetic: bool = False
    on_bp_treatment: bool = False


@router.post("/analyze-labs")
def analyze_labs(req: AnalyzeLabsRequest):
    results = [{"test": t.test, "value": t.value} for t in req.results]
    return analyze_lab_results(results, req.gender)


@router.post("/assess-vitals")
def vitals_assessment(req: AssessVitalsRequest):
    kwargs = {k: v for k, v in req.model_dump().items() if v is not None}
    return assess_vitals(**kwargs)


@router.post("/calculate-gfr")
def gfr(req: GfrRequest):
    return calculate_gfr(req.creatinine, req.age, req.gender)


@router.post("/cardiovascular-risk")
def cv_risk(req: CvRiskRequest):
    return calculate_cardiovascular_risk(
        req.age, req.gender, req.systolic_bp,
        req.total_cholesterol, req.hdl,
        req.smoker, req.diabetic, req.on_bp_treatment,
    )
