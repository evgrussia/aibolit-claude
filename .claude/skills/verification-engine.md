# Skill: Verification Engine

> Автоматизированная верификация реализации против спецификации

## Назначение

Проверка соответствия кода техническим спецификациям, расчёт процента выполнения.

---

## Возможности

1. **Spec Compliance Check** — проверка соответствия спецификации
2. **Coverage Analysis** — анализ покрытия
3. **Gap Detection** — обнаружение пробелов
4. **Completion Calculation** — расчёт процента выполнения

---

## Процесс верификации

### Step 1: Parse Specification

```yaml
INPUT: Technical Spec документ

PROCESS:
  1. Извлечь все requirements (FR-xxx)
  2. Извлечь acceptance criteria
  3. Извлечь edge cases
  4. Создать requirements checklist

OUTPUT:
  requirements_list:
    - id: "FR-001"
      description: "[Описание]"
      acceptance_criteria:
        - "[AC 1]"
        - "[AC 2]"
      edge_cases:
        - "[Edge case]"
```

### Step 2: Analyze Implementation

```yaml
INPUT: Code changes + Tests

PROCESS:
  1. Маппировать код к requirements
  2. Проверить test coverage
  3. Проверить обработку edge cases
  4. Проверить error handling

OUTPUT:
  implementation_mapping:
    - requirement_id: "FR-001"
      code_files:
        - "src/services/article_service.py"
        - "src/api/views.py"
      tests:
        - "tests/test_article_service.py"
      edge_cases_covered: true
      error_handling: true
```

### Step 3: Calculate Completion

```yaml
INPUT: Requirements + Implementation mapping

PROCESS:
  Для каждого requirement:
    - Fully implemented + tested: 100%
    - Implemented, minor issues: 75%
    - Partially implemented: 50%
    - Scaffolding only: 25%
    - Not implemented: 0%

  completion = sum(requirement_scores) / total_requirements

OUTPUT:
  completion_percentage: 85
  by_status:
    complete: 15
    mostly: 3
    partial: 2
    started: 0
    missing: 0
```

### Step 4: Generate Report

```yaml
INPUT: All analysis results

PROCESS:
  1. Список completed requirements
  2. Список incomplete requirements
  3. Список missing items
  4. Расчёт final score
  5. Генерация action items

OUTPUT: Verification Report
```

---

## Scoring System

| Status | Score | Определение |
|--------|-------|-------------|
| Complete | 100% | Полностью реализовано + тесты |
| Mostly | 75% | Реализовано, minor issues |
| Partial | 50% | Частично реализовано |
| Started | 25% | Только scaffolding |
| Missing | 0% | Не реализовано |

---

## Формат отчёта

```yaml
verification_report:
  feature: "[Feature Name]"
  spec_path: "[path to spec]"
  verification_date: "YYYY-MM-DD"

  overall_completion: 85

  categories:
    code_completeness: 90
    test_completeness: 80
    acceptance_criteria: 85
    edge_cases: 75

  requirements:
    completed:
      - id: "FR-001"
        description: "[Requirement]"
        evidence: "[file:line или test name]"

    incomplete:
      - id: "FR-002"
        description: "[Requirement]"
        status: "partial"
        current_score: 50
        missing: "[Что не хватает]"
        action: "[Что нужно сделать]"

    missing:
      - id: "FR-003"
        description: "[Requirement]"
        action: "[Что реализовать]"

  action_items:
    - priority: "high"
      action: "[Action]"
      effort: "2h"
    - priority: "medium"
      action: "[Action]"
      effort: "4h"

  decision:
    status: "PASS|CONDITIONAL|FAIL"
    reason: "[Объяснение]"
    next_step: "testing|rework"
```

---

## Checklists

### Code Completeness

```yaml
API:
  - [ ] Все endpoints реализованы
  - [ ] Request validation
  - [ ] Response format correct
  - [ ] Error responses

Business Logic:
  - [ ] Все AC выполнены
  - [ ] Edge cases обработаны
  - [ ] Validation rules

Database:
  - [ ] Migrations созданы
  - [ ] Indexes добавлены
```

### Test Completeness

```yaml
Unit Tests:
  - [ ] Все public methods
  - [ ] Edge cases
  - [ ] Error scenarios

Integration Tests:
  - [ ] All endpoints
  - [ ] Auth flows
  - [ ] Error handling

Coverage:
  - [ ] Statements > 80%
  - [ ] Branches > 70%
```

---

## Thresholds

| Decision | Completion Required |
|----------|---------------------|
| Ready for testing | 100% |
| Needs minor fixes | 90-99% |
| Needs significant work | < 90% |

---

## Использование

### Агентами

| Агент | Использование |
|-------|---------------|
| Review | Основной пользователь — верификация кода |
| QA | Верификация test coverage |
| Orchestrator | Проверка quality gates |

### Когда запускать

```yaml
- После завершения реализации (Coder → Review)
- Перед передачей на тестирование
- При code review
- При quality gate check
```

---

*Навык v1.0 | Claude Code Agent System*
