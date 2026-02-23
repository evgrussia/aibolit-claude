# Команда: /route

> Выполнить задачу как конкретный агент

## Синтаксис

```
/route <agent> <task>
```

## Параметры

- `<agent>` — имя агента (см. список ниже)
- `<task>` — описание задачи

---

## Доступные агенты

| Агент | Имя для команды |
|-------|-----------------|
| Orchestrator | `orchestrator` |
| Product | `product` |
| Research | `research` |
| Analytics | `analytics` |
| Business-Analyst | `business-analyst` |
| UX | `ux` |
| UI | `ui` |
| Content | `content` |
| Architect | `architect` |
| Data | `data` |
| Security | `security` |
| Dev | `dev` |
| AI-Agents | `ai-agents` |
| Coder | `coder` |
| QA | `qa` |
| Review | `review` |
| DevOps | `devops` |
| SRE | `sre` |
| Marketing | `marketing` |
| Medical-Domain | `medical-domain` |
| Compliance | `compliance` |

---

## Процесс

### Step 1: Валидация

```yaml
Действия:
  - Проверить существование агента
  - Проверить соответствие задачи агенту
  - Загрузить спецификацию агента
```

### Step 2: Контекст

```yaml
Действия:
  - Загрузить релевантный контекст
  - Загрузить предыдущие артефакты
  - Подготовить input для агента
```

### Step 3: Выполнение

```yaml
Действия:
  - Выполнить задачу согласно спецификации агента
  - Создать артефакты
  - Следовать workflow агента
```

### Step 4: Отчёт

```yaml
Действия:
  - Сформировать task_response
  - Добавить подпись агента
  - Определить следующие шаги
```

---

## Примеры использования

### Product Agent

```
/route product Создать PRD для функции авторизации через Telegram
```

### Coder Agent

```
/route coder Реализовать endpoint GET /api/articles/ с пагинацией
```

### Review Agent

```
/route review Проверить реализацию Article CRUD на соответствие SPEC-003
```

### DevOps Agent

```
/route devops Настроить GitHub Actions для автоматического деплоя
```

### Medical-Domain Agent

```
/route medical-domain Верифицировать клиническую корректность AI-агента кардиолога
```

### Compliance Agent

```
/route compliance Проверить соответствие обработки медданных 152-ФЗ
```

---

## Формат вывода

```yaml
task_response:
  id: "TASK-XXX"
  agent: "[Agent Name]"
  status: "completed|partial|blocked|failed"

  output:
    summary: "[Краткое резюме]"
    artifacts:
      - path: "[путь к файлу]"
        description: "[описание]"

  decisions:
    - id: "DEC-XXX"
      decision: "[Решение]"
      rationale: "[Обоснование]"

  next_steps:
    - action: "[Следующее действие]"
      agent: "[Ответственный]"

  signature: "[Agent Name] Agent"
```

---

## Пример полного вывода

### Ввод

```
/route coder Реализовать сервис для работы со статьями
```

### Вывод

```yaml
task_response:
  id: "TASK-015"
  agent: "Coder"
  status: "completed"

  output:
    summary: "Реализован ArticleService с CRUD операциями"
    artifacts:
      - path: "backend/content/services.py"
        description: "ArticleService class"
      - path: "backend/content/tests/test_services.py"
        description: "Unit tests"

  changes:
    files_created:
      - "backend/content/services.py"
    files_modified:
      - "backend/content/views.py"

  tests:
    unit: 8
    coverage: "87%"

  verification:
    lint_pass: true
    type_check_pass: true
    tests_pass: true

  next_steps:
    - action: "Code Review"
      agent: "Review"

  signature: "Coder Agent"

---
✍️ **Coder Agent**
```

---

## Правила

### Декомпозиция

Если задача слишком большая:
```yaml
1. Разбить на подзадачи
2. Выполнить последовательно
3. Собрать результат
```

### Делегирование

Если задача требует другого агента:
```yaml
1. Идентифицировать правильного агента
2. Сформировать task_request
3. Передать задачу
4. Дождаться результата
```

### Эскалация

Если задача неясна или требует уточнения:
```yaml
1. Запросить уточнение у пользователя
2. Документировать assumptions
3. Продолжить после уточнения
```

---

*Команда v1.1 | Aibolit AI — Claude Code Agent System*
