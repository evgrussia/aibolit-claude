# Skill: Context Manager

> Управление контекстом между агентами для экономии токенов

## Назначение

Управление контекстом проекта: создание summaries, checkpoints, оптимизация загрузки документов.

---

## Принципы

### Иерархическая компрессия

```yaml
Level 0: Project Brief (~100 токенов)
  - Всегда в контексте
  - Минимум информации о проекте

Level 1: Phase Summary (~500 токенов)
  - Загружается по фазам
  - Ключевые результаты фазы

Level 2: Document Summary (~200 токенов)
  - По запросу
  - Ключевые пункты документа

Level 3: Full Document (2000+ токенов)
  - Lazy loading
  - Только когда нужны детали
```

### Lazy Loading

```yaml
Правило: Загружай summaries по умолчанию
  - Полные документы — только когда необходимо
  - Сохраняй ссылки для on-demand доступа
```

### Token Budget

```yaml
Распределение:
  current_task: 40%        # Текущая задача
  relevant_summaries: 30%  # Релевантные summaries
  shared_context: 20%      # Project brief + decisions
  history: 10%             # Недавняя история
```

---

## Операции

### Summarize Document

```yaml
INPUT: Полный документ

PROCESS:
  1. Извлечь ключевые пункты (макс 5)
  2. Извлечь принятые решения
  3. Извлечь зависимости
  4. Извлечь следующие действия
  5. Сжать до целевой длины (200 токенов)

OUTPUT:
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
      - "[Ключевой пункт 5]"

    decisions:
      - "[Решение из документа]"

    related_to:
      - "[Связанный документ]"
```

### Create Phase Summary

```yaml
INPUT: Все документы фазы

PROCESS:
  1. Собрать все document summaries
  2. Выделить ключевые результаты
  3. Собрать решения
  4. Определить зависимости для следующей фазы
  5. Сжать до 500 токенов

OUTPUT:
  phase_summary:
    phase: "[Discovery|Design|Architecture|...]"
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
      - path: "[путь]"
        type: "[тип]"
        summary: "[1 предложение]"

    dependencies_for_next:
      - "[Что нужно следующей фазе]"

    blockers: []
```

### Create Checkpoint

```yaml
INPUT: Текущее состояние

PROCESS:
  1. Собрать все document summaries
  2. Список принятых решений
  3. Список созданных артефактов
  4. Определить следующие действия
  5. Архивировать полные документы

OUTPUT:
  checkpoint:
    id: "CP-{номер}-{фаза}-{timestamp}"
    created_at: "YYYY-MM-DD HH:MM"
    created_by: "Orchestrator Agent"

    phase: "[текущая фаза]"
    status: "completed|in_progress|blocked"

    summary: |
      [Семантически плотное резюме, макс 500 токенов]

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

    next_actions:
      - action: "[Действие]"
        agent: "[Ответственный]"
        priority: 1

    blockers: []
```

### Load Context for Agent

```yaml
INPUT:
  agent_type: "[Agent type]"
  task: "[Task description]"

PROCESS:
  1. Загрузить Project Brief (всегда)
  2. Определить релевантные фазы
  3. Загрузить релевантные phase summaries
  4. Определить релевантные документы
  5. Загрузить document summaries
  6. Если нужны детали: загрузить full documents
  7. Проверить бюджет токенов
  8. Урезать если превышен

OUTPUT:
  context_package:
    project_brief: {...}
    phase_summaries: [...]
    document_summaries: [...]
    full_documents: [...]  # если нужны
    total_tokens: 2500
    budget_used: "65%"
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

## Шаблоны

### Project Brief

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

---

## Когда использовать

```yaml
Summarize Document:
  - После создания нового документа
  - Перед передачей другому агенту

Create Phase Summary:
  - После завершения фазы
  - При создании checkpoint

Create Checkpoint:
  - После завершения фазы
  - Перед длинным перерывом
  - Перед major deployment

Load Context:
  - При старте работы агента
  - При переключении между задачами
```

---

*Навык v1.0 | Claude Code Agent System*
