# 02 - Управление контекстом и Checkpoints

> Правила управления контекстом, создания summaries и checkpoints

## Принцип токен-бюджета

```yaml
active_context:
  - Project Brief (Level 0)      # Всегда загружен
  - Phase Summaries (Level 1)    # По текущей фазе
  - Document Summaries (Level 2) # По запросу
  - Full Docs (Level 3)          # Lazy loading
```

---

## Иерархическая компрессия

### Level 0: Project Brief (~100 токенов)

**Всегда в контексте.** Краткое описание проекта.

```yaml
project_brief:
  name: "[Название проекта]"
  goal: "[Одно предложение — цель]"
  target_users: "[Кто пользователи]"

  scope:
    in:
      - "[Фича 1]"
      - "[Фича 2]"
    out:
      - "[Что НЕ включено]"

  constraints:
    - "[Ограничение 1]"
    - "[Ограничение 2]"

  tech_stack:
    frontend: "[framework]"
    backend: "[framework]"
    database: "[database]"
```

### Level 1: Phase Summary (~500 токенов)

**Загружается по фазам.** Резюме завершённой фазы.

```yaml
phase_summary:
  phase: "[Discovery|Design|Architecture|Development|...]"
  status: "completed|in_progress"
  duration: "[timeframe]"

  key_outcomes:
    - "[Результат 1]"
    - "[Результат 2]"

  key_decisions:
    - id: "DEC-001"
      decision: "[Краткое решение]"
      rationale: "[Обоснование]"

  artifacts:
    - path: "[путь к файлу]"
      type: "[тип документа]"
      summary: "[1 предложение]"

  dependencies_for_next:
    - "[Что нужно следующей фазе]"

  blockers: []
```

### Level 2: Document Summary (~200 токенов)

**Загружается по запросу.** Краткое содержание документа.

```yaml
document_summary:
  path: "[путь к файлу]"
  type: "[PRD|UserStory|Spec|ADR|...]"
  created_by: "[Agent]"
  created_at: "YYYY-MM-DD"

  key_points:
    - "[Ключевой пункт 1]"
    - "[Ключевой пункт 2]"
    - "[Ключевой пункт 3]"
    - "[Ключевой пункт 4]"
    - "[Ключевой пункт 5]"  # Максимум 5

  decisions:
    - "[Решение из документа]"

  related_to:
    - "[Связанный документ]"
```

### Level 3: Full Document (2000+ токенов)

**Lazy loading.** Полный текст — только когда необходимо.

Загружать полный документ когда:
- Нужны точные детали для реализации
- Требуется верификация конкретных требований
- Агент явно запрашивает полный текст

---

## Структура Context Store

```
context/
├── project-brief.yaml           # Level 0
├── summaries/
│   ├── discovery-summary.yaml   # Level 1
│   ├── design-summary.yaml
│   ├── architecture-summary.yaml
│   ├── development-summary.yaml
│   └── ...
├── checkpoints/
│   ├── CP-001-discovery-2024-01-15.yaml
│   ├── CP-002-design-2024-01-20.yaml
│   └── ...
└── archive/
    └── [archived documents]
```

---

## Checkpoints

### Когда создавать checkpoint

```yaml
Обязательно:
  - После завершения каждой фазы
  - После critical decisions
  - Перед major deployments

По запросу:
  - Команда /checkpoint
  - Перед длинным перерывом
  - При смене контекста
```

### Минимальное содержание checkpoint

```yaml
checkpoint:
  id: "CP-{номер}-{фаза}-{timestamp}"
  created_at: "YYYY-MM-DD HH:MM"
  created_by: "Orchestrator Agent"

  phase: "[текущая фаза]"
  status: "completed|in_progress|blocked"

  summary: |
    [Семантически плотное резюме, максимум 500 токенов]

  participating_agents:
    - agent: "[Agent Name]"
      contribution: "[Что сделал]"

  artifacts:
    - path: "[путь]"
      status: "created|updated|reviewed"
      summary: "[1 предложение]"

  decisions:
    - id: "DEC-001"
      decision: "[Решение]"
      rationale: "[Обоснование]"
      stakeholder: "[Кто принял]"

  next_actions:
    - action: "[Действие]"
      agent: "[Ответственный]"
      priority: 1

  blockers:
    - blocker: "[Описание]"
      impact: "[Влияние]"
      resolution: "[План решения]"

  metrics:
    completion_percentage: 75
    documents_created: 5
    decisions_made: 3
```

---

## Операции с контекстом

### Summarize Document (сжатие документа)

```yaml
INPUT: Полный документ

PROCESS:
  1. Извлечь ключевые пункты (макс 5)
  2. Извлечь принятые решения
  3. Извлечь зависимости
  4. Извлечь следующие действия
  5. Сжать до целевой длины

OUTPUT: Summary (макс 200 токенов)
```

### Create Checkpoint (создание checkpoint)

```yaml
INPUT: Текущее состояние фазы

PROCESS:
  1. Собрать все document summaries
  2. Список принятых решений
  3. Список созданных артефактов
  4. Определить следующие действия
  5. Архивировать полные документы

OUTPUT: Checkpoint YAML
```

### Load Context for Agent (загрузка контекста)

```yaml
INPUT: Тип агента + Задача

PROCESS:
  1. Загрузить Project Brief (всегда)
  2. Загрузить релевантные phase summaries
  3. Загрузить релевантные document summaries
  4. Если нужно: загрузить full documents
  5. Проверить бюджет, урезать если превышен

OUTPUT: Оптимизированный контекст
```

---

## Токен-оценки

| Тип контента | Примерно токенов |
|--------------|------------------|
| Project Brief | 100 |
| Phase Summary | 500 |
| Document Summary | 200 |
| Technical Spec (full) | 2000-5000 |
| Code file | 500-2000 |
| Checkpoint | 1000 |

---

## Распределение бюджета

```yaml
Для типичной задачи:
  current_task: 40%        # Текущая задача и инструкции
  relevant_summaries: 30%  # Релевантные summaries
  shared_context: 20%      # Project brief + decisions
  history: 10%             # Недавняя история

Для complex задачи:
  current_task: 50%        # Больше места для задачи
  relevant_summaries: 25%
  shared_context: 15%
  history: 10%
```

---

## Правила архивации

### Когда архивировать

```yaml
После завершения фазы:
  - Переместить full documents в archive/
  - Оставить только summaries в активном контексте

После закрытия epic:
  - Архивировать все артефакты
  - Создать финальный checkpoint
```

### Структура архива

```
context/archive/
├── discovery/
│   ├── vision.md
│   ├── prd.md
│   └── user-stories.md
├── design/
│   ├── user-flows.md
│   └── design-system.md
└── ...
```

---

## Восстановление контекста

### При старте новой сессии

```yaml
1. Загрузить project-brief.yaml
2. Загрузить последний checkpoint
3. Определить текущую фазу
4. Загрузить phase summary текущей фазы
5. Показать /status
```

### При команде /status

```yaml
OUTPUT:
  📍 Текущая фаза: [фаза]
  📋 Последний checkpoint: [CP-ID]
  ✅ Завершено: [что сделано]
  🔄 В процессе: [что делается]
  📌 Следующие действия:
    1. [действие 1]
    2. [действие 2]
    3. [действие 3]
  ⚠️ Blockers: [если есть]
```

---

*Правило версии 1.0 | Claude Code Agent System*
