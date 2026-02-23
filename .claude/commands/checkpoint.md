# Команда: /checkpoint

> Создать checkpoint текущего состояния

## Синтаксис

```
/checkpoint [описание]
```

## Параметры

- `[описание]` — опциональное описание checkpoint'а

---

## Описание

Создаёт snapshot текущего состояния проекта для сохранения прогресса и восстановления контекста.

---

## Процесс

### Step 1: Сбор состояния

```yaml
Действия:
  - Определить текущую фазу
  - Собрать созданные артефакты
  - Собрать принятые решения
  - Идентифицировать участвующих агентов
```

### Step 2: Создание summaries

```yaml
Действия:
  - Создать/обновить document summaries
  - Создать phase summary (если завершена фаза)
```

### Step 3: Формирование checkpoint

```yaml
Действия:
  - Сгенерировать ID: CP-{номер}-{фаза}-{timestamp}
  - Создать summary (≤500 токенов)
  - Определить next actions
  - Зафиксировать blockers
```

### Step 4: Сохранение

```yaml
Действия:
  - Сохранить в context/checkpoints/
  - Обновить phase summary (если нужно)
  - Архивировать полные документы (если фаза завершена)
```

---

## Формат checkpoint

```yaml
# context/checkpoints/CP-XXX-{phase}-{timestamp}.yaml

checkpoint:
  id: "CP-003-development-2024-01-15T14:30:00"
  created_at: "2024-01-15 14:30:00"
  created_by: "Orchestrator Agent"

  phase: "Development"
  status: "in_progress"  # completed | in_progress | blocked

  summary: |
    Завершена реализация Article CRUD. Создан ArticleService
    с полным покрытием тестами. Code review пройден успешно.
    Следующий этап — реализация Products CRUD.

  participating_agents:
    - agent: "Dev Agent"
      contribution: "Technical specification SPEC-003"
    - agent: "Coder Agent"
      contribution: "Article CRUD implementation"
    - agent: "Review Agent"
      contribution: "Code review, 100% compliance"

  artifacts:
    - path: "/docs/development/specs/article-crud.md"
      status: "completed"
      summary: "Tech spec для Article CRUD"
    - path: "backend/content/services.py"
      status: "created"
      summary: "ArticleService с CRUD операциями"
    - path: "backend/content/tests/"
      status: "created"
      summary: "Unit и integration тесты"

  decisions:
    - id: "DEC-015"
      decision: "Использовать slug для URL вместо ID"
      rationale: "Лучше для SEO и читаемости URL"
      stakeholder: "Architect Agent"

  metrics:
    features_completed: 1
    tests_written: 12
    coverage: "87%"

  next_actions:
    - action: "Реализовать Products CRUD"
      agent: "Coder"
      priority: 1
    - action: "Написать тесты для Products"
      agent: "QA"
      priority: 2
    - action: "Code review Products"
      agent: "Review"
      priority: 3

  blockers: []
    # - blocker: "Описание"
    #   impact: "Влияние"
    #   resolution: "План решения"
```

---

## Пример использования

### Ввод

```
/checkpoint Завершена реализация Article CRUD
```

### Вывод

```
📸 Checkpoint создан

🆔 ID: CP-003-development-2024-01-15T14:30:00
📍 Фаза: Development
📊 Статус: in_progress

📝 Summary:
Завершена реализация Article CRUD. ArticleService с полным
покрытием тестами (87%). Code review пройден — 100% compliance.

👥 Участники:
  - Dev Agent — Technical specification
  - Coder Agent — Implementation
  - Review Agent — Code review

📁 Артефакты:
  - /docs/development/specs/article-crud.md
  - backend/content/services.py
  - backend/content/tests/

📌 Следующие действия:
  1. Реализовать Products CRUD → Coder
  2. Написать тесты для Products → QA
  3. Code review Products → Review

💾 Сохранено: context/checkpoints/CP-003-development-2024-01-15T14-30-00.yaml

---
✍️ **Orchestrator Agent**
```

---

## Когда создавать checkpoint

```yaml
Обязательно:
  - После завершения фазы
  - После critical decisions
  - Перед major deployments

Рекомендуется:
  - После завершения крупной задачи
  - Перед длинным перерывом
  - При смене контекста
  - Еженедельно (для долгих проектов)

По запросу:
  - Команда /checkpoint
```

---

## Автоматические checkpoints

Система автоматически создаёт checkpoints при:

```yaml
- Завершении фазы (quality gate passed)
- Критических решениях (ADRs)
- Deployment events
```

---

*Команда v1.0 | Claude Code Agent System*
