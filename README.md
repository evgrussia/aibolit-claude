# Aibolit — AI Medical Clinic

> Виртуальная медицинская клиника с 35 AI-врачами, MCP-сервером для Claude и полноценным веб-порталом.

---

## Содержание

1. [Обзор системы](#обзор-системы)
2. [Быстрый старт](#быстрый-старт)
3. [Установка и запуск](#установка-и-запуск)
   - [Docker (рекомендуется)](#вариант-1-docker-рекомендуется)
   - [Локальная установка](#вариант-2-локальная-установка)
4. [MCP-сервер: интеграция с Claude](#mcp-сервер-интеграция-с-claude)
5. [Веб-портал](#веб-портал)
6. [Аутентификация](#аутентификация)
7. [Диагностические инструменты](#диагностические-инструменты)
8. [Справочник API](#справочник-api)
9. [35 Специализаций врачей](#35-специализаций-врачей)
10. [Примеры использования](#примеры-использования)
11. [Архитектура](#архитектура)
12. [Разработка](#разработка)
13. [FAQ](#faq)
14. [Отказ от ответственности](#отказ-от-ответственности)

---

## Обзор системы

**Aibolit** — это агентская система виртуальной медицинской клиники, которая работает в двух режимах:

| Режим | Описание |
|---|---|
| **MCP-сервер** | 31 инструмент для Claude.ai и Claude Code |
| **Веб-портал** | React-приложение с FastAPI бэкендом (порт 8007) |

### Что умеет система

- **Консультации у 35 AI-врачей** — от терапевта до нейрохирурга и врача скорой помощи
- **Расшифровка анализов** — 67 лабораторных показателей с автоматическим выявлением паттернов
- **Оценка витальных показателей** — АД, пульс, SpO2, температура, глюкоза
- **Расчёт СКФ** по формуле CKD-EPI 2021 со стадированием ХБП
- **10-летний СС-риск** по модели SCORE2
- **Информация о лекарствах** — показания, противопоказания, побочные эффекты из базы FDA
- **Проверка взаимодействий** — 12 критических пар + RxNorm API
- **Поиск литературы** в PubMed и клинических исследований на ClinicalTrials.gov
- **Генерация документов** — рецепты, направления, выписные эпикризы
- **Ведение пациентов** — регистрация, история анализов, витальных показателей, консультаций
- **Аутентификация** — JWT-авторизация, регистрация пациентов через веб-портал

---

## Быстрый старт

### Вариант A: Docker (одна команда)

```bash
git clone https://github.com/evgrussia/aibolit-claude.git
cd aibolit-claude
docker compose up -d
```

Откройте http://localhost — зарегистрируйтесь и начните работу.

### Вариант B: MCP-сервер (для Claude.ai / Claude Code)

```bash
git clone https://github.com/evgrussia/aibolit-claude.git
cd aibolit-claude
pip install -e .
```

Добавьте в конфигурацию Claude (подробнее в разделе [MCP-сервер](#mcp-сервер-интеграция-с-claude)):
```json
{
  "mcpServers": {
    "aibolit-clinic": {
      "command": "python",
      "args": ["run.py"],
      "cwd": "/path/to/aibolit-claude"
    }
  }
}
```

### Вариант C: Локальная разработка

```bash
git clone https://github.com/evgrussia/aibolit-claude.git
cd aibolit-claude

# Бэкенд
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart
python -m uvicorn web.backend.main:app --reload --port 8007

# Фронтенд (в другом терминале)
cd web/frontend
npm install
npm run dev
```

Откройте http://localhost:5173

---

## Установка и запуск

### Вариант 1: Docker (рекомендуется)

Docker — самый простой способ запустить систему. Все зависимости, сборка фронтенда и настройка nginx происходят автоматически.

#### Требования

| Компонент | Версия |
|---|---|
| Docker | 20.10+ |
| Docker Compose | v2+ |

#### Шаг 1: Клонирование

```bash
git clone https://github.com/evgrussia/aibolit-claude.git
cd aibolit-claude
```

#### Шаг 2: Настройка (опционально)

Создайте файл `.env` для переопределения параметров:

```env
# Секретный ключ для JWT-токенов (обязательно менять в продакшене!)
AIBOLIT_SECRET_KEY=my-super-secret-key

# Порт для доступа к приложению (по умолчанию 80)
PORT=8080
```

Если `.env` не создан, используются значения по умолчанию.

#### Шаг 3: Сборка и запуск

```bash
# Сборка образов (первый раз займёт 2-3 минуты)
docker compose build

# Запуск в фоне
docker compose up -d
```

#### Шаг 4: Проверка

```bash
# Проверка здоровья бэкенда
curl http://localhost/api/health
# → {"status":"ok","service":"aibolit-portal"}

# Просмотр логов
docker compose logs -f

# Статус контейнеров
docker compose ps
```

Откройте http://localhost (или http://localhost:8080 если указали `PORT=8080`) — должна загрузиться страница входа.

#### Управление

```bash
# Остановить
docker compose down

# Остановить и удалить данные (база пациентов!)
docker compose down -v

# Пересобрать после изменений кода
docker compose build && docker compose up -d

# Посмотреть логи бэкенда
docker compose logs backend

# Посмотреть логи nginx
docker compose logs nginx
```

#### Архитектура Docker

```
             :80 (или PORT)
              │
       ┌──────────────┐
       │     nginx     │
       │  (контейнер)  │
       │               │
       │  /api/* ──────────► backend:8007
       │  /*    → dist/ │    (контейнер)
       └──────────────┘
              │
       [named volume]  ← SQLite (aibolit-data)
```

- **nginx** — раздаёт собранный React SPA и проксирует `/api/` на бэкенд
- **backend** — Python/FastAPI, слушает порт 8007 внутри Docker-сети
- **aibolit-data** — именованный Docker-том для хранения SQLite базы

---

### Вариант 2: Локальная установка

Для разработки или если Docker не доступен.

#### Требования

| Компонент | Версия |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

#### Шаг 1: Клонирование и Python-зависимости

```bash
git clone https://github.com/evgrussia/aibolit-claude.git
cd aibolit-claude

# Установка как пакет (включает MCP-сервер)
pip install -e .

# Дополнительно для веб-портала
pip install fastapi uvicorn[standard] python-multipart PyJWT
# или всё сразу:
pip install -r requirements.txt fastapi uvicorn[standard] python-multipart
```

#### Шаг 2: Node-зависимости (для веб-портала)

```bash
cd web/frontend
npm install
cd ../..
```

#### Шаг 3: Инициализация базы данных

База данных SQLite создаётся **автоматически** при первом запуске в `data/aibolit.db`.

Если есть данные пациентов в формате JSON (`data/patients/*.json`), они автоматически мигрируются при первом запуске.

Ручная миграция:
```bash
python scripts/migrate_json_to_sqlite.py
```

#### Шаг 4: Запуск бэкенда

```bash
python -m uvicorn web.backend.main:app --reload --port 8007
```

Проверка:
```bash
curl http://localhost:8007/api/health
# → {"status":"ok","service":"aibolit-portal"}
```

#### Шаг 5: Запуск фронтенда (в другом терминале)

```bash
cd web/frontend
npm run dev
```

Фронтенд запустится на http://localhost:5173 и автоматически проксирует `/api/` запросы на бэкенд (порт 8007).

#### Шаг 6: Работа с системой

1. Откройте http://localhost:5173
2. Зарегистрируйтесь (логин, пароль, ФИО, дата рождения, пол)
3. После входа — попадёте на дашборд со своей медкартой

---

## MCP-сервер: интеграция с Claude

MCP-сервер предоставляет 31 инструмент, которые Claude вызывает автоматически во время диалога.

### Конфигурация для Claude Desktop

Файл конфигурации:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aibolit-clinic": {
      "command": "python",
      "args": ["run.py"],
      "cwd": "C:\\path\\to\\aibolit-claude"
    }
  }
}
```

> `run.py` — лаунчер, который корректно настраивает пути модулей на любой ОС.

### Конфигурация для Claude Code

Файл `.claude/settings.json` или глобальный конфиг:

```json
{
  "mcpServers": {
    "aibolit-clinic": {
      "command": "python",
      "args": ["run.py"],
      "cwd": "/path/to/aibolit-claude"
    }
  }
}
```

### Пример диалога с Claude

```
Пользователь: У меня болит голова уже 3 дня, особенно утром. Давление 145/95.

Claude: [вызывает clinic_reception → consult_doctor(specialty="neurologist")]

Невролог: Нарушение неврологического характера с элементами гипертензии...
Рекомендую дополнительно проверить АД в динамике и сдать ОАК.
```

### Доступные MCP-инструменты (31 tool)

| Категория | Инструменты |
|---|---|
| Навигация | `clinic_reception`, `list_doctors`, `consult_doctor` |
| Диагностика | `analyze_lab_results`, `assess_vitals`, `calculate_gfr`, `cardiovascular_risk` |
| Лекарства | `drug_info`, `check_drug_interactions`, `drug_adverse_events`, `check_drug_recall` |
| Литература | `search_medical_literature`, `get_article_abstract`, `search_clinical_trials` |
| Классификация | `search_icd`, `search_snomed` |
| Генетика | `gene_info`, `search_genetic_disorders`, `search_drug_targets` |
| Документы | `generate_medical_record`, `generate_referral`, `generate_prescription`, `generate_discharge_summary` |
| Пациенты | `register_patient`, `get_patient`, `list_patients`, `add_vitals`, `add_lab_result`, `add_diagnosis`, `add_medication`, `lab_reference_ranges` |
| История | `get_consultation_history`, `get_lab_trends`, `get_vitals_history`, `search_patients`, `get_patients_by_diagnosis` |

---

## Веб-портал

### Страницы

| Путь | Описание |
|---|---|
| `/login` | Вход и регистрация |
| `/patients/:id` | Дашборд пациента |
| `/patients/:id/labs` | Анализы и графики трендов |
| `/patients/:id/vitals` | Витальные показатели |
| `/patients/:id/consultations` | История консультаций AI-врачей |
| `/diagnostics` | Диагностические инструменты (4 вкладки) |
| `/drugs` | Информация о лекарствах и взаимодействия |
| `/documents` | Генератор документов (рецепты, направления) |

### Дашборд пациента (`/patients/:id`)

- **Карточка пациента** — ФИО, возраст, пол, группа крови, аллергии
- **Витальные показатели** — последние измерения (4 индикатора)
- **Диагнозы** — список с кодами МКБ-10
- **Назначенные препараты** — название, дозировка, кратность
- **Семейный анамнез**

### Анализы (`/patients/:id/labs`)

- Таблица всех результатов анализов
- Подсветка отклонений (норма / повышено / критически)
- **График трендов** — динамика любого показателя за всё время

### Витальные показатели (`/patients/:id/vitals`)

- Хронологическая таблица измерений
- **График АД** — систолическое и диастолическое давление в динамике

---

## Аутентификация

Веб-портал использует JWT-авторизацию.

### Регистрация

1. Откройте `/login` → вкладка «Регистрация»
2. Шаг 1: Логин и пароль (мин. 4 символа)
3. Шаг 2: ФИО, дата рождения, пол
4. Шаг 3: Группа крови, аллергии (опционально)
5. При регистрации автоматически создаётся медкарта пациента

### Вход

- Логин + пароль → JWT-токен (действителен 7 дней)
- Токен хранится в `localStorage` браузера
- После входа — автоматический переход на дашборд пациента

### API-аутентификация

```bash
# Регистрация
curl -X POST http://localhost:8007/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"ivan","password":"1234","first_name":"Иван","last_name":"Иванов","date_of_birth":"1985-03-15","gender":"male"}'

# Вход
curl -X POST http://localhost:8007/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ivan","password":"1234"}'
# → {"token":"eyJ...","patient_id":"7facb1f2","username":"ivan"}

# Защищённый запрос
curl http://localhost:8007/api/v1/auth/me \
  -H "Authorization: Bearer eyJ..."
```

---

## Диагностические инструменты

Раздел `/diagnostics` содержит 4 инструмента:

### 1. Анализ лабораторных показателей

| Показатель | Код | Единицы | Норма (муж.) | Норма (жен.) |
|---|---|---|---|---|
| Гемоглобин | `hemoglobin` | г/л | 130–170 | 120–150 |
| Глюкоза натощак | `glucose_fasting` | ммоль/л | 3.9–6.1 | 3.9–6.1 |
| АЛТ | `alt` | Ед/л | ≤41 | ≤31 |
| АСТ | `ast` | Ед/л | ≤40 | ≤35 |
| Креатинин | `creatinine` | мкмоль/л | 62–115 | 44–97 |
| Холестерин общий | `total_cholesterol` | ммоль/л | 3.0–5.2 | 3.0–5.2 |
| ТТГ | `tsh` | мкМЕ/мл | 0.4–4.0 | 0.4–4.0 |
| HbA1c | `hba1c` | % | <6.0 | <6.0 |

Результат: таблица с интерпретацией, критические отклонения, выявленные паттерны, итоговое заключение.

### 2. Оценка витальных показателей

| Показатель | Норма | Критические значения |
|---|---|---|
| АД систолическое | 90–130 мм рт.ст. | >180 или <80 |
| АД диастолическое | 60–85 мм рт.ст. | >120 или <50 |
| ЧСС | 60–100 уд/мин | >150 или <40 |
| Температура | 36.0–37.0 °C | >40.0 или <35.0 |
| SpO2 | 95–100% | <90% |
| ЧД | 12–20 /мин | >30 или <8 |
| Глюкоза | 3.9–6.1 ммоль/л | >15 или <2.8 |

### 3. Расчёт СКФ (CKD-EPI)

Требуется: **Креатинин** (мкмоль/л), **Возраст** (лет), **Пол**.

| Стадия | СКФ | Интерпретация |
|---|---|---|
| G1 | ≥ 90 | Нормальная или высокая функция |
| G2 | 60–89 | Лёгкое снижение |
| G3a | 45–59 | Умеренное снижение |
| G3b | 30–44 | Значимое снижение |
| G4 | 15–29 | Выраженное снижение |
| G5 | < 15 | Почечная недостаточность |

### 4. Сердечно-сосудистый риск (SCORE2)

Обязательные поля: Возраст, АД систолическое, Холестерин общий, ЛПВП.
Опциональные: Пол, Курение, Сахарный диабет, Лечение АД.

| Уровень риска | 10-летний риск |
|---|---|
| Низкий | < 5% |
| Умеренный | 5–9% |
| Высокий | ≥ 10% |

---

## Лекарства (`/drugs`)

### Поиск препарата

Используется база данных **OpenFDA** (США). Поиск **только на английском языке** (МНН).

Примеры: `metformin`, `lisinopril`, `warfarin`, `ibuprofen`, `atorvastatin`

### Проверка взаимодействий

Две базы данных:
1. Локальная база 12 критических пар (мгновенно)
2. **RxNorm API** (NLM/NIH) — расширенная проверка

**Критические взаимодействия** (встроенная база):

| Пара | Риск |
|---|---|
| Warfarin + Aspirin | Кровотечение |
| MAO inhibitors + SSRIs | Серотониновый синдром |
| Metformin + Alcohol | Лактоацидоз |
| Digoxin + Amiodarone | Токсичность дигоксина |
| Statins + Fibrates | Рабдомиолиз |

---

## Документы (`/documents`)

### Рецепт

1. Введите **ФИО пациента**
2. Укажите **диагнозы** (каждый с новой строки)
3. Добавьте препараты: название, доза, кратность, путь введения, длительность
4. Нажмите **«Сформировать рецепт»**

Готовый документ можно **скопировать** или **скачать** как `.txt`.

### Направление к специалисту

1. ФИО и возраст пациента
2. Специальность направляющего врача
3. Специальность получателя
4. Срочность: Плановое / Срочное / Экстренное
5. Причина направления

---

## Справочник API

### Базовый URL

| Режим | URL |
|---|---|
| Локальная разработка | `http://localhost:8007/api/v1` |
| Docker | `http://localhost/api/v1` (или `PORT` из `.env`) |

### Аутентификация

| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | Регистрация (создаёт пользователя + пациента) |
| POST | `/auth/login` | Вход (возвращает JWT-токен) |
| GET | `/auth/me` | Текущий пользователь (требует токен) |

### Пациенты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/patients` | Список всех пациентов |
| GET | `/patients/search?q=иванов` | Поиск по имени |
| GET | `/patients/by-diagnosis?icd10=E11` | По коду МКБ-10 |
| POST | `/patients` | Регистрация пациента |
| GET | `/patients/{id}` | Карта пациента |
| DELETE | `/patients/{id}` | Удалить пациента |
| POST | `/patients/{id}/vitals` | Записать витальные |
| POST | `/patients/{id}/labs` | Добавить анализ |
| POST | `/patients/{id}/diagnoses` | Добавить диагноз |
| POST | `/patients/{id}/medications` | Добавить препарат |
| GET | `/patients/{id}/lab-trends?test=glucose_fasting` | Тренд показателя |
| GET | `/patients/{id}/vitals-history` | История витальных |

### Диагностика

| Метод | Путь | Описание |
|---|---|---|
| POST | `/diagnostics/analyze-labs` | Анализ анализов |
| POST | `/diagnostics/assess-vitals` | Оценка витальных |
| POST | `/diagnostics/calculate-gfr` | Расчёт СКФ |
| POST | `/diagnostics/cardiovascular-risk` | СС-риск |

**Пример: Расчёт СКФ**
```bash
curl -X POST http://localhost:8007/api/v1/diagnostics/calculate-gfr \
  -H "Content-Type: application/json" \
  -d '{"creatinine": 92, "age": 39, "gender": "male"}'
```
```json
{
  "gfr": 93.6,
  "stage": "G1 — нормальная или высокая функция почек",
  "recommendation": "Регулярный мониторинг АД и анализов мочи"
}
```

### Лекарства

| Метод | Путь | Описание |
|---|---|---|
| GET | `/drugs/{drug_name}` | Информация о препарате |
| GET | `/drugs/{drug_name}/adverse-events` | Нежелательные эффекты |
| POST | `/drugs/interactions` | Проверка взаимодействий |

**Пример: Взаимодействия**
```bash
curl -X POST http://localhost:8007/api/v1/drugs/interactions \
  -H "Content-Type: application/json" \
  -d '{"drugs": ["warfarin", "aspirin"]}'
```

### Документы

| Метод | Путь | Описание |
|---|---|---|
| POST | `/documents/prescription` | Рецепт |
| POST | `/documents/referral` | Направление |
| POST | `/documents/medical-record` | Медкарта |
| POST | `/documents/discharge-summary` | Эпикриз |

### Health check

```bash
# Работает без аутентификации
curl http://localhost:8007/api/health
# → {"status":"ok","service":"aibolit-portal"}
```

---

## 35 Специализаций врачей

### Терапевтические

| ID | Название | Ключевые навыки |
|---|---|---|
| `therapist` | Терапевт | Первичный приём, дифференциальная диагностика, направления |
| `cardiologist` | Кардиолог | ЭКГ, СС-риск, гипертония, ИБС, аритмии |
| `neurologist` | Невролог | Головная боль, инсульт, эпилепсия, нейропатии |
| `pulmonologist` | Пульмонолог | Астма, ХОБЛ, пневмония, ФВД |
| `gastroenterologist` | Гастроэнтеролог | ЖКТ, печень, поджелудочная железа |
| `endocrinologist` | Эндокринолог | Диабет, щитовидная железа, гормоны |
| `nephrologist` | Нефролог | ХБП, СКФ, нефриты, диализ |
| `rheumatologist` | Ревматолог | Артриты, СКВ, подагра, системные заболевания |
| `hematologist` | Гематолог | ОАК, анемии, лейкозы, коагуляция |
| `infectionist` | Инфекционист | Инфекции, антибиотикотерапия, сепсис |
| `allergist` | Аллерголог-иммунолог | Аллергии, астма, иммунодефициты |
| `geriatrician` | Гериатр | Пожилые пациенты, полипрагмазия, деменция |

### Хирургические

| ID | Название | Ключевые навыки |
|---|---|---|
| `surgeon` | Хирург | Брюшная полость, грыжи, аппендицит |
| `cardiac_surgeon` | Кардиохирург | Шунтирование, клапаны, врождённые пороки |
| `neurosurgeon` | Нейрохирург | Опухоли мозга, травмы, стенозы |
| `vascular_surgeon` | Сосудистый хирург | Атеросклероз, аневризмы, тромбозы |
| `orthopedist` | Травматолог-ортопед | Переломы, суставы, позвоночник |
| `urologist` | Уролог | Почки, мочевой пузырь, простата |

### Специализированные

| ID | Название | Ключевые навыки |
|---|---|---|
| `oncologist` | Онколог | Диагностика, стадирование, химиотерапия |
| `dermatologist` | Дерматолог | Кожные заболевания, дерматоскопия |
| `ophthalmologist` | Офтальмолог | Глаукома, катаракта, диабетическая ретинопатия |
| `ent` | ЛОР | Уши, горло, нос |
| `gynecologist` | Гинеколог | Женские болезни, беременность |
| `pediatrician` | Педиатр | Дети от 0 до 18 лет, вакцинация |
| `psychiatrist` | Психиатр | Депрессия, тревога, психозы, нейролептики |
| `dentist` | Стоматолог | Кариес, пародонт, ортодонтия |
| `nutritionist` | Диетолог | Питание, ожирение, метаболический синдром |
| `sports_medicine` | Спортивный врач | Спортивные травмы, допинг, физическая нагрузка |
| `rehabilitation` | Реабилитолог | ЛФК, физиотерапия, восстановление |
| `geneticist` | Генетик | Наследственные болезни, фармакогенетика |

### Экстренные и диагностические

| ID | Название | Ключевые навыки |
|---|---|---|
| `emergency` | Врач скорой | Острые состояния, АВС, неотложная помощь |
| `intensivist` | Реаниматолог | ИВЛ, сепсис, интенсивная терапия |
| `radiologist` | Радиолог | КТ, МРТ, УЗИ, рентген |
| `pathologist` | Патологоанатом | Биопсия, гистология, аутопсия |
| `pharmacologist` | Клинический фармаколог | Взаимодействия, дозирование, побочные эффекты |

---

## Примеры использования

### Пример 1: Экстренная консультация (MCP)

```
Пользователь: У меня острая боль в груди справа при вдохе, одышка, температура 38.5

Claude:
[clinic_reception → consult_doctor(specialty="pulmonologist")]

Пульмонолог: По симптоматике — правосторонняя пневмония или плеврит.
SpO2 93% — показана оксигенотерапия.
Рекомендую: R-графия грудной клетки, ОАК с лейкоцитарной формулой, С-РБ.
```

### Пример 2: Расшифровка анализов (MCP)

```
Пользователь: Расшифруй мои анализы:
  глюкоза 7.8 ммоль/л, HbA1c 7.1%, холестерин 6.4, ЛПВП 0.9

Claude:
[analyze_lab_results(...)]

⚠️ Критические отклонения: HbA1c 7.1% — декомпенсация диабета

Выявленные паттерны:
• Сахарный диабет 2 типа (плохо контролируемый — HbA1c >7%)
• Дислипидемия (холестерин >6.2, ЛПВП снижен)
```

### Пример 3: Работа через веб-портал

1. Откройте http://localhost (Docker) или http://localhost:5173 (локально)
2. Зарегистрируйтесь → автоматически создастся медкарта
3. На дашборде — обзор состояния, витальные, диагнозы
4. **Анализы** → выберите показатель → смотрите тренд
5. **Диагностика** → введите значения → получите интерпретацию
6. **Документы** → заполните форму → скачайте готовый документ

### Пример 4: Проверка лекарственного назначения (MCP)

```
Пользователь: Пациенту назначили варфарин + аспирин + омепразол. Безопасно?

Claude:
[check_drug_interactions(drugs=["warfarin", "aspirin", "omeprazole"])]

warfarin + aspirin: MAJOR — Повышенный риск кровотечения.
omeprazole + warfarin: MODERATE — Мониторинг МНО обязателен.
```

---

## Архитектура

```
aibolit-claude/
├── src/                           # MCP-сервер
│   ├── mcp_server.py              # Главная точка входа, 31 tool
│   ├── agents/
│   │   ├── doctor.py              # Базовый класс врача
│   │   └── specializations.py     # 35 специализаций
│   ├── tools/
│   │   ├── diagnostic.py          # CKD-EPI, SCORE2, анализ анализов
│   │   └── documentation.py       # Генерация документов
│   ├── integrations/
│   │   ├── pubmed.py              # PubMed + ClinicalTrials.gov
│   │   ├── openfda.py             # FDA (препараты, FAERS, отзывы)
│   │   ├── who_icd.py             # ICD-11
│   │   └── medical_apis.py        # RxNorm, SNOMED, NCBI Gene, OMIM
│   ├── models/
│   │   ├── patient.py             # Датаклассы Patient, VitalSigns, ...
│   │   └── medical_refs.py        # 67 показателей, нормы, МКБ-10
│   └── utils/
│       ├── database.py            # SQLite-бэкенд (11 таблиц, WAL)
│       └── patient_db.py          # Обратная совместимость
│
├── web/
│   ├── backend/                   # FastAPI (порт 8007)
│   │   ├── main.py                # App + 8 роутеров
│   │   ├── config.py              # CORS, JWT-настройки
│   │   ├── auth.py                # JWT-хелперы (hash, verify, token)
│   │   ├── routers/               # auth, patients, diagnostics, drugs, ...
│   │   └── schemas/               # Pydantic-модели
│   └── frontend/                  # React + Vite + Tailwind v3
│       └── src/
│           ├── pages/             # LoginPage, DashboardPage, ...
│           ├── components/        # Layout, Charts, Forms, Shared
│           ├── contexts/          # AuthContext, ToastContext
│           ├── hooks/             # React Query хуки
│           ├── api/               # Axios-клиенты
│           └── types/             # TypeScript-интерфейсы
│
├── nginx/
│   └── nginx.conf                 # Конфиг для Docker (proxy + SPA)
│
├── data/
│   └── aibolit.db                 # SQLite (создаётся автоматически)
│
├── Dockerfile                     # Multi-stage (frontend-build → backend → nginx)
├── docker-compose.yml             # 2 сервиса: backend + nginx
├── .dockerignore
├── run.py                         # Лаунчер MCP-сервера
├── requirements.txt               # Python-зависимости
└── pyproject.toml                 # Метаданные пакета
```

### База данных (SQLite, WAL-режим)

| Таблица | Описание | Ключевые поля |
|---|---|---|
| `patients` | Основные данные | id, first_name, last_name, dob, gender, blood_type |
| `users` | Аутентификация | id, username, password_hash, patient_id |
| `allergies` | Аллергии | patient_id, substance, reaction, severity |
| `medications` | Препараты | patient_id, name, dosage, frequency, route |
| `diagnoses` | Диагнозы МКБ-10 | patient_id, icd10_code, name, status, confidence |
| `lab_results` | Анализы | patient_id, test_name, value, unit, timestamp |
| `vitals` | Витальные | patient_id, systolic_bp, heart_rate, spo2, ... |
| `family_history` | Семейный анамнез | patient_id, condition |
| `consultations` | История консультаций | patient_id, specialty, diagnosis, plan |
| `documents` | Загруженные документы | patient_id, file_name, content |
| `lifestyle` | Образ жизни | patient_id, key, value |
| `genetic_markers` | Генетика | patient_id, gene, variant |

### Внешние API (все бесплатные, без ключей)

| Сервис | Назначение | Лимиты |
|---|---|---|
| PubMed E-utilities | Медицинская литература | 3 запроса/сек |
| OpenFDA | Препараты, FAERS, отзывы | 1000 запросов/день |
| RxNorm (NLM) | Нормализация, взаимодействия | Без лимита |
| WHO ICD-11 API | Классификация болезней | Без лимита |
| SNOMED CT | Клиническая терминология | Без лимита |
| ClinicalTrials.gov | Клинические исследования | Без лимита |
| NCBI Gene | Генетическая информация | 3 запроса/сек |
| OMIM | Наследственные болезни | Без лимита |
| Open Targets | Мишени лекарств | Без лимита |

---

## Разработка

### Запуск в режиме разработки

```bash
# Бэкенд с авто-перезагрузкой
python -m uvicorn web.backend.main:app --reload --port 8007

# Фронтенд с HMR (в другом терминале)
cd web/frontend && npm run dev
```

### Тесты

```bash
# Frontend-тесты
cd web/frontend && npm run test:run
```

### Добавление нового лабораторного показателя

1. Добавьте норму в `src/models/medical_refs.py`:
```python
"new_test": {
    "name": "Новый показатель",
    "unit": "ммоль/л",
    "male": (0.5, 2.0),
    "female": (0.3, 1.8),
    "critical_low": 0.1,
    "critical_high": 5.0,
}
```

2. Добавьте в `COMMON_LABS` в `DiagnosticsPage.tsx`:
```typescript
{ code: 'new_test', label: 'Новый показатель', unit: 'ммоль/л' }
```

### Добавление нового API-эндпоинта

1. Создайте роутер в `web/backend/routers/`:
```python
from fastapi import APIRouter
router = APIRouter(prefix="/new", tags=["new"])

@router.get("/endpoint")
async def new_endpoint():
    return {"result": "ok"}
```

2. Подключите в `web/backend/main.py`:
```python
from .routers.new_router import router as new_router
app.include_router(new_router, prefix="/api/v1")
```

---

## FAQ

**Q: Нужны ли API-ключи?**
A: Нет. Все внешние API бесплатные и не требуют регистрации.

**Q: Можно ли использовать для реальных пациентов?**
A: Нет. Это учебно-демонстрационная система. См. [Отказ от ответственности](#отказ-от-ответственности).

**Q: Почему препараты только на английском?**
A: Базы OpenFDA и RxNorm содержат данные в международной номенклатуре (МНН). Используйте: `metformin` (не метформин), `lisinopril` (не лизиноприл).

**Q: Как добавить пациента?**
A: Через веб-портал — регистрация на странице `/login`. Через MCP: `register_patient(...)`. Через API: `POST /api/v1/patients`.

**Q: Где хранятся данные?**
A: Локальная установка: `data/aibolit.db` (SQLite). Docker: именованный том `aibolit-data`.

**Q: Какой порт у бэкенда?**
A: 8007. В Docker nginx слушает порт 80 (настраивается через `PORT`) и проксирует `/api/` на бэкенд.

**Q: Как сделать бэкап базы?**
A: Локально: скопируйте `data/aibolit.db`. Docker: `docker compose cp backend:/app/data/aibolit.db ./backup.db`.

---

## Отказ от ответственности

> **Aibolit — информационная и демонстрационная система.**
>
> - **НЕ является медицинским устройством** и не предназначена для диагностики или лечения
> - **НЕ заменяет** консультацию квалифицированного врача
> - Все диагнозы, рекомендации и расчёты AI-системы **требуют верификации** специалистом
> - **Не принимайте медицинских решений** исключительно на основе результатов системы
> - Данные пациентов хранятся локально и **не передаются** на внешние серверы (кроме анонимных запросов к публичным API)

---

*Python + FastAPI + React + Claude MCP*
