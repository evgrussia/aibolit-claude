# Команда: /start-project

> Инициализация нового проекта

## Синтаксис

```
/start-project <описание идеи>
```

## Описание

Создаёт начальный контекст проекта и план Discovery фазы.

---

## Процесс

### Step 0: Загрузка стартового шаблона

```yaml
ОБЯЗАТЕЛЬНО:
  - Загрузить context/STARTER-TEMPLATE.md
  - Проанализировать текущий tech stack
  - Определить какие компоненты шаблона будут:
    - Использованы как есть (core, users, auth, design-system)
    - Модифицированы под новый проект
    - Удалены (если не нужны)
    - Добавлены (новые модули)
  - Учесть существующие модели, API, компоненты при проектировании

Примечание:
  Новый проект строится ПОВЕРХ существующего шаблона.
  НЕ проектировать с нуля — адаптировать имеющееся.
```

### Step 1: Анализ идеи

```yaml
Действия:
  - Проанализировать описание
  - Выделить ключевые компоненты
  - Определить scope
  - Идентифицировать constraints
  - Сопоставить с компонентами Starter Template
```

### Step 2: Создание Project Brief

```yaml
Файл: context/project-brief.yaml

Содержание:
  - name: Название проекта
  - goal: Цель (1 предложение)
  - target_users: Целевая аудитория
  - scope.in: Что включено
  - scope.out: Что НЕ включено
  - constraints: Ограничения
  - tech_stack: Технологии (если известны)
```

### Step 3: Инициализация Context Store

```yaml
Структура:
  context/
  ├── project-brief.yaml
  ├── summaries/
  └── checkpoints/
```

### Step 4: Создание Checkpoint #0

```yaml
Файл: context/checkpoints/CP-000-intake-{timestamp}.yaml

Содержание:
  - Project Brief создан
  - Scope определён
  - Ready for Discovery
```

### Step 5: План Discovery

```yaml
Вывод:
  - Следующие шаги для Discovery фазы
  - Рекомендуемые агенты
  - Ключевые вопросы для уточнения
```

---

## Пример использования

### Ввод

```
/start-project Платформа для онлайн-курсов с персональным AI-ассистентом, интеграцией с Telegram и оплатой через TON
```

### Вывод

```yaml
🚀 Проект инициализирован

📋 Project Brief:
  name: "AI Learning Platform"
  goal: "Платформа онлайн-обучения с персональным AI-ассистентом"

  target_users:
    - Студенты и self-learners
    - Создатели курсов

  scope:
    in:
      - Каталог курсов
      - AI-ассистент для обучения
      - Telegram интеграция
      - TON платежи
    out:
      - Live стриминг
      - Мобильное приложение (в MVP)

  constraints:
    - MVP за 2 месяца
    - Telegram-first подход

  tech_stack:
    frontend: "React"
    backend: "Django"
    database: "PostgreSQL"
    ai: "LangChain"

📁 Создано:
  - context/project-brief.yaml
  - context/checkpoints/CP-000-intake-{timestamp}.yaml

📌 Следующие шаги (Discovery):
  1. Product Agent → Vision Document
  2. Product Agent → PRD
  3. Research Agent → Competitive Analysis
  4. Analytics Agent → Metrics Framework

❓ Требуется уточнение:
  - Количество курсов в MVP?
  - Модель монетизации?
  - Целевой рынок (RU/Global)?

---
✍️ **Orchestrator Agent**
```

---

## Формат вывода

```yaml
start_project_result:
  status: "initialized"

  project_brief:
    path: "context/project-brief.yaml"
    name: "[Название]"
    goal: "[Цель]"

  checkpoint:
    id: "CP-000-intake-{timestamp}"
    path: "context/checkpoints/..."

  next_steps:
    - agent: "Product"
      task: "Create Vision Document"
    - agent: "Research"
      task: "Competitive Analysis"

  questions:
    - "[Вопрос 1]"
    - "[Вопрос 2]"

  signature: "Orchestrator Agent"
```

---

## Шаблон Project Brief

```yaml
# context/project-brief.yaml

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

  starter_template:
    reference: "context/STARTER-TEMPLATE.md"
    components_keep:
      - "[Компонент 1 — используется как есть]"
    components_modify:
      - "[Компонент 2 — модифицируется под проект]"
    components_remove:
      - "[Компонент 3 — не нужен, удалить]"
    components_add:
      - "[Компонент 4 — новый, создать]"

  created_at: "YYYY-MM-DD"
  created_by: "Orchestrator Agent"
```

---

*Команда v1.0 | Claude Code Agent System*
