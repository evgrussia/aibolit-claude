---
title: "API Contracts — Aibolit AI"
created_by: "Data Agent"
created_at: "2025-02-24"
version: "1.0"
---

# API Contracts — Aibolit AI

## Общие сведения

| Параметр | Значение |
|----------|----------|
| Base URL | `http://localhost:8007/api/v1` (dev) / `https://aibolit-ai.ru/api/v1` (prod) |
| Формат данных | JSON (application/json) |
| Аутентификация | JWT Bearer Token |
| Версионирование | URL prefix: `/api/v1` |
| Кодировка | UTF-8 |

## Аутентификация

Все защищённые эндпоинты требуют заголовок:

```
Authorization: Bearer <JWT_TOKEN>
```

JWT payload:
```json
{
  "user_id": 1,
  "patient_id": "7facb1f2",
  "username": "evgeny",
  "exp": 1740000000
}
```

- Алгоритм: HS256
- Срок действия: 7 дней
- Secret key: `AIBOLIT_SECRET_KEY` (env var)

Некоторые эндпоинты используют `get_optional_user` — работают как с токеном, так и без него (для MCP-совместимости).

## Формат ошибок

```json
{
  "detail": "Описание ошибки на русском языке"
}
```

| HTTP код | Описание |
|----------|----------|
| 400 | Невалидные данные запроса |
| 401 | Требуется авторизация / токен истёк |
| 403 | Доступ запрещён (чужие данные) |
| 404 | Ресурс не найден |
| 409 | Конфликт (дублирование) |
| 413 | Файл слишком большой |
| 415 | Неподдерживаемый тип файла |
| 429 | Слишком много запросов (rate limit) |
| 500 | Внутренняя ошибка сервера |
| 503 | AI-сервис недоступен |

## Rate Limiting

| Эндпоинт | Лимит | Окно |
|----------|-------|------|
| POST /auth/login | 10 запросов | 60 секунд |
| POST /auth/register | 5 запросов | 300 секунд |
| Остальные | Без лимита | — |

Реализация: In-memory sliding window по IP (X-Forwarded-For или client.host).

---

## 1. Auth — Аутентификация

### POST /auth/register

Регистрация нового пользователя + создание карты пациента.

**Rate limit:** 5 req / 5 min

**Request:**
```json
{
  "username": "evgeny",
  "password": "MyPass123",
  "first_name": "Евгений",
  "last_name": "Пономарев",
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "blood_type": "A+",
  "allergies": [
    {"substance": "Пенициллин", "reaction": "Сыпь", "severity": "moderate"}
  ],
  "family_history": ["Гипертония у отца"]
}
```

**Response 200:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "patient_id": "7facb1f2",
  "username": "evgeny"
}
```

**Ошибки:** 400 (невалидный пароль), 409 (логин занят)

---

### POST /auth/login

**Rate limit:** 10 req / min

**Request:**
```json
{
  "username": "evgeny",
  "password": "MyPass123"
}
```

**Response 200:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "patient_id": "7facb1f2",
  "username": "evgeny"
}
```

**Ошибки:** 401 (неверный логин/пароль), 429 (rate limit)

---

### GET /auth/me

**Auth:** Required

**Response 200:**
```json
{
  "user_id": 1,
  "username": "evgeny",
  "patient_id": "7facb1f2"
}
```

---

### POST /auth/change-password

**Auth:** Required

**Request:**
```json
{
  "old_password": "MyPass123",
  "new_password": "NewPass456"
}
```

**Response 200:**
```json
{
  "message": "Пароль успешно изменён"
}
```

---

### DELETE /auth/me

**Auth:** Required

Удаление аккаунта пользователя.

**Response 200:**
```json
{
  "message": "Аккаунт удалён"
}
```

---

## 2. Patients — Пациенты

### GET /patients/me

**Auth:** Required

Получить свою карту пациента.

**Response 200:** `PatientResponse` (полная карта, см. ниже)

---

### GET /patients

**Auth:** Required

Список всех пациентов (для совместимости с MCP).

**Response 200:**
```json
[
  {
    "id": "7facb1f2",
    "name": "Пономарев Евгений",
    "dob": "1990-05-15",
    "gender": "male"
  }
]
```

---

### GET /patients/search?q={query}

**Auth:** Required

Поиск пациентов по имени (case-insensitive, кириллица).

**Query params:** `q` (min 1 символ)

**Response 200:** `PatientSummary[]`

---

### GET /patients/by-diagnosis?icd10={code}

**Auth:** Required

Поиск пациентов по коду МКБ-10.

**Query params:** `icd10` (min 1 символ)

---

### POST /patients

**Auth:** Required

Создание карты пациента.

**Request:**
```json
{
  "first_name": "Иван",
  "last_name": "Иванов",
  "date_of_birth": "1985-03-20",
  "gender": "male",
  "blood_type": "B+",
  "allergies": [],
  "family_history": []
}
```

**Response 200:**
```json
{
  "id": "a1b2c3d4",
  "message": "Пациент Иванов Иван зарегистрирован"
}
```

---

### GET /patients/{patient_id}

**Auth:** Optional (если есть — проверяет ownership)

Полная карта пациента.

**Response 200 (PatientResponse):**
```json
{
  "id": "7facb1f2",
  "first_name": "Евгений",
  "last_name": "Пономарев",
  "full_name": "Пономарев Евгений",
  "age": 34,
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "blood_type": "A+",
  "allergies": [
    {"id": 1, "substance": "Пенициллин", "reaction": "Сыпь", "severity": "moderate"}
  ],
  "medications": [
    {"id": 1, "name": "Лизиноприл", "dosage": "10 мг", "frequency": "1 раз/день",
     "route": "oral", "start_date": "2024-01-01", "end_date": null,
     "prescribing_doctor": "", "notes": ""}
  ],
  "diagnoses": [
    {"id": 1, "icd10_code": "I10", "name": "Артериальная гипертензия",
     "date_diagnosed": "2024-01-01", "status": "chronic", "notes": "", "confidence": 0.0}
  ],
  "lab_results": [
    {"id": 1, "test_name": "hemoglobin_male", "value": 145, "unit": "г/л",
     "reference_range": "130-170", "date": "2024-12-01", "is_abnormal": false, "notes": ""}
  ],
  "vitals_history": [
    {"id": 1, "timestamp": "2024-12-01T10:30:00", "systolic_bp": 130,
     "diastolic_bp": 85, "heart_rate": 72, "temperature": 36.6,
     "spo2": 98.0, "respiratory_rate": 16, "weight": 78.5, "height": 175.0,
     "blood_glucose": 5.2}
  ],
  "family_history": ["Гипертония у отца"],
  "surgical_history": [],
  "lifestyle": {"smoking": "no", "alcohol": "moderate"},
  "notes": ""
}
```

---

### PATCH /patients/{patient_id}

**Auth:** Optional (ownership check)

Частичное обновление карты пациента.

**Request:**
```json
{
  "first_name": "Евгений",
  "notes": "Обновлённые заметки",
  "family_history": ["Гипертония у отца", "Диабет у матери"]
}
```

**Response 200:**
```json
{
  "message": "Данные пациента обновлены"
}
```

---

### DELETE /patients/{patient_id}

**Auth:** Optional (ownership check)

Удаление карты пациента (каскадное удаление всех дочерних записей).

---

### POST /patients/{patient_id}/vitals

**Auth:** Optional (ownership check)

**Request:**
```json
{
  "systolic_bp": 130,
  "diastolic_bp": 85,
  "heart_rate": 72,
  "temperature": 36.6,
  "spo2": 98.0,
  "respiratory_rate": 16,
  "weight": 78.5,
  "height": 175.0,
  "blood_glucose": 5.2
}
```

**Response 200:**
```json
{
  "id": 5,
  "message": "Витальные показатели записаны"
}
```

---

### POST /patients/{patient_id}/labs

**Auth:** Optional (ownership check)

**Request:**
```json
{
  "test_name": "hemoglobin_male",
  "value": 145,
  "unit": "г/л",
  "reference_range": "130-170"
}
```

---

### POST /patients/{patient_id}/labs/bulk

**Auth:** Optional (ownership check)

Массовое добавление результатов анализов.

**Request:**
```json
{
  "results": [
    {"test_name": "hemoglobin_male", "value": 145, "unit": "г/л", "reference_range": "130-170"},
    {"test_name": "glucose_fasting", "value": 5.2, "unit": "ммоль/л", "reference_range": "3.9-6.1"}
  ]
}
```

**Response 200:**
```json
{
  "ids": [10, 11],
  "count": 2,
  "message": "Добавлено 2 результатов"
}
```

---

### POST /patients/{patient_id}/labs/upload-parse

**Auth:** Optional (ownership check)

Загрузка файла с анализами (CSV, PDF, изображение) и парсинг.

**Content-Type:** multipart/form-data

**Параметры:**
- `file` — файл (max 10 МБ; PDF, JPEG, PNG, WEBP, CSV, TXT)

**Response 200:**
```json
{
  "results": [
    {"test_name": "Гемоглобин", "value": 145, "unit": "г/л", "reference_range": "130-170"}
  ],
  "source_file": "analysis.pdf",
  "parsed_count": 5
}
```

---

### POST /patients/{patient_id}/diagnoses

**Auth:** Optional (ownership check)

**Request:**
```json
{
  "icd10_code": "I10",
  "name": "Артериальная гипертензия",
  "status": "chronic",
  "notes": "",
  "confidence": 0.85
}
```

---

### POST /patients/{patient_id}/medications

**Auth:** Optional (ownership check)

**Request:**
```json
{
  "name": "Лизиноприл",
  "dosage": "10 мг",
  "frequency": "1 раз/день",
  "route": "oral",
  "notes": ""
}
```

---

### POST /patients/{patient_id}/allergies

**Auth:** Optional (ownership check)

**Request:**
```json
{
  "substance": "Пенициллин",
  "reaction": "Сыпь",
  "severity": "moderate"
}
```

---

### GET /patients/{patient_id}/lab-trends?test={name}&limit={n}

**Auth:** Optional

Тренды лабораторного теста по времени.

**Query params:** `test` (required), `limit` (default 20)

---

### GET /patients/{patient_id}/vitals-history?limit={n}

**Auth:** Optional

История витальных показателей.

---

### GET /patients/{patient_id}/consultations?limit={n}

**Auth:** Optional

История консультаций пациента.

---

### DELETE /patients/{patient_id}/{table}/{record_id}

**Auth:** Optional (ownership check)

Удаление подзаписи. `table` должна быть одной из: `allergies`, `medications`, `diagnoses`, `lab_results`, `vitals`.

---

### PATCH /patients/{patient_id}/{table}/{record_id}

**Auth:** Optional (ownership check)

Частичное обновление подзаписи.

**Request body:** JSON с обновляемыми полями.

---

## 3. Chat — Мультитерновый AI-чат

### POST /chat/create

**Auth:** Required

Создание нового чата и получение первого ответа AI через SSE.

**Request:**
```json
{
  "specialty": "cardiologist",
  "complaints": "Боль в груди при физической нагрузке"
}
```

**Response:** SSE stream (Content-Type: text/event-stream)

```
event: meta
data: {"consultation_id": 42, "doctor": {"specialty_id": "cardiologist", "name": "AI-Кардиолог", "qualification": "..."}, "disclaimer": "...", "red_flags": [...], "emergency": {...}}

event: delta
data: {"text": "Здравствуйте! "}

event: delta
data: {"text": "Расскажите подробнее..."}

event: done
data: {"message_id": 101, "full_text": "Здравствуйте! Расскажите подробнее..."}
```

---

### POST /chat/{consultation_id}/message

**Auth:** Required (ownership check)

Отправка сообщения в существующий чат (текст + файлы).

**Content-Type:** multipart/form-data

**Параметры:**
- `text` — текст сообщения
- `files` — до 5 файлов (JPEG, PNG, GIF, WEBP, PDF, TXT), каждый до 10 МБ

**Response:** SSE stream

```
event: meta
data: {"red_flags": [...], "emergency": {...}}

event: delta
data: {"text": "На основании описанных симптомов..."}

event: done
data: {"message_id": 103, "full_text": "На основании описанных симптомов..."}
```

**SSE Events:**

| Event | Описание |
|-------|----------|
| `meta` | Метаданные: consultation_id, doctor info, disclaimers, red flags |
| `delta` | Фрагмент текста ответа AI |
| `done` | Завершение: message_id + full_text |
| `error` | Ошибка генерации |

---

### GET /chat/{consultation_id}/messages

**Auth:** Required (ownership check)

Все сообщения чата.

**Response 200:**
```json
[
  {"id": 100, "role": "user", "content": "Боль в груди...", "created_at": "2024-12-01T10:00:00"},
  {"id": 101, "role": "assistant", "content": "Здравствуйте!...", "created_at": "2024-12-01T10:00:05"}
]
```

---

### GET /chat/{consultation_id}

**Auth:** Required (ownership check)

Метаданные консультации.

**Response 200:**
```json
{
  "id": 42,
  "specialty": "cardiologist",
  "status": "active",
  "title": "Боль в груди при физической нагрузке",
  "complaints": "Боль в груди при физической нагрузке",
  "date": "2024-12-01T10:00:00",
  "session_id": "a1b2c3d4-...",
  "doctor": {
    "specialty_id": "cardiologist",
    "name": "AI-Кардиолог",
    "qualification": "Диагностика и лечение заболеваний ССС..."
  }
}
```

---

### GET /chat

**Auth:** Required

Все чаты текущего пользователя.

**Response 200:**
```json
[
  {
    "id": 42,
    "specialty": "cardiologist",
    "status": "active",
    "title": "Боль в груди при физической нагрузке",
    "date": "2024-12-01T10:00:00",
    "last_message_preview": "Рекомендую обратиться к кардиологу...",
    "message_count": 6,
    "doctor": {"specialty_id": "cardiologist", "name": "AI-Кардиолог", "qualification": "..."}
  }
]
```

---

### POST /chat/{consultation_id}/close

**Auth:** Required (ownership check)

Закрытие консультации.

**Response 200:**
```json
{
  "status": "closed"
}
```

---

### GET /chat/attachments/{attachment_id}

**Auth:** Required (ownership check)

Скачивание вложения чата. Возвращает файл с соответствующим Content-Type.

---

## 4. Consultations — Одноразовые AI-консультации

### POST /consultations/triage

Определение подходящего специалиста по жалобам.

**Request:**
```json
{
  "complaints": "Болит голова и тошнит"
}
```

**Response 200:**
```json
{
  "recommendations": [
    {
      "specialty_id": "neurologist",
      "name_ru": "Невролог",
      "description": "Заболевания нервной системы...",
      "relevance": 0.85,
      "reason": "Головная боль — ключевой симптом неврологических заболеваний"
    },
    {
      "specialty_id": "therapist",
      "name_ru": "Терапевт",
      "description": "Первичная диагностика...",
      "relevance": 0.7,
      "reason": "Общие симптомы, требующие первичной оценки"
    }
  ],
  "red_flags": [...],
  "emergency": {...}
}
```

---

### POST /consultations/start

**Auth:** Optional

Запуск одноразовой AI-консультации (без чата).

**Request:**
```json
{
  "specialty": "neurologist",
  "complaints": "Сильная головная боль в затылочной области",
  "patient_id": "7facb1f2"
}
```

**Response 200:**
```json
{
  "consultation": {
    "specialty": "neurologist",
    "summary": "... AI-сгенерированный текст консультации ...",
    "recommended_tests": [...],
    "icd_codes": [...]
  },
  "ai_generated": true,
  "disclaimer": "Информация предоставлена AI-ассистентом...",
  "red_flags": [
    {"category": "neurological", "description": "...", "urgency": 5, "action": "Вызовите скорую: 103"}
  ],
  "emergency": {
    "call": "103 / 112",
    "message": "Обнаружены признаки, требующие экстренной помощи!",
    "flags": [...]
  }
}
```

---

### GET /consultations?specialty={id}&limit={n}

Список консультаций (без аутентификации для MCP-совместимости).

---

## 5. Diagnostics — Диагностические калькуляторы

### POST /diagnostics/analyze-labs

**Request:**
```json
{
  "results": [
    {"test": "hemoglobin_male", "value": 145},
    {"test": "glucose_fasting", "value": 7.2}
  ],
  "gender": "male"
}
```

**Response 200:**
```json
{
  "interpretations": [
    {"test_name": "Гемоглобин (М)", "value": 145, "unit": "г/л", "status": "normal", "severity": "ok"},
    {"test_name": "Глюкоза натощак", "value": 7.2, "unit": "ммоль/л", "status": "high", "severity": "warning"}
  ],
  "patterns_detected": ["Повышенная глюкоза натощак — возможный преддиабет"],
  "summary": "Обнаружено 1 отклонение из 2 показателей"
}
```

---

### POST /diagnostics/assess-vitals

**Request:**
```json
{
  "systolic_bp": 185,
  "diastolic_bp": 110,
  "heart_rate": 95,
  "temperature": 36.6,
  "spo2": 97.0
}
```

**Response 200:**
```json
{
  "alerts": [
    "КРИТИЧНО: систолическое АД 185 mmHg (>=180) — гипертонический криз! Вызовите скорую: 103 / 112",
    "КРИТИЧНО: диастолическое АД 110 mmHg (>=110) — гипертонический криз!"
  ],
  "severity": "critical",
  "values": {
    "systolic_bp": 185,
    "diastolic_bp": 110,
    "heart_rate": 95,
    "temperature": 36.6,
    "spo2": 97.0
  }
}
```

---

### POST /diagnostics/calculate-gfr

**Request:**
```json
{
  "creatinine": 120,
  "age": 55,
  "gender": "male"
}
```

**Response 200:**
```json
{
  "gfr": 62.5,
  "stage": "G3a — Умеренно сниженная функция почек",
  "recommendation": "Рекомендуется консультация нефролога"
}
```

---

### POST /diagnostics/cardiovascular-risk

**Request:**
```json
{
  "age": 55,
  "gender": "male",
  "systolic_bp": 145,
  "total_cholesterol": 6.2,
  "hdl": 1.1,
  "smoker": true,
  "diabetic": false,
  "on_bp_treatment": true
}
```

**Response 200:**
```json
{
  "ten_year_risk_percent": 18.5,
  "category": "high",
  "color": "red",
  "recommendations": [
    "Рекомендуется отказ от курения",
    "Контроль артериального давления"
  ]
}
```

---

## 6. Drugs — Лекарства

### GET /drugs/{drug_name}

Информация о лекарственном препарате (OpenFDA).

**Response 200:**
```json
{
  "name": "Ibuprofen",
  "brand_names": ["Ibuprofen"],
  "drug_class": "NSAID",
  "indications": "...",
  "warnings": "...",
  "dosage_form": "tablet"
}
```

---

### GET /drugs/{drug_name}/adverse-events?limit={n}

Побочные эффекты препарата (OpenFDA).

**Response 200:**
```json
{
  "drug": "ibuprofen",
  "events": [
    {"reaction": "Nausea", "count": 150, "outcome": ""},
    {"reaction": "Headache", "count": 85, "outcome": ""}
  ]
}
```

---

### POST /drugs/interactions

Проверка лекарственных взаимодействий (локальная база).

**Request:**
```json
{
  "drugs": ["warfarin", "aspirin", "ibuprofen"]
}
```

**Response 200:**
```json
[
  {"drug1": "warfarin", "drug2": "aspirin", "warning": "Повышенный риск кровотечения", "severity": "major"},
  {"drug1": "warfarin", "drug2": "ibuprofen", "warning": "Усиление антикоагулянтного эффекта", "severity": "major"}
]
```

---

## 7. Documents — Медицинские документы

### POST /documents/medical-record

Генерация медицинской записи.

**Request:**
```json
{
  "patient_name": "Пономарев Евгений",
  "patient_age": 34,
  "gender": "male",
  "complaints": "Головная боль",
  "anamnesis": "...",
  "examination": "...",
  "diagnoses": [{"icd10": "G43", "name": "Мигрень"}],
  "plan": "..."
}
```

**Response 200:**
```json
{
  "document": "МЕДИЦИНСКАЯ ЗАПИСЬ\n\n..."
}
```

---

### POST /documents/prescription

Генерация рецепта.

**Request:**
```json
{
  "patient_name": "Пономарев Евгений",
  "medications": [{"name": "Ибупрофен", "dosage": "400 мг", "frequency": "3 раза/день"}],
  "diagnoses": ["G43 — Мигрень"]
}
```

---

### POST /documents/referral

Генерация направления к специалисту.

---

### POST /documents/discharge-summary

Генерация выписного эпикриза.

---

### POST /documents/upload

**Auth:** Required

Загрузка медицинского документа.

**Content-Type:** multipart/form-data

**Параметры:**
- `file` — файл (max 10 МБ; PDF, JPEG, PNG, WEBP, TXT, CSV, DOC, DOCX)
- `notes` — примечания (опционально)

**Response 200:**
```json
{
  "id": 5,
  "file_name": "analysis_results.pdf",
  "file_size": 245760
}
```

---

### GET /documents/my

**Auth:** Required

Список документов текущего пользователя.

---

### GET /documents/{doc_id}/download

**Auth:** Required (ownership check)

Скачивание документа. Возвращает файл с Content-Disposition: attachment.

---

### DELETE /documents/{doc_id}

**Auth:** Required (ownership check)

Удаление документа.

---

## 8. Knowledge — Медицинские знания

### GET /knowledge/icd-search?q={query}

Поиск по классификации МКБ-10/ICD-11 (WHO API).

---

### GET /knowledge/disease-info?name={name}

Информация о заболевании (WHO ICD-11).

---

### GET /knowledge/literature?q={query}&max_results={n}

Поиск медицинской литературы (PubMed).

**Query params:** `q` (required), `max_results` (default 10, max 30)

---

### GET /knowledge/article/{pmid}

Абстракт статьи из PubMed.

**Response 200:**
```json
{
  "pmid": "12345678",
  "abstract": "..."
}
```

---

## 9. Reference — Справочники

### GET /reference/lab-ranges

Справочник референсных диапазонов лабораторных тестов.

**Response 200:**
```json
{
  "hemoglobin_male": {"name": "Гемоглобин (М)", "min": 130, "max": 170, "unit": "г/л"},
  "glucose_fasting": {"name": "Глюкоза натощак", "min": 3.9, "max": 6.1, "unit": "ммоль/л"}
}
```

---

### GET /reference/specializations

Список всех 35 медицинских специализаций.

**Response 200:**
```json
[
  {
    "id": "cardiologist",
    "name_ru": "Кардиолог",
    "name_en": "Cardiologist",
    "description": "Диагностика и лечение заболеваний ССС...",
    "skills": [
      {"name": "Анализ ЭКГ", "description": "Расшифровка электрокардиограммы"}
    ]
  }
]
```

---

## 10. Health Check

### GET /api/health

**Auth:** Не требуется

**Response 200:**
```json
{
  "status": "ok",
  "service": "aibolit-portal"
}
```

---

*Документ создан: Data Agent | Дата: 2025-02-24*
