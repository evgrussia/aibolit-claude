"""Тесты детекции red flags в жалобах пациентов.

Покрывает:
- Детекцию по категориям (cardiac, neurological, allergic, и т.д.)
- Уровни срочности (Urgency.IMMEDIATE=5, Urgency.VERY_HIGH=4)
- Негативные кейсы (обычные жалобы НЕ должны срабатывать)
- Edge cases (пустой текст, длинный текст, латиница, множественные флаги)
- Метрику false negative rate < 5%
- Исправленные дефекты regex-паттернов (регрессионные тесты)

Основано на правилах: .claude/rules/05-medical-safety.md
"""
import pytest

from src.safety.red_flags import RedFlag, RedFlagDetector, Urgency, detector


# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------

@pytest.fixture
def det() -> RedFlagDetector:
    """Экземпляр детектора для каждого теста."""
    return RedFlagDetector()


# ===========================================================================
# 1. Детекция по категориям — Immediate (urgency 5)
# ===========================================================================

class TestCardiacRedFlags:
    """Кардиологические red flags (категория 'cardiac', urgency=5)."""

    @pytest.mark.parametrize("text", [
        "У меня острая боль в груди, не могу вздохнуть",
        "Сильное жжение в грудной клетке",
        "Тяжесть в груди, сердце колотится",
    ])
    def test_chest_pain_variants(self, det: RedFlagDetector, text: str):
        """Различные формулировки боли в груди детектируются."""
        flags = det.detect(text)
        assert len(flags) >= 1, f"Не обнаружен red flag для: {text}"
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac, f"Нет cardiac red flag для: {text}"
        assert cardiac[0].urgency == Urgency.IMMEDIATE

    def test_chest_pressure_behind_sternum(self, det: RedFlagDetector):
        """Давление за грудиной — регрессионный тест (BUG-001 исправлен)."""
        flags = det.detect("Чувствую давление за грудиной уже 20 минут")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac, "Не обнаружен cardiac red flag для: давление за грудиной"

    def test_radiation_to_left_arm(self, det: RedFlagDetector):
        """Боль, отдающая в левую руку / челюсть."""
        flags = det.detect("Боль в груди отдаёт в левую руку")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac
        assert cardiac[0].urgency == Urgency.IMMEDIATE

    def test_radiation_to_jaw(self, det: RedFlagDetector):
        """Боль, иррадиирующая в челюсть."""
        flags = det.detect("Боль в сердце отдаёт в челюсть")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac
        assert cardiac[0].urgency == Urgency.IMMEDIATE

    def test_sudden_dyspnea(self, det: RedFlagDetector):
        """Внезапная одышка в покое."""
        flags = det.detect("Внезапная одышка, не могу дышать")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac
        assert cardiac[0].urgency == Urgency.IMMEDIATE

    def test_syncope(self, det: RedFlagDetector):
        """Потеря сознания."""
        flags = det.detect("Я потерял сознание на несколько секунд")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac
        assert cardiac[0].urgency == Urgency.IMMEDIATE


class TestNeurologicalRedFlags:
    """Неврологические red flags (категория 'neurological', urgency=5)."""

    def test_weakness_in_right_arm(self, det: RedFlagDetector):
        """Слабость в правой руке — паттерн 'слабость' + 'прав\\w+'."""
        flags = det.detect("Слабость в правой руке, не могу поднять")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro, "Не обнаружен neuro red flag для: Слабость в правой руке"
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_paresis_one_side(self, det: RedFlagDetector):
        """Парез одной стороны лица."""
        flags = det.detect("Парез одной стороны лица")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro, "Не обнаружен neuro red flag для: Парез одной стороны"
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_numbness_left_side(self, det: RedFlagDetector):
        """Онемение левой стороны тела — регрессионный тест (BUG-002 исправлен)."""
        flags = det.detect("Онемение левой стороны тела")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro, "Не обнаружен neuro red flag для: Онемение левой стороны тела"

    def test_numbness_left_half(self, det: RedFlagDetector):
        """Онемение левой половины тела — регрессионный тест (BUG-002 исправлен)."""
        flags = det.detect("Онемение левой половины тела")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro, "Не обнаружен neuro red flag для: Онемение левой половины тела"

    def test_thunderclap_headache(self, det: RedFlagDetector):
        """Внезапная сильнейшая головная боль."""
        flags = det.detect("Внезапная сильнейшая головная боль, как удар")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_thunderclap_headache_alt(self, det: RedFlagDetector):
        """Громоподобная головная боль."""
        flags = det.detect("Громоподобная головная боль, как удар")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_first_seizure(self, det: RedFlagDetector):
        """Судороги впервые в жизни."""
        flags = det.detect("У меня были судороги впервые, я очень испугалась")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_confusion(self, det: RedFlagDetector):
        """Спутанность / нарушение сознания."""
        flags = det.detect("У мужа спутанное сознание, не узнаёт меня")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_consciousness_disorder(self, det: RedFlagDetector):
        """Нарушение сознания."""
        flags = det.detect("Нарушение сознания, речь спутана")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro
        assert neuro[0].urgency == Urgency.IMMEDIATE

    def test_sudden_vision_loss(self, det: RedFlagDetector):
        """Внезапная потеря зрения."""
        flags = det.detect("Внезапная потеря зрения на правый глаз")
        neuro = [f for f in flags if f.category == "neurological"]
        assert neuro
        assert neuro[0].urgency == Urgency.IMMEDIATE


class TestAllergicRedFlags:
    """Аллергические red flags (категория 'allergic', urgency=5)."""

    def test_anaphylaxis_keyword(self, det: RedFlagDetector):
        """Ключевое слово 'анафилаксия'."""
        flags = det.detect("Подозрение на анафилаксию после укуса пчелы")
        allergic = [f for f in flags if f.category == "allergic"]
        assert allergic
        assert allergic[0].urgency == Urgency.IMMEDIATE

    def test_anaphylactic_shock(self, det: RedFlagDetector):
        """Анафилактический шок."""
        flags = det.detect("Анафилактический шок")
        allergic = [f for f in flags if f.category == "allergic"]
        assert allergic
        assert allergic[0].urgency == Urgency.IMMEDIATE

    def test_quincke_edema(self, det: RedFlagDetector):
        """Отёк Квинке."""
        flags = det.detect("У ребёнка отёк Квинке, губы опухли")
        allergic = [f for f in flags if f.category == "allergic"]
        assert allergic
        assert allergic[0].urgency == Urgency.IMMEDIATE

    def test_throat_swelling_with_rash(self, det: RedFlagDetector):
        """Отёк горла с сыпью."""
        flags = det.detect("Отёк горла, затруднённое дыхание, по телу сыпь")
        allergic = [f for f in flags if f.category == "allergic"]
        assert allergic
        assert allergic[0].urgency == Urgency.IMMEDIATE


class TestPsychiatricRedFlags:
    """Психиатрические red flags (категория 'psychiatric', urgency=5)."""

    @pytest.mark.parametrize("text", [
        "Хочу покончить с собой",
        "Суицидальные мысли не отпускают",
        "Не хочу жить",
        "Думаю убить себя",
    ])
    def test_suicidal_ideation(self, det: RedFlagDetector, text: str):
        """Суицидальные мысли / намерения."""
        flags = det.detect(text)
        psych = [f for f in flags if f.category == "psychiatric"]
        assert psych, f"Не обнаружен psychiatric red flag для: {text}"
        assert psych[0].urgency == Urgency.IMMEDIATE


class TestAbdominalRedFlags:
    """Абдоминальные red flags (категория 'abdominal', urgency=5)."""

    def test_hematemesis(self, det: RedFlagDetector):
        """Рвота кровью."""
        flags = det.detect("У меня рвота кровью, алая кровь")
        abdom = [f for f in flags if f.category == "abdominal"]
        assert abdom
        assert abdom[0].urgency == Urgency.IMMEDIATE

    def test_hematemesis_with_preposition(self, det: RedFlagDetector):
        """Рвота с кровью (предлог между словами) — регрессионный тест (BUG-005 исправлен)."""
        flags = det.detect("Рвота с кровью после удара в живот")
        abdom = [f for f in flags if f.category == "abdominal"]
        assert abdom

    def test_melena(self, det: RedFlagDetector):
        """Чёрный дёгтеобразный стул (мелена)."""
        flags = det.detect("Чёрный дёгтеобразный стул последние два дня")
        abdom = [f for f in flags if f.category == "abdominal"]
        assert abdom
        assert abdom[0].urgency == Urgency.IMMEDIATE

    def test_melena_black_feces(self, det: RedFlagDetector):
        """Чёрный кал."""
        flags = det.detect("Чёрный кал, слабость")
        abdom = [f for f in flags if f.category == "abdominal"]
        assert abdom
        assert abdom[0].urgency == Urgency.IMMEDIATE

    def test_board_like_abdomen_correct_order(self, det: RedFlagDetector):
        """Доскообразный живот — порядок 'доскообразный живот'."""
        flags = det.detect("Доскообразный живот, нельзя прикоснуться")
        abdom = [f for f in flags if f.category == "abdominal"]
        assert abdom
        assert abdom[0].urgency == Urgency.IMMEDIATE

    def test_board_like_abdomen_reversed_order(self, det: RedFlagDetector):
        """Живот доскообразный (обратный порядок слов) — регрессионный тест (BUG-003 исправлен)."""
        flags = det.detect("Живот доскообразный, невозможно дотронуться")
        abdom = [f for f in flags if f.category == "abdominal"]
        assert abdom


class TestObstetricRedFlags:
    """Акушерские red flags (категория 'obstetric', urgency=5)."""

    def test_bleeding_in_pregnancy(self, det: RedFlagDetector):
        """Кровотечение при беременности."""
        flags = det.detect("Кровотечение при беременности, 28 недель")
        obstetric = [f for f in flags if f.category == "obstetric"]
        assert obstetric
        assert obstetric[0].urgency == Urgency.IMMEDIATE

    def test_bleeding_on_pregnancy_background(self, det: RedFlagDetector):
        """Кровотечение на фоне беременности."""
        flags = det.detect("Кровотечение на фоне беременности")
        obstetric = [f for f in flags if f.category == "obstetric"]
        assert obstetric
        assert obstetric[0].urgency == Urgency.IMMEDIATE


class TestInfectiousRedFlags:
    """Инфекционные red flags (категория 'infectious', urgency=5)."""

    def test_meningeal_signs(self, det: RedFlagDetector):
        """Ригидность затылочных мышц — менингит."""
        flags = det.detect("Ригидность затылочных мышц, высокая температура, сильная головная боль")
        infectious = [f for f in flags if f.category == "infectious"]
        assert infectious
        assert infectious[0].urgency == Urgency.IMMEDIATE


# ===========================================================================
# 2. Уровни срочности — High Priority (urgency 4)
# ===========================================================================

class TestRedFlagUrgencyLevels:
    """Тесты уровней срочности: immediate (5) vs high priority (4)."""

    def test_immediate_flags_have_urgency_5(self, det: RedFlagDetector):
        """Все immediate red flags имеют urgency=5."""
        flags = det.detect("Потерял сознание внезапно")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac
        assert cardiac[0].urgency == Urgency.IMMEDIATE

    @pytest.mark.parametrize("text,expected_category", [
        ("Сахар крови 25 ммоль/л", "endocrine"),
        ("Подозрение на тромбоз глубоких вен", "vascular"),
        ("Не могу мочиться, задержка мочеиспускания", "urological"),
        ("Обнаружили опухоль, выявлена впервые", "oncological"),
        ("Врач подозревает аппендицит", "surgical"),
    ])
    def test_high_priority_urgency_4(self, det: RedFlagDetector, text: str, expected_category: str):
        """Red flags высокого приоритета имеют urgency=4 (VERY_HIGH)."""
        flags = det.detect(text)
        matching = [f for f in flags if f.category == expected_category]
        assert matching, f"Не обнаружен {expected_category} red flag для: {text}"
        assert matching[0].urgency == Urgency.VERY_HIGH

    def test_hypertension_with_davlenie(self, det: RedFlagDetector):
        """Неконтролируемая гипертензия — 'Давление 190/120' — регрессионный тест (BUG-004 исправлен)."""
        flags = det.detect("Давление 190/120, не снижается")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac

    def test_hypertension_with_ad(self, det: RedFlagDetector):
        """Неконтролируемая гипертензия — формат 'АД 185/120' работает."""
        flags = det.detect("АД 185/120, не снижается таблетками")
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac
        assert cardiac[0].urgency == Urgency.VERY_HIGH

    def test_immediate_sorted_before_high(self, det: RedFlagDetector):
        """При наличии обоих уровней, immediate (5) идёт перед high (4)."""
        text = "Боль в груди, АД 195/130"
        flags = det.detect(text)
        if len(flags) >= 2:
            assert flags[0].urgency >= flags[1].urgency

    def test_action_text_immediate(self, det: RedFlagDetector):
        """Для immediate — action содержит рекомендацию вызвать скорую."""
        flags = det.detect("Рвота кровью обильная")
        immediate = [f for f in flags if f.urgency == Urgency.IMMEDIATE]
        assert immediate
        assert "103" in immediate[0].action or "112" in immediate[0].action

    def test_action_text_high_priority(self, det: RedFlagDetector):
        """Для high priority — action содержит рекомендацию обратиться к врачу."""
        flags = det.detect("Аппендицит, боль в правом боку")
        high = [f for f in flags if f.urgency == Urgency.VERY_HIGH]
        assert high
        assert "врач" in high[0].action.lower()


# ===========================================================================
# 3. Негативные тесты — НЕ должны срабатывать
# ===========================================================================

class TestRedFlagNegative:
    """Обычные жалобы НЕ должны вызывать red flag."""

    @pytest.mark.parametrize("text", [
        "Болит голова уже неделю, ноющая боль",
        "Немного температура 37.2, насморк",
        "Хочу похудеть, подскажите диету",
        "Насморк и кашель третий день",
        "Болит коленка при ходьбе",
        "Бессонница уже месяц, трудно уснуть",
        "Выпадают волосы, что делать",
        "Сухость кожи на руках",
        "Изжога после еды",
        "Лёгкая тошнота по утрам",
    ])
    def test_routine_complaints_no_flags(self, det: RedFlagDetector, text: str):
        """Рутинные жалобы не должны вызывать red flag."""
        flags = det.detect(text)
        assert len(flags) == 0, (
            f"Ложноположительный red flag для: {text!r} -> "
            f"{[f.description for f in flags]}"
        )

    def test_has_immediate_flags_negative(self, det: RedFlagDetector):
        """has_immediate_flags возвращает False для обычных жалоб."""
        assert not det.has_immediate_flags("Болит горло, больно глотать")
        assert not det.has_immediate_flags("Немного кружится голова")


# ===========================================================================
# 4. Edge cases
# ===========================================================================

class TestRedFlagEdgeCases:
    """Граничные и нестандартные случаи."""

    def test_empty_string(self, det: RedFlagDetector):
        """Пустая строка не вызывает ошибок и не даёт флагов."""
        flags = det.detect("")
        assert flags == []

    def test_whitespace_only(self, det: RedFlagDetector):
        """Строка из пробелов не вызывает ошибок."""
        flags = det.detect("   \t\n  ")
        assert flags == []

    def test_very_long_text(self, det: RedFlagDetector):
        """Длинный текст с red flag внутри обрабатывается корректно."""
        padding = "Обычный текст без симптомов. " * 500
        text = padding + "Внезапная одышка в покое." + padding
        flags = det.detect(text)
        cardiac = [f for f in flags if f.category == "cardiac"]
        assert cardiac, "Red flag не обнаружен в длинном тексте"

    def test_latin_text_no_flags(self, det: RedFlagDetector):
        """Текст на латинице (английский) не вызывает флагов."""
        flags = det.detect("I have chest pain and shortness of breath")
        assert flags == [], "Латинский текст не должен давать флаги (паттерны на русском)"

    def test_multiple_flags_in_one_text(self, det: RedFlagDetector):
        """Множественные red flags в одном тексте — все детектируются."""
        text = (
            "Рвота кровью, потерял сознание, "
            "спутанное сознание, боль в груди отдаёт в левую руку"
        )
        flags = det.detect(text)
        categories = {f.category for f in flags}
        assert "abdominal" in categories, "Не обнаружен abdominal flag"
        assert "cardiac" in categories, "Не обнаружен cardiac flag"
        assert "neurological" in categories, "Не обнаружен neurological flag"
        assert len(flags) >= 3, f"Обнаружено только {len(flags)} флагов вместо 3+"

    def test_flags_are_deduplicated(self, det: RedFlagDetector):
        """Одинаковый red flag не дублируется."""
        text = "Боль в груди сильная. Опять боль в грудной клетке."
        flags = det.detect(text)
        cardiac = [f for f in flags if f.category == "cardiac"]
        descriptions = [f.description for f in cardiac]
        assert len(descriptions) == len(set(descriptions)), "Найдены дубли red flags"

    def test_case_insensitive(self, det: RedFlagDetector):
        """Детекция нечувствительна к регистру."""
        flags_lower = det.detect("рвота кровью")
        flags_upper = det.detect("РВОТА КРОВЬЮ")
        flags_mixed = det.detect("Рвота Кровью")
        assert len(flags_lower) >= 1
        assert len(flags_upper) >= 1
        assert len(flags_mixed) >= 1

    def test_has_immediate_flags_consistency(self, det: RedFlagDetector):
        """has_immediate_flags согласован с detect: если detect нашёл immediate,
        то и has_immediate_flags = True."""
        text = "Потерял сознание, упал на пол"
        flags = det.detect(text)
        has_immediate = [f for f in flags if f.urgency == Urgency.IMMEDIATE]
        if has_immediate:
            assert det.has_immediate_flags(text)

    def test_module_level_singleton(self):
        """Синглтон detector на уровне модуля работает корректно."""
        flags = detector.detect("Рвота кровью, тяжело дышать")
        assert len(flags) >= 1

    def test_redflag_dataclass_frozen(self):
        """RedFlag — frozen dataclass, нельзя менять после создания."""
        flag = RedFlag(
            category="cardiac",
            description="Test",
            urgency=Urgency.IMMEDIATE,
            action="Call 103",
        )
        with pytest.raises(AttributeError):
            flag.category = "neurological"  # type: ignore[misc]


# ===========================================================================
# 5. Метрика false negative rate < 5%
# ===========================================================================

class TestRedFlagFalseNegativeRate:
    """Метрика: false negative rate должен быть < 5%.

    Набор из 40 тестовых кейсов с известными red flags.
    Все regex-баги исправлены — полный набор включает ранее пропускавшиеся кейсы.
    """

    # (текст жалобы, ожидаемая категория, ожидаемый urgency)
    KNOWN_RED_FLAG_CASES: list[tuple[str, str, Urgency]] = [
        # --- Cardiac immediate ---
        ("Острая боль в груди, не могу дышать", "cardiac", Urgency.IMMEDIATE),
        ("Жжение в грудной клетке", "cardiac", Urgency.IMMEDIATE),
        ("Боль в сердце отдаёт в челюсть", "cardiac", Urgency.IMMEDIATE),
        ("Потерял сознание в метро", "cardiac", Urgency.IMMEDIATE),
        ("Внезапная одышка, лежу и задыхаюсь", "cardiac", Urgency.IMMEDIATE),
        ("Тяжесть в грудной клетке, не проходит", "cardiac", Urgency.IMMEDIATE),
        ("Терял сознание дважды за день", "cardiac", Urgency.IMMEDIATE),

        # --- Neurological immediate ---
        ("Слабость в правой руке, не могу поднять", "neurological", Urgency.IMMEDIATE),
        ("Внезапная потеря зрения на один глаз", "neurological", Urgency.IMMEDIATE),
        ("Громоподобная головная боль, как удар", "neurological", Urgency.IMMEDIATE),
        ("Судороги впервые в жизни", "neurological", Urgency.IMMEDIATE),
        ("Спутанное сознание, не понимает где находится", "neurological", Urgency.IMMEDIATE),
        ("Нарушение сознания, речь спутана", "neurological", Urgency.IMMEDIATE),

        # --- Allergic immediate ---
        ("Началась анафилаксия после введения антибиотика", "allergic", Urgency.IMMEDIATE),
        ("Отёк Квинке, лицо опухло", "allergic", Urgency.IMMEDIATE),
        ("Анафилактический шок", "allergic", Urgency.IMMEDIATE),

        # --- Psychiatric immediate ---
        ("Хочу покончить с собой", "psychiatric", Urgency.IMMEDIATE),
        ("Суицидальные мысли каждый день", "psychiatric", Urgency.IMMEDIATE),
        ("Не хочу жить, устал от всего", "psychiatric", Urgency.IMMEDIATE),
        ("Думаю убить себя", "psychiatric", Urgency.IMMEDIATE),

        # --- Abdominal immediate ---
        ("Рвота кровью после алкоголя", "abdominal", Urgency.IMMEDIATE),
        ("Чёрный дёгтеобразный стул", "abdominal", Urgency.IMMEDIATE),
        ("Доскообразный живот, нельзя прикоснуться", "abdominal", Urgency.IMMEDIATE),
        ("Чёрный кал, слабость", "abdominal", Urgency.IMMEDIATE),

        # --- Obstetric immediate ---
        ("Кровотечение при беременности 32 недели", "obstetric", Urgency.IMMEDIATE),
        ("Кровотечение на фоне беременности", "obstetric", Urgency.IMMEDIATE),

        # --- Infectious immediate ---
        ("Ригидность затылочных мышц с лихорадкой", "infectious", Urgency.IMMEDIATE),

        # --- High priority (urgency 4) ---
        ("АД 185/120, не снижается таблетками", "cardiac", Urgency.VERY_HIGH),
        ("Сахар крови 28 ммоль/л", "endocrine", Urgency.VERY_HIGH),
        ("Глюкоза 22 ммоль", "endocrine", Urgency.VERY_HIGH),
        ("Подозрение на тромбоз глубоких вен левой ноги", "vascular", Urgency.VERY_HIGH),
        ("Острая задержка мочи, не могу мочиться", "urological", Urgency.VERY_HIGH),
        ("Обнаружили образование, выявлено впервые на УЗИ", "oncological", Urgency.VERY_HIGH),
        ("Подозрение на аппендицит, боль справа", "surgical", Urgency.VERY_HIGH),
        ("Не мог мочиться всю ночь, задержка мочи", "urological", Urgency.VERY_HIGH),

        # --- Регрессионные кейсы (ранее KNOWN_BUGS, исправлены) ---
        ("Сильное давление за грудиной", "cardiac", Urgency.IMMEDIATE),
        ("Онемение левой половины тела", "neurological", Urgency.IMMEDIATE),
        ("Давление 185/120, не снижается таблетками", "cardiac", Urgency.VERY_HIGH),
        ("Давление артериальное 200/110", "cardiac", Urgency.VERY_HIGH),
        ("Живот доскообразный", "abdominal", Urgency.IMMEDIATE),
        ("Рвота с кровью после удара в живот", "abdominal", Urgency.IMMEDIATE),
    ]

    def test_false_negative_rate_below_5_percent(self, det: RedFlagDetector):
        """False negative rate по основному набору должен быть < 5%.

        False negative = red flag не детектирован, хотя ожидался.
        Кейсы с известными regex-багами исключены (отдельный тест ниже).
        """
        total = len(self.KNOWN_RED_FLAG_CASES)
        missed = 0
        missed_details: list[str] = []

        for text, expected_cat, expected_urgency in self.KNOWN_RED_FLAG_CASES:
            flags = det.detect(text)
            matching = [
                f for f in flags
                if f.category == expected_cat and f.urgency == expected_urgency
            ]
            if not matching:
                missed += 1
                found_desc = (
                    [(f.category, f.urgency.name) for f in flags] if flags else "none"
                )
                missed_details.append(
                    f"  MISS: {text!r} -> expected ({expected_cat}, {expected_urgency.name}), "
                    f"found: {found_desc}"
                )

        fn_rate = missed / total
        report = (
            f"False negative rate: {fn_rate:.1%} ({missed}/{total})\n"
            + "\n".join(missed_details)
        )
        assert fn_rate < 0.05, (
            f"False negative rate {fn_rate:.1%} превышает допустимые 5%!\n{report}"
        )

    def test_regression_formerly_buggy_cases(self, det: RedFlagDetector):
        """Регрессионный тест: ранее пропускавшиеся кейсы теперь детектируются.

        Кейсы перенесены из KNOWN_BUGS в KNOWN_RED_FLAG_CASES после фикса BUG-001..005.
        """
        regression_cases = [
            ("Сильное давление за грудиной", "cardiac", Urgency.IMMEDIATE),
            ("Онемение левой половины тела", "neurological", Urgency.IMMEDIATE),
            ("Давление 185/120, не снижается таблетками", "cardiac", Urgency.VERY_HIGH),
            ("Давление артериальное 200/110", "cardiac", Urgency.VERY_HIGH),
            ("Живот доскообразный", "abdominal", Urgency.IMMEDIATE),
            ("Рвота с кровью после удара в живот", "abdominal", Urgency.IMMEDIATE),
        ]
        for text, expected_cat, expected_urgency in regression_cases:
            flags = det.detect(text)
            matching = [
                f for f in flags
                if f.category == expected_cat and f.urgency == expected_urgency
            ]
            assert matching, f"Регрессия! Не детектирован: {text!r}"

    def test_all_categories_represented(self):
        """Набор тестов покрывает все категории из паттернов."""
        tested_categories = {cat for _, cat, _ in self.KNOWN_RED_FLAG_CASES}
        expected_cats = {
            "cardiac", "neurological", "allergic", "psychiatric",
            "abdominal", "obstetric", "infectious",
            "endocrine", "vascular", "urological", "oncological", "surgical",
        }
        missing = expected_cats - tested_categories
        assert not missing, f"Категории не представлены в тестах: {missing}"

    def test_minimum_test_set_size(self):
        """Набор содержит минимум 30 кейсов (требование задачи)."""
        assert len(self.KNOWN_RED_FLAG_CASES) >= 30, (
            f"Только {len(self.KNOWN_RED_FLAG_CASES)} кейсов, нужно >= 30"
        )


# ===========================================================================
# 6. Обнаруженные дефекты regex-паттернов
# ===========================================================================

class TestRegexPatternDefects:
    """Регрессионные тесты для исправленных дефектов regex-паттернов (BUG-001..005).

    Все баги исправлены. Тесты оставлены как регрессионные — гарантируют,
    что исправления не будут случайно утеряны.
    """

    def test_bug001_davlenie_matched(self, det: RedFlagDetector):
        """BUG-001 ИСПРАВЛЕН: 'давление' теперь matchится паттерном 'давл\\w*'."""
        flags = det.detect("Чувствую давление за грудиной")
        assert any(f.category == "cardiac" for f in flags)

    def test_bug002_onemenie_matched(self, det: RedFlagDetector):
        """BUG-002 ИСПРАВЛЕН: 'Онемение' теперь matchится паттерном 'онемени\\w*'."""
        flags = det.detect("Онемение левой стороны тела")
        assert any(f.category == "neurological" for f in flags)

    def test_bug003_board_abdomen_reversed_order(self, det: RedFlagDetector):
        """BUG-003 ИСПРАВЛЕН: 'Живот доскообразный' детектируется (альтернативный порядок)."""
        flags = det.detect("Живот доскообразный, невозможно дотронуться")
        assert any(f.category == "abdominal" for f in flags)

    def test_bug004_davlenie_hypertension(self, det: RedFlagDetector):
        """BUG-004 ИСПРАВЛЕН: 'Давление 190/120' детектируется паттерном 'давлени\\w*'."""
        flags = det.detect("Давление 190/120, не снижается")
        assert any(f.category == "cardiac" for f in flags)

    def test_bug005_vomiting_with_preposition(self, det: RedFlagDetector):
        """BUG-005 ИСПРАВЛЕН: 'Рвота с кровью' детектируется (предлог допускается)."""
        flags = det.detect("Рвота с кровью после удара")
        assert any(f.category == "abdominal" for f in flags)
