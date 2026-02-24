---
title: "Data Model — Aibolit AI"
created_by: "Data Agent"
created_at: "2025-02-24"
version: "1.0"
---

# Data Model — Aibolit AI

## 1. ER-диаграмма

```
+-------------------+       +-------------------+
|      users        |       |    patients        |
+-------------------+       +-------------------+
| PK id        INT  |       | PK id        TEXT  |
|    username  TEXT  |------>|    first_name TEXT  |
|    password_hash   |  FK   |    last_name  TEXT  |
|    patient_id TEXT |       |    date_of_birth   |
|    created_at      |       |    gender     TEXT  |
+-------------------+       |    blood_type TEXT  |
                             |    notes      TEXT  |
                             |    created_at       |
                             |    updated_at       |
                             +--------+----------+
                                      |
            +----------+---------+----+----+---------+----------+
            |          |         |         |         |          |
            v          v         v         v         v          v
     +----------+ +----------+ +-------+ +------+ +--------+ +--------+
     |allergies | |medications| |diagnoses| |lab_  | |vitals  | |family_ |
     +----------+ +----------+ +-------+ |results| +--------+ |history |
     |PK id     | |PK id     | |PK id  | +------+ |PK id   | +--------+
     |FK patient_| |FK patient_| |FK pat | |PK id | |FK pat  | |PK id  |
     |substance | |name      | |icd10_ | |FK pat | |timestamp| |FK pat |
     |reaction  | |dosage    | |code   | |test_  | |systolic_| |descrip|
     |severity  | |frequency | |name   | |name   | |bp      | +--------+
     +----------+ |route     | |date_  | |value  | |diastol_|
                  |start_date| |diagno | |unit   | |ic_bp   |   +--------+
                  |end_date  | |sed    | |ref_   | |heart_  |   |surgical|
                  |prescrib_ | |status | |range  | |rate    |   |_history|
                  |doctor    | |notes  | |date   | |temper_ |   +--------+
                  |notes     | |confid | |is_abn | |ature   |   |PK id  |
                  +----------+ |ence   | |ormal  | |spo2    |   |FK pat |
                               +-------+ |notes  | |respir_ |   |descrip|
                                          +------+ |atory   |   +--------+
                                                    |rate    |
                                                    |weight  |
                                                    |height  |
                                                    |blood_  |
                                                    |glucose |
                                                    +--------+

     +----------+     +---------------+     +---------------+
     |lifestyle | ... |genetic_markers| ... |  documents    |
     +----------+     +---------------+     +---------------+
     |PK id     |     |PK id          |     |PK id          |
     |FK patient|     |FK patient_id  |     |FK patient_id  |
     |key  TEXT |     |key       TEXT |     |file_name TEXT |
     |value TEXT|     |value     TEXT |     |file_type TEXT |
     +----------+     +---------------+     |file_size INT  |
                                            |content  BLOB  |
                                            |notes    TEXT  |
                                            |uploaded_at    |
                                            +---------------+

     +-------------------+     +-------------------+     +-------------------+
     |  consultations    |     |  chat_messages    |     | chat_attachments  |
     +-------------------+     +-------------------+     +-------------------+
     | PK id        INT  |<----|FK consultation_id |<----|FK consultation_id |
     | FK patient_id TEXT|     | PK id        INT  |     | PK id        INT  |
     |    specialty  TEXT |     |    role       TEXT |     | FK message_id INT |
     |    complaints TEXT |     |    content    TEXT |     |    file_name TEXT |
     |    response   TEXT |     |    metadata   TEXT |     |    file_type TEXT |
     |    date       TEXT |     |    created_at TEXT |     |    file_size INT  |
     |    status     TEXT |     +-------------------+     |    file_path TEXT |
     |    title      TEXT |                               |    created_at TEXT|
     |    session_id TEXT |                               +-------------------+
     |    created_at TEXT |
     +-------------------+

     +-------------------+
     |  schema_version   |
     +-------------------+
     | PK version   INT  |
     |    applied_at TEXT |
     +-------------------+
```

## 2. Описание сущностей

### 2.1 users — Пользователи (аутентификация)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный идентификатор |
| username | TEXT | UNIQUE, NOT NULL | Логин пользователя |
| password_hash | TEXT | NOT NULL | bcrypt или SHA-256+salt хеш пароля |
| patient_id | TEXT | FK → patients(id) | Привязка к карте пациента |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата создания аккаунта |

**Индексы:**
- `idx_users_username` ON users(username)
- `idx_users_patient` ON users(patient_id)

### 2.2 patients — Пациенты (основная карта)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | TEXT | PK | UUID[:8], например "7facb1f2" |
| first_name | TEXT | NOT NULL | Имя |
| last_name | TEXT | NOT NULL | Фамилия |
| date_of_birth | TEXT | NOT NULL | ISO формат: YYYY-MM-DD |
| gender | TEXT | NOT NULL, CHECK IN ('male','female','other') | Пол |
| blood_type | TEXT | NULL | Группа крови (A+, B-, AB+, O-, ...) |
| notes | TEXT | NOT NULL, DEFAULT '' | Заметки |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата создания |
| updated_at | TEXT | NOT NULL, DEFAULT now | Дата обновления |

### 2.3 allergies — Аллергии

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE CASCADE | Пациент |
| substance | TEXT | NOT NULL | Аллерген |
| reaction | TEXT | NOT NULL, DEFAULT '' | Реакция |
| severity | TEXT | NOT NULL, DEFAULT 'moderate' | mild / moderate / severe |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата записи |

**Индексы:** `idx_allergies_patient` ON allergies(patient_id)

### 2.4 medications — Назначения лекарств

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE CASCADE | Пациент |
| name | TEXT | NOT NULL | Название препарата |
| dosage | TEXT | NOT NULL | Дозировка |
| frequency | TEXT | NOT NULL | Частота приёма |
| route | TEXT | NOT NULL, DEFAULT 'oral' | Путь введения |
| start_date | TEXT | NULL | Дата начала (ISO) |
| end_date | TEXT | NULL | Дата окончания (ISO) |
| prescribing_doctor | TEXT | NOT NULL, DEFAULT '' | Назначивший врач |
| notes | TEXT | NOT NULL, DEFAULT '' | Примечания |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата записи |

**Индексы:** `idx_medications_patient` ON medications(patient_id)

### 2.5 diagnoses — Диагнозы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE CASCADE | Пациент |
| icd10_code | TEXT | NOT NULL | Код МКБ-10 (I10, E11, ...) |
| name | TEXT | NOT NULL | Название диагноза |
| date_diagnosed | TEXT | NOT NULL | Дата постановки (ISO) |
| status | TEXT | NOT NULL, DEFAULT 'active' | active / resolved / chronic |
| notes | TEXT | NOT NULL, DEFAULT '' | Примечания |
| confidence | REAL | NOT NULL, DEFAULT 0.0 | Уверенность AI (0.0 - 1.0) |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата записи |

**Индексы:**
- `idx_diagnoses_patient` ON diagnoses(patient_id)
- `idx_diagnoses_status` ON diagnoses(patient_id, status)
- `idx_diagnoses_icd10` ON diagnoses(icd10_code)

### 2.6 lab_results — Результаты анализов

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE CASCADE | Пациент |
| test_name | TEXT | NOT NULL | Название теста (hemoglobin, glucose, ...) |
| value | TEXT | NOT NULL | Значение (хранится как TEXT) |
| unit | TEXT | NOT NULL, DEFAULT '' | Единица измерения |
| reference_range | TEXT | NOT NULL, DEFAULT '' | Референсный диапазон |
| date | TEXT | NOT NULL | Дата анализа (ISO) |
| is_abnormal | INTEGER | NOT NULL, DEFAULT 0 | 0/1 — отклонение от нормы |
| notes | TEXT | NOT NULL, DEFAULT '' | Примечания |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата записи |

**Индексы:**
- `idx_lab_results_patient` ON lab_results(patient_id)
- `idx_lab_results_test` ON lab_results(patient_id, test_name)
- `idx_lab_results_date` ON lab_results(patient_id, date)

### 2.7 vitals — Витальные показатели

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE CASCADE | Пациент |
| timestamp | TEXT | NOT NULL | Дата и время измерения |
| systolic_bp | INTEGER | NULL | Систолическое АД (mmHg) |
| diastolic_bp | INTEGER | NULL | Диастолическое АД (mmHg) |
| heart_rate | INTEGER | NULL | ЧСС (уд/мин) |
| temperature | REAL | NULL | Температура (°C) |
| spo2 | REAL | NULL | Сатурация (%) |
| respiratory_rate | INTEGER | NULL | Частота дыхания (/мин) |
| weight | REAL | NULL | Вес (кг) |
| height | REAL | NULL | Рост (см) |
| blood_glucose | REAL | NULL | Глюкоза крови (ммоль/л) |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата записи |

**Индексы:**
- `idx_vitals_patient` ON vitals(patient_id)
- `idx_vitals_timestamp` ON vitals(patient_id, timestamp)

### 2.8 consultations — Консультации

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE SET NULL | Пациент |
| specialty | TEXT | NOT NULL | ID специализации (therapist, cardiologist, ...) |
| complaints | TEXT | NOT NULL | Жалобы пациента |
| response | TEXT | NOT NULL | Ответ AI (JSON для одноразовых, '' для чатов) |
| date | TEXT | NOT NULL, DEFAULT now | Дата консультации |
| status | TEXT | NOT NULL, DEFAULT 'legacy' | legacy / active / closed |
| title | TEXT | NOT NULL, DEFAULT '' | Заголовок чата |
| session_id | TEXT | NULL | Claude CLI session ID |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата записи |

**Индексы:**
- `idx_consultations_patient` ON consultations(patient_id)
- `idx_consultations_specialty` ON consultations(specialty)
- `idx_consultations_date` ON consultations(date)

### 2.9 chat_messages — Сообщения чата

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| consultation_id | INTEGER | FK → consultations(id) ON DELETE CASCADE | Консультация |
| role | TEXT | NOT NULL, CHECK IN ('user','assistant','system') | Роль отправителя |
| content | TEXT | NOT NULL | Текст сообщения |
| metadata | TEXT | NOT NULL, DEFAULT '{}' | JSON с дополнительными данными |
| created_at | TEXT | NOT NULL, DEFAULT now | Время отправки |

**Индексы:** `idx_chat_msg_consult` ON chat_messages(consultation_id)

### 2.10 chat_attachments — Вложения чата

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| consultation_id | INTEGER | FK → consultations(id) ON DELETE CASCADE | Консультация |
| message_id | INTEGER | FK → chat_messages(id) ON DELETE SET NULL | Сообщение |
| file_name | TEXT | NOT NULL | Имя файла |
| file_type | TEXT | NOT NULL | MIME-тип |
| file_size | INTEGER | NOT NULL | Размер в байтах |
| file_path | TEXT | NOT NULL | Путь к файлу на диске |
| created_at | TEXT | NOT NULL, DEFAULT now | Дата загрузки |

**Индексы:** `idx_chat_att_consult` ON chat_attachments(consultation_id)

### 2.11 documents — Медицинские документы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| id | INTEGER | PK, AUTOINCREMENT | Уникальный ID |
| patient_id | TEXT | FK → patients(id) ON DELETE CASCADE | Пациент |
| file_name | TEXT | NOT NULL | Имя файла |
| file_type | TEXT | NOT NULL, DEFAULT '' | MIME-тип |
| file_size | INTEGER | NOT NULL, DEFAULT 0 | Размер в байтах |
| content | BLOB | NOT NULL | Содержимое файла |
| notes | TEXT | NOT NULL, DEFAULT '' | Примечания |
| uploaded_at | TEXT | NOT NULL, DEFAULT now | Дата загрузки |

**Индексы:** `idx_documents_patient` ON documents(patient_id)

### 2.12 Вспомогательные таблицы

**family_history** — Семейный анамнез

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Уникальный ID |
| patient_id | TEXT FK | Пациент |
| description | TEXT | Описание |

**surgical_history** — Хирургический анамнез

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Уникальный ID |
| patient_id | TEXT FK | Пациент |
| description | TEXT | Описание |

**lifestyle** — Образ жизни (key-value)

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Уникальный ID |
| patient_id | TEXT FK | Пациент |
| key | TEXT | Ключ (smoking, alcohol, exercise, ...) |
| value | TEXT | Значение |

**genetic_markers** — Генетические маркеры (key-value)

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | Уникальный ID |
| patient_id | TEXT FK | Пациент |
| key | TEXT | Маркер |
| value | TEXT | Значение |

**schema_version** — Версионирование схемы

| Поле | Тип | Описание |
|------|-----|----------|
| version | INTEGER PK | Номер версии |
| applied_at | TEXT | Дата применения |

## 3. Связи между сущностями

```
users.patient_id        → patients.id       (N:1, опциональная)
allergies.patient_id    → patients.id       (N:1, CASCADE)
medications.patient_id  → patients.id       (N:1, CASCADE)
diagnoses.patient_id    → patients.id       (N:1, CASCADE)
lab_results.patient_id  → patients.id       (N:1, CASCADE)
vitals.patient_id       → patients.id       (N:1, CASCADE)
family_history.patient_id → patients.id     (N:1, CASCADE)
surgical_history.patient_id → patients.id   (N:1, CASCADE)
lifestyle.patient_id    → patients.id       (N:1, CASCADE)
genetic_markers.patient_id → patients.id    (N:1, CASCADE)
documents.patient_id    → patients.id       (N:1, CASCADE)
consultations.patient_id → patients.id      (N:1, SET NULL)
chat_messages.consultation_id → consultations.id (N:1, CASCADE)
chat_attachments.consultation_id → consultations.id (N:1, CASCADE)
chat_attachments.message_id → chat_messages.id (N:1, SET NULL)
```

**Правила каскадного удаления:**
- Удаление `patient` → удаляет все дочерние записи (аллергии, анализы, витальные, и т.д.)
- Удаление `patient` → `consultations.patient_id` = NULL (консультации сохраняются)
- Удаление `consultation` → удаляет все сообщения и вложения чата
- Удаление `chat_message` → `chat_attachments.message_id` = NULL

## 4. Сводка индексов

| Таблица | Индекс | Столбцы | Назначение |
|---------|--------|---------|------------|
| users | idx_users_username | username | Быстрый поиск при логине |
| users | idx_users_patient | patient_id | Привязка пользователя к пациенту |
| allergies | idx_allergies_patient | patient_id | Загрузка аллергий пациента |
| medications | idx_medications_patient | patient_id | Загрузка назначений |
| diagnoses | idx_diagnoses_patient | patient_id | Загрузка диагнозов |
| diagnoses | idx_diagnoses_status | patient_id, status | Фильтр по статусу |
| diagnoses | idx_diagnoses_icd10 | icd10_code | Поиск пациентов по МКБ-10 |
| lab_results | idx_lab_results_patient | patient_id | Загрузка анализов |
| lab_results | idx_lab_results_test | patient_id, test_name | Тренды по тесту |
| lab_results | idx_lab_results_date | patient_id, date | Хронология анализов |
| vitals | idx_vitals_patient | patient_id | Загрузка витальных |
| vitals | idx_vitals_timestamp | patient_id, timestamp | Хронология измерений |
| consultations | idx_consultations_patient | patient_id | История консультаций |
| consultations | idx_consultations_specialty | specialty | Фильтр по специализации |
| consultations | idx_consultations_date | date | Хронология консультаций |
| chat_messages | idx_chat_msg_consult | consultation_id | Сообщения консультации |
| chat_attachments | idx_chat_att_consult | consultation_id | Вложения консультации |
| documents | idx_documents_patient | patient_id | Документы пациента |
| family_history | idx_family_history_patient | patient_id | Семейный анамнез |
| surgical_history | idx_surgical_history_patient | patient_id | Хирургический анамнез |
| lifestyle | idx_lifestyle_patient | patient_id | Образ жизни |
| genetic_markers | idx_genetic_markers_patient | patient_id | Генетические маркеры |

## 5. Медицинские справочники (in-memory)

### 5.1 LAB_REFERENCE_RANGES

Словарь `dict[str, dict]` в `src/models/medical_refs.py` с референсными диапазонами для лабораторных тестов:

```python
LAB_REFERENCE_RANGES = {
    "hemoglobin_male":    {"name": "Гемоглобин (М)", "min": 130, "max": 170, "unit": "г/л"},
    "hemoglobin_female":  {"name": "Гемоглобин (Ж)", "min": 120, "max": 155, "unit": "г/л"},
    "leukocytes":         {"name": "Лейкоциты",      "min": 4.0, "max": 9.0, "unit": "10^9/л"},
    "glucose_fasting":    {"name": "Глюкоза натощак", "min": 3.9, "max": 6.1, "unit": "ммоль/л"},
    "total_cholesterol":  {"name": "Общий холестерин","min": 0,   "max": 5.2, "unit": "ммоль/л"},
    # ... 30+ тестов
}
```

Используется в:
- `diagnostics/analyze-labs` (API)
- `reference/lab-ranges` (API)
- Генерация контекста для AI-консультаций

### 5.2 DRUG_INTERACTIONS_CRITICAL

Словарь критических лекарственных взаимодействий:

```python
DRUG_INTERACTIONS_CRITICAL = {
    ("warfarin", "aspirin"): {"severity": "major", "warning": "..."},
    ("metformin", "alcohol"): {"severity": "moderate", "warning": "..."},
    # ... 20+ пар
}
```

Используется в: `diagnostics/drug-interactions` (API), `POST /drugs/interactions`

### 5.3 Specializations (35 штук)

Конфигурации AI-врачей в `src/agents/specializations.py`:

```python
@dataclass
class Specialization:
    id: str                          # "cardiologist"
    name_ru: str                     # "Кардиолог"
    name_en: str                     # "Cardiologist"
    description: str                 # Описание компетенций
    skills: list[MedicalSkill]       # Навыки AI-врача
    related_icd_prefixes: list[str]  # ["I10", "I20", "I25"]
    required_lab_tests: list[str]    # ["total_cholesterol", "ldl"]
```

ID специализаций: therapist, cardiologist, neurologist, gastroenterologist, pulmonologist, endocrinologist, rheumatologist, nephrologist, hematologist, dermatologist, allergist, ophthalmologist, otolaryngologist, urologist, gynecologist, orthopedist, surgeon, oncologist, psychiatrist, pediatrician, infectious_disease, geriatrician, phlebologist, proctologist, immunologist, geneticist, nutritionist, sports_medicine, rehabilitation, pain_management, palliative_care, sleep_medicine, toxicologist, emergency_medicine, sexologist.

## 6. Планируемая модель: AuditLog

```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL DEFAULT (datetime('now')),
    level           TEXT NOT NULL DEFAULT 'INFO',        -- DEBUG/INFO/WARNING/ERROR/CRITICAL
    category        TEXT NOT NULL DEFAULT 'general',     -- auth/crud/medical/event/task
    action          TEXT NOT NULL,                       -- login/create/update/delete/...
    entity_type     TEXT,                                -- patient/user/consultation/...
    entity_id       TEXT,                                -- ID сущности
    actor_type      TEXT NOT NULL DEFAULT 'system',      -- user/system
    actor_id        TEXT,                                -- ID пользователя или 'system'
    actor_name      TEXT,                                -- username или 'system'
    message         TEXT NOT NULL DEFAULT '',             -- Человекочитаемое описание
    data            TEXT NOT NULL DEFAULT '{}',           -- JSON с деталями (masked)
    old_values      TEXT,                                -- JSON предыдущих значений (для update)
    ip_address      TEXT,                                -- IP клиента
    user_agent      TEXT,                                -- User-Agent браузера
    request_id      TEXT,                                -- UUID запроса для корреляции
    duration_ms     INTEGER,                             -- Длительность операции
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_logs(category);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_level ON audit_logs(level);
```

**Retention:** 5 лет для медицинских событий (category='medical'), 90 дней для остальных.

## 7. Стратегия шифрования медицинских данных

### 7.1 Алгоритм

**Fernet** (из библиотеки `cryptography`):
- AES-128 в режиме CBC
- HMAC-SHA256 для аутентификации
- Автоматическое включение timestamp и IV
- Симметричный ключ 32 байта (base64-encoded)

### 7.2 Шифруемые поля

| Таблица | Поле | Причина |
|---------|------|---------|
| patients | notes | Может содержать мед. данные |
| allergies | substance | Медицинская информация |
| allergies | reaction | Медицинская информация |
| medications | name | Лекарственная информация |
| medications | notes | Медицинские заметки |
| diagnoses | name | Диагноз — врачебная тайна |
| diagnoses | notes | Медицинские заметки |
| lab_results | value | Результат анализа |
| lab_results | notes | Медицинские заметки |
| consultations | complaints | Жалобы — мед. данные |
| consultations | response | Ответ AI — мед. данные |
| chat_messages | content | Содержание чата — мед. данные |
| documents | content | Медицинские документы (BLOB) |

### 7.3 Key Management

```
1. Ключ шифрования: AIBOLIT_ENCRYPTION_KEY (env var)
   - Формат: Fernet.generate_key() → base64-encoded 32 bytes
   - Генерируется при первом запуске, если не задан
   - В production: секрет из vault / env var

2. Хранение ключа:
   - НЕ в коде и НЕ в БД
   - В переменной окружения (docker-compose.yml)
   - Для production: HashiCorp Vault / AWS Secrets Manager

3. Ротация ключей:
   - Offline-скрипт: decrypt all → re-encrypt with new key
   - Downtime required (или двойное чтение на период миграции)

4. Потеря ключа:
   - Данные невосстановимы
   - Backup ключа в защищённом месте обязателен
```

### 7.4 Реализация (планируемая)

```python
# src/utils/encryption.py

from cryptography.fernet import Fernet
import os

_KEY = os.environ.get("AIBOLIT_ENCRYPTION_KEY")
_fernet = Fernet(_KEY.encode()) if _KEY else None

def encrypt(plaintext: str) -> str:
    """Encrypt string. Returns base64-encoded ciphertext."""
    if not _fernet:
        return plaintext  # Fallback: no encryption
    return _fernet.encrypt(plaintext.encode()).decode()

def decrypt(ciphertext: str) -> str:
    """Decrypt base64-encoded ciphertext."""
    if not _fernet:
        return ciphertext
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ciphertext  # Fallback: already plaintext

def encrypt_blob(data: bytes) -> bytes:
    """Encrypt binary data."""
    if not _fernet:
        return data
    return _fernet.encrypt(data)

def decrypt_blob(data: bytes) -> bytes:
    """Decrypt binary data."""
    if not _fernet:
        return data
    try:
        return _fernet.decrypt(data)
    except Exception:
        return data
```

### 7.5 Миграция существующих данных

```
1. Добавить AIBOLIT_ENCRYPTION_KEY в окружение
2. Запустить миграционный скрипт:
   - Прочитать все записи с незашифрованными полями
   - Зашифровать и обновить
   - Пометить version в schema_version
3. Обновить все read/write операции для encrypt/decrypt
```

## 8. Особенности SQLite

### 8.1 WAL Mode

```sql
PRAGMA journal_mode = WAL;  -- Write-Ahead Logging
```

Преимущества:
- Множественные читатели одновременно
- Писатель не блокирует читателей
- Лучшая производительность для read-heavy нагрузки

### 8.2 Foreign Keys

```sql
PRAGMA foreign_keys = ON;   -- Включение проверки FK
```

Обязательно при каждом подключении (SQLite по умолчанию отключает FK).

### 8.3 Busy Timeout

```sql
PRAGMA busy_timeout = 5000; -- 5 секунд ожидания блокировки
```

Предотвращает ошибки `database is locked` при concurrent writes.

### 8.4 Thread-Local Connections

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

Каждый поток Uvicorn получает свой connection. Row factory обеспечивает dict-like доступ.

### 8.5 Unicode LOWER

SQLite встроенная LOWER() не поддерживает кириллицу. Зарегистрирована Python-функция:

```python
conn.create_function("PY_LOWER", 1, str.lower)
```

Используется для case-insensitive поиска пациентов и лабораторных трендов.

---

*Документ создан: Data Agent | Дата: 2025-02-24*
