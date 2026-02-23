# Skill: Medical Knowledge Base

> RAG для медицинских знаний: векторные БД, клинические рекомендации, retrieval

## Назначение

Построение и поддержка базы медицинских знаний для AI-агентов Aibolit AI: индексация клинических рекомендаций, retrieval с учётом медицинской специфики, управление коллекциями.

---

## Использование

| Агент | Применение |
|-------|-----------|
| AI-Agents | Проектирование RAG pipeline, выбор embedding |
| Medical-Domain | Верификация и курация источников |
| Coder | Реализация RAG компонентов |
| Research | Поиск и подготовка медицинских источников |

---

## Архитектура RAG

### Компоненты

```yaml
Ingestion Pipeline:
  1. Document Loader:
     - PDF (клинические рекомендации Минздрав)
     - JSON (PubMed abstracts)
     - HTML (MedlinePlus, WHO)
     - FHIR Bundle (структурированные данные)

  2. Preprocessor:
     - Очистка текста (удаление headers/footers/watermarks)
     - Извлечение таблиц и структурированных данных
     - Определение языка (RU/EN)
     - Нормализация медицинских терминов

  3. Chunker:
     - По семантическим блокам (не по символам)
     - Сохранение контекста (overlap)
     - Метаданные для каждого chunk

  4. Embedder:
     - Модель: sentence-transformers/all-MiniLM-L6-v2 (общий)
     - Или: pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb (медицинский)
     - Размерность: 384-768

  5. Vector Store:
     - Primary: ChromaDB (development, MVP)
     - Production: pgvector (PostgreSQL extension)

Retrieval Pipeline:
  1. Query Processing:
     - Расширение запроса медицинскими синонимами
     - Перевод терминов (RU→EN для PubMed)
     - Генерация sub-queries

  2. Retrieval:
     - Hybrid search (semantic + keyword)
     - Re-ranking по релевантности
     - Фильтрация по metadata (specialty, date, evidence_grade)

  3. Context Assembly:
     - Группировка по источнику
     - Дедупликация
     - Ограничение по токенам
```

---

## Коллекции данных

### 1. clinical_guidelines

```yaml
Описание: Клинические рекомендации Минздрав РФ + международные
Источники:
  - Клинические рекомендации Минздрав (cr.minzdrav.gov.ru)
  - WHO Guidelines
  - NICE Guidelines (перевод ключевых)
  - Национальные руководства по специальностям

Chunking:
  strategy: "semantic"
  chunk_size: 1000 tokens
  overlap: 200 tokens
  preserve: [headers, lists, tables, dosages]

Metadata:
  - specialty: str          # Специальность (cardiology, neurology...)
  - icd10_codes: list[str]  # Связанные коды МКБ-10
  - evidence_grade: str     # A/B/C/D/E
  - publication_date: date  # Дата публикации
  - source: str             # Источник
  - language: str           # ru/en
  - version: str            # Версия рекомендации

Обновление: Ежеквартально (при публикации новых рекомендаций)
```

### 2. pubmed_abstracts

```yaml
Описание: Абстракты из PubMed по профильным тематикам
Источники:
  - PubMed E-utilities API
  - Фильтр: meta-analysis, systematic review, RCT, clinical trial
  - Фокус: последние 10 лет

Chunking:
  strategy: "document"  # Один абстракт = один chunk
  max_size: 500 tokens

Metadata:
  - pmid: str             # PubMed ID
  - authors: list[str]    # Авторы
  - journal: str          # Журнал
  - publication_date: date
  - study_type: str       # RCT, meta-analysis, cohort, case-report
  - mesh_terms: list[str] # MeSH термины
  - evidence_level: str   # По иерархии доказательств

Обновление: Еженедельно (автоматический поиск новых публикаций)
```

### 3. icd10_knowledge

```yaml
Описание: МКБ-10 с описаниями, критериями, связями
Источники:
  - МКБ-10 (русская версия)
  - МКБ-11 (для маппинга)
  - Описания заболеваний с диагностическими критериями

Chunking:
  strategy: "entity"  # Один код = один chunk
  includes: [код, название, описание, включения, исключения, критерии]

Metadata:
  - icd10_code: str
  - chapter: str
  - block: str
  - specialty: str
  - synonyms: list[str]

Обновление: При обновлении классификации
```

### 4. drug_interactions

```yaml
Описание: Лекарственные взаимодействия и противопоказания
Источники:
  - DrugBank
  - RxNorm
  - OpenFDA
  - Государственный реестр лекарственных средств РФ

Chunking:
  strategy: "pair"  # Одна пара лекарств = один chunk

Metadata:
  - drug_a: str
  - drug_b: str
  - rxnorm_a: str
  - rxnorm_b: str
  - severity: str        # major/moderate/minor
  - mechanism: str
  - clinical_effect: str
  - management: str
  - source: str

Обновление: Ежемесячно
```

### 5. lab_reference_ranges

```yaml
Описание: Референсные значения лабораторных анализов
Источники:
  - LOINC
  - Клинические лаборатории (Invitro, Helix)
  - Рекомендации по лабораторной диагностике

Chunking:
  strategy: "test"  # Один тест = один chunk

Metadata:
  - loinc_code: str
  - test_name_ru: str
  - test_name_en: str
  - unit: str
  - reference_ranges:
      male: {min, max}
      female: {min, max}
      children: [{age_range, min, max}]
  - critical_values: {low, high}
  - sample_type: str
  - methodology: str

Обновление: При изменении нормативов
```

---

## Конфигурация Embedding

```yaml
Development:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  dimension: 384
  language: "multilingual"
  speed: "fast"
  quality: "good"

Production:
  model: "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
  dimension: 768
  language: "en (primary), ru (через перевод)"
  speed: "medium"
  quality: "best for medical"

Fallback:
  model: "cohere/embed-multilingual-v3.0"
  dimension: 1024
  language: "multilingual (native)"
  speed: "api-dependent"
  quality: "excellent"
```

---

## Retrieval конфигурация

```yaml
Hybrid Search:
  semantic_weight: 0.7
  keyword_weight: 0.3
  top_k: 10
  rerank_top_k: 5
  min_similarity: 0.65

Medical Query Expansion:
  synonyms: true               # Медицинские синонимы
  abbreviations: true          # Расшифровка аббревиатур (ОАК → общий анализ крови)
  icd10_enrichment: true       # Добавление связанных МКБ-10 кодов
  snomed_mapping: true         # Маппинг на SNOMED CT

Filtering:
  by_specialty: true           # Фильтр по специализации агента
  by_evidence_grade: "A,B,C"   # Минимум grade C
  by_date: "last_10_years"     # Для PubMed
  by_language: ["ru", "en"]    # Русский приоритетен

Context Window:
  max_tokens: 4000             # Максимум для контекста RAG
  source_limit: 5              # Максимум источников в одном ответе
```

---

## Индексация и обновление

### Автоматическая индексация

```yaml
Schedule:
  clinical_guidelines: "0 3 1 */3 *"     # Каждый квартал
  pubmed_abstracts: "0 4 * * 1"          # Каждый понедельник
  drug_interactions: "0 3 1 * *"         # Каждый месяц
  lab_reference_ranges: "manual"          # Вручную
  icd10_knowledge: "manual"              # Вручную

Process:
  1. Fetch новых документов
  2. Preprocess + chunk
  3. Embed
  4. Upsert в vector store
  5. Validate (spot-check на корректность)
  6. Log: AuditLogService.log_task_end('rag_indexing', ...)
```

### Валидация качества

```yaml
After indexing:
  - Тестовые запросы по каждой коллекции (минимум 5)
  - Проверка relevance score > 0.7
  - Проверка отсутствия дубликатов
  - Spot-check метаданных

Monthly:
  - Medical-Domain Agent проверяет выборку (20 chunks)
  - Удаление устаревших данных
  - Обновление невалидных ссылок
```

---

## Безопасность данных

```yaml
Хранение:
  - Vector store: шифрование at rest (AES-256)
  - Метаданные: отдельно от персональных данных пациентов
  - Backup: ежедневно

Доступ:
  - Только AI-агенты через API (не прямой доступ к БД)
  - Логирование всех запросов к RAG
  - Rate limiting по patient_id

Контент:
  - Только верифицированные медицинские источники
  - Запрет на индексацию рекламных материалов
  - Запрет на народную медицину без evidence base
```

---

## Ссылки

- **AI-агенты:** `.claude/agents/ai-agents.md`
- **LangChain:** `.claude/skills/langchain-development.md`
- **Clinical Reasoning:** `.claude/skills/clinical-reasoning.md`
- **Medical API:** `.claude/skills/medical-api-integration.md`
- **Правила безопасности:** `.claude/rules/05-medical-safety.md`

---

*Спецификация навыка v1.0 | Aibolit AI — Claude Code Agent System*
