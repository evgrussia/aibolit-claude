"""All medical specializations and their AI doctor configurations."""
from dataclasses import dataclass, field


@dataclass
class MedicalSkill:
    """A specific clinical skill an AI doctor can perform."""
    name: str
    description: str
    tool_name: str  # MCP tool name


@dataclass
class Specialization:
    """Medical specialization configuration."""
    id: str
    name_ru: str
    name_en: str
    description: str
    skills: list[MedicalSkill] = field(default_factory=list)
    related_icd_prefixes: list[str] = field(default_factory=list)
    required_lab_tests: list[str] = field(default_factory=list)


# Complete registry of all medical specializations
SPECIALIZATIONS: dict[str, Specialization] = {}


def _reg(spec: Specialization) -> None:
    SPECIALIZATIONS[spec.id] = spec


# ─────────────────────────────────────────────────
# 1. ТЕРАПИЯ / INTERNAL MEDICINE
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="therapist",
    name_ru="Терапевт",
    name_en="General Practitioner / Internist",
    description="Первичная диагностика, общий осмотр, направление к узким специалистам. "
                "Ведение хронических заболеваний, профилактика.",
    skills=[
        MedicalSkill("Первичный осмотр", "Сбор анамнеза, оценка жалоб, витальных показателей", "therapist_examine"),
        MedicalSkill("Расшифровка анализов", "Интерпретация ОАК, биохимии, мочи", "analyze_lab_results"),
        MedicalSkill("Диспансеризация", "Профилактический осмотр по возрасту и полу", "preventive_screening"),
        MedicalSkill("Маршрутизация", "Направление к узкому специалисту", "route_to_specialist"),
    ],
    related_icd_prefixes=["J06", "J18", "I10", "E11", "K29"],
    required_lab_tests=["leukocytes", "hemoglobin_male", "hemoglobin_female", "glucose_fasting", "crp"],
))

# ─────────────────────────────────────────────────
# 2. КАРДИОЛОГИЯ / CARDIOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="cardiologist",
    name_ru="Кардиолог",
    name_en="Cardiologist",
    description="Диагностика и лечение заболеваний сердечно-сосудистой системы. "
                "ИБС, аритмии, сердечная недостаточность, гипертензия.",
    skills=[
        MedicalSkill("Анализ ЭКГ", "Расшифровка электрокардиограммы", "analyze_ecg"),
        MedicalSkill("Оценка риска ССЗ", "Расчёт SCORE, Framingham", "cardiovascular_risk"),
        MedicalSkill("Анализ ЭхоКГ", "Интерпретация результатов ЭхоКГ", "analyze_echo"),
        MedicalSkill("Подбор антигипертензивной терапии", "Выбор препаратов по профилю пациента", "prescribe_antihypertensive"),
        MedicalSkill("Анализ холтеровского мониторирования", "Расшифровка суточного ЭКГ", "analyze_holter"),
        MedicalSkill("Коронарный кальциевый скор", "Оценка кальцификации коронарных артерий", "coronary_calcium_score"),
    ],
    related_icd_prefixes=["I10", "I20", "I21", "I25", "I48", "I50", "I42"],
    required_lab_tests=["total_cholesterol", "ldl", "hdl_male", "triglycerides", "crp", "d_dimer", "nt_probnp"],
))

# ─────────────────────────────────────────────────
# 3. НЕВРОЛОГИЯ / NEUROLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="neurologist",
    name_ru="Невролог",
    name_en="Neurologist",
    description="Заболевания центральной и периферической нервной системы. "
                "Инсульты, эпилепсия, болезнь Паркинсона, рассеянный склероз.",
    skills=[
        MedicalSkill("Неврологический осмотр", "Оценка рефлексов, чувствительности, когнитивных функций", "neurological_exam"),
        MedicalSkill("Анализ МРТ головного мозга", "Интерпретация МРТ снимков", "analyze_brain_mri"),
        MedicalSkill("Оценка инсульта (NIHSS)", "Шкала тяжести инсульта", "nihss_score"),
        MedicalSkill("Оценка когнитивных нарушений", "MMSE, MoCA тестирование", "cognitive_assessment"),
        MedicalSkill("Анализ ЭЭГ", "Расшифровка электроэнцефалограммы", "analyze_eeg"),
        MedicalSkill("Оценка боли", "Шкалы боли, дифференциальная диагностика", "pain_assessment"),
    ],
    related_icd_prefixes=["G20", "G35", "G40", "G43", "G47", "I60", "I63", "I64"],
    required_lab_tests=["crp", "glucose_fasting", "total_cholesterol"],
))

# ─────────────────────────────────────────────────
# 4. ПУЛЬМОНОЛОГИЯ / PULMONOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="pulmonologist",
    name_ru="Пульмонолог",
    name_en="Pulmonologist",
    description="Заболевания органов дыхания. ХОБЛ, астма, пневмония, "
                "интерстициальные заболевания лёгких, лёгочная гипертензия.",
    skills=[
        MedicalSkill("Анализ рентгена грудной клетки", "Интерпретация рентгенограммы", "analyze_chest_xray"),
        MedicalSkill("Анализ КТ лёгких", "Интерпретация КТ грудной клетки", "analyze_chest_ct"),
        MedicalSkill("Оценка спирометрии", "Интерпретация ФВД", "analyze_spirometry"),
        MedicalSkill("Оценка газов крови", "Анализ КЩС, газового состава", "blood_gas_analysis"),
        MedicalSkill("Ведение астмы", "Ступенчатая терапия по GINA", "asthma_management"),
        MedicalSkill("Ведение ХОБЛ", "Терапия по GOLD", "copd_management"),
    ],
    related_icd_prefixes=["J18", "J44", "J45", "J84", "J96"],
    required_lab_tests=["leukocytes", "crp", "d_dimer"],
))

# ─────────────────────────────────────────────────
# 5. ГАСТРОЭНТЕРОЛОГИЯ / GASTROENTEROLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="gastroenterologist",
    name_ru="Гастроэнтеролог",
    name_en="Gastroenterologist",
    description="Заболевания ЖКТ, печени, поджелудочной железы, желчевыводящих путей.",
    skills=[
        MedicalSkill("Оценка функций печени", "Интерпретация печёночных проб", "liver_function_assessment"),
        MedicalSkill("Диагностика ГЭРБ", "Оценка по шкале GERD-Q", "gerd_assessment"),
        MedicalSkill("Оценка риска кровотечения", "Шкалы Blatchford, Rockall", "gi_bleeding_risk"),
        MedicalSkill("Скрининг гепатитов", "Интерпретация маркеров гепатитов", "hepatitis_screening"),
        MedicalSkill("Диагностика ВЗК", "Болезнь Крона, НЯК — критерии диагноза", "ibd_assessment"),
        MedicalSkill("Анализ УЗИ брюшной полости", "Интерпретация УЗ-исследования", "analyze_abdominal_us"),
    ],
    related_icd_prefixes=["K21", "K25", "K29", "K50", "K51", "K70", "K73", "K80", "K85", "K86"],
    required_lab_tests=["alt", "ast", "total_bilirubin", "direct_bilirubin", "alkaline_phosphatase", "ggt", "albumin"],
))

# ─────────────────────────────────────────────────
# 6. ЭНДОКРИНОЛОГИЯ / ENDOCRINOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="endocrinologist",
    name_ru="Эндокринолог",
    name_en="Endocrinologist",
    description="Заболевания эндокринной системы. Сахарный диабет, заболевания щитовидной железы, "
                "ожирение, остеопороз, заболевания надпочечников.",
    skills=[
        MedicalSkill("Ведение сахарного диабета", "Подбор сахароснижающей терапии", "diabetes_management"),
        MedicalSkill("Оценка щитовидной железы", "Интерпретация ТТГ, Т3, Т4, УЗИ", "thyroid_assessment"),
        MedicalSkill("Расчёт инсулинотерапии", "Подбор дозы инсулина", "insulin_dosing"),
        MedicalSkill("Оценка ожирения", "ИМТ, метаболический синдром", "obesity_assessment"),
        MedicalSkill("Скрининг остеопороза", "FRAX, денситометрия", "osteoporosis_screening"),
        MedicalSkill("Анализ гормонального профиля", "Интерпретация гормонов", "hormone_analysis"),
    ],
    related_icd_prefixes=["E03", "E05", "E10", "E11", "E66", "E78", "M81"],
    required_lab_tests=["glucose_fasting", "hba1c", "tsh", "free_t4", "total_cholesterol", "calcium"],
))

# ─────────────────────────────────────────────────
# 7. НЕФРОЛОГИЯ / NEPHROLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="nephrologist",
    name_ru="Нефролог",
    name_en="Nephrologist",
    description="Заболевания почек. ХБП, гломерулонефрит, нефротический синдром, диализ.",
    skills=[
        MedicalSkill("Расчёт СКФ", "eGFR по CKD-EPI", "calculate_gfr"),
        MedicalSkill("Стадирование ХБП", "Классификация по KDIGO", "ckd_staging"),
        MedicalSkill("Анализ мочи", "Интерпретация ОАМ, суточной протеинурии", "urinalysis_interpretation"),
        MedicalSkill("Коррекция электролитов", "Расчёт коррекции Na, K, Ca", "electrolyte_correction"),
        MedicalSkill("Оценка необходимости диализа", "Показания к началу ЗПТ", "dialysis_assessment"),
    ],
    related_icd_prefixes=["N00", "N03", "N04", "N17", "N18", "N19"],
    required_lab_tests=["creatinine_male", "creatinine_female", "urea", "potassium", "sodium", "calcium", "phosphorus", "albumin"],
))

# ─────────────────────────────────────────────────
# 8. РЕВМАТОЛОГИЯ / RHEUMATOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="rheumatologist",
    name_ru="Ревматолог",
    name_en="Rheumatologist",
    description="Аутоиммунные и воспалительные заболевания. РА, СКВ, подагра, "
                "спондилоартриты, васкулиты.",
    skills=[
        MedicalSkill("Оценка активности РА", "DAS28, ACR/EULAR критерии", "ra_activity_score"),
        MedicalSkill("Диагностика СКВ", "SLICC критерии, индекс SLEDAI", "lupus_assessment"),
        MedicalSkill("Оценка подагры", "Критерии ACR/EULAR 2015", "gout_assessment"),
        MedicalSkill("Анализ иммунологии", "АНА, РФ, АЦЦП, комплемент", "immunology_analysis"),
        MedicalSkill("Подбор БМАРП", "Выбор базисной терапии", "dmard_selection"),
    ],
    related_icd_prefixes=["M05", "M06", "M10", "M15", "M32", "M34", "M45"],
    required_lab_tests=["crp", "esr_male", "esr_female", "uric_acid_male", "uric_acid_female"],
))

# ─────────────────────────────────────────────────
# 9. ОНКОЛОГИЯ / ONCOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="oncologist",
    name_ru="Онколог",
    name_en="Oncologist",
    description="Диагностика и лечение злокачественных новообразований. "
                "Стадирование, химиотерапия, таргетная терапия, иммунотерапия.",
    skills=[
        MedicalSkill("Скрининг онкозаболеваний", "Рекомендации по скринингу по возрасту", "cancer_screening"),
        MedicalSkill("Стадирование TNM", "Классификация по системе TNM", "tnm_staging"),
        MedicalSkill("Анализ онкомаркёров", "Интерпретация ПСА, РЭА, CA-125, AFP", "tumor_markers_analysis"),
        MedicalSkill("Оценка ECOG/Karnofsky", "Функциональный статус пациента", "performance_status"),
        MedicalSkill("Подбор химиотерапии", "Протоколы ХТ по типу опухоли", "chemo_protocol_selection"),
        MedicalSkill("Генетика опухоли", "Анализ мутаций, MSI, TMB", "tumor_genetics"),
        MedicalSkill("Анализ гистологии", "Интерпретация гистологического заключения", "histology_analysis"),
    ],
    related_icd_prefixes=["C" + str(i) for i in range(100)],
    required_lab_tests=["psa", "cea", "ca125", "ca199", "afp", "leukocytes", "hemoglobin_male", "hemoglobin_female", "platelets"],
))

# ─────────────────────────────────────────────────
# 10. ГЕМАТОЛОГИЯ / HEMATOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="hematologist",
    name_ru="Гематолог",
    name_en="Hematologist",
    description="Заболевания крови и кроветворных органов. Анемии, лейкозы, "
                "лимфомы, коагулопатии, тромбозы.",
    skills=[
        MedicalSkill("Расшифровка ОАК", "Детальный анализ гемограммы", "cbc_interpretation"),
        MedicalSkill("Дифференциальная диагностика анемии", "Классификация и диагностика анемий", "anemia_workup"),
        MedicalSkill("Оценка коагулограммы", "Интерпретация ПВ, МНО, АЧТВ, фибриноген", "coagulation_assessment"),
        MedicalSkill("Оценка риска тромбоза", "Шкалы Wells, Geneva", "thrombosis_risk"),
        MedicalSkill("Анализ мазка крови", "Описание морфологии клеток", "blood_smear_analysis"),
        MedicalSkill("Антикоагулянтная терапия", "Подбор и мониторинг антикоагулянтов", "anticoagulation_management"),
    ],
    related_icd_prefixes=["D50", "D56", "D59", "D60", "D64", "C81", "C82", "C83", "C91", "C92"],
    required_lab_tests=["hemoglobin_male", "hemoglobin_female", "erythrocytes_male", "leukocytes", "platelets",
                        "reticulocytes", "mcv", "mch", "mchc", "iron_male", "ferritin_male", "pt_time", "inr", "aptt", "fibrinogen"],
))

# ─────────────────────────────────────────────────
# 11. ДЕРМАТОЛОГИЯ / DERMATOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="dermatologist",
    name_ru="Дерматолог",
    name_en="Dermatologist",
    description="Заболевания кожи, волос и ногтей. Дерматиты, псориаз, "
                "меланома, акне, грибковые инфекции.",
    skills=[
        MedicalSkill("Анализ дерматоскопии", "Оценка пигментных образований по ABCDE", "dermoscopy_analysis"),
        MedicalSkill("Оценка меланомы", "Критерии ABCDE, шкала Breslow", "melanoma_assessment"),
        MedicalSkill("Ведение псориаза", "PASI, BSA, выбор терапии", "psoriasis_management"),
        MedicalSkill("Ведение атопического дерматита", "SCORAD, выбор терапии", "atopic_dermatitis_management"),
        MedicalSkill("Анализ кожных поражений", "Описание элементов сыпи, дифференциальная диагностика", "skin_lesion_analysis"),
        MedicalSkill("Анализ фото кожи", "Оценка изображения кожного поражения", "analyze_skin_image"),
    ],
    related_icd_prefixes=["L20", "L23", "L40", "L50", "L70", "L80", "C43", "C44", "B35", "B36"],
    required_lab_tests=["leukocytes", "eosinophils", "crp"],
))

# ─────────────────────────────────────────────────
# 12. ОФТАЛЬМОЛОГИЯ / OPHTHALMOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="ophthalmologist",
    name_ru="Офтальмолог",
    name_en="Ophthalmologist",
    description="Заболевания глаз. Катаракта, глаукома, возрастная макулодистрофия, "
                "диабетическая ретинопатия.",
    skills=[
        MedicalSkill("Анализ глазного дна", "Оценка фундоскопии", "fundoscopy_analysis"),
        MedicalSkill("Скрининг глаукомы", "Оценка ВГД, полей зрения", "glaucoma_screening"),
        MedicalSkill("Оценка диабетической ретинопатии", "Стадирование по ETDRS", "diabetic_retinopathy"),
        MedicalSkill("Анализ ОКТ", "Интерпретация оптической когерентной томографии", "oct_analysis"),
        MedicalSkill("Оценка остроты зрения", "Рефракция, коррекция", "visual_acuity"),
    ],
    related_icd_prefixes=["H25", "H26", "H35", "H40"],
    required_lab_tests=["glucose_fasting", "hba1c"],
))

# ─────────────────────────────────────────────────
# 13. ОТОРИНОЛАРИНГОЛОГИЯ / ENT
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="ent",
    name_ru="ЛОР (оториноларинголог)",
    name_en="Otorhinolaryngologist (ENT)",
    description="Заболевания уха, горла, носа. Синуситы, отиты, тонзиллит, "
                "нарушения слуха, апноэ во сне.",
    skills=[
        MedicalSkill("Оценка слуха", "Аудиометрия, камертональные пробы", "hearing_assessment"),
        MedicalSkill("Диагностика синусита", "Критерии, дифференциальная диагностика", "sinusitis_assessment"),
        MedicalSkill("Оценка апноэ во сне", "Шкала Epworth, STOP-Bang", "sleep_apnea_assessment"),
        MedicalSkill("Осмотр ЛОР-органов", "Описание отоскопии, риноскопии, фарингоскопии", "ent_examination"),
    ],
    related_icd_prefixes=["H60", "H65", "H66", "J01", "J02", "J03", "J32", "J35", "G47.3"],
    required_lab_tests=["leukocytes", "crp"],
))

# ─────────────────────────────────────────────────
# 14. УРОЛОГИЯ / UROLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="urologist",
    name_ru="Уролог",
    name_en="Urologist",
    description="Заболевания мочевыводящих путей и мужской репродуктивной системы. "
                "МКБ, ДГПЖ, простатит, инфекции мочевых путей.",
    skills=[
        MedicalSkill("Оценка ДГПЖ", "Шкала IPSS, выбор терапии", "bph_assessment"),
        MedicalSkill("Скрининг рака простаты", "Интерпретация ПСА, PIRADS", "prostate_cancer_screening"),
        MedicalSkill("Диагностика МКБ", "Оценка состава камней, метафилактика", "urolithiasis_assessment"),
        MedicalSkill("Анализ урофлоуметрии", "Интерпретация потока мочи", "uroflowmetry_analysis"),
        MedicalSkill("Ведение ИМП", "Диагностика и лечение инфекций мочевых путей", "uti_management"),
    ],
    related_icd_prefixes=["N20", "N40", "N41", "N30", "C61"],
    required_lab_tests=["creatinine_male", "urea", "psa"],
))

# ─────────────────────────────────────────────────
# 15. ГИНЕКОЛОГИЯ / GYNECOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="gynecologist",
    name_ru="Гинеколог",
    name_en="Gynecologist",
    description="Женская репродуктивная система. Нарушения менструального цикла, "
                "миома, эндометриоз, бесплодие, ведение беременности.",
    skills=[
        MedicalSkill("Ведение беременности", "Мониторинг по триместрам, скрининги", "pregnancy_management"),
        MedicalSkill("Скрининг рака шейки матки", "Интерпретация ПАП-теста, ВПЧ", "cervical_cancer_screening"),
        MedicalSkill("Оценка гормонального статуса", "Анализ половых гормонов", "reproductive_hormones"),
        MedicalSkill("Ведение менопаузы", "МГТ, оценка рисков", "menopause_management"),
        MedicalSkill("Диагностика эндометриоза", "Критерии, стадирование", "endometriosis_assessment"),
        MedicalSkill("Анализ УЗИ малого таза", "Интерпретация гинекологического УЗИ", "pelvic_ultrasound_analysis"),
    ],
    related_icd_prefixes=["N80", "N84", "N85", "N91", "N92", "N97", "C53", "C54", "O"],
    required_lab_tests=["hemoglobin_female", "ferritin_female", "tsh"],
))

# ─────────────────────────────────────────────────
# 16. ПЕДИАТРИЯ / PEDIATRICS
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="pediatrician",
    name_ru="Педиатр",
    name_en="Pediatrician",
    description="Здоровье детей от рождения до 18 лет. Развитие, "
                "вакцинация, детские инфекции, педиатрическая фармакология.",
    skills=[
        MedicalSkill("Оценка развития ребёнка", "Центили роста/веса, нервно-психическое развитие", "child_development"),
        MedicalSkill("Календарь вакцинации", "Рекомендации по прививкам по возрасту", "vaccination_schedule"),
        MedicalSkill("Педиатрические дозировки", "Расчёт дозы по весу/возрасту", "pediatric_dosing"),
        MedicalSkill("Оценка обезвоживания", "Шкалы дегидратации у детей", "dehydration_assessment"),
        MedicalSkill("Детские инфекции", "Диагностика и лечение детских инфекций", "pediatric_infections"),
        MedicalSkill("Неонатальный скрининг", "Оценка результатов неонатального скрининга", "neonatal_screening"),
    ],
    related_icd_prefixes=["P", "Q", "J06", "J18", "A08", "B05", "B06", "B26"],
    required_lab_tests=["leukocytes", "hemoglobin_female", "crp"],
))

# ─────────────────────────────────────────────────
# 17. ПСИХИАТРИЯ / PSYCHIATRY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="psychiatrist",
    name_ru="Психиатр",
    name_en="Psychiatrist",
    description="Психические расстройства. Депрессия, тревожные расстройства, "
                "шизофрения, биполярное расстройство, СДВГ.",
    skills=[
        MedicalSkill("Оценка депрессии", "PHQ-9, шкала Бека", "depression_assessment"),
        MedicalSkill("Оценка тревожности", "GAD-7, шкала Гамильтона", "anxiety_assessment"),
        MedicalSkill("Оценка суицидального риска", "Columbia Protocol, SAD PERSONS", "suicide_risk_assessment"),
        MedicalSkill("Подбор антидепрессантов", "Выбор СИОЗС/СИОЗСН по профилю", "antidepressant_selection"),
        MedicalSkill("Оценка когнитивных функций", "MoCA, MMSE", "cognitive_screening"),
        MedicalSkill("Скрининг СДВГ", "Шкала ASRS", "adhd_screening"),
    ],
    related_icd_prefixes=["F20", "F31", "F32", "F33", "F40", "F41", "F42", "F43", "F90"],
    required_lab_tests=["tsh", "glucose_fasting", "hemoglobin_male", "hemoglobin_female"],
))

# ─────────────────────────────────────────────────
# 18. ТРАВМАТОЛОГИЯ И ОРТОПЕДИЯ / ORTHOPEDICS
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="orthopedist",
    name_ru="Травматолог-ортопед",
    name_en="Orthopedic Surgeon / Traumatologist",
    description="Травмы и заболевания опорно-двигательного аппарата. "
                "Переломы, артрозы, остеопороз, спортивные травмы.",
    skills=[
        MedicalSkill("Анализ рентгена костей", "Интерпретация рентгенограммы ОДА", "bone_xray_analysis"),
        MedicalSkill("Классификация переломов", "AO/OTA классификация", "fracture_classification"),
        MedicalSkill("Оценка остеоартроза", "Шкала Kellgren-Lawrence", "osteoarthritis_grading"),
        MedicalSkill("Оценка остеопороза", "T-score, FRAX", "osteoporosis_assessment"),
        MedicalSkill("Оценка функции суставов", "ROM, функциональные шкалы", "joint_function_assessment"),
        MedicalSkill("Анализ МРТ суставов", "Интерпретация МРТ коленного, плечевого суставов", "joint_mri_analysis"),
    ],
    related_icd_prefixes=["M15", "M16", "M17", "M54", "M75", "M81", "S"],
    required_lab_tests=["calcium", "phosphorus", "alkaline_phosphatase", "crp"],
))

# ─────────────────────────────────────────────────
# 19. ХИРУРГИЯ / SURGERY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="surgeon",
    name_ru="Хирург",
    name_en="Surgeon",
    description="Хирургическое лечение. Аппендицит, грыжи, холецистит, "
                "предоперационная оценка, послеоперационное ведение.",
    skills=[
        MedicalSkill("Предоперационная оценка", "ASA, Lee Cardiac Risk Index", "preoperative_assessment"),
        MedicalSkill("Оценка острого живота", "Шкалы Alvarado, RIPASA", "acute_abdomen_assessment"),
        MedicalSkill("Послеоперационный мониторинг", "Контроль осложнений, Clavien-Dindo", "postop_monitoring"),
        MedicalSkill("Оценка раны", "Классификация, тактика ведения", "wound_assessment"),
        MedicalSkill("Хирургический чек-лист", "WHO Surgical Safety Checklist", "surgical_checklist"),
    ],
    related_icd_prefixes=["K35", "K40", "K41", "K80", "K81"],
    required_lab_tests=["hemoglobin_male", "hemoglobin_female", "leukocytes", "platelets", "pt_time", "inr", "aptt", "creatinine_male"],
))

# ─────────────────────────────────────────────────
# 20. АЛЛЕРГОЛОГИЯ-ИММУНОЛОГИЯ / ALLERGY & IMMUNOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="allergist",
    name_ru="Аллерголог-иммунолог",
    name_en="Allergist-Immunologist",
    description="Аллергические и иммунодефицитные состояния. "
                "Анафилаксия, бронхиальная астма, пищевая аллергия, иммунодефициты.",
    skills=[
        MedicalSkill("Оценка аллергии", "Диагностика по анамнезу и обследованию", "allergy_assessment"),
        MedicalSkill("Анализ IgE", "Интерпретация общего и специфического IgE", "ige_analysis"),
        MedicalSkill("Ведение анафилаксии", "Алгоритм экстренной помощи", "anaphylaxis_management"),
        MedicalSkill("Подбор АСИТ", "Аллерген-специфическая иммунотерапия", "asit_selection"),
        MedicalSkill("Оценка иммунного статуса", "Иммунограмма, субпопуляции", "immune_status"),
    ],
    related_icd_prefixes=["J45", "L20", "L23", "T78", "D80", "D83", "D84"],
    required_lab_tests=["eosinophils", "leukocytes", "crp"],
))

# ─────────────────────────────────────────────────
# 21. ИНФЕКЦИОННЫЕ БОЛЕЗНИ / INFECTIOUS DISEASES
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="infectionist",
    name_ru="Инфекционист",
    name_en="Infectious Disease Specialist",
    description="Инфекционные заболевания. ВИЧ, гепатиты, туберкулёз, "
                "тропические инфекции, антибиотикотерапия.",
    skills=[
        MedicalSkill("Подбор антибиотиков", "Эмпирическая и целенаправленная АБТ", "antibiotic_selection"),
        MedicalSkill("Ведение ВИЧ", "АРТ, мониторинг CD4, вирусной нагрузки", "hiv_management"),
        MedicalSkill("Ведение гепатитов", "Лечение HBV, HCV", "hepatitis_management"),
        MedicalSkill("Оценка сепсиса", "qSOFA, SOFA", "sepsis_assessment"),
        MedicalSkill("Интерпретация посевов", "Чувствительность к антибиотикам", "culture_interpretation"),
        MedicalSkill("Вакцинопрофилактика", "Рекомендации по вакцинации взрослых", "adult_vaccination"),
    ],
    related_icd_prefixes=["A", "B"],
    required_lab_tests=["leukocytes", "neutrophils", "lymphocytes", "crp", "alt", "ast"],
))

# ─────────────────────────────────────────────────
# 22. КАРДИОХИРУРГИЯ / CARDIAC SURGERY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="cardiac_surgeon",
    name_ru="Кардиохирург",
    name_en="Cardiac Surgeon",
    description="Хирургическое лечение заболеваний сердца. АКШ, протезирование клапанов, "
                "коррекция врождённых пороков.",
    skills=[
        MedicalSkill("Оценка показаний к АКШ", "SYNTAX Score, критерии реваскуляризации", "cabg_assessment"),
        MedicalSkill("Оценка клапанных пороков", "Стадирование стеноза/недостаточности", "valve_assessment"),
        MedicalSkill("Хирургический риск", "EuroSCORE II, STS Score", "surgical_risk_score"),
        MedicalSkill("Послеоперационное ведение", "Мониторинг после кардиохирургии", "postop_cardiac_care"),
    ],
    related_icd_prefixes=["I05", "I06", "I07", "I08", "I20", "I21", "I25", "Q20", "Q21"],
    required_lab_tests=["hemoglobin_male", "platelets", "inr", "creatinine_male", "d_dimer"],
))

# ─────────────────────────────────────────────────
# 23. НЕЙРОХИРУРГИЯ / NEUROSURGERY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="neurosurgeon",
    name_ru="Нейрохирург",
    name_en="Neurosurgeon",
    description="Хирургия ЦНС и периферических нервов. Опухоли мозга, "
                "грыжи дисков, гидроцефалия, черепно-мозговые травмы.",
    skills=[
        MedicalSkill("Анализ КТ/МРТ головного мозга", "Хирургическая оценка нейровизуализации", "neuro_imaging_surgical"),
        MedicalSkill("Оценка ЧМТ", "GCS, Marshall CT classification", "tbi_assessment"),
        MedicalSkill("Оценка спинальной патологии", "Показания к операции на позвоночнике", "spinal_surgery_assessment"),
        MedicalSkill("Оценка опухоли мозга", "WHO grading, локализация, резектабельность", "brain_tumor_assessment"),
    ],
    related_icd_prefixes=["C71", "G91", "M50", "M51", "S06"],
    required_lab_tests=["hemoglobin_male", "platelets", "inr", "sodium"],
))

# ─────────────────────────────────────────────────
# 24. АНГИОЛОГИЯ / VASCULAR SURGERY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="vascular_surgeon",
    name_ru="Сосудистый хирург (ангиолог)",
    name_en="Vascular Surgeon",
    description="Заболевания сосудов. Атеросклероз, аневризмы, тромбозы, "
                "варикозная болезнь, диабетическая стопа.",
    skills=[
        MedicalSkill("Оценка ЛПИ", "Лодыжечно-плечевой индекс", "ankle_brachial_index"),
        MedicalSkill("Оценка аневризмы аорты", "Критерии наблюдения/операции", "aortic_aneurysm_assessment"),
        MedicalSkill("Оценка варикозной болезни", "CEAP классификация", "varicose_veins_assessment"),
        MedicalSkill("Диабетическая стопа", "Wagner, UT классификация", "diabetic_foot_assessment"),
        MedicalSkill("Анализ УЗДГ сосудов", "Интерпретация дуплексного сканирования", "vascular_ultrasound"),
    ],
    related_icd_prefixes=["I70", "I71", "I73", "I80", "I83"],
    required_lab_tests=["total_cholesterol", "ldl", "hba1c", "d_dimer", "fibrinogen"],
))

# ─────────────────────────────────────────────────
# 25. АНЕСТЕЗИОЛОГИЯ И РЕАНИМАТОЛОГИЯ / ICU
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="intensivist",
    name_ru="Реаниматолог (анестезиолог)",
    name_en="Intensivist / Anesthesiologist",
    description="Интенсивная терапия и анестезиология. Критические состояния, "
                "ИВЛ, сепсис, шок, полиорганная недостаточность.",
    skills=[
        MedicalSkill("Оценка APACHE II/SOFA", "Прогноз тяжести в ОРИТ", "icu_severity_score"),
        MedicalSkill("Параметры ИВЛ", "Расчёт параметров вентиляции", "ventilator_settings"),
        MedicalSkill("Инфузионная терапия", "Расчёт объёма, состава инфузии", "fluid_management"),
        MedicalSkill("Вазопрессорная поддержка", "Выбор и титрование вазопрессоров", "vasopressor_management"),
        MedicalSkill("Анализ КЩС", "Интерпретация газов крови и КЩС", "abg_analysis"),
        MedicalSkill("Оценка боли/седации", "RASS, BPS, CPOT", "sedation_assessment"),
    ],
    related_icd_prefixes=["R57", "A41", "J96", "N17"],
    required_lab_tests=["sodium", "potassium", "chloride", "creatinine_male", "hemoglobin_male", "platelets", "inr", "d_dimer"],
))

# ─────────────────────────────────────────────────
# 26. РАДИОЛОГИЯ / RADIOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="radiologist",
    name_ru="Радиолог (лучевая диагностика)",
    name_en="Radiologist",
    description="Лучевая диагностика. Интерпретация КТ, МРТ, рентген, "
                "УЗИ, маммография, ПЭТ-КТ.",
    skills=[
        MedicalSkill("Анализ рентгена", "Интерпретация рентгенограмм любой локализации", "xray_analysis"),
        MedicalSkill("Анализ КТ", "Интерпретация компьютерной томографии", "ct_analysis"),
        MedicalSkill("Анализ МРТ", "Интерпретация магнитно-резонансной томографии", "mri_analysis"),
        MedicalSkill("Анализ маммограммы", "BI-RADS классификация", "mammography_analysis"),
        MedicalSkill("Анализ УЗИ", "Интерпретация ультразвукового исследования", "ultrasound_analysis"),
        MedicalSkill("Описание DICOM", "Структурированное описание исследования", "structured_report"),
    ],
    related_icd_prefixes=[],
    required_lab_tests=[],
))

# ─────────────────────────────────────────────────
# 27. ПАТОЛОГИЧЕСКАЯ АНАТОМИЯ / PATHOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="pathologist",
    name_ru="Патологоанатом (патоморфолог)",
    name_en="Pathologist",
    description="Гистологическая и цитологическая диагностика. "
                "Биопсии, операционный материал, аутопсия.",
    skills=[
        MedicalSkill("Анализ гистологии", "Описание микропрепаратов", "histopathology_analysis"),
        MedicalSkill("Анализ цитологии", "Интерпретация цитологических препаратов", "cytology_analysis"),
        MedicalSkill("Иммуногистохимия", "Интерпретация ИГХ маркёров", "ihc_interpretation"),
        MedicalSkill("Классификация опухолей", "WHO classification of tumours", "tumor_classification"),
        MedicalSkill("Анализ микропрепарата", "Оценка изображения микропрепарата", "analyze_histology_image"),
    ],
    related_icd_prefixes=["C", "D"],
    required_lab_tests=[],
))

# ─────────────────────────────────────────────────
# 28. КЛИНИЧЕСКАЯ ФАРМАКОЛОГИЯ / PHARMACOLOGY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="pharmacologist",
    name_ru="Клинический фармаколог",
    name_en="Clinical Pharmacologist",
    description="Рациональная фармакотерапия. Лекарственные взаимодействия, "
                "побочные эффекты, фармакогенетика, дозирование.",
    skills=[
        MedicalSkill("Проверка взаимодействий", "Drug-drug interactions", "check_interactions"),
        MedicalSkill("Подбор дозировки", "Коррекция по возрасту, почкам, печени", "dose_adjustment"),
        MedicalSkill("Фармакогенетика", "Анализ CYP450, фармакогеномика", "pharmacogenetics"),
        MedicalSkill("Анализ побочных эффектов", "Оценка НЯ, шкала Naranjo", "adverse_effect_analysis"),
        MedicalSkill("Терапевтический мониторинг", "TDM — контроль концентраций", "therapeutic_monitoring"),
        MedicalSkill("Информация о препарате", "Полная информация из FDA/RxNorm", "drug_info_lookup"),
    ],
    related_icd_prefixes=["T36", "T37", "T38", "T39", "T40", "T41", "T42", "T43", "T44", "T45", "T46", "T47", "T48", "T49", "T50", "Y40", "Y41", "Y42", "Y43", "Y44", "Y45", "Y46", "Y47", "Y48", "Y49", "Y50", "Y51", "Y52", "Y53", "Y54", "Y55", "Y56", "Y57"],
    required_lab_tests=["creatinine_male", "creatinine_female", "alt", "ast", "albumin"],
))

# ─────────────────────────────────────────────────
# 29. РЕАБИЛИТОЛОГИЯ / REHABILITATION
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="rehabilitation",
    name_ru="Реабилитолог",
    name_en="Rehabilitation Specialist",
    description="Медицинская реабилитация. После инсульта, травм, операций, "
                "кардиореабилитация, ЛФК.",
    skills=[
        MedicalSkill("Оценка функционального статуса", "Индекс Бартела, FIM", "functional_status"),
        MedicalSkill("Программа реабилитации", "Составление индивидуального плана", "rehab_program"),
        MedicalSkill("Кардиореабилитация", "Программа после ОКС/АКШ", "cardiac_rehab"),
        MedicalSkill("Нейрореабилитация", "Программа после инсульта", "neuro_rehab"),
        MedicalSkill("Оценка боли и подвижности", "VAS, ROM, мышечная сила", "mobility_assessment"),
    ],
    related_icd_prefixes=["Z50"],
    required_lab_tests=[],
))

# ─────────────────────────────────────────────────
# 30. ГЕНЕТИКА / GENETICS
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="geneticist",
    name_ru="Генетик",
    name_en="Medical Geneticist",
    description="Наследственные заболевания. Генетическое консультирование, "
                "пренатальная диагностика, орфанные заболевания.",
    skills=[
        MedicalSkill("Генетическое консультирование", "Оценка наследственного риска", "genetic_counseling"),
        MedicalSkill("Анализ кариотипа", "Интерпретация хромосомного анализа", "karyotype_analysis"),
        MedicalSkill("Пренатальный скрининг", "Интерпретация скрининга 1-2 триместра", "prenatal_screening"),
        MedicalSkill("Поиск по OMIM", "Поиск генетических заболеваний", "omim_search"),
        MedicalSkill("Анализ генетических вариантов", "Интерпретация NGS результатов", "variant_interpretation"),
    ],
    related_icd_prefixes=["Q"],
    required_lab_tests=[],
))

# ─────────────────────────────────────────────────
# 31. СТОМАТОЛОГИЯ / DENTISTRY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="dentist",
    name_ru="Стоматолог",
    name_en="Dentist",
    description="Заболевания полости рта. Кариес, пародонтит, "
                "ортодонтия, имплантация, хирургическая стоматология.",
    skills=[
        MedicalSkill("Стоматологический осмотр", "Оценка стоматологического статуса", "dental_examination"),
        MedicalSkill("Анализ ортопантомограммы", "Интерпретация ОПТГ", "panoramic_xray_analysis"),
        MedicalSkill("Оценка пародонта", "PSI, глубина карманов", "periodontal_assessment"),
        MedicalSkill("План лечения", "Комплексный план стоматологического лечения", "dental_treatment_plan"),
    ],
    related_icd_prefixes=["K00", "K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08"],
    required_lab_tests=["glucose_fasting", "inr"],
))

# ─────────────────────────────────────────────────
# 32. ДИЕТОЛОГИЯ / NUTRITION
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="nutritionist",
    name_ru="Диетолог",
    name_en="Nutritionist / Dietitian",
    description="Лечебное питание. Диетотерапия при хронических заболеваниях, "
                "ожирение, нарушения пищевого поведения, нутритивная поддержка.",
    skills=[
        MedicalSkill("Расчёт нутритивного статуса", "BMI, NRS-2002, MNA", "nutritional_status"),
        MedicalSkill("Расчёт калоража", "Потребности в калориях и макронутриентах", "calorie_calculation"),
        MedicalSkill("Диета при диабете", "План питания при СД", "diabetic_diet"),
        MedicalSkill("Диета при ХБП", "Ограничение белка, калия, фосфора", "renal_diet"),
        MedicalSkill("Безглютеновая диета", "План питания при целиакии", "gluten_free_diet"),
        MedicalSkill("Нутритивная поддержка", "Энтеральное/парентеральное питание", "nutritional_support"),
    ],
    related_icd_prefixes=["E40", "E41", "E43", "E44", "E46", "E66", "K90"],
    required_lab_tests=["total_protein", "albumin", "glucose_fasting", "total_cholesterol", "triglycerides", "iron_male", "ferritin_male"],
))

# ─────────────────────────────────────────────────
# 33. СПОРТИВНАЯ МЕДИЦИНА / SPORTS MEDICINE
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="sports_medicine",
    name_ru="Спортивный врач",
    name_en="Sports Medicine Specialist",
    description="Медицина спорта и физической активности. Допуск к занятиям, "
                "спортивные травмы, восстановление, допинг-контроль.",
    skills=[
        MedicalSkill("Допуск к спорту", "Предспортивный скрининг", "sports_clearance"),
        MedicalSkill("Оценка спортивной травмы", "Диагностика повреждений связок/мышц", "sports_injury_assessment"),
        MedicalSkill("Программа возвращения к спорту", "Return-to-play протокол", "return_to_play"),
        MedicalSkill("Оценка перетренированности", "Признаки перетренированности", "overtraining_assessment"),
    ],
    related_icd_prefixes=["S", "M"],
    required_lab_tests=["hemoglobin_male", "hemoglobin_female", "ferritin_male", "crp"],
))

# ─────────────────────────────────────────────────
# 34. ГЕРИАТРИЯ / GERIATRICS
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="geriatrician",
    name_ru="Гериатр",
    name_en="Geriatrician",
    description="Здоровье пожилых людей. Полипрагмазия, падения, деменция, "
                "саркопения, паллиативная помощь.",
    skills=[
        MedicalSkill("Комплексная гериатрическая оценка", "CGA, индекс старческой астении", "geriatric_assessment"),
        MedicalSkill("Оценка риска падений", "Morse Fall Scale, Timed Up and Go", "fall_risk_assessment"),
        MedicalSkill("Деполипрагмазия", "Критерии Beers, STOPP/START", "deprescribing"),
        MedicalSkill("Оценка деменции", "Стадирование, поведенческие нарушения", "dementia_assessment"),
        MedicalSkill("Паллиативная помощь", "Оценка симптомов, план помощи", "palliative_care"),
    ],
    related_icd_prefixes=["F00", "F01", "F03", "R54", "W"],
    required_lab_tests=["creatinine_male", "creatinine_female", "hemoglobin_male", "hemoglobin_female", "albumin", "calcium", "tsh"],
))

# ─────────────────────────────────────────────────
# 35. МЕДИЦИНА НЕОТЛОЖНЫХ СОСТОЯНИЙ / EMERGENCY
# ─────────────────────────────────────────────────
_reg(Specialization(
    id="emergency",
    name_ru="Врач скорой помощи",
    name_en="Emergency Medicine Physician",
    description="Экстренная медицинская помощь. Травмы, ОКС, инсульт, "
                "анафилаксия, отравления, реанимация.",
    skills=[
        MedicalSkill("Первичная сортировка (триаж)", "ESI, Manchester Triage", "triage"),
        MedicalSkill("ABCDE-оценка", "Первичный осмотр при неотложном состоянии", "abcde_assessment"),
        MedicalSkill("Алгоритм ACLS", "Расширенная сердечно-лёгочная реанимация", "acls_algorithm"),
        MedicalSkill("Оценка травмы (ATLS)", "Протокол ATLS", "trauma_assessment"),
        MedicalSkill("Ведение отравлений", "Антидоты, детоксикация", "toxicology_management"),
        MedicalSkill("Оценка ОКС", "HEART score, TIMI, GRACE", "acs_assessment"),
    ],
    related_icd_prefixes=["R", "S", "T", "I21", "I63"],
    required_lab_tests=["hemoglobin_male", "leukocytes", "creatinine_male", "potassium", "glucose_fasting", "d_dimer", "inr"],
))


def get_specialization(spec_id: str) -> Specialization | None:
    return SPECIALIZATIONS.get(spec_id)


def list_specializations() -> list[dict]:
    return [
        {"id": s.id, "name_ru": s.name_ru, "name_en": s.name_en, "description": s.description}
        for s in SPECIALIZATIONS.values()
    ]


def find_specialist_for_icd(icd_code: str) -> list[str]:
    """Find which specialists handle a given ICD code."""
    results = []
    for spec_id, spec in SPECIALIZATIONS.items():
        for prefix in spec.related_icd_prefixes:
            if icd_code.startswith(prefix):
                results.append(spec_id)
                break
    return results
