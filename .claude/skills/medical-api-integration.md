# Skill: Medical API Integration

> Интеграция с 10 медицинскими API: PubMed, OpenFDA, RxNorm, ICD-10 и др.

## Назначение

Подключение и использование внешних медицинских API для обогащения AI-ответов доказательной информацией: поиск литературы, проверка лекарств, кодирование диагнозов.

---

## Использование

| Агент | Применение |
|-------|-----------|
| AI-Agents | Проектирование API tools для LangGraph |
| Coder | Реализация API клиентов |
| Medical-Domain | Верификация корректности данных API |
| Research | Поиск медицинской литературы |

---

## Перечень API

### 1. PubMed E-utilities (NCBI)

```yaml
URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
Auth: API Key (бесплатный, лимит 10 req/sec)
Назначение: Поиск научных статей, абстрактов

Endpoints:
  esearch: Поиск по ключевым словам
  efetch: Получение абстрактов и метаданных
  elink: Связанные статьи

Использование в Aibolit:
  - Поиск доказательной базы для рекомендаций
  - Ссылки на источники в ответах AI
  - Наполнение RAG коллекции pubmed_abstracts

Rate Limit: 10 req/sec (с API key), 3 req/sec (без)
Fallback: Tavily Search API (медицинские сайты)
```

### 2. OpenFDA

```yaml
URL: https://api.fda.gov/
Auth: API Key (бесплатный)
Назначение: Информация о лекарствах (FDA)

Endpoints:
  /drug/label: Инструкции к препаратам (label)
  /drug/event: Побочные эффекты (FAERS)
  /drug/enforcement: Отзывы препаратов (recall)

Использование в Aibolit:
  - Справочная информация о препаратах
  - Побочные эффекты и предупреждения
  - Проверка отзывов лекарств

Rate Limit: 240 req/min (с key), 40 req/min (без)
Fallback: DrugBank (если OpenFDA недоступен)
```

### 3. RxNorm (NLM)

```yaml
URL: https://rxnav.nlm.nih.gov/REST/
Auth: Без ключа (бесплатный)
Назначение: Нормализация названий лекарств, взаимодействия

Endpoints:
  /rxcui: Поиск RxCUI по названию
  /interaction: Проверка взаимодействий
  /drugs: Информация о препарате
  /allrelated: Связанные препараты

Использование в Aibolit:
  - Нормализация названий препаратов (brand → generic)
  - Проверка лекарственных взаимодействий
  - Маппинг международных названий

Rate Limit: 20 req/sec
Fallback: Локальная база взаимодействий (критических пар)
```

### 4. ICD-10 API (WHO)

```yaml
URL: https://icd.who.int/icdapi/
Auth: OAuth2 (client_credentials)
Назначение: Коды МКБ-10 / МКБ-11

Endpoints:
  /icd/entity/search: Поиск по названию
  /icd/release/10: МКБ-10 коды
  /icd/release/11: МКБ-11 коды

Использование в Aibolit:
  - Кодирование диагнозов
  - Маппинг МКБ-10 ↔ МКБ-11
  - Поиск по симптомам и диагнозам

Rate Limit: Не документирован (разумный: 5 req/sec)
Fallback: Локальная база МКБ-10 (SQLite)
```

### 5. ClinicalTrials.gov

```yaml
URL: https://clinicaltrials.gov/api/v2/
Auth: Без ключа
Назначение: Клинические исследования

Endpoints:
  /studies: Поиск исследований
  /studies/{nctId}: Детали исследования

Использование в Aibolit:
  - Информирование о текущих исследованиях
  - Evidence base для рекомендаций

Rate Limit: Не документирован
Fallback: PubMed (поиск clinical trials)
```

### 6. MedlinePlus Connect

```yaml
URL: https://connect.medlineplus.gov/service
Auth: Без ключа
Назначение: Информация для пациентов (health literacy)

Endpoints:
  ?mainSearchCriteria.v.c={ICD10}: По коду МКБ-10
  ?mainSearchCriteria.v.c={SNOMED}: По коду SNOMED

Использование в Aibolit:
  - Понятные пациенту описания заболеваний
  - Дополнительная информация для образовательных целей

Rate Limit: Не документирован
Fallback: Собственная база описаний
```

### 7. LOINC (Regenstrief Institute)

```yaml
URL: https://fhir.loinc.org/
Auth: Basic Auth (бесплатная регистрация)
Назначение: Коды лабораторных тестов

Endpoints:
  /CodeSystem/$lookup: Поиск LOINC кода
  /ValueSet: Наборы значений

Использование в Aibolit:
  - Стандартизация названий лабораторных тестов
  - Референсные значения
  - Маппинг локальных названий на международные

Rate Limit: Разумный
Fallback: Локальная таблица лабораторных тестов
```

### 8. DrugBank (Open Data)

```yaml
URL: https://go.drugbank.com/
Auth: API Key (коммерческий / academic бесплатный)
Назначение: Детальная информация о лекарствах

Data:
  - Механизм действия
  - Фармакокинетика
  - Взаимодействия
  - Противопоказания
  - Метаболизм (CYP450)

Использование в Aibolit:
  - Глубокая информация о препаратах
  - Фармакогенетика (CYP2D6, CYP3A4)
  - Дополнение к RxNorm

Rate Limit: По тарифу
Fallback: OpenFDA + RxNorm
```

### 9. WHO GHO (Global Health Observatory)

```yaml
URL: https://ghoapi.azureedge.net/api/
Auth: Без ключа
Назначение: Глобальная статистика здоровья

Endpoints:
  /Indicator: Список индикаторов
  /{IndicatorCode}: Данные индикатора

Использование в Aibolit:
  - Эпидемиологические данные
  - Статистика заболеваемости
  - Prior probabilities для Bayesian reasoning

Rate Limit: Не документирован
Fallback: Кэшированные данные
```

### 10. Tavily Search API

```yaml
URL: https://api.tavily.com/search
Auth: API Key
Назначение: AI-оптимизированный веб-поиск

Параметры:
  include_domains: [
    "pubmed.ncbi.nlm.nih.gov",
    "who.int",
    "cdc.gov",
    "medlineplus.gov",
    "uptodate.com",
    "cochranelibrary.com",
    "cr.minzdrav.gov.ru"
  ]
  search_depth: "advanced"

Использование в Aibolit:
  - Поиск актуальной медицинской информации
  - Fallback когда специализированные API не дают результатов
  - Поиск новых клинических рекомендаций

Rate Limit: По тарифу
```

---

## Архитектура интеграции

### Circuit Breaker

```yaml
Паттерн: Circuit Breaker для каждого API

States:
  CLOSED: Нормальная работа
  OPEN: API недоступен, используем fallback
  HALF_OPEN: Пробуем восстановить

Config:
  failure_threshold: 5          # Ошибок до OPEN
  recovery_timeout: 60          # Секунд до HALF_OPEN
  success_threshold: 3          # Успехов для CLOSED

Implementation:
  - Каждый API client обёрнут в CircuitBreaker
  - При OPEN — автоматический fallback
  - Логирование всех state transitions
```

### Кэширование

```yaml
Strategy:
  PubMed abstracts: TTL 24h (редко меняются)
  Drug interactions: TTL 7d (стабильные данные)
  ICD-10 codes: TTL 30d (очень стабильные)
  Lab references: TTL 30d
  FDA events: TTL 1h (могут обновляться)
  Clinical trials: TTL 12h

Storage: Redis
Key pattern: "medical_api:{api_name}:{hash(params)}"
```

### Fallback Chain

```yaml
Для лекарственной информации:
  1. RxNorm → 2. OpenFDA → 3. DrugBank → 4. Локальная БД

Для научной литературы:
  1. PubMed → 2. Tavily (medical domains) → 3. RAG knowledge base

Для кодирования диагнозов:
  1. WHO ICD API → 2. Локальная база МКБ-10

Для лабораторных данных:
  1. LOINC API → 2. Локальная таблица референсов
```

---

## Обработка ошибок

```yaml
API Errors:
  timeout:
    action: "Retry 1x, затем fallback"
    log_level: WARNING

  rate_limit:
    action: "Exponential backoff, затем fallback"
    log_level: WARNING

  auth_error:
    action: "Refresh token, retry, затем alert"
    log_level: ERROR

  data_error:
    action: "Log + skip, не показывать пользователю некорректные данные"
    log_level: ERROR

  network_error:
    action: "Fallback chain"
    log_level: WARNING

Принцип: AI-ответ НИКОГДА не должен блокироваться из-за недоступности API.
Всегда есть fallback или graceful degradation.
```

---

## Credentials

```yaml
Переменные окружения:
  PUBMED_API_KEY: str
  OPENFDA_API_KEY: str
  WHO_ICD_CLIENT_ID: str
  WHO_ICD_CLIENT_SECRET: str
  LOINC_USERNAME: str
  LOINC_PASSWORD: str
  DRUGBANK_API_KEY: str
  TAVILY_API_KEY: str

Хранение: .env файл (НЕ в git)
Production: Docker secrets или Vault
```

---

## Ссылки

- **AI-агенты:** `.claude/agents/ai-agents.md`
- **Clinical Reasoning:** `.claude/skills/clinical-reasoning.md`
- **Knowledge Base:** `.claude/skills/medical-knowledge-base.md`
- **Правила безопасности:** `.claude/rules/05-medical-safety.md`

---

*Спецификация навыка v1.0 | Aibolit AI — Claude Code Agent System*
