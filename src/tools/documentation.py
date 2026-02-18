"""Medical documentation generation tools."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any


def generate_medical_record(
    patient_name: str,
    patient_age: int,
    gender: str,
    complaints: str,
    anamnesis: str,
    examination: str,
    diagnoses: list[dict],
    plan: str,
    doctor_specialty: str = "Терапевт",
    vitals: dict | None = None,
    lab_results: list[dict] | None = None,
) -> str:
    """Generate a structured medical record (история болезни)."""
    now = datetime.now()
    record = []

    record.append("=" * 60)
    record.append("МЕДИЦИНСКАЯ КАРТА ПАЦИЕНТА")
    record.append("=" * 60)
    record.append(f"Дата: {now.strftime('%d.%m.%Y %H:%M')}")
    record.append(f"Специалист: AI-{doctor_specialty}")
    record.append("")
    record.append(f"Пациент: {patient_name}")
    record.append(f"Возраст: {patient_age} лет")
    record.append(f"Пол: {'Мужской' if gender == 'male' else 'Женский'}")
    record.append("")

    if vitals:
        record.append("─── ВИТАЛЬНЫЕ ПОКАЗАТЕЛИ ───")
        if vitals.get("systolic_bp"):
            record.append(f"АД: {vitals['systolic_bp']}/{vitals.get('diastolic_bp', '?')} мм рт.ст.")
        if vitals.get("heart_rate"):
            record.append(f"ЧСС: {vitals['heart_rate']} уд/мин")
        if vitals.get("temperature"):
            record.append(f"Температура: {vitals['temperature']}°C")
        if vitals.get("spo2"):
            record.append(f"SpO2: {vitals['spo2']}%")
        if vitals.get("respiratory_rate"):
            record.append(f"ЧД: {vitals['respiratory_rate']}/мин")
        record.append("")

    record.append("─── ЖАЛОБЫ ───")
    record.append(complaints)
    record.append("")

    record.append("─── АНАМНЕЗ ЗАБОЛЕВАНИЯ ───")
    record.append(anamnesis)
    record.append("")

    record.append("─── ОБЪЕКТИВНЫЙ ОСМОТР ───")
    record.append(examination)
    record.append("")

    if lab_results:
        record.append("─── РЕЗУЛЬТАТЫ ОБСЛЕДОВАНИЙ ───")
        for lr in lab_results:
            status = ""
            if lr.get("is_abnormal"):
                status = " ⚠️"
            record.append(f"  {lr['test_name']}: {lr['value']} {lr.get('unit', '')}{status}")
        record.append("")

    record.append("─── ДИАГНОЗ ───")
    for i, d in enumerate(diagnoses, 1):
        main = " (основной)" if i == 1 else ""
        record.append(f"  {i}. {d.get('name', '')} [{d.get('icd10_code', '')}]{main}")
        if d.get("confidence"):
            record.append(f"     Уверенность AI: {d['confidence']*100:.0f}%")
    record.append("")

    record.append("─── ПЛАН ОБСЛЕДОВАНИЯ И ЛЕЧЕНИЯ ───")
    record.append(plan)
    record.append("")

    record.append("─" * 60)
    record.append("⚠️ Данный документ сгенерирован AI-системой Aibolit")
    record.append("и требует верификации лечащим врачом.")
    record.append(f"Система: Aibolit AI Medical Clinic v1.0")
    record.append(f"Дата генерации: {now.isoformat()}")

    return "\n".join(record)


def generate_referral(
    patient_name: str,
    patient_age: int,
    from_specialty: str,
    to_specialty: str,
    reason: str,
    current_diagnoses: list[str],
    relevant_results: str = "",
    urgency: str = "routine",
) -> str:
    """Generate a referral to another specialist."""
    now = datetime.now()
    urgency_text = {
        "routine": "Плановая",
        "urgent": "Срочная",
        "emergency": "Экстренная",
    }.get(urgency, "Плановая")

    referral = []
    referral.append("=" * 50)
    referral.append(f"НАПРАВЛЕНИЕ К СПЕЦИАЛИСТУ")
    referral.append(f"Срочность: {urgency_text}")
    referral.append("=" * 50)
    referral.append(f"Дата: {now.strftime('%d.%m.%Y')}")
    referral.append(f"От: AI-{from_specialty}")
    referral.append(f"Кому: {to_specialty}")
    referral.append("")
    referral.append(f"Пациент: {patient_name}, {patient_age} лет")
    referral.append("")
    referral.append("Диагноз:")
    for d in current_diagnoses:
        referral.append(f"  • {d}")
    referral.append("")
    referral.append("Причина направления:")
    referral.append(reason)
    if relevant_results:
        referral.append("")
        referral.append("Результаты обследований:")
        referral.append(relevant_results)
    referral.append("")
    referral.append("─" * 50)
    referral.append("AI-система Aibolit | Требует верификации врачом")

    return "\n".join(referral)


def generate_prescription(
    patient_name: str,
    medications: list[dict],
    diagnoses: list[str],
    doctor_specialty: str = "Терапевт",
    notes: str = "",
) -> str:
    """Generate a prescription document."""
    now = datetime.now()
    rx = []
    rx.append("=" * 50)
    rx.append("ЛИСТ НАЗНАЧЕНИЙ")
    rx.append("=" * 50)
    rx.append(f"Дата: {now.strftime('%d.%m.%Y')}")
    rx.append(f"Пациент: {patient_name}")
    rx.append(f"Специалист: AI-{doctor_specialty}")
    rx.append("")
    rx.append("Диагноз:")
    for d in diagnoses:
        rx.append(f"  • {d}")
    rx.append("")
    rx.append("─── НАЗНАЧЕНИЯ ───")
    for i, med in enumerate(medications, 1):
        rx.append(f"\n{i}. {med['name']}")
        rx.append(f"   Дозировка: {med.get('dosage', 'см. инструкцию')}")
        rx.append(f"   Режим: {med.get('frequency', '')}")
        rx.append(f"   Путь введения: {med.get('route', 'внутрь')}")
        if med.get("duration"):
            rx.append(f"   Длительность: {med['duration']}")
        if med.get("notes"):
            rx.append(f"   Примечание: {med['notes']}")
    if notes:
        rx.append(f"\nДополнительные указания: {notes}")
    rx.append("")
    rx.append("─" * 50)
    rx.append("⚠️ AI-назначение требует утверждения лечащим врачом")
    rx.append("Aibolit AI Medical Clinic v1.0")
    return "\n".join(rx)


def generate_discharge_summary(
    patient_name: str,
    patient_age: int,
    gender: str,
    admission_date: str,
    discharge_date: str,
    admission_diagnosis: str,
    final_diagnosis: str,
    treatment_summary: str,
    discharge_condition: str,
    discharge_medications: list[dict],
    follow_up: str,
    recommendations: list[str],
) -> str:
    """Generate a discharge summary."""
    doc = []
    doc.append("=" * 60)
    doc.append("ВЫПИСНОЙ ЭПИКРИЗ")
    doc.append("=" * 60)
    doc.append(f"Пациент: {patient_name}, {patient_age} лет, {'муж' if gender == 'male' else 'жен'}.")
    doc.append(f"Дата госпитализации: {admission_date}")
    doc.append(f"Дата выписки: {discharge_date}")
    doc.append("")
    doc.append(f"Диагноз при поступлении: {admission_diagnosis}")
    doc.append(f"Заключительный диагноз: {final_diagnosis}")
    doc.append("")
    doc.append("─── ПРОВЕДЁННОЕ ЛЕЧЕНИЕ ───")
    doc.append(treatment_summary)
    doc.append("")
    doc.append(f"Состояние при выписке: {discharge_condition}")
    doc.append("")
    if discharge_medications:
        doc.append("─── НАЗНАЧЕНИЯ ПРИ ВЫПИСКЕ ───")
        for i, med in enumerate(discharge_medications, 1):
            doc.append(f"  {i}. {med['name']} {med.get('dosage', '')} — {med.get('frequency', '')}")
    doc.append("")
    doc.append("─── РЕКОМЕНДАЦИИ ───")
    for r in recommendations:
        doc.append(f"  • {r}")
    doc.append("")
    doc.append(f"Контрольный визит: {follow_up}")
    doc.append("")
    doc.append("─" * 60)
    doc.append("AI-система Aibolit | Требует подписи лечащего врача")
    return "\n".join(doc)
