"""Medical disclaimer templates per rules/05-medical-safety.md."""
from __future__ import annotations

from enum import Enum


class DisclaimerType(str, Enum):
    GENERAL = "general"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MEDICATION = "medication"
    LAB_ANALYSIS = "lab_analysis"
    IMAGING = "imaging"
    EMERGENCY = "emergency"
    CHILDREN = "children"


DISCLAIMERS: dict[str, str] = {
    DisclaimerType.GENERAL: (
        "Информация предоставлена AI-ассистентом и носит исключительно "
        "информационный характер. Не является медицинской консультацией, "
        "диагнозом или назначением лечения. Обратитесь к врачу для получения "
        "квалифицированной медицинской помощи."
    ),
    DisclaimerType.DIAGNOSIS: (
        "Предположительный анализ симптомов выполнен AI-системой. Это НЕ диагноз. "
        "Только врач может поставить диагноз на основе полного обследования. "
        "Обратитесь к специалисту."
    ),
    DisclaimerType.TREATMENT: (
        "Информация о лечении предоставлена в образовательных целях. "
        "НЕ начинайте, не изменяйте и не прекращайте лечение без консультации "
        "с врачом. Самолечение может быть опасным."
    ),
    DisclaimerType.MEDICATION: (
        "Информация о лекарственных препаратах носит справочный характер. "
        "AI НЕ назначает лекарства. Перед приёмом любых препаратов "
        "проконсультируйтесь с врачом. Учитывайте противопоказания "
        "и индивидуальную непереносимость."
    ),
    DisclaimerType.LAB_ANALYSIS: (
        "Расшифровка анализов выполнена AI-системой и требует подтверждения "
        "врачом. Отклонения от нормы не обязательно означают заболевание. "
        "Врач интерпретирует результаты в контексте вашего состояния."
    ),
    DisclaimerType.IMAGING: (
        "Анализ изображения выполнен AI-моделью и является предварительным "
        "скринингом. Это НЕ радиологическое заключение. Окончательную "
        "интерпретацию должен выполнить врач-рентгенолог."
    ),
    DisclaimerType.EMERGENCY: (
        "ВНИМАНИЕ! При угрозе жизни немедленно вызовите скорую помощь: "
        "103 (или 112). AI-система НЕ предназначена для экстренных ситуаций."
    ),
    DisclaimerType.CHILDREN: (
        "Информация о здоровье детей требует особой осторожности. Всегда "
        "консультируйтесь с педиатром. Дозировки и рекомендации для взрослых "
        "НЕ применимы к детям."
    ),
}


def get_disclaimer(dtype: str | DisclaimerType) -> str:
    """Return the disclaimer string for the given type, with warning icon."""
    text = DISCLAIMERS.get(dtype, DISCLAIMERS[DisclaimerType.GENERAL])
    return text


def get_disclaimer_text(dtype: str | DisclaimerType) -> str:
    """Alias kept for backward compatibility."""
    return get_disclaimer(dtype)
