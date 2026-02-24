"""Medical safety tests — red flags detection and AI output validation.

Covers:
- Red flags false negative rate (must be < 5%)
- AI output guard: prohibited formulations detection
- Disclaimer templates existence
"""
import pytest

from src.safety.red_flags import RedFlagDetector, Urgency
from src.safety.output_guard import check_ai_output, SafetyViolation
from src.safety.disclaimers import DisclaimerType, get_disclaimer


# ══════════════════════════════════════════════════════════════
# Red Flags Detection Tests
# ══════════════════════════════════════════════════════════════

class TestRedFlagDetection:
    """Test that red flags are detected correctly (false negative < 5%)."""

    def setup_method(self):
        self.detector = RedFlagDetector()

    # --- IMMEDIATE (urgency 5) ---

    @pytest.mark.parametrize("text", [
        "Сильная боль в груди, отдаёт в левую руку",
        "Давление в грудной клетке и жжение за грудиной",
        "Тяжесть в области сердца уже 2 часа",
        "Боль за грудиной, отдаёт в челюсть",
    ])
    def test_cardiac_chest_pain(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"
        assert any(f.category == "cardiac" for f in flags)
        assert any(f.urgency == Urgency.IMMEDIATE for f in flags)

    @pytest.mark.parametrize("text", [
        "Внезапная одышка в покое, задыхаюсь",
        "Острая одышка началась 10 минут назад",
    ])
    def test_cardiac_dyspnea(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"
        assert any(f.category == "cardiac" for f in flags)

    @pytest.mark.parametrize("text", [
        "Потерял сознание на улице",
        "Терял сознание дважды за день",
        "Теряю сознание при подъёме по лестнице",
    ])
    def test_cardiac_syncope(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"

    @pytest.mark.parametrize("text", [
        "Слабость в правой руке и онемение правой стороны лица",
        "Онемение одной стороны тела началось внезапно",
        "Парез левой руки и ноги",
    ])
    def test_neurological_stroke(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"
        assert any(f.category == "neurological" for f in flags)

    @pytest.mark.parametrize("text", [
        "Внезапная потеря зрения на один глаз",
        "Острое нарушение зрения",
    ])
    def test_neurological_vision_loss(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"

    @pytest.mark.parametrize("text", [
        "Громоподобная головная боль, самая сильная в жизни",
        "Внезапная сильнейшая головная боль",
    ])
    def test_neurological_thunderclap(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"

    def test_neurological_seizure(self):
        flags = self.detector.detect("Судороги впервые в жизни, длились 3 минуты")
        assert len(flags) > 0
        assert any(f.category == "neurological" for f in flags)

    def test_neurological_confusion(self):
        flags = self.detector.detect("Спутанное сознание, не узнаёт родных")
        assert len(flags) > 0

    @pytest.mark.parametrize("text", [
        "Признаки анафилаксии: сыпь, отёк, падение давления",
        "Анафилактический шок после укуса пчелы",
    ])
    def test_allergic_anaphylaxis(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"
        assert any(f.category == "allergic" for f in flags)

    def test_allergic_angioedema(self):
        flags = self.detector.detect("Отёк Квинке, опухло лицо и горло")
        assert len(flags) > 0
        assert any(f.category == "allergic" for f in flags)

    @pytest.mark.parametrize("text", [
        "Не хочу жить, думаю о суициде",
        "Хочу покончить с собой",
        "Планирую убить себя",
    ])
    def test_psychiatric_suicidal(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"
        assert any(f.category == "psychiatric" for f in flags)

    @pytest.mark.parametrize("text", [
        "Рвота с кровью, сгустки",
        "Чёрный стул, похож на дёготь",
        "Доскообразный живот, сильная боль",
    ])
    def test_abdominal_emergencies(self, text):
        flags = self.detector.detect(text)
        assert len(flags) > 0, f"Red flag not detected: {text}"
        assert any(f.category == "abdominal" for f in flags)

    def test_obstetric_bleeding(self):
        flags = self.detector.detect("Кровотечение при беременности 32 недели")
        assert len(flags) > 0
        assert any(f.category == "obstetric" for f in flags)

    def test_infectious_meningitis(self):
        flags = self.detector.detect("Ригидность затылочных мышц, лихорадка 39.5")
        assert len(flags) > 0
        assert any(f.category == "infectious" for f in flags)

    # --- HIGH PRIORITY (urgency 4) ---

    def test_hypertension_crisis(self):
        flags = self.detector.detect("Давление 190/110, головная боль")
        assert len(flags) > 0, "Hypertension crisis not detected"
        assert any(f.urgency == Urgency.VERY_HIGH for f in flags)

    def test_hyperglycemia(self):
        flags = self.detector.detect("Сахар 25 ммоль, жажда, частое мочеиспускание")
        assert len(flags) > 0, "Hyperglycemia not detected"

    def test_dvt(self):
        flags = self.detector.detect("Подозрение на тромбоз глубоких вен, нога отекла")
        assert len(flags) > 0

    def test_urinary_retention(self):
        flags = self.detector.detect("Острая задержка мочи, не мог мочиться 12 часов")
        assert len(flags) > 0

    def test_new_tumor(self):
        flags = self.detector.detect("Обнаружили опухоль впервые при УЗИ")
        assert len(flags) > 0

    def test_appendicitis(self):
        flags = self.detector.detect("Подозрение на аппендицит, боль в правой нижней части живота")
        assert len(flags) > 0

    # --- FALSE NEGATIVE RATE ---

    def test_no_false_positive_on_normal(self):
        """Normal complaints should NOT trigger red flags."""
        normal_texts = [
            "Болит горло, насморк, кашель",
            "Головная боль уже 3 дня, обычная",
            "Тошнота после еды",
            "Боль в колене при ходьбе",
            "Сыпь на руках, зуд",
            "Бессонница третий день",
            "Болит спина в пояснице",
        ]
        for text in normal_texts:
            flags = self.detector.detect(text)
            immediate = [f for f in flags if f.urgency == Urgency.IMMEDIATE]
            assert len(immediate) == 0, f"False positive on normal text: {text}"

    def test_has_immediate_flags(self):
        assert self.detector.has_immediate_flags("Боль в груди, отдаёт в руку")
        assert not self.detector.has_immediate_flags("Болит горло")

    def test_false_negative_rate(self):
        """Overall false negative rate must be < 5%.

        Test with a comprehensive list of emergency scenarios.
        """
        emergency_texts = [
            "Сильная боль в груди",
            "Потерял сознание",
            "Слабость в правой руке, онемение правой стороны",
            "Анафилаксия после еды",
            "Отёк Квинке",
            "Не хочу жить",
            "Рвота с кровью",
            "Чёрный дёгтеобразный кал",
            "Кровотечение при беременности",
            "Ригидность затылочных мышц",
            "Внезапная одышка в покое",
            "Внезапная потеря зрения",
            "Громоподобная головная боль",
            "Судороги впервые",
            "Спутанное сознание",
            "Доскообразный живот",
            "Суицидальные мысли",
            "Хочу покончить с собой",
            "Боль в грудной клетке, иррадиирует в челюсть",
            "Теряю сознание при нагрузке",
        ]

        detected = 0
        missed = []
        for text in emergency_texts:
            flags = self.detector.detect(text)
            if flags:
                detected += 1
            else:
                missed.append(text)

        total = len(emergency_texts)
        false_negative_rate = (total - detected) / total

        assert false_negative_rate < 0.05, (
            f"False negative rate {false_negative_rate:.1%} exceeds 5% threshold. "
            f"Missed: {missed}"
        )


# ══════════════════════════════════════════════════════════════
# AI Output Guard Tests
# ══════════════════════════════════════════════════════════════

class TestOutputGuard:
    """Test AI output safety validation."""

    # --- Definitive diagnosis (PROHIBITED) ---

    @pytest.mark.parametrize("text", [
        "У вас гастрит, нужно лечение",
        "У вас обнаружена аритмия",
        "У вас выявлен диабет второго типа",
        "У вас диагностирована гипертония",
        "Это точно аппендицит",
        "Это однозначно инфекция",
        "Ваш диагноз — пневмония",
        "Я ставлю диагноз бронхит",
    ])
    def test_detects_definitive_diagnosis(self, text):
        violations = check_ai_output(text)
        assert any(v.category == "diagnosis" for v in violations), (
            f"Definitive diagnosis not detected: {text}"
        )

    # --- Direct prescription (PROHIBITED) ---

    @pytest.mark.parametrize("text", [
        "Вам нужно принимать ибупрофен",
        "Вам необходимо начать приём антибиотиков",
        "Принимайте парацетамол три раза в день",
        "Назначаю вам амоксициллин",
        "Я выписываю рецепт на антибиотики",
        "Я прописываю вам лекарство",
    ])
    def test_detects_direct_prescription(self, text):
        violations = check_ai_output(text)
        assert any(v.category == "prescription" for v in violations), (
            f"Direct prescription not detected: {text}"
        )

    # --- Dismissal (PROHIBITED) ---

    @pytest.mark.parametrize("text", [
        "Это не опасно, не волнуйтесь",
        "Ничего страшного, просто отдохните",
        "Ничего серьёзного в ваших симптомах",
        "Не волнуйтесь, это пройдёт само",
        "Можете не обращаться к врачу",
    ])
    def test_detects_dismissal(self, text):
        violations = check_ai_output(text)
        assert any(v.category == "dismissal" for v in violations), (
            f"Dismissal not detected: {text}"
        )

    # --- Dosage as prescription (PROHIBITED) ---

    @pytest.mark.parametrize("text", [
        "Принимайте по 500 мг парацетамола",
        "Пейте по 200 мл раствора",
    ])
    def test_detects_dosage_prescription(self, text):
        violations = check_ai_output(text)
        assert any(v.category == "dosage" for v in violations), (
            f"Dosage prescription not detected: {text}"
        )

    # --- Safe formulations (SHOULD PASS) ---

    @pytest.mark.parametrize("text", [
        "Ваши симптомы ВОЗМОЖНО связаны с гастритом. Рекомендуется обратиться к гастроэнтерологу.",
        "В медицинской литературе при таких симптомах РАССМАТРИВАЕТСЯ возможность хронического бронхита.",
        "Рекомендуется обсудить с врачом возможность приёма ибупрофена.",
        "Для уточнения диагноза необходимо дополнительное обследование.",
        "Согласно клиническим рекомендациям, при таких показателях может применяться физиотерапия.",
        "Один из возможных вариантов — обратиться к неврологу для дообследования.",
    ])
    def test_safe_formulations_pass(self, text):
        violations = check_ai_output(text)
        assert len(violations) == 0, (
            f"False positive on safe text: {text}, violations: {[v.category for v in violations]}"
        )


# ══════════════════════════════════════════════════════════════
# Disclaimer Tests
# ══════════════════════════════════════════════════════════════

class TestDisclaimers:
    """Test that all required disclaimer templates exist and are non-empty."""

    @pytest.mark.parametrize("dtype", [
        DisclaimerType.GENERAL,
        DisclaimerType.DIAGNOSIS,
        DisclaimerType.EMERGENCY,
        DisclaimerType.CHILDREN,
    ])
    def test_disclaimer_exists(self, dtype):
        text = get_disclaimer(dtype)
        assert text, f"Disclaimer {dtype.value} is empty"
        assert len(text) > 20, f"Disclaimer {dtype.value} too short"

    def test_general_disclaimer_mentions_ai(self):
        text = get_disclaimer(DisclaimerType.GENERAL)
        assert "AI" in text or "ИИ" in text or "информационн" in text.lower()

    def test_emergency_disclaimer_mentions_103(self):
        text = get_disclaimer(DisclaimerType.EMERGENCY)
        assert "103" in text or "112" in text
