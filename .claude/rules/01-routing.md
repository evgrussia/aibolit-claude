# 01 - Маршрутизация агентов и форматы

> Правила маршрутизации задач к агентам и форматы обмена данными

## Дерево маршрутизации

Каждая задача классифицируется и направляется к подходящему агенту:

| Тип задачи | Агент |
|------------|-------|
| Новая идея проекта | Orchestrator |
| Product vision / PRD / Stories | Product |
| Исследование рынка / конкурентов | Research |
| Метрики / tracking plans | Analytics |
| Бизнес-модель / процессы | Business-Analyst |
| User flows / wireframes / IA | UX |
| Design system / UI / визуал | UI |
| Копирайтинг / tone / microcopy | Content |
| Системная архитектура / tech stack | Architect |
| Модели данных / схемы | Data |
| Безопасность / threats | Security |
| Технические спецификации | Dev |
| AI-агенты / LangChain | AI-Agents |
| Реализация кода | Coder |
| Тестовая стратегия / выполнение | QA |
| Code review / верификация | Review |
| CI/CD / deployment | DevOps |
| Мониторинг / инциденты | SRE |
| Маркетинг / запуск | Marketing |
| **Медицинская верификация AI / клинические требования** | **Medical-Domain** |
| **Регуляторика / 152-ФЗ / комплаенс медданных** | **Compliance** |
| **Медицинский AI review (корректность ответов)** | **Medical-Domain + AI-Agents** |
| **Клинические рекомендации / протоколы лечения** | **Medical-Domain** |
| **Медицинский RAG / knowledge base** | **AI-Agents + Medical-Domain** |
| **Эскалация к врачу / doctor escalation** | **AI-Agents** |

---

## Формат передачи задачи (Handoff)

### task_request (запрос задачи)

```yaml
task_request:
  id: "TASK-001"
  agent: "<имя агента>"
  type: "create|review|update|verify"
  priority: "critical|high|medium|low"

  input:
    summary: "<краткий контекст задачи>"
    references:
      - "<путь к документу>"
      - "<путь к спецификации>"
    constraints:
      - "<ограничение 1>"
      - "<ограничение 2>"

  expected_output:
    deliverables:
      - "<путь к артефакту>"
    format: "<описание формата>"
    quality_criteria:
      - "<критерий 1>"
      - "<критерий 2>"
```

### task_response (ответ на задачу)

```yaml
task_response:
  id: "TASK-001"
  agent: "<имя агента>"
  status: "completed|partial|blocked|failed"

  output:
    summary: "<краткое резюме результата>"
    artifacts:
      - path: "<путь к файлу>"
        description: "<описание>"
    decisions:
      - id: "DEC-001"
        decision: "<решение>"
        rationale: "<обоснование>"

  quality:
    completion_percentage: 100
    criteria_met:
      - "<критерий 1>: passed"
      - "<критерий 2>: passed"

  issues:
    - severity: "high|medium|low"
      description: "<описание проблемы>"
      recommendation: "<рекомендация>"

  next_steps:
    - action: "<следующее действие>"
      agent: "<ответственный агент>"
      priority: "high|medium|low"

  signature: "[Имя агента] Agent"  # ОБЯЗАТЕЛЬНО
```

---

## Правила делегирования

### 1. Один агент на атомарную задачу

```yaml
Правильно:
  - "Создать PRD" → Product Agent
  - "Реализовать endpoint" → Coder Agent

Неправильно:
  - "Создать PRD и реализовать API" → разделить!
```

### 2. Следовать последовательности фаз

```
Discovery → Design → Architecture → Development → QA → Deployment → Marketing
```

### 3. Обязательные переходы

```yaml
После Coder:
  - ВСЕГДА → Review Agent

После Review (если 100%):
  - ВСЕГДА → QA Agent

После Review (если <100%):
  - Вернуть → Coder Agent с findings

Для медицинского функционала (ДОПОЛНИТЕЛЬНО):
  После Coder (медицинский код):
    - ВСЕГДА → Medical-Domain Agent (medical review)
    - ЗАТЕМ → Review Agent (code review)

  После QA (медицинский функционал):
    - ВСЕГДА → Compliance Agent (regulatory check)

  Новый медицинский AI-агент:
    - Product → Medical-Domain → AI-Agents → Compliance → Dev → Coder → Medical-Domain → Review → QA
```

### 4. Уточнять при неясности

Если задача неясна или может быть выполнена несколькими агентами:
- Запросить уточнение у пользователя
- Или декомпозировать на подзадачи

---

## Примеры маршрутизации

### Пример 1: Новая фича

```yaml
Задача: "Добавить авторизацию через Telegram"

Маршрут:
  1. Product Agent → User Story + AC
  2. Architect Agent → Technical approach
  3. Security Agent → Security requirements
  4. Dev Agent → Technical spec
  5. Coder Agent → Implementation
  6. Review Agent → Code review
  7. QA Agent → Testing
  8. DevOps Agent → Deployment
```

### Пример 2: Баг-фикс

```yaml
Задача: "Исправить ошибку в валидации email"

Маршрут:
  1. Coder Agent → Bug fix
  2. Review Agent → Verification
  3. QA Agent → Regression test
```

### Пример 3: Исследование

```yaml
Задача: "Изучить конкурентов в нише онлайн-образования"

Маршрут:
  1. Research Agent → Competitive analysis

  # Не требует Design, Architecture, Development
```

### Пример 4: Новый медицинский AI-агент

```yaml
Задача: "Создать AI-агента кардиолога"

Маршрут:
  1. Product Agent → User Story + AC для кардиолога
  2. Medical-Domain Agent → Клинические требования (симптомы, диагнозы, протоколы, red flags)
  3. AI-Agents Agent → Дизайн агента (LangGraph state machine, tools, RAG)
  4. Compliance Agent → Проверка регуляторных требований
  5. Dev Agent → Technical spec
  6. Coder Agent → Implementation
  7. Medical-Domain Agent → Medical review (клиническая корректность)
  8. Review Agent → Code review
  9. QA Agent → Testing (включая medical safety tests)
```

### Пример 5: Медицинское исследование

```yaml
Задача: "Подготовить данные для RAG по кардиологии"

Маршрут:
  1. Research Agent → Поиск клинических рекомендаций (PubMed, Минздрав)
  2. Medical-Domain Agent → Верификация и курация источников
  3. AI-Agents Agent → Настройка RAG pipeline
```

### Пример 6: Рефакторинг

```yaml
Задача: "Отрефакторить модуль аутентификации"

Маршрут:
  1. Architect Agent → Refactoring plan
  2. Dev Agent → Technical spec
  3. Coder Agent → Implementation
  4. Review Agent → Code review
  5. QA Agent → Regression testing
```

---

## Классификация задач

### По сложности

```yaml
Simple (1 агент):
  - Исправить typo
  - Добавить поле в модель
  - Написать unit test

Medium (2-3 агента):
  - Добавить endpoint
  - Создать новый компонент
  - Исправить bug

Complex (4+ агентов):
  - Новая фича
  - Интеграция с внешним API
  - Рефакторинг модуля

Epic (все фазы):
  - Новый продукт
  - Крупная функциональность
  - Миграция системы
```

### По типу

```yaml
Create: Создать новое
  - Агенты: Product, Architect, Dev, Coder

Review: Проверить существующее
  - Агенты: Review, QA, Security

Update: Изменить существующее
  - Агенты: Dev, Coder, Review

Verify: Верифицировать
  - Агенты: Review, QA

Research: Исследовать
  - Агенты: Research, Analytics

Deploy: Развернуть
  - Агенты: DevOps, SRE

Medical-Create: Создать медицинский функционал
  - Агенты: Product, Medical-Domain, AI-Agents, Compliance, Dev, Coder

Medical-Review: Проверить медицинский AI
  - Агенты: Medical-Domain, Review, QA, Security, Compliance

Medical-Research: Медицинское исследование
  - Агенты: Research, Medical-Domain
```

---

## Эскалация

### Когда эскалировать к пользователю

```yaml
1. Конфликт между агентами (разные подходы)
2. Недостаточно информации для решения
3. Решение выходит за рамки scope
4. Критические риски обнаружены
5. Требуется business decision
```

### Формат эскалации

```yaml
escalation:
  type: "clarification|decision|approval|risk"
  from_agent: "<имя агента>"

  context:
    summary: "<краткое описание ситуации>"
    options:
      - option: "<вариант 1>"
        pros: ["<плюс>"]
        cons: ["<минус>"]
      - option: "<вариант 2>"
        pros: ["<плюс>"]
        cons: ["<минус>"]

  recommendation: "<рекомендуемый вариант>"
  urgency: "high|medium|low"
```

---

## Параллельное выполнение

### Когда можно параллелить

```yaml
Параллельно:
  - Research + Analytics (в Discovery)
  - Research + Medical-Domain (медицинские исследования + клинические требования)
  - UX + Content (в Design)
  - Security + Data + Compliance (в Architecture)
  - Medical-Domain + Compliance (медицинская верификация + регуляторика)
  - Unit tests + Integration tests (в QA)

Последовательно:
  - PRD → Tech Spec → Code
  - Code → Medical Review → Code Review → QA (для медицинского кода)
  - Code → Review → QA (для не-медицинского кода)
  - QA → Deploy
```

### Формат параллельного запроса

```yaml
parallel_tasks:
  - task_request: { ... }
  - task_request: { ... }

sync_point:
  wait_for: "all|any"
  timeout: "2h"
  on_timeout: "escalate|proceed"
```

---

*Правило версии 1.1 | Aibolit AI — Claude Code Agent System*
