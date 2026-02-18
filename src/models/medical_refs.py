"""Medical reference ranges and clinical decision support data."""

# Standard laboratory reference ranges
LAB_REFERENCE_RANGES = {
    # Общий анализ крови (CBC)
    "hemoglobin_male": {"min": 130, "max": 170, "unit": "г/л", "name": "Гемоглобин (муж)"},
    "hemoglobin_female": {"min": 120, "max": 150, "unit": "г/л", "name": "Гемоглобин (жен)"},
    "erythrocytes_male": {"min": 4.0, "max": 5.5, "unit": "×10¹²/л", "name": "Эритроциты (муж)"},
    "erythrocytes_female": {"min": 3.5, "max": 5.0, "unit": "×10¹²/л", "name": "Эритроциты (жен)"},
    "leukocytes": {"min": 4.0, "max": 9.0, "unit": "×10⁹/л", "name": "Лейкоциты"},
    "platelets": {"min": 150, "max": 400, "unit": "×10⁹/л", "name": "Тромбоциты"},
    "esr_male": {"min": 1, "max": 10, "unit": "мм/ч", "name": "СОЭ (муж)"},
    "esr_female": {"min": 2, "max": 15, "unit": "мм/ч", "name": "СОЭ (жен)"},
    "hematocrit_male": {"min": 40, "max": 48, "unit": "%", "name": "Гематокрит (муж)"},
    "hematocrit_female": {"min": 36, "max": 42, "unit": "%", "name": "Гематокрит (жен)"},
    "mcv": {"min": 80, "max": 100, "unit": "фл", "name": "Средний объем эритроцита (MCV)"},
    "mch": {"min": 27, "max": 31, "unit": "пг", "name": "Среднее содержание Hb в эритроците (MCH)"},
    "mchc": {"min": 320, "max": 360, "unit": "г/л", "name": "Средняя концентрация Hb (MCHC)"},
    "reticulocytes": {"min": 0.2, "max": 1.2, "unit": "%", "name": "Ретикулоциты"},

    # Лейкоцитарная формула
    "neutrophils": {"min": 47, "max": 72, "unit": "%", "name": "Нейтрофилы"},
    "lymphocytes": {"min": 19, "max": 37, "unit": "%", "name": "Лимфоциты"},
    "monocytes": {"min": 3, "max": 11, "unit": "%", "name": "Моноциты"},
    "eosinophils": {"min": 0.5, "max": 5, "unit": "%", "name": "Эозинофилы"},
    "basophils": {"min": 0, "max": 1, "unit": "%", "name": "Базофилы"},

    # Биохимия крови
    "glucose_fasting": {"min": 3.9, "max": 5.5, "unit": "ммоль/л", "name": "Глюкоза натощак"},
    "glucose_postprandial": {"min": 3.9, "max": 7.8, "unit": "ммоль/л", "name": "Глюкоза постпрандиальная"},
    "hba1c": {"min": 4.0, "max": 5.6, "unit": "%", "name": "Гликированный гемоглобин (HbA1c)"},
    "total_cholesterol": {"min": 0, "max": 5.2, "unit": "ммоль/л", "name": "Общий холестерин"},
    "ldl": {"min": 0, "max": 3.0, "unit": "ммоль/л", "name": "ЛПНП"},
    "hdl_male": {"min": 1.0, "max": 99, "unit": "ммоль/л", "name": "ЛПВП (муж)"},
    "hdl_female": {"min": 1.2, "max": 99, "unit": "ммоль/л", "name": "ЛПВП (жен)"},
    "triglycerides": {"min": 0, "max": 1.7, "unit": "ммоль/л", "name": "Триглицериды"},
    "total_bilirubin": {"min": 3.4, "max": 17.1, "unit": "мкмоль/л", "name": "Общий билирубин"},
    "direct_bilirubin": {"min": 0, "max": 5.1, "unit": "мкмоль/л", "name": "Прямой билирубин"},
    "alt": {"min": 0, "max": 41, "unit": "ед/л", "name": "АЛТ"},
    "ast": {"min": 0, "max": 40, "unit": "ед/л", "name": "АСТ"},
    "alkaline_phosphatase": {"min": 35, "max": 105, "unit": "ед/л", "name": "Щелочная фосфатаза"},
    "ggt": {"min": 0, "max": 55, "unit": "ед/л", "name": "ГГТ"},
    "total_protein": {"min": 64, "max": 83, "unit": "г/л", "name": "Общий белок"},
    "albumin": {"min": 35, "max": 50, "unit": "г/л", "name": "Альбумин"},
    "creatinine_male": {"min": 62, "max": 106, "unit": "мкмоль/л", "name": "Креатинин (муж)"},
    "creatinine_female": {"min": 44, "max": 80, "unit": "мкмоль/л", "name": "Креатинин (жен)"},
    "urea": {"min": 2.5, "max": 8.3, "unit": "ммоль/л", "name": "Мочевина"},
    "uric_acid_male": {"min": 210, "max": 420, "unit": "мкмоль/л", "name": "Мочевая кислота (муж)"},
    "uric_acid_female": {"min": 150, "max": 350, "unit": "мкмоль/л", "name": "Мочевая кислота (жен)"},
    "crp": {"min": 0, "max": 5, "unit": "мг/л", "name": "С-реактивный белок (СРБ)"},
    "iron_male": {"min": 11.6, "max": 31.3, "unit": "мкмоль/л", "name": "Железо (муж)"},
    "iron_female": {"min": 9.0, "max": 30.4, "unit": "мкмоль/л", "name": "Железо (жен)"},
    "ferritin_male": {"min": 20, "max": 250, "unit": "мкг/л", "name": "Ферритин (муж)"},
    "ferritin_female": {"min": 10, "max": 120, "unit": "мкг/л", "name": "Ферритин (жен)"},

    # Электролиты
    "sodium": {"min": 136, "max": 145, "unit": "ммоль/л", "name": "Натрий"},
    "potassium": {"min": 3.5, "max": 5.1, "unit": "ммоль/л", "name": "Калий"},
    "chloride": {"min": 98, "max": 107, "unit": "ммоль/л", "name": "Хлориды"},
    "calcium": {"min": 2.15, "max": 2.55, "unit": "ммоль/л", "name": "Кальций общий"},
    "magnesium": {"min": 0.66, "max": 1.07, "unit": "ммоль/л", "name": "Магний"},
    "phosphorus": {"min": 0.81, "max": 1.45, "unit": "ммоль/л", "name": "Фосфор"},

    # Коагулограмма
    "pt_time": {"min": 11, "max": 15, "unit": "сек", "name": "Протромбиновое время"},
    "inr": {"min": 0.8, "max": 1.2, "unit": "", "name": "МНО"},
    "aptt": {"min": 25, "max": 35, "unit": "сек", "name": "АЧТВ"},
    "fibrinogen": {"min": 2.0, "max": 4.0, "unit": "г/л", "name": "Фибриноген"},
    "d_dimer": {"min": 0, "max": 0.5, "unit": "мкг/мл", "name": "D-димер"},

    # Гормоны щитовидной железы
    "tsh": {"min": 0.4, "max": 4.0, "unit": "мМЕ/л", "name": "ТТГ"},
    "free_t4": {"min": 9.0, "max": 22.0, "unit": "пмоль/л", "name": "Свободный Т4"},
    "free_t3": {"min": 2.6, "max": 5.7, "unit": "пмоль/л", "name": "Свободный Т3"},

    # Онкомаркёры
    "psa": {"min": 0, "max": 4.0, "unit": "нг/мл", "name": "ПСА"},
    "cea": {"min": 0, "max": 5.0, "unit": "нг/мл", "name": "РЭА"},
    "ca125": {"min": 0, "max": 35, "unit": "ед/мл", "name": "CA-125"},
    "ca199": {"min": 0, "max": 37, "unit": "ед/мл", "name": "CA 19-9"},
    "afp": {"min": 0, "max": 10, "unit": "нг/мл", "name": "Альфа-фетопротеин"},

    # Почечные показатели
    "gfr": {"min": 90, "max": 999, "unit": "мл/мин/1.73м²", "name": "СКФ"},

    # Анализ мочи
    "urine_ph": {"min": 5.0, "max": 7.0, "unit": "", "name": "pH мочи"},
    "urine_specific_gravity": {"min": 1.010, "max": 1.025, "unit": "", "name": "Удельный вес мочи"},
}


def interpret_lab_value(test_key: str, value: float) -> dict:
    """Interpret a lab value against reference ranges."""
    ref = LAB_REFERENCE_RANGES.get(test_key)
    if not ref:
        return {"status": "unknown", "message": f"Референсный диапазон для '{test_key}' не найден"}

    status = "normal"
    if value < ref["min"]:
        status = "low"
    elif value > ref["max"]:
        status = "high"

    deviation = 0
    if status == "low":
        deviation = round((ref["min"] - value) / ref["min"] * 100, 1)
    elif status == "high":
        deviation = round((value - ref["max"]) / ref["max"] * 100, 1)

    severity = "normal"
    if deviation > 50:
        severity = "critical"
    elif deviation > 20:
        severity = "significant"
    elif deviation > 0:
        severity = "mild"

    return {
        "test_name": ref["name"],
        "value": value,
        "unit": ref["unit"],
        "reference": f"{ref['min']}–{ref['max']}",
        "status": status,
        "deviation_percent": deviation,
        "severity": severity,
    }


# ICD-10 common codes for quick reference
ICD10_COMMON = {
    "I10": "Эссенциальная гипертензия",
    "I25.1": "Атеросклеротическая болезнь сердца",
    "I48": "Фибрилляция и трепетание предсердий",
    "I50": "Сердечная недостаточность",
    "E11": "Сахарный диабет 2 типа",
    "E10": "Сахарный диабет 1 типа",
    "E03": "Гипотиреоз",
    "E05": "Тиреотоксикоз",
    "E78": "Нарушения обмена липопротеинов",
    "J06": "ОРВИ",
    "J18": "Пневмония",
    "J44": "ХОБЛ",
    "J45": "Бронхиальная астма",
    "K21": "ГЭРБ",
    "K25": "Язвенная болезнь желудка",
    "K29": "Гастрит и дуоденит",
    "K80": "Желчнокаменная болезнь",
    "N18": "Хроническая болезнь почек",
    "N20": "Мочекаменная болезнь",
    "M54.5": "Боль в пояснице",
    "M15": "Полиартроз",
    "M81": "Остеопороз",
    "G43": "Мигрень",
    "G47.3": "Апноэ во сне",
    "F32": "Депрессивный эпизод",
    "F41": "Тревожные расстройства",
    "L20": "Атопический дерматит",
    "L40": "Псориаз",
    "C34": "Злокачественное новообразование бронхов и лёгкого",
    "C50": "Злокачественное новообразование молочной железы",
    "C61": "Злокачественное новообразование предстательной железы",
    "D50": "Железодефицитная анемия",
    "B34": "Вирусная инфекция неуточнённая",
}


# Drug interaction severity levels
DRUG_INTERACTIONS_CRITICAL = {
    ("warfarin", "aspirin"): "Повышенный риск кровотечения. Мониторинг МНО обязателен.",
    ("warfarin", "ibuprofen"): "Повышенный риск кровотечения. Избегать НПВС при терапии варфарином.",
    ("metformin", "contrast_dye"): "Риск лактоацидоза. Отменить за 48ч до и после контрастирования.",
    ("ssri", "mao_inhibitor"): "КРИТИЧНО: Серотониновый синдром. Категорически противопоказано.",
    ("ace_inhibitor", "potassium"): "Риск гиперкалиемии. Контроль электролитов.",
    ("statin", "fibrate"): "Повышенный риск рабдомиолиза. Мониторинг КФК.",
    ("methotrexate", "nsaid"): "Снижение клиренса метотрексата. Повышенная токсичность.",
    ("lithium", "nsaid"): "Повышение уровня лития. Мониторинг концентрации.",
    ("digoxin", "amiodarone"): "Повышение уровня дигоксина. Снизить дозу дигоксина на 50%.",
    ("clopidogrel", "omeprazole"): "Снижение антиагрегантного эффекта клопидогрела.",
    ("ciprofloxacin", "theophylline"): "Повышение уровня теофиллина. Риск токсичности.",
    ("simvastatin", "clarithromycin"): "Повышенный риск рабдомиолиза. Противопоказано.",
}
