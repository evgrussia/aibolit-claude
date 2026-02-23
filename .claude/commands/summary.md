# Команда: /summary

> Сжатое резюме текущего состояния

## Синтаксис

```
/summary [scope]
```

## Параметры

- `[scope]` — опционально: `project`, `phase`, `task` (по умолчанию: `project`)

---

## Описание

Генерирует сжатое резюме состояния (≤500 токенов) для передачи контекста или отчётности.

---

## Процесс

### Step 1: Определение scope

```yaml
project:
  - Общий статус проекта
  - Все фазы
  - Ключевые решения

phase:
  - Текущая фаза
  - Артефакты фазы
  - Прогресс

task:
  - Текущая задача
  - Контекст задачи
  - Blockers
```

### Step 2: Компрессия

```yaml
Действия:
  - Извлечь ключевые пункты
  - Удалить избыточность
  - Сохранить семантическую плотность
  - Ограничить до 500 токенов
```

### Step 3: Форматирование

```yaml
Действия:
  - Структурированный вывод
  - Ключевые метрики
  - Следующие действия
```

---

## Формат вывода

### /summary (project)

```yaml
project_summary:
  name: "[Название]"
  goal: "[Цель]"
  status: "on_track|at_risk|blocked"
  progress: 45%

  current_phase: "Development"
  phases_completed: ["Discovery", "Design", "Architecture"]

  key_outcomes:
    - "PRD с 15 user stories"
    - "Modular Monolith architecture"
    - "3/10 features implemented"

  key_decisions:
    - "DEC-001: Django + React stack"
    - "DEC-005: Telegram-first auth"

  active_tasks:
    - "Article CRUD implementation"

  blockers: []

  next_milestone: "MVP Release"
  estimated_progress: "35% to MVP"
```

### /summary phase

```yaml
phase_summary:
  phase: "Development"
  status: "in_progress"
  progress: 30%

  features:
    total: 10
    completed: 3
    in_progress: 1

  key_outcomes:
    - "User auth implemented"
    - "Article CRUD in progress"

  active_work:
    agent: "Coder"
    task: "SPEC-003 implementation"

  next_steps:
    - "Complete Article CRUD"
    - "Review & QA"
    - "Start Products CRUD"
```

### /summary task

```yaml
task_summary:
  task: "Article CRUD Implementation"
  spec: "SPEC-003"
  status: "in_progress"
  progress: 70%

  completed:
    - "ArticleService created"
    - "Unit tests written"

  remaining:
    - "Integration tests"
    - "Edge case handling"

  blockers: []

  context:
    - "Spec: /docs/development/specs/article-crud.md"
    - "Related: User Stories US-005, US-006"
```

---

## Пример использования

### Ввод

```
/summary
```

### Вывод

```
📊 Project Summary

🎯 AI Learning Platform
   Платформа онлайн-обучения с AI-ассистентом

📈 Прогресс: 45% | Статус: ✅ On Track

📍 Текущая фаза: Development (30%)
✅ Завершено: Discovery, Design, Architecture

🏆 Ключевые результаты:
  • PRD с 15 user stories
  • Modular Monolith architecture
  • 3/10 features implemented

🔑 Ключевые решения:
  • Django + React stack
  • Telegram-first authentication
  • PostgreSQL + pgvector for AI

🔄 Активная работа:
  • Article CRUD implementation (Coder Agent)

📌 К MVP:
  • 7 features remaining
  • ~35% to release

---
✍️ **Orchestrator Agent**
```

---

## Использование для передачи контекста

Summary можно использовать для:

```yaml
1. Handoff между сессиями:
   - Сохранить summary
   - Восстановить контекст в новой сессии

2. Отчёт stakeholders:
   - Краткий статус проекта
   - Без технических деталей

3. Координация агентов:
   - Передача контекста между агентами
   - Минимизация токенов
```

---

## Token Budget

```yaml
Максимум: 500 токенов

Распределение:
  - Status & progress: 50 токенов
  - Key outcomes: 150 токенов
  - Key decisions: 100 токенов
  - Active work: 100 токенов
  - Next steps: 100 токенов
```

---

*Команда v1.0 | Claude Code Agent System*
