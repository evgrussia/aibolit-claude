"""Triage service — matches patient complaints to the best medical specialty.

Uses keyword-based matching with weighted scoring. Each specialization has
associated symptom keywords. The service scores all 35 specializations and
returns top matches ranked by relevance.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from src.agents.specializations import SPECIALIZATIONS, Specialization


@dataclass(frozen=True)
class TriageMatch:
    """A matched specialization with relevance score."""
    specialty_id: str
    name_ru: str
    description: str
    score: float       # 0.0–1.0 relevance
    reason: str        # why this specialist was matched


# Symptom keywords mapped to specialty IDs with weights.
# Higher weight = stronger association.
_SYMPTOM_MAP: list[tuple[str, str, float, str]] = [
    # (regex_pattern, specialty_id, weight, reason)

    # Cardiology
    (r"(?:боль|давлен|тяжест|жжен)\w*\s.*(?:груд|сердц|за\s*грудин)", "cardiologist", 0.9,
     "Боль/дискомфорт в области сердца"),
    (r"(?:аритми|перебо\w*\s+серд|экстрасистол)", "cardiologist", 0.85, "Нарушения ритма сердца"),
    (r"(?:повышен|высок)\w*\s*(?:давлен|ад|артериальн)", "cardiologist", 0.8, "Артериальная гипертензия"),
    (r"одышк\w*", "cardiologist", 0.5, "Одышка (может быть кардиологической причины)"),
    (r"(?:от[её]к\w*\s+ног|отёчност)", "cardiologist", 0.6, "Отёки нижних конечностей"),

    # Neurology
    (r"(?:головн\w*\s+бол|мигрен|цефалги)", "neurologist", 0.85, "Головная боль"),
    (r"(?:головокруж|вертиго)", "neurologist", 0.8, "Головокружение"),
    (r"(?:онемен|парестез|покалыван)\w*", "neurologist", 0.75, "Онемение/покалывание"),
    (r"(?:судорог|эпилепс|припадок)", "neurologist", 0.9, "Судороги/эпилепсия"),
    (r"(?:тремор|дрожан)", "neurologist", 0.8, "Тремор"),
    (r"(?:нарушен\w*\s+сна|бессонниц|инсомни)", "neurologist", 0.6, "Нарушения сна"),
    (r"(?:потер\w*\s+сознан|обморок|синкоп)", "neurologist", 0.85, "Потеря сознания"),

    # Pulmonology
    (r"(?:кашел|мокрот)", "pulmonologist", 0.8, "Кашель/мокрота"),
    (r"(?:хрип|свист\w*\s+дыхан)", "pulmonologist", 0.85, "Хрипы при дыхании"),
    (r"(?:астм|бронхоспазм)", "pulmonologist", 0.9, "Бронхиальная астма"),
    (r"одышк\w*", "pulmonologist", 0.5, "Одышка"),

    # Gastroenterology
    (r"(?:бол\w*\s+(?:в\s+)?живот|абдоминальн)", "gastroenterologist", 0.8, "Боль в животе"),
    (r"(?:изжог|рефлюкс|отрыжк)", "gastroenterologist", 0.85, "Изжога/рефлюкс"),
    (r"(?:тошнот|рвот)", "gastroenterologist", 0.7, "Тошнота/рвота"),
    (r"(?:диаре|понос|запор|констипаци)", "gastroenterologist", 0.8, "Нарушения стула"),
    (r"(?:вздути|метеоризм|газообразован)", "gastroenterologist", 0.7, "Вздутие живота"),
    (r"(?:гастрит|язв\w*\s+желудк)", "gastroenterologist", 0.9, "Гастрит/язва"),

    # Endocrinology
    (r"(?:сахар\w*\s+диабет|диабет|гипергликем|гипогликем)", "endocrinologist", 0.9, "Сахарный диабет"),
    (r"(?:щитовидн|тиреоид|гипотирео|гипертирео)", "endocrinologist", 0.9, "Заболевания щитовидной железы"),
    (r"(?:набор|потер|колебани)\w*\s+вес", "endocrinologist", 0.6, "Изменение массы тела"),
    (r"(?:гормон\w*\s+нарушен|гормональн)", "endocrinologist", 0.8, "Гормональные нарушения"),

    # Nephrology
    (r"(?:почк|почечн|нефр)", "nephrologist", 0.85, "Заболевания почек"),
    (r"(?:отёк\w*\s+лиц|отёк\w*\s+утр)", "nephrologist", 0.7, "Отёки лица/утром"),
    (r"(?:бол\w*\s+пояснице\s*$|бол\w*\s+поясниц)", "nephrologist", 0.5, "Боль в пояснице"),

    # Dermatology
    (r"(?:сыпь|высыпан|покраснен\w*\s+кож)", "dermatologist", 0.9, "Кожные высыпания"),
    (r"(?:зуд|чешет)", "dermatologist", 0.8, "Кожный зуд"),
    (r"(?:угр|акне|прыщ)", "dermatologist", 0.85, "Акне"),
    (r"(?:родинк|невус|пигментац)", "dermatologist", 0.8, "Образования на коже"),
    (r"(?:экзем|дерматит|псориаз)", "dermatologist", 0.9, "Дерматит/экзема/псориаз"),

    # Ophthalmology
    (r"(?:зрен|глаз\w*\s+бол|глаз\w*\s+красн|конъюнктивит)", "ophthalmologist", 0.9, "Проблемы с глазами"),
    (r"(?:слезотечен|сухост\w*\s+глаз)", "ophthalmologist", 0.8, "Слезотечение/сухость глаз"),

    # ENT
    (r"(?:горл|ангин|тонзиллит|фаринги)", "ent", 0.85, "Боль в горле"),
    (r"(?:нос\w*\s+заложен|насморк|ринит|синусит|гайморит)", "ent", 0.85, "Заложенность носа/насморк"),
    (r"(?:ух\w*\s+бол|отит|снижен\w*\s+слух|шум\w*\s+в\s+уш)", "ent", 0.85, "Проблемы с ушами"),

    # Urology
    (r"(?:моч\w*\s+бол|рез\w*\s+при\s+мочеиспускан|цистит)", "urologist", 0.85, "Боль при мочеиспускании"),
    (r"(?:простат|предстательн)", "urologist", 0.9, "Заболевания простаты"),
    (r"(?:учащ\w*\s+мочеиспускан|никтури|частое\s+мочеиспускан)", "urologist", 0.8, "Учащённое мочеиспускание"),

    # Gynecology
    (r"(?:менструац|месячн|нарушен\w*\s+цикл|аменоре)", "gynecologist", 0.9, "Нарушения менструального цикла"),
    (r"(?:беременн|задержк\w*\s+месячн)", "gynecologist", 0.9, "Вопросы беременности"),
    (r"(?:бол\w*\s+(?:вниз|в\s+низ)\w*\s+живот)", "gynecologist", 0.6, "Боль внизу живота (у женщин)"),

    # Orthopedics
    (r"(?:бол\w*\s+(?:в\s+)?(?:спин|колен|суставах|суставе|плече|тазобедр))", "orthopedist", 0.85, "Боль в суставах/спине"),
    (r"(?:перелом|травм|ушиб|вывих|растяжен)", "orthopedist", 0.9, "Травмы"),

    # Psychiatry
    (r"(?:депресс|тревог|тревожн|панич\w*\s+атак)", "psychiatrist", 0.9, "Тревога/депрессия"),
    (r"(?:бессонниц|нарушен\w*\s+сна)", "psychiatrist", 0.5, "Нарушения сна"),

    # Allergy
    (r"(?:аллерги|крапивниц|атопич)", "allergist", 0.9, "Аллергические реакции"),

    # Pediatrics
    (r"(?:ребён|ребенок|малыш|дет\w*\s+(?:бол|температ|кашел))", "pediatrician", 0.9, "Симптомы у ребёнка"),

    # Oncology
    (r"(?:опухол|образован\w*\s+(?:подозрительн|злокачествен)|онколог)", "oncologist", 0.8, "Подозрение на новообразование"),

    # Emergency
    (r"(?:скорая|неотложн|экстренн|острая|резк\w*\s+(?:бол|ухудшен))", "emergency", 0.7, "Экстренная ситуация"),

    # Therapist as fallback with moderate score
    (r"(?:ОРВИ|простуд|температур\w*\s+повышен|общ\w*\s+недомоган|слабость|утомля)", "therapist", 0.75,
     "Общие симптомы / ОРВИ"),

    # Dentist
    (r"(?:зуб|дёсн|десн|стоматит|кариес)", "dentist", 0.9, "Стоматологические проблемы"),

    # Rheumatology
    (r"(?:ревмат|артрит|системн\w*\s+(?:красн|волчанк))", "rheumatologist", 0.9, "Ревматологические заболевания"),
    (r"(?:утренн\w*\s+скованност|бол\w*\s+суставах\s+(?:по\s+утр|утром))", "rheumatologist", 0.8,
     "Утренняя скованность в суставах"),
]


class TriageEngine:
    """Symptom-based triage engine."""

    def __init__(self) -> None:
        self._patterns = [
            (re.compile(pat, re.IGNORECASE), spec_id, weight, reason)
            for pat, spec_id, weight, reason in _SYMPTOM_MAP
        ]

    def triage(self, complaints: str, top_n: int = 3) -> list[TriageMatch]:
        """Analyze complaints and return top-N matching specializations."""
        scores: dict[str, tuple[float, list[str]]] = {}

        for pattern, spec_id, weight, reason in self._patterns:
            if pattern.search(complaints):
                if spec_id not in scores:
                    scores[spec_id] = (0.0, [])
                current_score, reasons = scores[spec_id]
                # Diminishing returns for multiple matches in same specialty
                bonus = weight * (0.7 ** len(reasons))
                scores[spec_id] = (current_score + bonus, reasons + [reason])

        # Always include therapist as fallback if no matches
        if not scores:
            scores["therapist"] = (0.5, ["Терапевт — первичная диагностика при неспецифических жалобах"])

        # Normalize scores to 0-1 range
        max_score = max(s for s, _ in scores.values()) if scores else 1.0
        if max_score == 0:
            max_score = 1.0

        matches: list[TriageMatch] = []
        for spec_id, (raw_score, reasons) in scores.items():
            spec = SPECIALIZATIONS.get(spec_id)
            if not spec:
                continue
            matches.append(TriageMatch(
                specialty_id=spec_id,
                name_ru=spec.name_ru,
                description=spec.description,
                score=round(min(raw_score / max_score, 1.0), 2),
                reason="; ".join(reasons[:3]),
            ))

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:top_n]


# Module-level singleton
engine = TriageEngine()
