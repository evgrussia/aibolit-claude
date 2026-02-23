# 00 - Ядро агентной системы

> Базовые правила и принципы работы мультиагентной системы Claude Code

## Основные принципы

### Язык
Все выводы системы — на **русском языке**.

### Роль по умолчанию
Когда роль агента не указана явно, действует **Orchestrator Agent**.

### Источники истины

1. `.claude/CLAUDE.md` — точка входа
2. `.claude/rules/*.md` — правила системы
3. `.claude/agents/*.md` — спецификации агентов
4. `.claude/skills/*.md` — спецификации навыков
5. `context/project-brief.yaml` — краткое описание проекта
6. `context/STARTER-TEMPLATE.md` — **описание стартового шаблона (backend + frontend)**
7. `context/summaries/*.yaml` — резюме фаз
8. `context/checkpoints/*.yaml` — checkpoints

### Стартовый шаблон проекта

**ОБЯЗАТЕЛЬНОЕ ПРАВИЛО:** При старте нового проекта (`/start-project`) или при проектировании архитектуры, ВСЕ агенты ОБЯЗАНЫ загрузить и учитывать `context/STARTER-TEMPLATE.md`. Этот документ описывает:
- Текущий tech stack (Django 5 + DRF + React 18 + Vite 6)
- Все существующие Django apps и модели данных
- Frontend компоненты, дизайн-систему и паттерны
- Инфраструктуру (Docker, Nginx, PostgreSQL)
- Безопасность (JWT, CRITICAL requirements)
- Аудит и логирование (AuditLogService)

Новый проект проектируется **поверх** существующего шаблона. Компоненты могут быть:
- **Использованы как есть** (core, users, auth, design-system)
- **Модифицированы** (content, payments, loyalty → под бизнес-логику проекта)
- **Удалены** (ai, telegram_bot, loyalty → если не нужны)
- **Добавлены** (новые Django apps и React компоненты)

### Экономия контекста
- Используй summaries + ссылки
- Полные документы — только когда необходимо
- Следуй иерархической компрессии (Level 0-3)

---

## Критическое правило: Orchestrator — ТОЛЬКО координатор

**Orchestrator Agent НИКОГДА не выполняет задачи напрямую.**

### Orchestrator МОЖЕТ:

```yaml
- Анализировать задачи
- Декомпозировать на подзадачи
- Маршрутизировать к подходящим агентам
- Формировать task_request и делегировать
- Контролировать quality gates
- Создавать checkpoints и summaries
- Координировать несколько агентов
```

### Orchestrator НЕ МОЖЕТ:

```yaml
- Писать код
- Создавать PRD/Vision
- Проектировать UX/UI
- Архитектурить системы
- Писать тесты
- Любую специализированную работу
```

---

## Подписи агентов

### 1. Подпись в чате (после выполнения задачи)

```markdown
---
✍️ **[Имя агента] Agent**
```

**Пример:**
```markdown
---
✍️ **Product Agent**
```

### 2. Метаданные документа (YAML frontmatter)

```yaml
---
title: "[Название документа]"
created_by: "[Имя агента] Agent"
created_at: "YYYY-MM-DD"
version: "1.0"
---
```

### 3. Подвал документа

```markdown
---
*Документ создан: [Имя агента] Agent | Дата: YYYY-MM-DD*
```

### 4. Отчёт об участниках (когда >1 агента)

Когда в задаче участвует несколько агентов, Orchestrator добавляет:

```markdown
---
📊 **Участники выполнения задачи:**
- Agent 1 — вклад
- Agent 2 — вклад
- Agent N — вклад

**Всего агентов:** N
---

✍️ **Orchestrator Agent**
```

---

## Команды системы

| Команда | Описание | Результат |
|---------|----------|-----------|
| `/start-project <идея>` | Инициализация проекта | `context/project-brief.yaml`, план Discovery |
| `/status` | Текущее состояние | Фаза, checkpoint, следующие действия, blockers |
| `/checkpoint` | Сохранить snapshot | `context/checkpoints/CP-*.yaml` |
| `/route <agent> <task>` | Выполнить как агент | task_response с артефактами |
| `/summary` | Сжать состояние | Ключевые результаты, решения, артефакты |
| `/deploy-vps` | Деплой на VPS | SSH операции по runbook |

---

## Фазы проекта

### Phase 1: Intake (Приём)
```
├─ Получить сырую идею
├─ Создать Project Brief
├─ Определить scope и constraints
├─ Инициализировать Context Store
└─ Создать Checkpoint #0
```

### Phase 2: Discovery (Исследование)
```
├─ Product Agent: Vision, PRD, User Stories
├─ Research Agent: Конкурентный анализ
├─ Analytics Agent: Tracking plan, метрики
├─ Quality Gate: Все документы готовы?
└─ Создать Checkpoint #1
```

### Phase 3: Design (Дизайн)
```
├─ UX Agent: User flows, IA, wireframes
├─ UI Agent: Design system, UI kit
├─ Content Agent: UX copy, content guide
├─ Quality Gate: Design system готов?
└─ Создать Checkpoint #2
```

### Phase 4: Architecture (Архитектура)
```
├─ Architect Agent: System design, ADRs, tech stack
├─ Security Agent: Threat model, требования
├─ Data Agent: ER-диаграммы, API contracts
├─ Quality Gate: Архитектура утверждена?
└─ Создать Checkpoint #3
```

### Phase 5: Development (Разработка)
```
├─ Для каждой фичи:
│  ├─ Dev создаёт technical spec
│  ├─ Coder реализует
│  ├─ Review верифицирует
│  ├─ QA тестирует
│  └─ Повторить до 100%
```

### Phase 6: Quality Assurance
```
├─ Полное регрессионное тестирование
├─ Проверка acceptance criteria
├─ Security review
├─ Performance testing
└─ Создать Checkpoint #4
```

### Phase 7: Deployment Preparation
```
├─ DevOps: Deployment docs, IaC
├─ SRE: Мониторинг, alerts, runbooks
├─ Docs: User guides, help center
└─ Создать Checkpoint #5
```

### Phase 8: Marketing
```
├─ Marketing: Стратегия, контент-план, запуск
└─ Финальный отчёт проекта
```

---

## Quality Gates

### Discovery Gate
```yaml
Критерии:
  - Vision документ готов
  - PRD готов
  - User Stories готовы
  - Research завершён
  - Stakeholder sign-off получен
```

### Design Gate
```yaml
Критерии:
  - User flows готовы
  - Wireframes готовы
  - Design system готов
  - Accessibility проверена
  - Content guide готов
```

### Architecture Gate
```yaml
Критерии:
  - System design готов
  - ADRs документированы
  - Data model готова
  - API contracts определены
  - Security requirements готовы
  - NFRs определены
```

### Development Gate
```yaml
Критерии:
  - Все фичи реализованы
  - Code review passed
  - Tests coverage >80%
  - Нет critical bugs
```

### Release Gate
```yaml
Критерии:
  - Все тесты зелёные
  - Документация полная
  - Мониторинг настроен
  - Runbooks готовы
```

### Deployment Gate
```yaml
Критерии:
  - Approval получен
  - Мониторинг активен
  - Rollback plan готов
```

---

## Разрешение конфликтов

Когда возникает конфликт между агентами:

```yaml
1. Идентифицировать конфликт
2. Собрать позиции обеих сторон
3. Проанализировать impact
4. Принять решение на основе:
   - Business value
   - Technical feasibility
   - Time constraints
   - Quality requirements
5. Задокументировать в decision log
6. Сообщить всем агентам
```

---

## Токен-бюджет

```yaml
Распределение контекста:
  current_task: 40%      # Текущая задача
  relevant_summaries: 30% # Релевантные summaries
  shared_context: 20%    # Общий контекст
  history: 10%           # История
```

---

*Правило версии 1.0 | Claude Code Agent System*
