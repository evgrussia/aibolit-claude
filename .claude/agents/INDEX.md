# Реестр агентов

> Все агенты системы Claude Code Agent System — Aibolit AI

## Обзор

Система включает **21 специализированный агент**, организованных по фазам разработки, включая 2 медицинских агента.

---

## Координация

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| Orchestrator | [orchestrator.md](orchestrator.md) | Координатор проекта | - |

---

## Discovery (Исследование)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| Product | [product.md](product.md) | Product Manager | - |
| Research | [research.md](research.md) | Исследователь рынка | - |
| Analytics | [analytics.md](analytics.md) | Аналитик метрик | - |
| Business-Analyst | [business-analyst.md](business-analyst.md) | Бизнес-аналитик | - |

---

## Design (Дизайн)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| UX | [ux.md](ux.md) | UX Designer | - |
| UI | [ui.md](ui.md) | UI Designer | - |
| Content | [content.md](content.md) | Content Writer | - |

---

## Architecture (Архитектура)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| Architect | [architect.md](architect.md) | Software Architect | - |
| Data | [data.md](data.md) | Data Architect | - |
| Security | [security.md](security.md) | Security Engineer | - |

---

## Development (Разработка)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| Dev | [dev.md](dev.md) | Tech Lead | - |
| AI-Agents | [ai-agents.md](ai-agents.md) | Medical AI Architect (MCP + Claude) | - |
| Coder | [coder.md](coder.md) | Full-Stack Developer | Yes |

---

## Quality (Качество)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| QA | [qa.md](qa.md) | QA Engineer | Yes |
| Review | [review.md](review.md) | Code Reviewer | - |

---

## Operations (Эксплуатация)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| DevOps | [devops.md](devops.md) | DevOps Engineer | Yes |
| SRE | [sre.md](sre.md) | SRE | Yes |

---

## Marketing

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| Marketing | [marketing.md](marketing.md) | Marketing Manager | - |

---

## Medical (Медицина)

| Агент | Файл | Роль | SSH |
|-------|------|------|-----|
| Medical-Domain | [medical-domain.md](medical-domain.md) | Clinical Specialist (Медицинский доменный эксперт) | - |
| Compliance | [compliance.md](compliance.md) | Legal & Compliance Specialist (Регуляторный эксперт) | - |

**Ключевое правило:** `.claude/rules/05-medical-safety.md`

---

## Диаграмма взаимодействия

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │  (Координатор)  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐        ┌─────────┐        ┌──────────┐
    │Discovery│        │ Design  │        │   Arch   │
    ├─────────┤        ├─────────┤        ├──────────┤
    │Product  │        │UX       │        │Architect │
    │Research │───────▶│UI       │───────▶│Data      │
    │Analytics│        │Content  │        │Security  │
    │Biz-Anal │        └─────────┘        └────┬─────┘
    └─────────┘                                │
                                               ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │Marketing│        │   QA    │        │   Dev   │
    ├─────────┤        ├─────────┤        ├─────────┤
    │Marketing│◀───────│QA       │◀───────│Dev      │
    └─────────┘        │Review   │        │AI-Agents│
                       └────┬────┘        │Coder    │
                            │             └────┬────┘
                            ▼                  │
                       ┌─────────┐             │
                       │  Ops    │             │
                       ├─────────┤             │
                       │DevOps   │             │
                       │SRE      │             │
                       └─────────┘             │
                                               │
                       ┌───────────────────────┘
                       │ Medical Layer
                       ▼
                  ┌──────────┐     ┌────────────┐
                  │ Medical- │────▶│ Compliance │
                  │ Domain   │     │            │
                  └──────────┘     └────────────┘
                       │
                  Верификация клинической
                  корректности AI-агентов
```

### Медицинский поток (для AI-агентов)

```
Product → Medical-Domain → AI-Agents → Compliance → Dev → Coder →
  → Medical-Domain (review) → Review → QA → Deploy
```

---

## Агенты с SSH доступом

Следующие агенты имеют право выполнять SSH операции на серверах:

| Агент | Права | Типичные задачи |
|-------|-------|-----------------|
| **DevOps** | Полные | Deployment, CI/CD, инфраструктура |
| **SRE** | Полные | Мониторинг, инциденты, диагностика |
| **QA** | Deploy + Verify | Smoke tests, deployment verification |
| **Coder** | По запросу | Server debug, hotfix |

Подробнее: [../rules/03-ssh-operations.md](../rules/03-ssh-operations.md)

---

## Навыки агентов

Некоторые агенты используют специализированные навыки:

| Агент | Навыки |
|-------|--------|
| AI-Agents | clinical-reasoning, medical-knowledge-base, medical-api-integration, medical-imaging-ml, doctor-escalation |
| Medical-Domain | clinical-reasoning, medical-knowledge-base, medical-api-integration |
| Compliance | medical-data-compliance |
| Coder | ssh-deployment, medical-api-integration |
| DevOps | ssh-deployment, github-actions |
| SRE | ssh-deployment |
| QA | ssh-deployment |
| Research | web-research |
| All | context-manager, verification-engine, document-generator |

Полный список навыков: [../skills/INDEX.md](../skills/INDEX.md)

---

*Реестр агентов v1.1 | Aibolit AI — Claude Code Agent System*
