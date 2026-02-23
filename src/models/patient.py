"""Patient data models."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodType(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


@dataclass
class VitalSigns:
    """Patient vital signs snapshot."""
    id: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    systolic_bp: int | None = None  # mmHg
    diastolic_bp: int | None = None  # mmHg
    heart_rate: int | None = None  # bpm
    temperature: float | None = None  # Celsius
    spo2: float | None = None  # %
    respiratory_rate: int | None = None  # breaths/min
    weight: float | None = None  # kg
    height: float | None = None  # cm
    blood_glucose: float | None = None  # mmol/L

    def bmi(self) -> float | None:
        if self.weight and self.height:
            return round(self.weight / (self.height / 100) ** 2, 1)
        return None

    def map_pressure(self) -> float | None:
        """Mean arterial pressure."""
        if self.systolic_bp and self.diastolic_bp:
            return round(self.diastolic_bp + (self.systolic_bp - self.diastolic_bp) / 3, 1)
        return None

    def assess(self) -> list[str]:
        """Return list of abnormalities detected."""
        alerts = []
        # --- Blood pressure ---
        if self.systolic_bp and self.systolic_bp >= 180:
            alerts.append(
                f"КРИТИЧНО: систолическое АД {self.systolic_bp} mmHg (>=180) "
                "— гипертонический криз! Вызовите скорую: 103 / 112"
            )
        elif self.systolic_bp and self.systolic_bp > 140:
            alerts.append(f"Гипертензия: систолическое {self.systolic_bp} mmHg (>140)")
        if self.systolic_bp and self.systolic_bp < 90:
            alerts.append(f"Гипотензия: систолическое {self.systolic_bp} mmHg (<90)")
        if self.diastolic_bp and self.diastolic_bp >= 110:
            alerts.append(
                f"КРИТИЧНО: диастолическое АД {self.diastolic_bp} mmHg (>=110) "
                "— гипертонический криз! Вызовите скорую: 103 / 112"
            )
        elif self.diastolic_bp and self.diastolic_bp > 90:
            alerts.append(f"Гипертензия: диастолическое {self.diastolic_bp} mmHg (>90)")

        # --- Heart rate ---
        if self.heart_rate and self.heart_rate >= 150:
            alerts.append(
                f"КРИТИЧНО: ЧСС {self.heart_rate} уд/мин (>=150) "
                "— тахиаритмия! Вызовите скорую: 103 / 112"
            )
        elif self.heart_rate and self.heart_rate > 100:
            alerts.append(f"Тахикардия: ЧСС {self.heart_rate} уд/мин (>100)")
        if self.heart_rate and self.heart_rate < 40:
            alerts.append(
                f"КРИТИЧНО: ЧСС {self.heart_rate} уд/мин (<40) "
                "— выраженная брадикардия! Вызовите скорую: 103 / 112"
            )
        elif self.heart_rate and self.heart_rate < 60:
            alerts.append(f"Брадикардия: ЧСС {self.heart_rate} уд/мин (<60)")

        # --- Temperature ---
        if self.temperature and self.temperature >= 40.0:
            alerts.append(
                f"КРИТИЧНО: температура {self.temperature}°C (>=40) "
                "— гиперпирексия! Вызовите скорую: 103 / 112"
            )
        elif self.temperature and self.temperature > 37.5:
            alerts.append(f"Лихорадка: {self.temperature}°C (>37.5)")
        if self.temperature and self.temperature < 35.0:
            alerts.append(
                f"КРИТИЧНО: температура {self.temperature}°C (<35) "
                "— выраженная гипотермия! Вызовите скорую: 103 / 112"
            )
        elif self.temperature and self.temperature < 36.0:
            alerts.append(f"Гипотермия: {self.temperature}°C (<36.0)")

        # --- SpO2 ---
        if self.spo2 and self.spo2 < 90:
            alerts.append(
                f"КРИТИЧНО: SpO2 {self.spo2}% (<90) "
                "— тяжёлая гипоксия! Вызовите скорую: 103 / 112"
            )
        elif self.spo2 and self.spo2 < 95:
            alerts.append(f"Гипоксемия: SpO2 {self.spo2}% (<95)")

        # --- Respiratory rate ---
        if self.respiratory_rate and self.respiratory_rate > 20:
            alerts.append(f"Тахипноэ: ЧД {self.respiratory_rate}/мин (>20)")

        # --- Blood glucose ---
        if self.blood_glucose and self.blood_glucose >= 20.0:
            alerts.append(
                f"КРИТИЧНО: глюкоза {self.blood_glucose} ммоль/л (>=20) "
                "— гипергликемический криз! Вызовите скорую: 103 / 112"
            )
        elif self.blood_glucose and self.blood_glucose > 11.1:
            alerts.append(f"Гипергликемия: {self.blood_glucose} ммоль/л (>11.1)")
        if self.blood_glucose and self.blood_glucose < 2.8:
            alerts.append(
                f"КРИТИЧНО: глюкоза {self.blood_glucose} ммоль/л (<2.8) "
                "— тяжёлая гипогликемия! Вызовите скорую: 103 / 112"
            )
        elif self.blood_glucose and self.blood_glucose < 3.9:
            alerts.append(f"Гипогликемия: {self.blood_glucose} ммоль/л (<3.9)")

        # --- BMI ---
        bmi = self.bmi()
        if bmi and bmi > 30:
            alerts.append(f"Ожирение: ИМТ {bmi} (>30)")
        if bmi and bmi < 18.5:
            alerts.append(f"Дефицит массы тела: ИМТ {bmi} (<18.5)")
        return alerts


@dataclass
class Allergy:
    substance: str
    reaction: str = ""
    severity: str = "moderate"  # mild, moderate, severe
    id: int | None = None


@dataclass
class Medication:
    name: str
    dosage: str
    frequency: str
    route: str = "oral"
    start_date: date | None = None
    end_date: date | None = None
    prescribing_doctor: str = ""
    notes: str = ""
    id: int | None = None


@dataclass
class LabResult:
    test_name: str
    value: float | str
    unit: str = ""
    reference_range: str = ""
    date: date = field(default_factory=date.today)
    is_abnormal: bool = False
    notes: str = ""
    id: int | None = None


@dataclass
class Diagnosis:
    icd10_code: str
    name: str
    date_diagnosed: date = field(default_factory=date.today)
    status: str = "active"  # active, resolved, chronic
    notes: str = ""
    confidence: float = 0.0  # AI confidence 0-1
    id: int | None = None


@dataclass
class Patient:
    """Complete patient record."""
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    blood_type: BloodType | None = None
    allergies: list[Allergy] = field(default_factory=list)
    medications: list[Medication] = field(default_factory=list)
    diagnoses: list[Diagnosis] = field(default_factory=list)
    lab_results: list[LabResult] = field(default_factory=list)
    vitals_history: list[VitalSigns] = field(default_factory=list)
    family_history: list[str] = field(default_factory=list)
    surgical_history: list[str] = field(default_factory=list)
    lifestyle: dict[str, str] = field(default_factory=dict)
    genetic_markers: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name}"

    @property
    def latest_vitals(self) -> VitalSigns | None:
        return self.vitals_history[-1] if self.vitals_history else None

    @property
    def active_diagnoses(self) -> list[Diagnosis]:
        return [d for d in self.diagnoses if d.status == "active"]

    @property
    def chronic_conditions(self) -> list[Diagnosis]:
        return [d for d in self.diagnoses if d.status == "chronic"]

    def get_recent_labs(self, days: int = 30) -> list[LabResult]:
        cutoff = date.today()
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=days)
        return [lr for lr in self.lab_results if lr.date >= cutoff]

    def summary(self) -> str:
        """Generate patient summary for AI doctors."""
        parts = [
            f"Пациент: {self.full_name}, {self.age} лет, {self.gender.value}",
        ]
        if self.blood_type:
            parts.append(f"Группа крови: {self.blood_type.value}")
        if self.allergies:
            parts.append(f"Аллергии: {', '.join(a.substance for a in self.allergies)}")
        if self.active_diagnoses:
            parts.append(f"Активные диагнозы: {', '.join(d.name for d in self.active_diagnoses)}")
        if self.chronic_conditions:
            parts.append(f"Хронические заболевания: {', '.join(d.name for d in self.chronic_conditions)}")
        if self.medications:
            parts.append(f"Текущие препараты: {', '.join(f'{m.name} {m.dosage}' for m in self.medications)}")
        if self.latest_vitals:
            alerts = self.latest_vitals.assess()
            if alerts:
                parts.append(f"Отклонения витальных показателей: {'; '.join(alerts)}")
        return "\n".join(parts)
