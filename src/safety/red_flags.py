"""Red-flag detection from patient complaints and vital signs.

Based on rules/05-medical-safety.md — immediate and high-priority triggers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum


class Urgency(IntEnum):
    """Urgency levels for escalation (1=lowest, 5=highest)."""
    LOW = 1
    MODERATE = 2
    HIGH = 3
    VERY_HIGH = 4
    IMMEDIATE = 5


@dataclass(frozen=True)
class RedFlag:
    """A detected red-flag condition."""
    category: str          # e.g. "cardiac", "neurological", "psychiatric"
    description: str       # Human-readable description
    urgency: Urgency       # Urgency level
    action: str            # Recommended action


# ---------- keyword patterns mapped to (category, description, urgency) ----------

_IMMEDIATE_PATTERNS: list[tuple[str, str, str]] = [
    # Cardiac
    (r"(?:боль|давл\w*|жжение|тяжесть)\s.*(?:груд|сердц|за\s?грудин)",
     "cardiac", "Боль / давление в груди — возможный острый коронарный синдром"),
    (r"(?:отда[её]т|иррадиир)\s.*(?:лев\w*\s+рук|челюсть|лопатк)",
     "cardiac", "Иррадиация боли в левую руку / челюсть"),
    (r"(?:потер|терял|теряю)\s.*сознани",
     "cardiac", "Потеря сознания — обморок / синкопе"),
    (r"(?:внезапн|остр)\w*\s+одышк",
     "cardiac", "Внезапная одышка в покое"),

    # Neurological
    (r"(?:слабость|онемени\w*|парез)\s.*(?:одн\w+\s+сторон|половин|лев\w+|прав\w+)",
     "neurological", "Односторонняя слабость / онемение — возможный инсульт"),
    (r"(?:внезапн|остр)\w*\s.*(?:потер|наруш)\w*\s+зрени",
     "neurological", "Внезапная потеря / нарушение зрения"),
    (r"(?:громоподобн|внезапн|сильнейш)\w*\s+головн\w*\s+бол",
     "neurological", "Внезапная сильнейшая головная боль"),
    (r"судорог\w*\s+впервые",
     "neurological", "Впервые возникшие судороги"),
    (r"(?:спутанн|нарушен)\w*\s+сознани",
     "neurological", "Нарушение / спутанность сознания"),

    # Allergic
    (r"(?:анафилакс|анафилакт)",
     "allergic", "Признаки анафилаксии"),
    (r"от[её]к\s*квинке",
     "allergic", "Отёк Квинке"),
    (r"(?:от[её]к\s+горл|затруднён\w*\s+дыхан)\w*.*(?:сыпь|крапивниц)",
     "allergic", "Отёк горла + сыпь — возможная анафилаксия"),

    # Psychiatric
    (r"(?:суицид|покончить\s+с\s+собой|убить\s+себя|не\s+хочу\s+жить)",
     "psychiatric", "Суицидальные мысли / намерения"),

    # Abdominal
    (r"рвот\w*\s+.*кров",
     "abdominal", "Рвота кровью — возможное ЖКТ-кровотечение"),
    (r"(?:чёрн|дёгте)\w*\s+(?:стул|кал)",
     "abdominal", "Чёрный дёгтеобразный стул (мелена)"),
    (r"(?:доскообразн\w*\s+живот|живот\s+доскообразн\w*)",
     "abdominal", "Доскообразный живот — возможный перитонит"),

    # Obstetric
    (r"кровотечени\w*\s.*беременн",
     "obstetric", "Кровотечение при беременности"),

    # Infectious
    (r"ригидност\w*\s+затылочн",
     "infectious", "Ригидность затылочных мышц — возможный менингит"),
]

_HIGH_PATTERNS: list[tuple[str, str, str]] = [
    (r"(?:давлени\w*|ад)\s.*(?:18[0-9]|19[0-9]|2[0-9]{2})\s*/",
     "cardiac", "Неконтролируемая гипертензия (>180 мм рт.ст.)"),
    (r"(?:сахар|глюкоз)\w*\s.*(?:2[0-9]|3[0-9])\s*(?:ммоль)?",
     "endocrine", "Гипергликемия >20 ммоль/л — возможный дебют/декомпенсация СД"),
    (r"(?:тромбоз|тромб)\s.*(?:глубок|вен)",
     "vascular", "Подозрение на тромбоз глубоких вен"),
    (r"(?:задержк\w*|не\s+мог\w+)\s+(?:мочеиспускан|мочи)",
     "urological", "Острая задержка мочи"),
    (r"(?:опухол|образовани|узел)\w*.*(?:впервые|обнаруж|выявлен|нашли)",
     "oncological", "Впервые выявленное новообразование"),
    (r"аппендицит",
     "surgical", "Подозрение на аппендицит"),
]


class RedFlagDetector:
    """Detect red-flag conditions from free-text complaints."""

    def __init__(self) -> None:
        self._immediate = [
            (re.compile(pat, re.IGNORECASE), cat, desc)
            for pat, cat, desc in _IMMEDIATE_PATTERNS
        ]
        self._high = [
            (re.compile(pat, re.IGNORECASE), cat, desc)
            for pat, cat, desc in _HIGH_PATTERNS
        ]

    def detect(self, text: str) -> list[RedFlag]:
        """Scan text and return all detected red flags, highest urgency first."""
        flags: list[RedFlag] = []
        seen_descs: set[str] = set()

        for pattern, category, description in self._immediate:
            if pattern.search(text) and description not in seen_descs:
                seen_descs.add(description)
                flags.append(RedFlag(
                    category=category,
                    description=description,
                    urgency=Urgency.IMMEDIATE,
                    action="Немедленно вызовите скорую помощь: 103 (или 112)",
                ))

        for pattern, category, description in self._high:
            if pattern.search(text) and description not in seen_descs:
                seen_descs.add(description)
                flags.append(RedFlag(
                    category=category,
                    description=description,
                    urgency=Urgency.VERY_HIGH,
                    action="Срочно обратитесь к врачу",
                ))

        flags.sort(key=lambda f: f.urgency, reverse=True)
        return flags

    def has_immediate_flags(self, text: str) -> bool:
        """Quick check: are there any urgency-5 flags?"""
        for pattern, _, _ in self._immediate:
            if pattern.search(text):
                return True
        return False


# Module-level singleton for convenience
detector = RedFlagDetector()
