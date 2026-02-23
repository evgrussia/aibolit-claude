# Команда: /status

> Текущее состояние проекта

## Синтаксис

```
/status
```

## Описание

Показывает текущее состояние проекта: фаза, последний checkpoint, следующие действия, blockers.

---

## Процесс

### Step 1: Загрузка контекста

```yaml
Действия:
  - Загрузить project-brief.yaml
  - Загрузить последний checkpoint
  - Определить текущую фазу
```

### Step 2: Анализ состояния

```yaml
Действия:
  - Определить завершённые задачи
  - Определить текущие задачи
  - Идентифицировать blockers
  - Сформировать следующие действия
```

### Step 3: Формирование отчёта

```yaml
Действия:
  - Собрать статус по категориям
  - Подготовить краткий вывод
```

---

## Формат вывода

```
📍 Текущая фаза: [фаза]
📋 Последний checkpoint: [CP-ID]

✅ Завершено:
  - [Завершённая задача 1]
  - [Завершённая задача 2]

🔄 В процессе:
  - [Текущая задача]

📌 Следующие действия:
  1. [Действие 1] → [Agent]
  2. [Действие 2] → [Agent]
  3. [Действие 3] → [Agent]

⚠️ Blockers:
  - [Blocker, если есть]

📊 Прогресс фазы: [X]%

---
✍️ **Orchestrator Agent**
```

---

## Пример использования

### Ввод

```
/status
```

### Вывод

```
📍 Текущая фаза: Development
📋 Последний checkpoint: CP-003-architecture-2024-01-15

✅ Завершено:
  - Vision Document
  - PRD с 15 User Stories
  - Competitive Analysis
  - System Architecture (Modular Monolith)
  - Database Schema
  - API Contracts

🔄 В процессе:
  - SPEC-003: Article CRUD (Coder Agent)

📌 Следующие действия:
  1. Завершить реализацию Article CRUD → Coder
  2. Code Review → Review Agent
  3. Написать тесты → QA Agent

⚠️ Blockers:
  - Нет активных blockers

📊 Прогресс фазы: 35%

---
✍️ **Orchestrator Agent**
```

---

## Детальный статус

При необходимости более детального статуса:

```
/status detailed
```

### Вывод detailed

```yaml
project_status:
  project: "[Название]"
  current_phase: "Development"
  phase_progress: 35

  phases:
    discovery:
      status: "completed"
      checkpoint: "CP-001"
      documents: 5

    design:
      status: "completed"
      checkpoint: "CP-002"
      documents: 4

    architecture:
      status: "completed"
      checkpoint: "CP-003"
      documents: 6

    development:
      status: "in_progress"
      features:
        total: 10
        completed: 3
        in_progress: 1
        pending: 6

  recent_activity:
    - date: "2024-01-15"
      action: "Architecture approved"
      agent: "Architect"
    - date: "2024-01-16"
      action: "Started SPEC-003"
      agent: "Dev"

  blockers: []

  next_actions:
    - action: "Complete Article CRUD"
      agent: "Coder"
      priority: 1
    - action: "Code Review"
      agent: "Review"
      priority: 2

  signature: "Orchestrator Agent"
```

---

## Когда использовать

```yaml
- В начале работы (для понимания контекста)
- После перерыва
- Для отчёта о прогрессе
- Перед передачей задачи
- При планировании следующих шагов
```

---

*Команда v1.0 | Claude Code Agent System*
