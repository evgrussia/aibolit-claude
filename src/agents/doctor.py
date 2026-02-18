"""AI Doctor agent logic — clinical reasoning engine for all specializations."""
from __future__ import annotations
import json
from datetime import date
from ..models.patient import Patient, VitalSigns, LabResult, Diagnosis, Medication
from ..models.medical_refs import interpret_lab_value, LAB_REFERENCE_RANGES, DRUG_INTERACTIONS_CRITICAL
from .specializations import SPECIALIZATIONS, get_specialization


class AIDoctorEngine:
    """Core clinical reasoning engine used by all AI doctor specializations."""

    def __init__(self, specialization_id: str):
        self.spec = get_specialization(specialization_id)
        if not self.spec:
            raise ValueError(f"Unknown specialization: {specialization_id}")

    @property
    def doctor_name(self) -> str:
        return f"AI {self.spec.name_ru}"

    def get_system_prompt(self) -> str:
        """Generate the system prompt for this AI doctor."""
        skills_desc = "\n".join(
            f"  - {s.name}: {s.description}" for s in self.spec.skills
        )
        return f"""Вы — {self.spec.name_ru} ({self.spec.name_en}) в AI-клинике «Айболит».

Специализация: {self.spec.description}

Ваши навыки:
{skills_desc}

ВАЖНЫЕ ПРАВИЛА:
1. Всегда основывайтесь на доказательной медицине (EBM)
2. Указывайте уровень доказательности рекомендаций когда возможно
3. При неуверенности в диагнозе — рекомендуйте дополнительные обследования
4. Всегда учитывайте противопоказания и лекарственные взаимодействия
5. При угрожающих жизни состояниях — рекомендуйте экстренную помощь
6. Формулируйте диагнозы по МКБ-10/МКБ-11
7. Вы можете направить пациента к другому специалисту клиники
8. DISCLAIMER: Вы — AI-ассистент, не замена реальному врачу

Доступные внешние источники данных:
- PubMed (медицинская литература)
- OpenFDA (информация о лекарствах)
- RxNorm (лекарственные взаимодействия)
- ClinicalTrials.gov (клинические исследования)
- WHO ICD-11 (классификация болезней)
- NCBI Gene/OMIM (генетика)
- SNOMED CT (клиническая терминология)
- Open Targets (мишени для лекарств)
"""

    def analyze_vitals(self, vitals: VitalSigns) -> dict:
        """Analyze patient vital signs."""
        alerts = vitals.assess()
        bmi = vitals.bmi()
        map_val = vitals.map_pressure()

        return {
            "alerts": alerts,
            "bmi": bmi,
            "mean_arterial_pressure": map_val,
            "summary": f"Выявлено отклонений: {len(alerts)}" if alerts else "Витальные показатели в пределах нормы",
        }

    def analyze_labs(self, results: list[dict], gender: str = "male") -> dict:
        """Analyze laboratory results."""
        interpretations = []
        abnormal_count = 0

        for lab in results:
            test_key = lab.get("test_key", "")
            value = lab.get("value", 0)

            # Adjust for gender-specific tests
            if gender == "female" and f"{test_key}_female" in LAB_REFERENCE_RANGES:
                test_key = f"{test_key}_female"
            elif gender == "male" and f"{test_key}_male" in LAB_REFERENCE_RANGES:
                test_key = f"{test_key}_male"

            interpretation = interpret_lab_value(test_key, value)
            interpretations.append(interpretation)
            if interpretation["status"] != "normal":
                abnormal_count += 1

        return {
            "total_tests": len(results),
            "abnormal_count": abnormal_count,
            "results": interpretations,
            "summary": self._generate_lab_summary(interpretations),
        }

    def _generate_lab_summary(self, interpretations: list[dict]) -> str:
        """Generate a clinical summary of lab results."""
        critical = [i for i in interpretations if i.get("severity") == "critical"]
        significant = [i for i in interpretations if i.get("severity") == "significant"]
        mild = [i for i in interpretations if i.get("severity") == "mild"]

        parts = []
        if critical:
            parts.append(f"КРИТИЧЕСКИЕ отклонения ({len(critical)}): " +
                        ", ".join(f"{i['test_name']} = {i['value']} {i['unit']} ({i['status']})"
                                  for i in critical))
        if significant:
            parts.append(f"Значительные отклонения ({len(significant)}): " +
                        ", ".join(f"{i['test_name']} = {i['value']} {i['unit']}"
                                  for i in significant))
        if mild:
            parts.append(f"Незначительные отклонения ({len(mild)}): " +
                        ", ".join(f"{i['test_name']}" for i in mild))
        if not parts:
            parts.append("Все показатели в пределах референсных значений.")

        return "\n".join(parts)

    def check_drug_interactions(self, medications: list[str]) -> list[dict]:
        """Check for known drug interactions."""
        interactions = []
        meds_lower = [m.lower() for m in medications]

        for (drug1, drug2), warning in DRUG_INTERACTIONS_CRITICAL.items():
            for i, m1 in enumerate(meds_lower):
                for m2 in meds_lower[i + 1:]:
                    if (drug1 in m1 and drug2 in m2) or (drug2 in m1 and drug1 in m2):
                        interactions.append({
                            "drug1": medications[meds_lower.index(m1)],
                            "drug2": medications[meds_lower.index(m2)],
                            "warning": warning,
                            "severity": "critical",
                        })

        return interactions

    def calculate_cardiovascular_risk(self, age: int, gender: str, systolic_bp: int,
                                       total_cholesterol: float, hdl: float,
                                       smoker: bool, diabetic: bool) -> dict:
        """Simplified cardiovascular risk calculation (Framingham-like)."""
        risk_score = 0

        # Age
        if gender == "male":
            if age >= 55: risk_score += 12
            elif age >= 50: risk_score += 10
            elif age >= 45: risk_score += 8
            elif age >= 40: risk_score += 5
            elif age >= 35: risk_score += 2
        else:
            if age >= 55: risk_score += 10
            elif age >= 50: risk_score += 8
            elif age >= 45: risk_score += 6
            elif age >= 40: risk_score += 3
            elif age >= 35: risk_score += 1

        # Blood pressure
        if systolic_bp >= 180: risk_score += 5
        elif systolic_bp >= 160: risk_score += 4
        elif systolic_bp >= 140: risk_score += 3
        elif systolic_bp >= 130: risk_score += 1

        # Cholesterol
        ratio = total_cholesterol / hdl if hdl > 0 else 5.0
        if ratio >= 7: risk_score += 5
        elif ratio >= 6: risk_score += 3
        elif ratio >= 5: risk_score += 1

        if smoker: risk_score += 4
        if diabetic: risk_score += 4

        # Convert to approximate 10-year risk percentage
        risk_percent = min(risk_score * 1.5, 50)

        if risk_percent < 5:
            category = "Низкий"
        elif risk_percent < 10:
            category = "Умеренный"
        elif risk_percent < 20:
            category = "Высокий"
        else:
            category = "Очень высокий"

        return {
            "risk_percent_10yr": round(risk_percent, 1),
            "category": category,
            "recommendation": self._cv_risk_recommendation(category),
        }

    def _cv_risk_recommendation(self, category: str) -> str:
        recs = {
            "Низкий": "Модификация образа жизни. Повторная оценка через 5 лет.",
            "Умеренный": "Модификация образа жизни. Рассмотреть медикаментозную терапию при наличии дополнительных факторов риска.",
            "Высокий": "Модификация образа жизни + медикаментозная терапия (статины, антигипертензивные). Контроль через 3-6 месяцев.",
            "Очень высокий": "Агрессивная медикаментозная терапия. Целевой ЛПНП < 1.4 ммоль/л. Контроль через 1-3 месяца.",
        }
        return recs.get(category, "")

    def calculate_gfr(self, creatinine: float, age: int, gender: str) -> dict:
        """Calculate eGFR using CKD-EPI formula (simplified)."""
        # Simplified CKD-EPI
        if gender == "female":
            if creatinine <= 62:
                gfr = 144 * (creatinine / 62) ** (-0.329) * 0.993 ** age
            else:
                gfr = 144 * (creatinine / 62) ** (-1.209) * 0.993 ** age
        else:
            if creatinine <= 80:
                gfr = 141 * (creatinine / 80) ** (-0.411) * 0.993 ** age
            else:
                gfr = 141 * (creatinine / 80) ** (-1.209) * 0.993 ** age

        gfr = round(gfr, 1)

        # CKD staging
        if gfr >= 90:
            stage = "G1 (нормальная или высокая)"
        elif gfr >= 60:
            stage = "G2 (незначительно снижена)"
        elif gfr >= 45:
            stage = "G3a (умеренно снижена)"
        elif gfr >= 30:
            stage = "G3b (существенно снижена)"
        elif gfr >= 15:
            stage = "G4 (резко снижена)"
        else:
            stage = "G5 (терминальная почечная недостаточность)"

        return {
            "egfr": gfr,
            "unit": "мл/мин/1.73м²",
            "ckd_stage": stage,
            "needs_dialysis_referral": gfr < 15,
        }

    def generate_consultation(self, patient_summary: str, complaint: str) -> str:
        """Generate a consultation template."""
        return f"""
═══════════════════════════════════════════
  КОНСУЛЬТАЦИЯ: {self.spec.name_ru}
  AI-клиника «Айболит»
  Дата: {date.today().isoformat()}
═══════════════════════════════════════════

{patient_summary}

ЖАЛОБЫ: {complaint}

РЕКОМЕНДУЕМЫЕ ОБСЛЕДОВАНИЯ:
[На основании жалоб и анамнеза AI-доктор предложит необходимые исследования]

ПРЕДВАРИТЕЛЬНОЕ ЗАКЛЮЧЕНИЕ:
[Будет сформировано после анализа данных]

ПЛАН ЛЕЧЕНИЯ:
[Будет составлен с учётом доказательной медицины]

═══════════════════════════════════════════
⚕ Данная консультация сгенерирована AI-системой
  и не заменяет очную консультацию врача.
═══════════════════════════════════════════
"""
