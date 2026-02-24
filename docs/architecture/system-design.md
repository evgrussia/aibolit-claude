---
title: "System Design — Aibolit AI"
created_by: "Architect Agent"
created_at: "2025-02-24"
version: "1.0"
---

# System Design — Aibolit AI

## 1. Обзор архитектуры

Aibolit AI — бесплатный некоммерческий веб-портал пациента с AI-врачами 35 медицинских специализаций. Система построена по архитектуре SPA + REST API + AI Engine и развёртывается в Docker-контейнерах.

### Высокоуровневая диаграмма

```
                          +-------------------+
                          |    Пользователь    |
                          |   (Браузер/PWA)    |
                          +---------+---------+
                                    |
                                    | HTTPS
                                    v
                          +---------+---------+
                          |      Nginx        |
                          |  (reverse proxy)  |
                          |  порт 80 / 443    |
                          +---------+---------+
                                    |
                     +--------------+--------------+
                     |                             |
              /api/* запросы              статика (SPA)
                     |                             |
                     v                             v
          +----------+----------+      +-----------+-----------+
          |   FastAPI Backend   |      |   React SPA (Vite)    |
          |    (Uvicorn)        |      |   Build → dist/       |
          |    порт 8007        |      |   Nginx serves        |
          +-----+-----+--------+      +-----------------------+
                |     |
        +-------+     +-------+
        |                     |
        v                     v
+-------+-------+    +--------+--------+
|  SQLite DB    |    |  Claude CLI     |
|  (WAL mode)   |    |  (subprocess)   |
|  data/        |    |  --session-id   |
|  aibolit.db   |    |  SSE streaming  |
+---------------+    +--------+--------+
                              |
                     +--------+--------+
                     |   Anthropic     |
                     |   Cloud API     |
                     +-----------------+

        +-------------------------------------------+
        |        Внешние медицинские API             |
        |  +--------+ +--------+ +------+ +-------+ |
        |  | PubMed | |OpenFDA | |RxNorm| |WHO ICD| |
        |  +--------+ +--------+ +------+ +-------+ |
        +-------------------------------------------+
```

## 2. Компоненты системы и их взаимодействие

### 2.1 Frontend (React SPA)

| Характеристика | Значение |
|----------------|----------|
| Фреймворк | React 18 + TypeScript |
| Сборщик | Vite 6 |
| Стили | Tailwind CSS v3 + PostCSS |
| Роутинг | React Router v6 |
| Состояние сервера | TanStack React Query |
| Аутентификация | AuthContext + localStorage |
| Уведомления | ToastContext |

**Структура страниц (15 роутов):**

```
/login                           — Авторизация / Регистрация
/                                — Редирект на dashboard пациента
/patients/:id                    — Дашборд пациента
/patients/:id/labs               — Результаты анализов + тренды
/patients/:id/vitals             — История витальных показателей
/patients/:id/consultations      — История консультаций
/patients/:id/timeline           — Хронология здоровья
/patients/:id/diagnoses/:icd     — Детали диагноза
/consult                         — Консультация с AI-врачом (одноразовая)
/chat                            — История чатов
/chat/:id                        — Мультитерновый чат с AI-врачом
/diagnostics                     — Диагностические калькуляторы
/drugs                           — Поиск лекарств и взаимодействий
/documents                       — Медицинские документы
/settings                        — Настройки аккаунта
```

**Компонентная архитектура:**

```
App.tsx
  |-- ErrorBoundary
  |-- QueryClientProvider
  |-- AuthProvider
  |-- ToastProvider
  |-- BrowserRouter
        |-- ProtectedRoute (проверка JWT)
        |-- Layout
              |-- Sidebar (навигация)
              |-- Outlet (контент страницы)
```

### 2.2 Backend (FastAPI)

| Характеристика | Значение |
|----------------|----------|
| Фреймворк | FastAPI (Python 3.12) |
| ASGI-сервер | Uvicorn |
| Порт | 8007 |
| Аутентификация | JWT (PyJWT) + bcrypt/SHA-256 |
| Валидация | Pydantic v2 |
| БД | SQLite 3 (WAL mode) |

**Архитектура роутеров:**

```
FastAPI App (main.py)
  |-- Middleware: CORS, Request Logging, Global Exception Handler
  |-- Lifespan: init_db() при старте
  |
  |-- /api/v1/auth/        — Аутентификация (register, login, me, change-password)
  |-- /api/v1/patients/    — CRUD пациентов, витальные, анализы, диагнозы, назначения
  |-- /api/v1/chat/        — Мультитерновый чат (create, message, messages, close)
  |-- /api/v1/consultations/ — Одноразовые консультации + триаж
  |-- /api/v1/diagnostics/ — Калькуляторы (GFR, CV risk, анализы, витальные)
  |-- /api/v1/drugs/       — Поиск лекарств (OpenFDA), взаимодействия
  |-- /api/v1/documents/   — Генерация + загрузка/скачивание документов
  |-- /api/v1/knowledge/   — PubMed, ICD-11, информация о заболеваниях
  |-- /api/v1/reference/   — Справочники (лаб. нормы, специализации)
  |-- /api/health          — Health check (без аутентификации)
```

**Слой сервисов:**

```
services/
  |-- chat_service.py           — Claude CLI subprocess, SSE streaming, session management
  |-- consultation_service.py   — Построение структурированной консультации
  |-- triage_service.py         — Маршрутизация к специалисту по жалобам
  |-- claude_service.py         — Claude CLI wrapper для одноразовых консультаций
  |-- lab_parser_service.py     — Парсинг анализов из CSV/изображений
```

### 2.3 Доменная модель (src/)

```
src/
  |-- agents/
  |     |-- doctor.py           — AIDoctorEngine (клиническое рассуждение)
  |     |-- specializations.py  — 35 Specialization dataclass'ов
  |
  |-- models/
  |     |-- patient.py          — Patient, VitalSigns, LabResult, Diagnosis, Medication, Allergy
  |     |-- medical_refs.py     — LAB_REFERENCE_RANGES, DRUG_INTERACTIONS_CRITICAL
  |
  |-- safety/
  |     |-- red_flags.py        — RedFlagDetector: keyword patterns, Urgency levels (1-5)
  |     |-- disclaimers.py      — 8 типов дисклеймеров (general, diagnosis, treatment, ...)
  |
  |-- integrations/
  |     |-- pubmed.py           — NCBI E-utilities (PubMed поиск)
  |     |-- openfda.py          — OpenFDA (информация о лекарствах, побочные эффекты)
  |     |-- medical_apis.py     — RxNorm (NLM)
  |     |-- who_icd.py          — WHO ICD-11 (классификация болезней)
  |
  |-- tools/
  |     |-- diagnostic.py       — analyze_lab_results, assess_vitals, calculate_gfr, cv_risk
  |     |-- documentation.py    — Генерация мед. записей, рецептов, направлений
  |
  |-- utils/
        |-- database.py         — SQLite CRUD, миграции, thread-local connections
        |-- patient_db.py       — Высокоуровневые операции с пациентами
```

## 3. AI Engine Architecture

### 3.1 Claude CLI Integration

Система использует Claude CLI как AI-движок через subprocess с двумя режимами:

**Режим 1: Одноразовая консультация** (`consultation_service.py` + `claude_service.py`)
- Один запрос — один ответ
- Без сохранения контекста между запросами
- Используется на странице `/consult`

**Режим 2: Мультитерновый чат** (`chat_service.py`)
- `--session-id` для первого сообщения
- `--resume` для последующих сообщений в той же сессии
- `--output-format stream-json` для SSE-подобного потокового вывода
- `--max-turns 3` ограничивает рекурсию инструментов
- Используется на странице `/chat/:id`

### 3.2 System Prompt Architecture

```
+-----------------------------+
|  Роль AI-специалиста        |  "Ты — AI-Кардиолог в клинике Aibolit"
+-----------------------------+
|  Компетенции (skills)       |  Из Specialization dataclass
|  Группы МКБ-10              |  related_icd_prefixes
+-----------------------------+
|  Контекст пациента          |  Patient.summary() — аллергии, диагнозы,
|  (из медкарты)              |  препараты, витальные отклонения
+-----------------------------+
|  Правила безопасности       |  Русский язык, формулировки "ВОЗМОЖНО",
|  (hardcoded)                |  запрет диагнозов, напоминание в конце
+-----------------------------+
```

### 3.3 SSE Streaming Pipeline

```
Browser                FastAPI              Claude CLI Process
  |                       |                        |
  |-- POST /chat/create ->|                        |
  |                       |-- asyncio.subprocess ->|
  |                       |     (--session-id)     |
  |<- SSE: event:meta ----|                        |
  |   {consultation_id,   |                        |
  |    doctor, disclaimer}|                        |
  |                       |<-- stream-json lines --|
  |<- SSE: event:delta ---|   {type: "content_block_delta",
  |   {text: "..."}       |    delta: {text: "..."}}
  |<- SSE: event:delta ---|                        |
  |   {text: "..."}       |                        |
  |                       |<-- process exit -------|
  |<- SSE: event:done ----|                        |
  |   {message_id,        |                        |
  |    full_text}          |                        |
```

### 3.4 Медицинская безопасность в AI Pipeline

На каждом входящем сообщении:
1. **Sanitization** — удаление prompt injection паттернов (`sanitize_user_input()`)
2. **Red Flag Detection** — regex-детекция экстренных состояний (`RedFlagDetector`)
3. **Disclaimer Injection** — добавление дисклеймеров по типу контента
4. **Emergency Alert** — при urgency >= 5 рекомендация вызвать 103/112

## 4. Data Flow

### 4.1 Регистрация и вход

```
Пользователь → POST /auth/register
  → Валидация пароля (>= 8, буквы + цифры)
  → Создание Patient record (UUID[:8])
  → Создание User record (bcrypt hash)
  → Генерация JWT (HS256, 7 дней)
  → Ответ {token, patient_id, username}
  → Frontend сохраняет в localStorage
```

### 4.2 Мультитерновый AI-чат

```
1. POST /chat/create {specialty, complaints}
   → Загрузка Patient из БД
   → Загрузка Specialization config
   → Создание consultation record (status=active)
   → Сохранение user message
   → Red flag detection на жалобах
   → Построение system prompt
   → Запуск Claude CLI subprocess (--session-id)
   → SSE stream: meta → delta* → done
   → Сохранение assistant message

2. POST /chat/{id}/message (text + files)
   → Проверка ownership и status
   → Валидация и сохранение файлов (до 5, до 10МБ)
   → Сохранение user message
   → Red flag detection
   → Claude CLI (--resume session-id)
   → SSE stream: meta? → delta* → done
   → Сохранение assistant message
```

### 4.3 Диагностические инструменты

```
POST /diagnostics/analyze-labs {results, gender}
  → analyze_lab_results() — сравнение с LAB_REFERENCE_RANGES
  → {interpretations, patterns_detected, summary}

POST /diagnostics/assess-vitals {systolic_bp, ...}
  → VitalSigns.assess() — пороговые значения
  → {alerts, severity, values}

POST /diagnostics/calculate-gfr {creatinine, age, gender}
  → CKD-EPI formula
  → {gfr, stage, recommendation}

POST /diagnostics/cardiovascular-risk {age, gender, bp, cholesterol, ...}
  → Framingham Risk Score
  → {ten_year_risk_percent, category, color, recommendations}
```

## 5. Интеграции с внешними API

| API | Назначение | Протокол | Аутентификация |
|-----|-----------|----------|----------------|
| PubMed (NCBI E-utilities) | Поиск медицинской литературы | REST/XML | API key (опционально) |
| OpenFDA | Информация о лекарствах, побочные эффекты | REST/JSON | Без аутентификации |
| RxNorm (NLM) | Нормализация названий лекарств | REST/JSON | Без аутентификации |
| WHO ICD-11 | Классификация болезней | REST/JSON | Client ID + Secret |
| Anthropic (через CLI) | AI-генерация медицинских ответов | CLI subprocess | OAuth Token |

Все внешние API вызываются **асинхронно** (httpx/aiohttp) и имеют graceful degradation при недоступности (HTTP 503 с понятным сообщением).

## 6. Деплой-архитектура

### 6.1 Docker Compose

```yaml
services:
  backend:          # FastAPI + Uvicorn, Python 3.12
    build: .        # Multi-stage Dockerfile (target: backend)
    volumes:
      - aibolit-data:/app/data    # SQLite DB + attachments
    environment:
      - AIBOLIT_SECRET_KEY
      - CLAUDE_CODE_OAUTH_TOKEN
    healthcheck:
      test: curl http://localhost:8007/api/health

  nginx:            # Reverse proxy + SPA static files
    build: .        # Multi-stage Dockerfile (target: nginx)
    ports:
      - "80:80"
    depends_on:
      backend: {condition: service_healthy}

volumes:
  aibolit-data:     # Named volume для персистентности
```

### 6.2 Nginx конфигурация

```
/api/*          → proxy_pass http://backend:8007
/               → serve /usr/share/nginx/html (SPA)
*               → try_files $uri /index.html (SPA fallback)
```

### 6.3 Разработка (без Docker)

```
Backend:   python -m uvicorn web.backend.main:app --reload --port 8007
Frontend:  cd web/frontend && npm run dev   (Vite dev server, порт 5173)
           Vite proxy: /api → http://127.0.0.1:8007
```

## 7. Масштабируемость и ограничения

### Текущие ограничения

| Ограничение | Причина | Влияние |
|-------------|---------|---------|
| SQLite — один writer | WAL mode, но запись сериализована | До ~100 одновременных пользователей |
| Claude CLI subprocess | Один процесс на консультацию | Ограничено CPU/памятью сервера |
| In-memory rate limiter | Сбрасывается при рестарте | Не работает при горизонтальном масштабировании |
| Thread-local DB connections | Привязка к потоку | Нормально для Uvicorn workers |
| Файлы вложений на диске | Нет CDN/S3 | Ограничено объёмом диска |

### План масштабирования (при необходимости)

1. **SQLite → PostgreSQL** — при >100 concurrent users (см. ADR-003)
2. **Claude CLI → Claude API** — прямые HTTP-вызовы для большей гибкости (см. ADR-002)
3. **Rate limiter → Redis** — для multi-worker/multi-server
4. **File storage → S3-compatible** — для масштабирования хранилища
5. **Nginx → CDN** — для статики и снижения нагрузки

## 8. Решения для текущих gaps

### GAP-001: Шифрование медданных at rest (CRITICAL)

**Решение:** Fernet (AES-128-CBC + HMAC-SHA256) через библиотеку `cryptography`.

```
Шифруемые поля:
  - diagnoses.notes, diagnoses.name
  - lab_results.value, lab_results.notes
  - medications.name, medications.notes
  - allergies.substance, allergies.reaction
  - consultations.complaints, consultations.response
  - chat_messages.content
  - documents.content (BLOB)

Key management:
  - AIBOLIT_ENCRYPTION_KEY env var (Fernet key, 32 bytes base64)
  - При отсутствии — генерация и warning (как SECRET_KEY)
  - Ротация ключей: decrypt old → encrypt new (offline скрипт)
```

### GAP-002: AuditLogService (HIGH)

**Решение:** Таблица `audit_logs` в SQLite + Python middleware.

```
Логируемые события:
  - Все CRUD операции с данными пациента
  - Аутентификация (login, register, failed attempts)
  - AI-консультации (start, complete, red flags)
  - Доступ к медицинским документам
  - Изменение настроек аккаунта

Retention: 5 лет для медицинских событий
```

### GAP-003: Тесты red flags и дисклеймеров (HIGH)

**Решение:** pytest-модуль с покрытием всех паттернов.

```
Тесты:
  - Все IMMEDIATE patterns (urgency 5) — false negative < 5%
  - Все HIGH patterns (urgency 4)
  - Наличие дисклеймеров во всех типах ответов
  - Sanitization prompt injection
  - Edge cases: пустой текст, очень длинный текст, Unicode
```

### GAP-004: PWA (MEDIUM)

**Решение:** Vite PWA plugin + Service Worker.

```
Функционал:
  - manifest.json (иконки, тема, ориентация)
  - Service Worker (кэширование статики)
  - Offline fallback page
  - Push-уведомления (будущее)
  - Install prompt
```

## 9. Безопасность (обзор)

Подробности в `docs/architecture/security-requirements.md`.

| Аспект | Текущее состояние | Приоритет |
|--------|-------------------|-----------|
| HTTPS/TLS | Nginx (production) | Реализовано |
| JWT аутентификация | HS256, 7 дней | Реализовано |
| Пароли | bcrypt (или SHA-256 fallback) | Реализовано |
| Rate limiting | In-memory, 10 req/min login | Реализовано |
| CORS | Whitelist origins | Реализовано |
| Input sanitization | prompt injection removal | Реализовано |
| Red flags | 20+ immediate patterns | Реализовано |
| Дисклеймеры | 8 типов | Реализовано |
| Шифрование at rest | **НЕ реализовано** | CRITICAL |
| Audit logging | **НЕ реализовано** | HIGH |
| Safety tests | **НЕ реализовано** | HIGH |

---

*Документ создан: Architect Agent | Дата: 2025-02-24*
