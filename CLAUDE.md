# Aibolit — AI Medical Clinic / Виртуальная AI-клиника

## Обзор системы

**Aibolit** — это агентская система виртуальной медицинской клиники с AI-докторами
по 35 медицинским специализациям. Система работает как MCP-сервер, интегрируемый
в Claude.ai и Claude Code.

## Как работать с клиникой

### Быстрый старт для пациента

1. **Обратиться на ресепшн**: Опишите свои жалобы — система подберёт специалиста
2. **Консультация у врача**: AI-врач соберёт анамнез, проведёт осмотр, поставит диагноз
3. **Анализы**: Система расшифрует результаты лабораторных исследований
4. **Лечение**: Получите персонализированные рекомендации по лечению

### Доступные инструменты (MCP Tools)

#### Навигация по клинике
- `clinic_reception` — Ресепшн: помогает выбрать специалиста по жалобам
- `list_doctors` — Список всех 35 AI-врачей с навыками
- `consult_doctor` — Консультация у специалиста

#### Диагностика
- `analyze_lab_results` — Расшифровка анализов (ОАК, биохимия, гормоны, онкомаркёры)
- `assess_vitals` — Оценка витальных показателей (АД, пульс, SpO2, температура)
- `calculate_gfr` — Расчёт СКФ и стадии ХБП
- `cardiovascular_risk` — Оценка сердечно-сосудистого риска

#### Лекарства и взаимодействия
- `drug_info` — Информация о препарате (FDA)
- `check_drug_interactions` — Проверка лекарственных взаимодействий
- `drug_adverse_events` — Побочные эффекты (FDA FAERS)
- `check_drug_recall` — Отзывы препаратов

#### Медицинские исследования
- `search_medical_literature` — Поиск в PubMed
- `get_article_abstract` — Абстракт статьи
- `search_clinical_trials` — Клинические исследования (ClinicalTrials.gov)

#### Классификация
- `search_icd` — Поиск кодов МКБ-10/11
- `search_snomed` — Поиск в SNOMED CT

#### Генетика
- `gene_info` — Информация о гене (NCBI)
- `search_genetic_disorders` — Поиск в OMIM
- `search_drug_targets` — Мишени терапии (Open Targets)

#### Документация
- `generate_medical_record` — Медицинская карта
- `generate_referral` — Направление к специалисту
- `generate_prescription` — Лист назначений
- `generate_discharge_summary` — Выписной эпикриз

#### Управление пациентами
- `register_patient` — Регистрация пациента
- `get_patient` — Получить карту пациента
- `list_patients` — Список пациентов
- `add_vitals` — Записать витальные показатели
- `add_lab_result` — Добавить результат анализа
- `add_diagnosis` — Добавить диагноз
- `add_medication` — Назначить лекарство
- `lab_reference_ranges` — Справочник норм

## 35 Специализаций врачей

| # | Специализация | ID |
|---|---|---|
| 1 | Терапевт | `therapist` |
| 2 | Кардиолог | `cardiologist` |
| 3 | Невролог | `neurologist` |
| 4 | Пульмонолог | `pulmonologist` |
| 5 | Гастроэнтеролог | `gastroenterologist` |
| 6 | Эндокринолог | `endocrinologist` |
| 7 | Нефролог | `nephrologist` |
| 8 | Ревматолог | `rheumatologist` |
| 9 | Онколог | `oncologist` |
| 10 | Гематолог | `hematologist` |
| 11 | Дерматолог | `dermatologist` |
| 12 | Офтальмолог | `ophthalmologist` |
| 13 | ЛОР | `ent` |
| 14 | Уролог | `urologist` |
| 15 | Гинеколог | `gynecologist` |
| 16 | Педиатр | `pediatrician` |
| 17 | Психиатр | `psychiatrist` |
| 18 | Травматолог-ортопед | `orthopedist` |
| 19 | Хирург | `surgeon` |
| 20 | Аллерголог-иммунолог | `allergist` |
| 21 | Инфекционист | `infectionist` |
| 22 | Кардиохирург | `cardiac_surgeon` |
| 23 | Нейрохирург | `neurosurgeon` |
| 24 | Сосудистый хирург | `vascular_surgeon` |
| 25 | Реаниматолог | `intensivist` |
| 26 | Радиолог | `radiologist` |
| 27 | Патологоанатом | `pathologist` |
| 28 | Клинический фармаколог | `pharmacologist` |
| 29 | Реабилитолог | `rehabilitation` |
| 30 | Генетик | `geneticist` |
| 31 | Стоматолог | `dentist` |
| 32 | Диетолог | `nutritionist` |
| 33 | Спортивный врач | `sports_medicine` |
| 34 | Гериатр | `geriatrician` |
| 35 | Врач скорой помощи | `emergency` |

## Внешние интеграции (бесплатные API)

| Источник | Назначение |
|---|---|
| **PubMed / NCBI** | Медицинская литература, доказательная медицина |
| **OpenFDA** | Информация о лекарствах, побочные эффекты, отзывы |
| **RxNorm (NLM)** | Нормализация названий лекарств, взаимодействия |
| **WHO ICD-11** | Классификация болезней |
| **SNOMED CT** | Клиническая терминология |
| **ClinicalTrials.gov** | Клинические исследования |
| **NCBI Gene** | Генетическая информация |
| **OMIM** | Наследственные заболевания |
| **Open Targets** | Лекарственные мишени |

## Архитектура

```
aibolit-clinic/
├── src/
│   ├── mcp_server.py          # Главный MCP-сервер (точка входа)
│   ├── agents/
│   │   └── specializations.py # 35 специализаций с навыками
│   ├── tools/
│   │   ├── diagnostic.py      # Диагностические инструменты
│   │   └── documentation.py   # Генерация медицинских документов
│   ├── integrations/
│   │   ├── pubmed.py          # PubMed/NCBI API
│   │   ├── openfda.py         # OpenFDA API
│   │   ├── who_icd.py         # WHO ICD-11 API
│   │   └── medical_apis.py    # RxNorm, SNOMED, OMIM, Open Targets, Gene
│   ├── models/
│   │   ├── patient.py         # Модели данных пациентов
│   │   └── medical_refs.py    # Референсные значения, МКБ-10, взаимодействия
│   └── utils/
│       └── patient_db.py      # JSON-хранилище пациентов
├── config/
│   └── claude_mcp_config.json # Конфигурация MCP для Claude
└── data/
    └── patients/              # Данные пациентов (JSON)
```

## Disclaimer / Отказ от ответственности

⚠️ **Aibolit — это информационная система. Она НЕ заменяет консультацию
реального врача.** Все диагнозы, назначения и рекомендации AI-системы
требуют верификации квалифицированным медицинским специалистом.
Не принимайте медицинских решений исключительно на основе рекомендаций AI.
