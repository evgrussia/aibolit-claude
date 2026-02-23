"""Consultation builder — structures doctor info, ICD codes, and recommended tests.

Extracted from the former MCP server. Does NOT save to database —
the caller (router) saves after AI enrichment.
"""
from __future__ import annotations

from src.agents.specializations import SPECIALIZATIONS, get_specialization
from src.models.medical_refs import LAB_REFERENCE_RANGES, ICD10_COMMON
from src.safety.disclaimers import DisclaimerType, get_disclaimer
from src.utils.database import load_patient


def build_consultation(specialty: str, complaints: str, patient_id: str | None = None) -> dict:
    """Build a structured AI doctor consultation (template, no LLM call)."""
    spec = get_specialization(specialty)
    if not spec:
        available = [s.id for s in SPECIALIZATIONS.values()]
        return {"error": f"Специализация '{specialty}' не найдена. Доступные: {', '.join(available)}"}

    patient_summary = ""
    if patient_id:
        patient = load_patient(patient_id)
        if patient:
            patient_summary = patient.summary()

    summary = build_consultation_summary(spec, complaints, patient_summary)

    return {
        "doctor": {
            "specialty_id": spec.id,
            "name": f"AI-{spec.name_ru}",
            "qualification": spec.description,
        },
        "consultation": {
            "complaints": complaints,
            "patient_context": patient_summary or "Карта пациента не загружена",
            "summary": summary,
            "available_skills": [
                {"name": s.name, "description": s.description, "tool": s.tool_name}
                for s in spec.skills
            ],
            "relevant_icd_prefixes": spec.related_icd_prefixes[:10],
            "recommended_tests": spec.required_lab_tests,
        },
        "instructions": (
            f"Вы — AI-{spec.name_ru}. Проведите консультацию по жалобам пациента.\n"
            f"1. Соберите детальный анамнез (уточняющие вопросы)\n"
            f"2. Используйте доступные навыки для диагностики\n"
            f"3. Сформулируйте предварительный диагноз с кодом МКБ-10\n"
            f"4. Назначьте обследования и лечение\n"
            f"5. При необходимости направьте к другому специалисту\n\n"
            f"⚠️ Все рекомендации носят информационный характер."
        ),
        "disclaimer": get_disclaimer(DisclaimerType.GENERAL),
    }


def build_consultation_summary(spec, complaints: str, patient_summary: str) -> str:
    """Build a human-readable doctor consultation summary."""
    lines: list[str] = []

    lines.append(f"Здравствуйте! Я AI-{spec.name_ru}.")
    lines.append(f"Вы обратились с жалобами: {complaints}")
    lines.append("")

    if patient_summary and patient_summary != "Карта пациента не загружена":
        lines.append("Данные из вашей медицинской карты учтены при оценке.")
        lines.append("")

    matched_conditions = []
    for prefix in spec.related_icd_prefixes[:10]:
        for code, name in ICD10_COMMON.items():
            if code.startswith(prefix):
                matched_conditions.append(f"{code} — {name}")
                break
    if matched_conditions:
        lines.append("На основании жалоб и специализации, возможные состояния:")
        for cond in matched_conditions[:5]:
            lines.append(f"  • {cond}")
        lines.append("")

    if spec.required_lab_tests:
        test_names = []
        for key in spec.required_lab_tests[:8]:
            ref = LAB_REFERENCE_RANGES.get(key)
            test_names.append(ref["name"] if ref else key)
        lines.append("Рекомендуемые обследования:")
        for name in test_names:
            lines.append(f"  • {name}")
        lines.append("")

    lines.append("Рекомендации:")
    lines.append("  • Обратитесь к врачу очно для подтверждения диагноза")
    lines.append("  • Пройдите рекомендованные обследования")
    lines.append("  • При ухудшении состояния вызовите скорую помощь")

    return "\n".join(lines)
