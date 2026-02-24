"""AI output safety guard — validates AI responses for prohibited medical content.

Checks for:
- Definitive diagnoses ("У вас [диагноз]")
- Direct prescriptions ("Вам нужно принимать [лекарство]")
- Dismissal of symptoms ("Это не опасно")
- Specific dosage recommendations as prescriptions

Returns a list of safety violations found. If violations are detected,
the AI response should be post-processed to add extra warnings.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger("aibolit.output_guard")


@dataclass
class SafetyViolation:
    """A detected safety violation in AI output."""
    category: str       # "diagnosis", "prescription", "dismissal", "dosage"
    pattern: str        # The regex pattern that matched
    matched_text: str   # The actual text that matched
    severity: str       # "high", "medium"


# ── Prohibited patterns ─────────────────────────────────────

_DEFINITIVE_DIAGNOSIS = [
    # "У вас [диагноз]" — with optional definitive qualifier (есть/обнаружен/выявлен/диагностирован)
    # Negative lookahead excludes hedged forms: "может", "возможно", "вероятно", "скорее"
    r'[Уу]\s+вас\s+(?!(?:может|возможно|вероятно|скорее|предположительно|ВОЗМОЖНО)\b)(?:есть\s+|обнаружен[аоы]?\s+|выявлен[аоы]?\s+|диагностирован[аоы]?\s+)?[А-ЯЁа-яё]{3,}',
    # "Это точно ..."
    r'[Ээ]то\s+(?:точно|однозначно|определённо|несомненно|безусловно)\s+',
    # "Ваш диагноз — ..."
    r'[Вв]аш\s+диагноз\s*[—:–-]\s*',
    # "Я ставлю диагноз"
    r'[Яя]\s+(?:ставлю|устанавливаю)\s+диагноз',
]

_DIRECT_PRESCRIPTION = [
    # "Вам нужно принимать ..."
    r'[Вв]ам\s+(?:нужно|необходимо|следует|надо)\s+(?:принимать|пить|начать\s+приём)',
    # "Принимайте [лекарство]"
    r'[Пп]ринимайте\s+[А-ЯЁа-яё]{3,}',
    # "Назначаю [лекарство]"
    r'[Нн]азначаю\s+(?:вам\s+)?[А-ЯЁа-яё]{3,}',
    # "Я выписываю / прописываю"
    r'[Яя]\s+(?:выписываю|прописываю)\s+',
    # "Рецепт: ..."
    r'[Рр]ецепт\s*[:—–-]',
]

_DISMISSAL = [
    # "Это не опасно" / "Ничего страшного"
    r'[Ээ]то\s+(?:не\s+опасно|совершенно\s+безопасно|абсолютно\s+безвредно)',
    r'[Нн]ичего\s+(?:страшного|серь[её]зного|опасного)',
    # "Не волнуйтесь, это пройдёт"
    r'[Нн]е\s+(?:волнуйтесь|беспокойтесь|переживайте),?\s+это\s+прой[дт]',
    # "Можете не обращаться к врачу"
    r'[Мм]ожете\s+не\s+(?:обращаться|ходить|идти)\s+к\s+врач',
]

_DOSAGE_AS_PRESCRIPTION = [
    # "по X мг N раз в день" with preceding imperative
    r'(?:[Пп]ринимайте|[Пп]ейте|[Вв]ыпейте)\s+(?:по\s+)?\d+\s*(?:мг|мл|г|таблет)',
    # "дозировка: X мг" in prescriptive context
    r'[Дд]озировка\s*[:—–-]\s*\d+\s*(?:мг|мл|г)',
]


def _compile_patterns(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


_COMPILED: dict[str, list[re.Pattern]] = {
    "diagnosis": _compile_patterns(_DEFINITIVE_DIAGNOSIS),
    "prescription": _compile_patterns(_DIRECT_PRESCRIPTION),
    "dismissal": _compile_patterns(_DISMISSAL),
    "dosage": _compile_patterns(_DOSAGE_AS_PRESCRIPTION),
}

_SEVERITY: dict[str, str] = {
    "diagnosis": "high",
    "prescription": "high",
    "dismissal": "medium",
    "dosage": "high",
}


def check_ai_output(text: str) -> list[SafetyViolation]:
    """Check AI-generated text for prohibited medical content.

    Returns a list of SafetyViolation objects. Empty list means the text passes.
    """
    violations: list[SafetyViolation] = []

    for category, patterns in _COMPILED.items():
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                violations.append(SafetyViolation(
                    category=category,
                    pattern=pattern.pattern,
                    matched_text=match.group()[:100],
                    severity=_SEVERITY[category],
                ))
                break  # one violation per category is enough

    if violations:
        logger.warning(
            "[OUTPUT_GUARD] %d violations detected: %s",
            len(violations),
            [(v.category, v.matched_text[:50]) for v in violations],
        )

    return violations


# Extra disclaimer to append when violations are found
SAFETY_ADDENDUM = (
    "\n\n---\n"
    "**ВАЖНО:** Данный ответ может содержать формулировки, которые следует "
    "интерпретировать исключительно как информационные. AI-система НЕ ставит "
    "диагнозы и НЕ назначает лечение. Все решения о диагностике и лечении "
    "принимаются ТОЛЬКО квалифицированным врачом."
)
