---
title: "ADR-001: Выбор FastAPI вместо Django для медицинского AI-портала"
created_by: "Architect Agent"
created_at: "2025-02-24"
version: "1.0"
---

# ADR-001: Выбор FastAPI вместо Django для медицинского AI-портала

## Статус

Accepted

## Контекст

Проект Aibolit AI — бесплатный некоммерческий веб-портал пациента с AI-врачами 35 медицинских специализаций. Ключевые технические требования:

1. **Streaming AI-ответов** — мультитерновый чат с AI-врачами через SSE (Server-Sent Events) с потоковой генерацией ответов в реальном времени.
2. **Асинхронные внешние API** — интеграция с PubMed, OpenFDA, RxNorm, WHO ICD-11 (все HTTP-запросы).
3. **Claude CLI subprocess** — AI-движок реализован через asyncio subprocess с потоковым чтением stdout.
4. **Простота API** — REST API без сложной бизнес-логики (основная логика в AI-движке).
5. **Скорость разработки** — MVP для некоммерческого проекта, один разработчик.

Стартовый шаблон мультиагентной системы предусматривает Django 5 + DRF (Django REST Framework) как базовый стек. Решение принято об отклонении от шаблона.

## Решение

Выбран **FastAPI** (Python 3.12) + **Uvicorn** в качестве backend-фреймворка.

### Обоснование

| Критерий | FastAPI | Django + DRF |
|----------|---------|-------------|
| Async/SSE | Нативная поддержка `async def`, `StreamingResponse` | Ограниченная async поддержка, ASGI через Daphne/Uvicorn сложнее |
| Subprocess streaming | `asyncio.create_subprocess_exec` — нативно | Требует дополнительного слоя (Channels, Celery) |
| Производительность | Высокая (Starlette/Uvicorn) | Средняя (Django ORM overhead) |
| Валидация | Pydantic v2 — встроенная | DRF Serializers — больше boilerplate |
| OpenAPI docs | Автоматическая генерация | Через drf-spectacular (дополнительная настройка) |
| Размер кода | Минимальный boilerplate | Значительный (settings, apps, urls, serializers, viewsets) |
| Кривая обучения | Низкая для данного проекта | Избыточна для API-only |
| Admin panel | Нет (не нужен для портала пациента) | Есть (не используется) |
| ORM | Не нужен (SQLite + raw SQL) | Django ORM (избыточен) |

### Ключевые факторы решения

1. **SSE Streaming** — основная функция портала (чат с AI). FastAPI поддерживает `StreamingResponse` из коробки, что критически важно для потоковой генерации ответов Claude CLI.

2. **Asyncio subprocess** — Claude CLI запускается как subprocess, stdout читается построчно через asyncio. Django потребовал бы Channels или отдельный async worker.

3. **Простая модель данных** — SQLite с raw SQL-запросами через sqlite3. Django ORM избыточен и не даёт преимуществ.

4. **Один разработчик** — минимум boilerplate кода, фокус на бизнес-логике.

## Альтернативы

### 1. Django 5 + DRF (стартовый шаблон)

**Плюсы:**
- Встроенная admin panel
- Django ORM с миграциями
- Зрелая экосистема
- Совместимость со стартовым шаблоном

**Минусы:**
- Сложная настройка async SSE
- Избыточный ORM для SQLite
- Больше кода для простого REST API
- Channels для WebSocket/SSE — дополнительная сложность

**Отклонено:** Избыточная сложность для API-only проекта с потоковым AI.

### 2. Flask + Flask-SocketIO

**Плюсы:**
- Минимальный фреймворк
- Большая экосистема расширений

**Минусы:**
- Синхронный по умолчанию
- Нет встроенной валидации
- Нет автоматической OpenAPI документации
- Async поддержка через Quart (отдельный фреймворк)

**Отклонено:** Хуже async-поддержка, чем FastAPI.

### 3. Node.js (Express/Fastify)

**Плюсы:**
- Нативный event loop, отличная работа со streaming
- Единый язык с фронтендом

**Минусы:**
- Python — основной язык ML/AI-экосистемы
- Claude CLI удобнее вызывать из Python (asyncio subprocess)
- Медицинские библиотеки (numpy, pandas) — Python
- Двуязычный стек усложняет поддержку

**Отклонено:** Python-экосистема критична для медицинского AI.

## Последствия

### Положительные

1. **Простой SSE streaming** — `StreamingResponse` + `async def event_stream()` реализуется в 20 строк кода.
2. **Быстрая разработка** — минимум boilerplate, Pydantic-валидация, auto-docs.
3. **Высокая производительность** — Uvicorn + asyncio для I/O-bound операций (внешние API, Claude CLI).
4. **Лёгкий деплой** — один процесс, без Celery/Redis/Channels.

### Отрицательные

1. **Нет admin panel** — просмотр данных только через API или прямой доступ к SQLite.
2. **Ручные SQL-миграции** — нет Django-миграций, миграции через `schema_version` + `_run_migrations()`.
3. **Нет совместимости со стартовым шаблоном** — AuditLogService, модели и компоненты из Django-шаблона нужно реализовывать заново.
4. **Нет ORM** — все запросы через raw SQL (допустимо для SQLite, но увеличивает объём кода в `database.py`).

### Технический долг

- При миграции на PostgreSQL потребуется SQLAlchemy или другой ORM.
- AuditLogService необходимо реализовать с нуля (не из Django-шаблона).

---

*Документ создан: Architect Agent | Дата: 2025-02-24*
