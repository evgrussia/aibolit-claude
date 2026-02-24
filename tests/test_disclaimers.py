"""Тесты медицинских дисклеймеров.

Покрывает:
- Наличие всех типов дисклеймеров (general, diagnosis, treatment, ...)
- Корректность содержания (ключевые слова и фразы)
- Функции получения дисклеймеров (get_disclaimer, get_disclaimer_text)
- Формат и валидность текстов
- Fallback при неизвестном типе

Основано на правилах: .claude/rules/05-medical-safety.md
"""
import pytest

from src.safety.disclaimers import (
    DISCLAIMERS,
    DisclaimerType,
    get_disclaimer,
    get_disclaimer_text,
)


# ===========================================================================
# 1. Наличие всех типов дисклеймеров
# ===========================================================================

class TestDisclaimerTypes:
    """Все типы дисклеймеров определены и доступны."""

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_all_enum_types_in_dict(self, dtype: DisclaimerType):
        """Каждый элемент DisclaimerType имеет соответствующий текст в DISCLAIMERS."""
        assert dtype in DISCLAIMERS, f"Тип {dtype.value} отсутствует в DISCLAIMERS"

    def test_expected_types_exist(self):
        """Все ожидаемые типы дисклеймеров присутствуют в enum."""
        expected = {
            "general", "diagnosis", "treatment", "medication",
            "lab_analysis", "imaging", "emergency", "children",
        }
        actual = {t.value for t in DisclaimerType}
        missing = expected - actual
        assert not missing, f"Отсутствуют типы дисклеймеров: {missing}"

    def test_disclaimers_dict_has_8_types(self):
        """Словарь DISCLAIMERS содержит ровно 8 типов."""
        assert len(DISCLAIMERS) == 8, (
            f"Ожидалось 8 типов, получено {len(DISCLAIMERS)}"
        )


# ===========================================================================
# 2. Содержание дисклеймеров — ключевые слова
# ===========================================================================

class TestDisclaimerContent:
    """Содержание каждого дисклеймера включает обязательные ключевые слова."""

    def test_general_contains_informational(self):
        """General содержит 'информационный характер'."""
        text = DISCLAIMERS[DisclaimerType.GENERAL]
        assert "информационный характер" in text

    def test_general_contains_not_consultation(self):
        """General содержит 'не является медицинской консультацией'."""
        text = DISCLAIMERS[DisclaimerType.GENERAL].lower()
        assert "не является медицинской консультацией" in text

    def test_diagnosis_contains_not_diagnosis(self):
        """Diagnosis содержит 'НЕ диагноз'."""
        text = DISCLAIMERS[DisclaimerType.DIAGNOSIS]
        assert "НЕ диагноз" in text

    def test_diagnosis_contains_specialist(self):
        """Diagnosis рекомендует обратиться к специалисту."""
        text = DISCLAIMERS[DisclaimerType.DIAGNOSIS].lower()
        assert "специалист" in text or "врач" in text

    def test_treatment_contains_doctor_consultation(self):
        """Treatment содержит 'без консультации с врачом'."""
        text = DISCLAIMERS[DisclaimerType.TREATMENT].lower()
        assert "без консультации" in text and "врач" in text

    def test_treatment_warns_self_medication(self):
        """Treatment предупреждает о самолечении."""
        text = DISCLAIMERS[DisclaimerType.TREATMENT].lower()
        assert "самолечение" in text

    def test_medication_not_prescribes(self):
        """Medication содержит 'НЕ назначает лекарства'."""
        text = DISCLAIMERS[DisclaimerType.MEDICATION]
        assert "НЕ назначает лекарства" in text

    def test_medication_mentions_contraindications(self):
        """Medication упоминает противопоказания."""
        text = DISCLAIMERS[DisclaimerType.MEDICATION].lower()
        assert "противопоказания" in text

    def test_lab_analysis_requires_doctor(self):
        """Lab analysis требует подтверждения врачом."""
        text = DISCLAIMERS[DisclaimerType.LAB_ANALYSIS].lower()
        assert "врач" in text

    def test_lab_analysis_mentions_ai(self):
        """Lab analysis упоминает AI-систему."""
        text = DISCLAIMERS[DisclaimerType.LAB_ANALYSIS].lower()
        assert "ai" in text

    def test_imaging_not_radiology_report(self):
        """Imaging содержит 'НЕ радиологическое заключение'."""
        text = DISCLAIMERS[DisclaimerType.IMAGING]
        assert "НЕ радиологическое заключение" in text

    def test_imaging_mentions_radiologist(self):
        """Imaging рекомендует врача-рентгенолога."""
        text = DISCLAIMERS[DisclaimerType.IMAGING].lower()
        assert "рентгенолог" in text

    def test_emergency_contains_103(self):
        """Emergency содержит номер скорой помощи 103."""
        text = DISCLAIMERS[DisclaimerType.EMERGENCY]
        assert "103" in text

    def test_emergency_contains_112(self):
        """Emergency содержит универсальный номер 112."""
        text = DISCLAIMERS[DisclaimerType.EMERGENCY]
        assert "112" in text

    def test_emergency_mentions_ambulance(self):
        """Emergency упоминает скорую помощь."""
        text = DISCLAIMERS[DisclaimerType.EMERGENCY].lower()
        assert "скорую" in text or "скорой" in text

    def test_children_mentions_pediatrician(self):
        """Children упоминает педиатра."""
        text = DISCLAIMERS[DisclaimerType.CHILDREN].lower()
        assert "педиатр" in text

    def test_children_warns_adult_dosage(self):
        """Children предупреждает о неприменимости взрослых дозировок."""
        text = DISCLAIMERS[DisclaimerType.CHILDREN].lower()
        assert "дозировк" in text or "не применим" in text


# ===========================================================================
# 3. Функции получения дисклеймеров
# ===========================================================================

class TestGetDisclaimer:
    """Тесты функций get_disclaimer и get_disclaimer_text."""

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_get_disclaimer_returns_string(self, dtype: DisclaimerType):
        """get_disclaimer возвращает непустую строку для всех типов."""
        result = get_disclaimer(dtype)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_get_disclaimer_matches_dict(self, dtype: DisclaimerType):
        """get_disclaimer возвращает текст из словаря DISCLAIMERS."""
        result = get_disclaimer(dtype)
        expected = DISCLAIMERS[dtype]
        assert result == expected

    def test_get_disclaimer_by_string_value(self):
        """get_disclaimer принимает строковое значение типа."""
        result = get_disclaimer("general")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_disclaimer_fallback_unknown_type(self):
        """При неизвестном типе возвращается general дисклеймер."""
        result = get_disclaimer("nonexistent_type")
        expected = DISCLAIMERS[DisclaimerType.GENERAL]
        assert result == expected

    def test_get_disclaimer_text_alias(self):
        """get_disclaimer_text — алиас get_disclaimer, возвращает тот же результат."""
        for dtype in DisclaimerType:
            assert get_disclaimer(dtype) == get_disclaimer_text(dtype)

    def test_get_disclaimer_text_with_string(self):
        """get_disclaimer_text принимает строковые значения."""
        result = get_disclaimer_text("emergency")
        assert "103" in result


# ===========================================================================
# 4. Формат и валидность текстов
# ===========================================================================

class TestDisclaimerFormat:
    """Формат дисклеймеров: язык, длина, непустота."""

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_disclaimer_not_empty(self, dtype: DisclaimerType):
        """Дисклеймер не пуст."""
        text = DISCLAIMERS[dtype]
        assert text.strip(), f"Дисклеймер {dtype.value} пуст"

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_disclaimer_min_length(self, dtype: DisclaimerType):
        """Дисклеймер длиннее 20 символов (минимальная осмысленность)."""
        text = DISCLAIMERS[dtype]
        assert len(text) > 20, (
            f"Дисклеймер {dtype.value} слишком короткий: {len(text)} символов"
        )

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_disclaimer_max_length(self, dtype: DisclaimerType):
        """Дисклеймер короче 500 символов (читабельность)."""
        text = DISCLAIMERS[dtype]
        assert len(text) < 500, (
            f"Дисклеймер {dtype.value} слишком длинный: {len(text)} символов"
        )

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_disclaimer_is_russian(self, dtype: DisclaimerType):
        """Дисклеймер содержит кириллические символы (на русском языке)."""
        text = DISCLAIMERS[dtype]
        cyrillic_count = sum(1 for ch in text if "\u0400" <= ch <= "\u04ff")
        assert cyrillic_count > 10, (
            f"Дисклеймер {dtype.value} не содержит достаточно кириллицы "
            f"({cyrillic_count} символов)"
        )

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_disclaimer_no_leading_trailing_whitespace(self, dtype: DisclaimerType):
        """Дисклеймер не содержит лишних пробелов в начале/конце."""
        text = DISCLAIMERS[dtype]
        assert text == text.strip(), (
            f"Дисклеймер {dtype.value} содержит лишние пробелы"
        )

    @pytest.mark.parametrize("dtype", list(DisclaimerType))
    def test_disclaimer_ends_with_period(self, dtype: DisclaimerType):
        """Дисклеймер заканчивается точкой (корректная пунктуация)."""
        text = DISCLAIMERS[dtype]
        assert text.endswith("."), (
            f"Дисклеймер {dtype.value} не заканчивается точкой: ...{text[-20:]!r}"
        )


# ===========================================================================
# 5. DisclaimerType enum
# ===========================================================================

class TestDisclaimerTypeEnum:
    """Тесты enum DisclaimerType."""

    def test_enum_is_str_enum(self):
        """DisclaimerType наследует str для удобного сравнения со строками."""
        assert isinstance(DisclaimerType.GENERAL, str)

    def test_enum_values_are_lowercase(self):
        """Все значения enum в нижнем регистре."""
        for dtype in DisclaimerType:
            assert dtype.value == dtype.value.lower(), (
                f"{dtype.name}.value = {dtype.value!r} не в нижнем регистре"
            )

    def test_enum_members_count(self):
        """Enum содержит ровно 8 элементов."""
        assert len(DisclaimerType) == 8
