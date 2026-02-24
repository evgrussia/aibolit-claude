---
title: "ADR-003: SQLite вместо PostgreSQL для MVP"
created_by: "Architect Agent"
created_at: "2025-02-24"
version: "1.0"
---

# ADR-003: SQLite вместо PostgreSQL для MVP

## Статус

Accepted

## Контекст

Проект Aibolit AI — некоммерческий MVP с ожидаемой нагрузкой до 100 одновременных пользователей. Требования к базе данных:

1. **Нормализованная реляционная схема** — 15+ таблиц с FK, CASCADE, индексами.
2. **Concurrent access** — несколько пользователей одновременно (read-heavy, write-light).
3. **Транзакционность** — атомарные операции при сохранении карты пациента (пациент + дочерние записи).
4. **Простой деплой** — минимум инфраструктуры (Docker compose с 2 сервисами: backend + nginx).
5. **Медицинские данные** — потенциальное шифрование at rest.
6. **Поиск по кириллице** — case-insensitive поиск пациентов и лабораторных тестов.

Стартовый шаблон предусматривает PostgreSQL. Решение принято об использовании SQLite для MVP.

## Решение

Выбрана **SQLite 3** с WAL mode через встроенный модуль `sqlite3` (Python stdlib).

### Конфигурация

```python
# PRAGMA settings (на каждом соединении)
PRAGMA journal_mode = WAL;      # Write-Ahead Logging
PRAGMA foreign_keys = ON;       # Проверка FK constraints
PRAGMA busy_timeout = 5000;     # 5 сек ожидания при блокировке
```

### Особенности реализации

**Thread-local connections:**
```python
_local = threading.local()

def get_connection() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # ... pragmas
        _local.conn = conn
    return conn
```

Каждый worker thread Uvicorn получает собственное соединение. Соединения переиспользуются в рамках потока.

**Unicode LOWER:**
```python
conn.create_function("PY_LOWER", 1, str.lower)
```

SQLite встроенная `LOWER()` не поддерживает кириллицу. Зарегистрирована Python-функция `PY_LOWER()` для case-insensitive поиска.

**Инкрементальные миграции:**
```python
def _run_migrations(conn):
    row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
    current_version = row[0] if row[0] is not None else 0
    if current_version < 2:
        # Migration v2: chat support
        ...
        conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (2)")
```

Вместо Django-миграций используется таблица `schema_version` с ручными инкрементальными миграциями.

**JSON → SQLite автомиграция:**
При первом запуске с пустой БД система автоматически мигрирует данные из JSON-файлов (если есть) в `data/patients/` директории.

### Расположение файла

```
data/
  aibolit.db       # Основной файл БД
  aibolit.db-wal   # WAL-файл (автоматически)
  aibolit.db-shm   # Shared memory (автоматически)
  attachments/     # Вложения чатов (файловая система)
```

Docker volume `aibolit-data` монтируется на `/app/data` для персистентности.

## Альтернативы

### 1. PostgreSQL

**Плюсы:**
- Полноценный concurrent access (MVCC)
- Встроенная поддержка Unicode (LOWER, ILIKE)
- Расширенные типы (JSONB, ARRAY, UUID)
- Full-text search
- Лучше для production с высокой нагрузкой
- Совместимость со стартовым шаблоном (Django ORM)

**Минусы:**
- Дополнительный сервис в docker-compose
- Управление миграциями, backup, monitoring
- Overhead для MVP с <100 пользователей
- Требует настройки connection pooling

**Отклонено для MVP:** Избыточная инфраструктура.

### 2. MySQL / MariaDB

**Плюсы:**
- Зрелая СУБД, широко используется
- Хорошая поддержка UTF-8

**Минусы:**
- Те же инфраструктурные затраты, что и PostgreSQL
- Менее мощный SQL-диалект
- Нет преимуществ над PostgreSQL для данного проекта

**Отклонено:** Нет преимуществ перед PostgreSQL или SQLite.

### 3. MongoDB

**Плюсы:**
- Гибкая schema для медицинских записей
- Нативный JSON

**Минусы:**
- Нет реляционной целостности (FK, CASCADE)
- Сложнее обеспечить consistency
- Не подходит для строго структурированных мед. данных

**Отклонено:** Реляционная целостность критична для медицинских данных.

## Последствия

### Положительные

1. **Zero-config deployment** — нет отдельного сервиса БД, файл создаётся автоматически.
2. **Простой backup** — копирование одного файла (`aibolit.db`).
3. **Нет зависимостей** — sqlite3 входит в Python stdlib.
4. **Транзакционность** — ACID через WAL mode.
5. **Достаточная производительность** — WAL позволяет параллельное чтение.
6. **Портативность** — БД можно скопировать на другую машину.

### Отрицательные

1. **Один writer** — в WAL mode запись сериализована, потенциальные задержки при >50 concurrent writes.
2. **Нет Unicode LOWER** — требуется Python-функция `PY_LOWER()`, медленнее нативного.
3. **Ручные миграции** — `schema_version` + ручной SQL вместо автоматических миграций.
4. **Нет full-text search** — для сложного поиска потребуется FTS5 расширение.
5. **Thread-local connections** — не работает с asyncio (используется sync sqlite3 в async FastAPI — допустимо для текущей нагрузки).
6. **Нет connection pooling** — каждый thread создаёт своё соединение.

### Ограничения масштабируемости

| Метрика | SQLite (текущее) | Ограничение |
|---------|-----------------|-------------|
| Concurrent readers | Unlimited | OK |
| Concurrent writers | 1 (serialized) | Bottleneck при >50 writes/sec |
| Max DB size | 281 TB (теоретически) | OK |
| Max row size | 1 GB | OK |
| Transactions/sec (write) | ~50-100 (WAL) | Достаточно для MVP |
| Transactions/sec (read) | ~10,000+ | Более чем достаточно |

### План миграции на PostgreSQL

При достижении ограничений (>100 concurrent users, >50 writes/sec):

```yaml
Этапы:
  1. Добавить PostgreSQL в docker-compose.yml
  2. Установить psycopg2 или asyncpg
  3. Рассмотреть SQLAlchemy как ORM (или сохранить raw SQL)
  4. Адаптировать SQL-запросы:
     - AUTOINCREMENT → SERIAL/BIGSERIAL
     - TEXT → VARCHAR с ограничениями
     - datetime('now') → NOW()
     - PY_LOWER() → LOWER() (нативная Unicode поддержка)
     - BLOB → BYTEA
  5. Написать скрипт миграции данных SQLite → PostgreSQL
  6. Обновить connection management (pool вместо thread-local)
  7. Настроить pg_dump для backup
  8. Обновить healthcheck

Трудозатраты: 3-5 дней
Совместимость: Текущая SQL-схема на 90% совместима с PostgreSQL
```

---

*Документ создан: Architect Agent | Дата: 2025-02-24*
